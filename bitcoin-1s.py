import asyncio
import json
import os
from datetime import datetime
import pytz
from websockets import connect
import pandas as pd
import numpy as np
from collections import defaultdict
from termcolor import cprint

WEBSOCKET_URL = 'wss://fstream.binance.com/ws/btcusdt@aggTrade'
OHLCV_FILENAME = 'bitcoin_1s_ohlcv.csv'

# Initialize the OHLCV file if it doesn't exist
if not os.path.isfile(OHLCV_FILENAME):
    with open(OHLCV_FILENAME, 'w') as f:
        f.write('datetime,open,high,low,close,volume\n')

class OHLCVAggregator:
    def __init__(self):
        self.current_second = None
        self.prices = []
        self.volume = 0
        self.last_save_time = None
    
    def process_trade(self, timestamp_ms, price, quantity):
        """Process a single trade and aggregate into 1-second OHLCV data"""
        timestamp_s = int(timestamp_ms / 1000)  # Convert to seconds
        
        # If this is a new second or first trade
        if self.current_second != timestamp_s:
            if self.current_second is not None:
                self._save_current_candle()
            
            self.current_second = timestamp_s
            self.prices = [price]
            self.volume = quantity
        else:
            self.prices.append(price)
            self.volume += quantity

    def _save_current_candle(self):
        """Save the current 1-second candle to CSV file and print to console"""
        if not self.prices:
            return
            
        candle = {
            'timestamp': self.current_second,
            'open': self.prices[0],
            'high': max(self.prices),
            'low': min(self.prices),
            'close': self.prices[-1],
            'volume': self.volume
        }
        
        est = pytz.timezone('US/Central')
        # Format datetime as YYYY-MM-DD HH:MM:SS
        readable_time = datetime.fromtimestamp(self.current_second, est).strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to file in the requested format
        with open(OHLCV_FILENAME, 'a') as f:
            f.write(f"{readable_time},{candle['open']:.2f},{candle['high']:.2f},"
                   f"{candle['low']:.2f},{candle['close']:.2f},{candle['volume']:.8f}\n")
        
        # Print to console with color
        price_change = candle['close'] - candle['open']
        color = 'green' if price_change >= 0 else 'red'
        
        # Print in the requested format
        output = (
            f"{readable_time},"
            f"{candle['open']:.2f},"
            f"{candle['high']:.2f},"
            f"{candle['low']:.2f},"
            f"{candle['close']:.2f},"
            f"{candle['volume']:.8f}"
        )
        
        cprint(output, color, attrs=['bold'] if abs(price_change) > 0.1 else [])

async def collect_trades():
    aggregator = OHLCVAggregator()
    
    while True:
        try:
            async with connect(WEBSOCKET_URL) as websocket:
                print(f"Connected to Binance WebSocket feed for BTC-USDT")
                
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    trade_time = int(data['T'])  # Trade time
                    price = float(data['p'])     # Price
                    quantity = float(data['q'])   # Quantity
                    
                    aggregator.process_trade(trade_time, price, quantity)
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

async def main():
    print(f"Starting Bitcoin 1-second OHLCV data collection...")
    print(f"Data will be saved to: {OHLCV_FILENAME}")
    await collect_trades()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nData collection stopped by user")
