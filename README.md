# docker-ohlcv

Real-time cryptocurrency price monitoring system that collects and stores 1-second OHLCV (Open, High, Low, Close, Volume) data from Binance Futures. Configure symbols in config.yml.

## Features
- Real-time futures price monitoring via Binance WebSocket
- 1-second OHLCV data aggregation
- Automatic hourly S3 uploads
- SQLite database for local querying
- Docker containerized
- Configurable symbols via config.yml

## AWS Deployment

### 1. EC2 Setup
Launch an EC2 instance:
- Instance type: t2.micro (whatever is cheapest/free)
- OS: Amazon Linux 2023
- Security group: Allow outbound traffic

### 2. IAM Role
- Create a new IAM role that has S3 read/write permissions
- Attach this role to your EC2 instance

### 3. Install Docker
After ssh'ing into your instance, run the following commands:
```bash
# Update system
sudo dnf update -y

# Install Docker
sudo dnf install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# Apply group changes
groups ec2-user
```

### 4. Deploy Application
```bash
# Clone repository
git clone https://github.com/yourusername/docker-ohlcv.git
cd docker-ohlcv

# Create data directory
mkdir -p data

# Configure symbols
nano config.yml

# Build and start
docker compose build
docker compose up -d
```

### 5. Monitor
```bash
# View logs
docker-compose logs -f
```

### 6. Data Management
- CSV files stored in `data/` directory
- Hourly uploads to S3 in format: `YYYY/MM/DD/symbol_1s_ohlcv.csv`
- Local files older than 7 days automatically cleaned up
- Query recent data via SQLite:
```python
from db_handler import DBHandler

db = DBHandler()
db.export_to_csv('btcusdt', '2024-01-01', '2024-01-02', 'btc_export.csv')
```

### 7. Auto-start (Optional)
Add to EC2 User Data:
```bash
#!/bin/bash
cd /home/ec2-user
git clone https://github.com/yourusername/docker-ohlcv.git
cd docker-ohlcv
docker-compose up -d
```