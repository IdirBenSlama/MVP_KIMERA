# KIMERA SWM Installation Guide

## Complete Installation Documentation

This guide provides comprehensive instructions for installing and configuring the KIMERA SWM (Semantic Working Memory) system across different environments and deployment scenarios.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Installation](#quick-installation)
3. [Development Setup](#development-setup)
4. [Production Deployment](#production-deployment)
5. [Docker Installation](#docker-installation)
6. [Configuration](#configuration)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

#### Minimum Requirements
```
Hardware:
├── CPU: 2 cores, 2.0 GHz
├── Memory: 4GB RAM
├── Storage: 10GB available space
└── Network: Internet connection for dependencies

Software:
├── Python 3.12 or higher
├── pip (Python package manager)
├── Git (for source code)
└── SQLite (included with Python)
```

#### Recommended Requirements
```
Hardware:
├── CPU: 4+ cores, 3.0 GHz
├── Memory: 8GB+ RAM
├── Storage: 50GB+ SSD
└── Network: Stable broadband connection

Software:
├── Python 3.12+
├── PostgreSQL 13+ (for production)
├── Redis (for caching)
└── Docker (for containerized deployment)
```

### Operating System Support

| OS | Version | Status | Notes |
|---|---|---|---|
| **Windows** | 10, 11 | ✅ Fully Supported | Tested on Windows 11 |
| **macOS** | 10.15+ | ✅ Fully Supported | Intel and Apple Silicon |
| **Linux** | Ubuntu 20.04+, CentOS 8+ | ✅ Fully Supported | Recommended for production |
| **Docker** | Any OS with Docker | ✅ Fully Supported | Cross-platform |

### Python Version Compatibility

| Python Version | Status | Notes |
|---|---|---|
| **3.12** | ✅ Recommended | Fully tested and validated |
| **3.11** | ✅ Supported | Compatible with minor limitations |
| **3.10** | ⚠️ Limited Support | Some features may not work |
| **3.9 and below** | ❌ Not Supported | Incompatible |

---

## Quick Installation

### 1. Clone Repository

```bash
# Clone the KIMERA SWM repository
git clone https://github.com/your-org/kimera-swm.git
cd kimera-swm

# Verify repository structure
ls -la
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Basic Configuration

```bash
# Copy example configuration
cp config/example.env .env

# Edit configuration (optional for quick start)
# The system will work with default settings
```

### 4. Start System

```bash
# Start KIMERA SWM system
python run_kimera.py
```

### 5. Verify Installation

```bash
# Test API endpoint
curl http://localhost:8001/system/status

# Expected response:
# {"status": "healthy", "version": "1.0.0", ...}
```

---

## Development Setup

### 1. Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/kimera-swm.git
cd kimera-swm

# Create development virtual environment
python -m venv venv-dev
source venv-dev/bin/activate  # or venv-dev\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Development Configuration

Create development configuration file:

```bash
# Create development environment file
cat > .env.development << EOF
# Development Configuration
DEBUG=true
ENVIRONMENT=development
DATABASE_URL=sqlite:///./dev_kimera.db
LIGHTWEIGHT_EMBEDDING=1
ENABLE_JOBS=0
LOG_LEVEL=DEBUG
API_HOST=localhost
API_PORT=8001
EOF
```

### 3. Development Tools Setup

```bash
# Install pre-commit hooks
pre-commit install

# Install code formatting tools
pip install black flake8 mypy

# Setup IDE configuration (VS Code example)
mkdir .vscode
cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./venv-dev/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
EOF
```

### 4. Database Setup (Development)

```bash
# Initialize development database
python scripts/init_database.py --env=development

# Run database migrations
python scripts/migrate_database.py

# Seed with test data (optional)
python scripts/seed_test_data.py
```

### 5. Run Development Server

```bash
# Start development server with auto-reload
python run_kimera.py --env=development --reload

# Or use uvicorn directly for more control
uvicorn backend.api.main:app --reload --host localhost --port 8001
```

### 6. Development Testing

```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test categories
pytest -m "unit" -v
pytest -m "integration" -v
```

---

## Production Deployment

### 1. Production Environment Setup

#### Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3.12 python3.12-venv python3-pip git nginx postgresql postgresql-contrib redis-server

# Create application user
sudo useradd -m -s /bin/bash kimera
sudo usermod -aG sudo kimera
```

#### Application Deployment

```bash
# Switch to application user
sudo su - kimera

# Clone repository
git clone https://github.com/your-org/kimera-swm.git /opt/kimera-swm
cd /opt/kimera-swm

# Create production virtual environment
python3.12 -m venv venv-prod
source venv-prod/bin/activate

# Install production dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 2. Database Setup (Production)

#### PostgreSQL Configuration

```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb kimera_prod
createuser kimera_user
psql -c "ALTER USER kimera_user WITH PASSWORD 'secure_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE kimera_prod TO kimera_user;"

# Enable required extensions
psql kimera_prod -c "CREATE EXTENSION IF NOT EXISTS pgvector;"
```

#### Database Migration

```bash
# Return to application user
sudo su - kimera
cd /opt/kimera-swm
source venv-prod/bin/activate

# Set production database URL
export DATABASE_URL="postgresql://kimera_user:secure_password@localhost/kimera_prod"

# Run migrations
python scripts/migrate_database.py --env=production
```

### 3. Production Configuration

Create production configuration:

```bash
# Create production environment file
cat > /opt/kimera-swm/.env.production << EOF
# Production Configuration
DEBUG=false
ENVIRONMENT=production
DATABASE_URL=postgresql://kimera_user:secure_password@localhost/kimera_prod
LIGHTWEIGHT_EMBEDDING=0
ENABLE_JOBS=1
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
REDIS_URL=redis://localhost:6379/0

# Security settings
SECRET_KEY=your-secret-key-here
API_KEY_REQUIRED=true
CORS_ORIGINS=["https://yourdomain.com"]

# Performance settings
MAX_CONCURRENT_THREADS=13
CACHE_TTL=300
BATCH_SIZE=100

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
EOF
```

### 4. Process Management

#### Systemd Service

```bash
# Create systemd service file
sudo cat > /etc/systemd/system/kimera-swm.service << EOF
[Unit]
Description=KIMERA SWM API Server
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=kimera
Group=kimera
WorkingDirectory=/opt/kimera-swm
Environment=PATH=/opt/kimera-swm/venv-prod/bin
EnvironmentFile=/opt/kimera-swm/.env.production
ExecStart=/opt/kimera-swm/venv-prod/bin/gunicorn backend.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable kimera-swm
sudo systemctl start kimera-swm

# Check service status
sudo systemctl status kimera-swm
```

### 5. Reverse Proxy Setup

#### Nginx Configuration

```bash
# Create Nginx configuration
sudo cat > /etc/nginx/sites-available/kimera-swm << EOF
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # API proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }

    # Metrics endpoint (restrict access)
    location /metrics {
        proxy_pass http://127.0.0.1:8000/metrics;
        allow 10.0.0.0/8;
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;
        deny all;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/kimera-swm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Monitoring Setup

#### Prometheus Configuration

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kimera-swm'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

#### Log Management

```bash
# Configure log rotation
sudo cat > /etc/logrotate.d/kimera-swm << EOF
/opt/kimera-swm/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 kimera kimera
    postrotate
        systemctl reload kimera-swm
    endscript
}
EOF
```

---

## Docker Installation

### 1. Docker Compose Setup

Create Docker Compose configuration:

```yaml
# docker-compose.yml
version: '3.8'

services:
  kimera-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://kimera:password@postgres:5432/kimera
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=kimera
      - POSTGRES_USER=kimera
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - kimera-api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 2. Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 kimera && chown -R kimera:kimera /app
USER kimera

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["gunicorn", "backend.api.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### 3. Docker Deployment

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f kimera-api

# Scale API service
docker-compose up -d --scale kimera-api=3

# Update application
docker-compose pull
docker-compose up -d --force-recreate
```

---

## Configuration

### Environment Variables

#### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `ENVIRONMENT` | `production` | Environment name |
| `DATABASE_URL` | `sqlite:///./kimera.db` | Database connection string |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8001` | API server port |

#### Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `LIGHTWEIGHT_EMBEDDING` | `0` | Use lightweight embeddings |
| `ENABLE_JOBS` | `1` | Enable background jobs |
| `ENABLE_METRICS` | `true` | Enable metrics collection |
| `API_KEY_REQUIRED` | `false` | Require API key authentication |

#### Performance Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_CONCURRENT_THREADS` | `13` | Maximum concurrent threads |
| `CACHE_TTL` | `300` | Cache time-to-live (seconds) |
| `BATCH_SIZE` | `100` | Batch processing size |
| `TIMEOUT` | `30` | Request timeout (seconds) |

### Configuration Files

#### Main Configuration

```python
# config/settings.py
import os
from typing import Optional

class Settings:
    # Core settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./kimera.db")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_KEY_REQUIRED: bool = os.getenv("API_KEY_REQUIRED", "false").lower() == "true"
    
    # Performance settings
    MAX_CONCURRENT_THREADS: int = int(os.getenv("MAX_CONCURRENT_THREADS", "13"))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))
    
    # Feature flags
    LIGHTWEIGHT_EMBEDDING: bool = os.getenv("LIGHTWEIGHT_EMBEDDING", "0") == "1"
    ENABLE_JOBS: bool = os.getenv("ENABLE_JOBS", "1") == "1"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"

settings = Settings()
```

---

## Verification

### 1. Installation Verification

```bash
# Check system status
curl http://localhost:8001/system/status

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 123,
  "system_metrics": {
    "active_geoids": 0,
    "total_scars": 0,
    "system_entropy": 0.0
  }
}
```

### 2. API Functionality Test

```bash
# Create a test geoid
curl -X POST http://localhost:8001/geoids \
  -H "Content-Type: application/json" \
  -d '{
    "semantic_features": {"test": 0.5},
    "symbolic_content": {"type": "verification"},
    "metadata": {"source": "installation_test"}
  }'

# Expected response includes geoid_id
```

### 3. Database Connectivity Test

```bash
# Check database health
curl http://localhost:8001/health/detailed

# Verify database component shows "healthy"
```

### 4. Performance Verification

```bash
# Run basic performance test
python tests/verification/basic_performance_test.py

# Expected: All tests pass with acceptable performance
```

### 5. Integration Test

```bash
# Run integration test suite
pytest tests/integration/test_installation.py -v

# Expected: All integration tests pass
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Problem**: `Address already in use` error

**Solution**:
```bash
# Find process using port 8001
lsof -i :8001  # On macOS/Linux
netstat -ano | findstr :8001  # On Windows

# Kill the process
kill -9 <PID>  # On macOS/Linux
taskkill /PID <PID> /F  # On Windows

# Or use different port
python run_kimera.py --port 8002
```

#### 2. Database Connection Issues

**Problem**: Database connection errors

**Solution**:
```bash
# Check database service
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS

# Test connection manually
psql -h localhost -U kimera_user -d kimera_prod

# Check connection string format
export DATABASE_URL="postgresql://user:password@host:port/database"
```

#### 3. Python Version Issues

**Problem**: Incompatible Python version

**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.12 if needed
# Ubuntu/Debian:
sudo apt install python3.12 python3.12-venv

# macOS with Homebrew:
brew install python@3.12

# Windows: Download from python.org
```

#### 4. Dependency Installation Issues

**Problem**: Package installation failures

**Solution**:
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Use alternative index if needed
pip install -r requirements.txt -i https://pypi.org/simple/

# Install system dependencies (Ubuntu/Debian)
sudo apt install python3-dev build-essential
```

#### 5. Permission Issues

**Problem**: Permission denied errors

**Solution**:
```bash
# Fix file permissions
chmod +x run_kimera.py
chmod -R 755 /opt/kimera-swm

# Fix ownership
sudo chown -R kimera:kimera /opt/kimera-swm

# Use virtual environment
python -m venv venv
source venv/bin/activate
```

### Diagnostic Commands

#### System Diagnostics

```bash
# Check system resources
free -h  # Memory usage
df -h    # Disk usage
top      # CPU usage

# Check network connectivity
curl -I http://localhost:8001/health
netstat -tlnp | grep 8001

# Check logs
tail -f /opt/kimera-swm/logs/kimera.log
journalctl -u kimera-swm -f
```

#### Application Diagnostics

```bash
# Check Python environment
python -c "import sys; print(sys.version)"
pip list | grep -E "(fastapi|uvicorn|sqlalchemy)"

# Test imports
python -c "from backend.api.main import app; print('Import successful')"

# Check configuration
python -c "from config.settings import settings; print(settings.DATABASE_URL)"
```

### Getting Help

#### Support Channels

1. **Documentation**: Check this installation guide and API documentation
2. **GitHub Issues**: Report bugs and request features
3. **Community Forum**: Ask questions and share experiences
4. **Professional Support**: Contact support team for enterprise assistance

#### Reporting Issues

When reporting installation issues, please include:

1. Operating system and version
2. Python version
3. Complete error messages
4. Installation steps attempted
5. System resource information
6. Log files (if available)

---

This comprehensive installation guide ensures successful deployment of KIMERA SWM across various environments and use cases.
