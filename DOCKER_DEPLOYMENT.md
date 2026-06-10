# Docker Deployment Guide

Complete Docker setup for production deployment with PostgreSQL, Redis, and Nginx.

---

## 📦 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ RAM
- 20GB+ disk space

---

## 🐳 Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
```

---

## 🔧 Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.9'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: salon_postgres
    environment:
      POSTGRES_DB: salon_booking_prod
      POSTGRES_USER: salon_user
      POSTGRES_PASSWORD: strong_password_here_change_me
      POSTGRES_INITDB_ARGS: "--encoding=UTF8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - salon_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U salon_user -d salon_booking_prod"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: salon_redis
    command: redis-server --requirepass redis_password_here_change_me --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - salon_network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Telegram Bot Application
  bot:
    build: .
    container_name: salon_bot
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      ADMIN_ID: ${ADMIN_ID}
      DATABASE_URL: postgresql://salon_user:strong_password_here_change_me@postgres:5432/salon_booking_prod
      REDIS_URL: redis://:redis_password_here_change_me@redis:6379/0
      SERVER_HOST: 0.0.0.0
      SERVER_PORT: 8000
      WEBHOOK_URL: ${WEBHOOK_URL}
      WEBHOOK_PATH: /webhook
      JWT_SECRET: ${JWT_SECRET}
      ENVIRONMENT: production
      DEBUG: "False"
      LOG_LEVEL: INFO
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    ports:
      - "8000:8000"
    networks:
      - salon_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: salon_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - bot
    networks:
      - salon_network
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  salon_network:
    driver: bridge
```

---

## 🌐 Nginx Configuration

Create `nginx.conf`:

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=webhook_limit:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=50r/s;

    upstream bot_backend {
        server bot:8000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name _;
        location / {
            return 301 https://$host$request_uri;
        }
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # Webhook endpoint with rate limiting
        location /webhook {
            limit_req zone=webhook_limit burst=200;
            proxy_pass http://bot_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 30s;
        }

        # API endpoints with rate limiting
        location /api/ {
            limit_req zone=api_limit burst=50;
            proxy_pass http://bot_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://bot_backend;
            proxy_set_header Host $host;
            access_log off;
        }

        # Default location
        location / {
            proxy_pass http://bot_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 🚀 Deployment Steps

### 1. Prepare Environment

```bash
# Clone repository
git clone https://github.com/molebelr-crypto/Salon-Booking-.git
cd Salon-Booking-

# Create .env file
cat > .env << EOF
BOT_TOKEN=your_new_regenerated_token_here
ADMIN_ID=your_telegram_admin_id
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
WEBHOOK_URL=https://your-domain.com
ENVIRONMENT=production
EOF

# Create logs directory
mkdir -p logs/nginx
```

### 2. Setup SSL Certificate (Let's Encrypt)

```bash
# Using Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com

# Copy to project
mkdir -p ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/
sudo chown $USER:$USER ssl/*
```

### 3. Build and Start

```bash
# Build Docker image
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f bot
```

### 4. Initialize Database

```bash
# Run migrations/init
docker-compose exec bot python -c "from database import init_db; init_db()"

# Verify
docker-compose exec postgres psql -U salon_user -d salon_booking_prod -c "\dt"
```

### 5. Configure Telegram Webhook

```bash
# Set webhook
BOT_TOKEN="your_token_here"
WEBHOOK_URL="https://your-domain.com/webhook"

curl -X POST https://api.telegram.org/bot${BOT_TOKEN}/setWebhook \
  -d "url=${WEBHOOK_URL}" \
  -d "max_connections=40" \
  -d "allowed_updates=message,callback_query"

# Verify
curl https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo
```

---

## 📊 Monitoring

```bash
# View all container logs
docker-compose logs -f

# Follow bot logs
docker-compose logs -f bot

# Follow Nginx logs
docker-compose logs -f nginx

# View resource usage
docker stats

# Check container health
docker-compose ps
```

---

## 🔄 Auto-Renewal SSL Certificate

Create `renew-cert.sh`:

```bash
#!/bin/bash

# Renew certificate
certbot renew --quiet

# Copy to project
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/

# Restart Nginx
docker-compose restart nginx

echo "Certificate renewed at $(date)" >> logs/cert_renewal.log
```

Add to crontab:
```bash
0 2 * * * /path/to/renew-cert.sh
```

---

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose down

# Stop with volume cleanup
docker-compose down -v

# Restart specific service
docker-compose restart bot

# Rebuild and restart
docker-compose up --build -d
```

---

## 🔧 Troubleshooting

### Check logs
```bash
docker-compose logs bot | grep ERROR
```

### Test database connection
```bash
docker-compose exec postgres psql -U salon_user -d salon_booking_prod
```

### Test Redis connection
```bash
docker-compose exec redis redis-cli ping
```

### Restart all services
```bash
docker-compose restart
```

---

## 📈 Scaling

For production with high traffic:

```yaml
# Add this to docker-compose.yml for multiple bot instances

  bot-2:
    build: .
    depends_on:
      - postgres
      - redis
    # ... (same config as bot)
    container_name: salon_bot_2

  bot-3:
    build: .
    depends_on:
      - postgres
      - redis
    # ... (same config as bot)
    container_name: salon_bot_3

# Update Nginx upstream to:
upstream bot_backend {
    server bot:8000;
    server bot-2:8000;
    server bot-3:8000;
}
```

---

**Ready for production deployment! 🚀**
