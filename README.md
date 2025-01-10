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
```
2024-02-20 10:30:01,52000.00,52010.50,51995.00,52005.25,1.23456789
2024-02-20 10:30:02,52005.25,52015.75,52000.00,52010.00,0.98765432
```

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

## AWS EC2 Deployment

### 1. Launch EC2 Instance
- Launch a t3.micro or t3.small instance
- Use Amazon Linux 2023 or Ubuntu
- Ensure security group allows outbound internet access

### 2. Install Docker
For Amazon Linux 2023:
```bash
sudo dnf update -y
sudo dnf install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user
```

For Ubuntu:
```bash
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ubuntu
```

### 3. Configure AWS Credentials
Create a `.env` file in your project directory:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

### 4. Deploy Application
```bash
# Clone repository
git clone https://github.com/yourusername/docker-ohlcv.git
cd docker-ohlcv

# Create data directory
mkdir -p data

# Start the container
docker-compose up -d
```

### 5. Monitor Logs
```bash
# View logs
docker-compose logs -f
```

### 6. Auto-start on Instance Launch (Optional)
Create a startup script:
```bash
#!/bin/bash
cd /home/ec2-user/docker-ohlcv
docker-compose up -d
```

Or add to EC2 User Data:
```bash
#!/bin/bash
cd /home/ec2-user
git clone https://github.com/yourusername/docker-ohlcv.git
cd docker-ohlcv
docker-compose up -d
```

### 7. Monitoring with CloudWatch (Optional)
Install and configure CloudWatch agent:
```bash
# Install CloudWatch agent
sudo yum install amazon-cloudwatch-agent -y

# Configure CloudWatch
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

### Data Storage
- CSV files are stored in the `data` directory
- Data is automatically uploaded to S3 every hour
- Local files older than 7 days are automatically cleaned up
- SQLite database provides queryable access to recent data

### Accessing Data
- CSV files are available in the `data` directory
- Use the DBHandler to query or export specific date ranges:
```python
from db_handler import DBHandler

db = DBHandler()
db.export_to_csv('btcusdt', '2024-01-01', '2024-01-02', 'btc_export.csv')
```