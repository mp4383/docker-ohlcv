import websockets
import json
import pandas as pd
from datetime import datetime
import pytz
import asyncio
import yaml
from termcolor import colored
import logging
import os
from data_uploader import DataUploader
from db_handler import DBHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

class PriceFeed:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.tz = pytz.timezone('US/Central')
        self.current_tick = {
            'open': None,
            'high': None,
            'low': None,
            'close': None,
            'volume': 0
        }
        self.last_price = None
        self.csv_filename = f"data/{symbol.lower()}_1s_ohlcv.csv"
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        self.db = DBHandler()

    async def process_trades(self):
        while True:
            try:
                uri = f"wss://fstream.binance.com/ws/{self.symbol.lower()}@aggTrade"
                async with websockets.connect(uri) as websocket:
                    logger.info(f"Connected to {self.symbol} feed")
                    
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if 'p' in data:
                            price = float(data['p'])
                            volume = float(data['q'])
                            
                            if self.current_tick['open'] is None:
                                self.current_tick['open'] = price
                                self.current_tick['high'] = price
                                self.current_tick['low'] = price
                            else:
                                self.current_tick['high'] = max(self.current_tick['high'], price)
                                self.current_tick['low'] = min(self.current_tick['low'], price)
                            
                            self.current_tick['close'] = price
                            self.current_tick['volume'] += volume
                            
                            # Color output based on price movement
                            if self.last_price:
                                if price > self.last_price:
                                    color = 'green'
                                elif price < self.last_price:
                                    color = 'red'
                                else:
                                    color = 'white'
                                
                                # Bold significant price changes
                                attrs = ['bold'] if abs(price - self.last_price) > (100 if 'BTC' in self.symbol else 0.1) else None
                                print(colored(f"{self.symbol}: {price}", color, attrs=attrs))
                            else:
                                print(colored(f"{self.symbol}: {price}", 'white'))
                            
                            self.last_price = price
                            
            except Exception as e:
                logger.error(f"Error in {self.symbol} feed: {str(e)}")
                await asyncio.sleep(5)

    async def save_ticks(self):
        while True:
            try:
                await asyncio.sleep(1)
                
                if self.current_tick['open'] is not None:
                    timestamp = datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')
                    data = {
                        'datetime': timestamp,
                        'open': self.current_tick['open'],
                        'high': self.current_tick['high'],
                        'low': self.current_tick['low'],
                        'close': self.current_tick['close'],
                        'volume': self.current_tick['volume']
                    }
                    
                    # Save to both CSV and SQLite
                    df = pd.DataFrame([data])
                    df.to_csv(self.csv_filename, mode='a', header=not os.path.exists(self.csv_filename), index=False)
                    self.db.save_tick(self.symbol, data)
                    
                    # Reset tick data
                    self.current_tick = {
                        'open': None,
                        'high': None,
                        'low': None,
                        'close': None,
                        'volume': 0
                    }
            except Exception as e:
                logger.error(f"Error saving tick for {self.symbol}: {str(e)}")
                await asyncio.sleep(1)

    async def upload_task(self):
        """Periodic upload to S3"""
        # Load config
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        bucket_name = config.get('s3', {}).get('bucket_name')
        if not bucket_name:
            raise ValueError("S3 bucket name not configured in config.yml")
        
        uploader = DataUploader(bucket_name)
        while True:
            await asyncio.sleep(3600)  # Upload every hour
            await uploader.upload_and_cleanup()

    async def run(self):
        # Run both the trade processing and tick saving concurrently
        await asyncio.gather(
            self.process_trades(),
            self.save_ticks(),
            self.upload_task()
        )

async def main():
    try:
        # Load configuration
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        if not config or 'symbols' not in config or not config['symbols']:
            raise ValueError("No symbols configured in config.yml")
        
        # Create price feed tasks for each symbol
        feeds = [PriceFeed(symbol) for symbol in config['symbols']]
        tasks = [feed.run() for feed in feeds]
        
        # Run all feeds concurrently
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Main loop error: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}") 