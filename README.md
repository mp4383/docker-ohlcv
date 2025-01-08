# docker-ohlcv

Real-time cryptocurrency price monitoring system that collects and stores 1-second OHLCV (Open, High, Low, Close, Volume) data for Bitcoin and Solana from Binance. My primary purpose is data collection for scalping strategies that require 1-second data.

## Features

- Real-time price monitoring via Binance WebSocket feeds
- 1-second OHLCV (Open, High, Low, Close, Volume) data aggregation
- Colored console output (green for price increases, red for decreases)
- Automatic data storage in CSV format
- Docker containerization for easy deployment
- Automatic reconnection on connection failures
- Timezone support (US/Central)

## Prerequisites

- Docker
- Docker Compose

## Installation & Setup

1. Clone the repository:
```
git clone https://github.com/mp4383/docker-ohlcv.git
cd docker-ohlcv
```

2. Build the Docker images:
```
docker-compose build
```

3. Start the containers:
```
docker-compose up -d
```

### Start individual containers
```
docker-compose up solana_feed
docker-compose up bitcoin_feed
```

## View logs
```
docker-compose logs -f solana_feed
docker-compose logs -f bitcoin_feed
```

## Data Output

The system creates two CSV files:
- `bitcoin_1s_ohlcv.csv`: Bitcoin price data
- `solana_1s_ohlcv.csv`: Solana price data

Each file contains the following columns:
- datetime: Timestamp in YYYY-MM-DD HH:MM:SS format
- open: Opening price for the 1-second period
- high: Highest price during the period
- low: Lowest price during the period
- close: Closing price for the period
- volume: Trading volume during the period

## Console Output

The console displays real-time price updates with color coding:
- Green: Price increased
- Red: Price decreased
- Bold: Significant price changes (>$100 for Bitcoin, >$0.1 for Solana)

Example output:
2024-02-20 10:30:01,52000.00,52010.50,51995.00,52005.25,1.23456789
2024-02-20 10:30:02,52005.25,52015.75,52000.00,52010.00,0.98765432

## Stopping the Service

To stop the monitors:
```
docker-compose down
```

## Stop individual containers
```
docker stop bitcoin_feed solana_feed
docker stop solana_feed
```