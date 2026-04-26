# Technology Stack

## Shell Version

**Language:** Python 3.8+

**Dependencies:**
- `requests` - HTTP client for CPA API calls
- `concurrent.futures` - Parallel processing for batch operations

**Key Files:**
- `shell/manage_accounts.py` - Main interactive CLI tool
- `shell/config.json` - Server configuration

**Common Commands:**
```bash
# Run the interactive menu
python manage_accounts.py

# Setup virtual environment (if needed)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install requests
```

## Cloudflare Version

**Runtime:** Cloudflare Workers (Edge Computing)

**Language:** JavaScript (ES6+)

**Infrastructure:**
- Cloudflare Workers - Serverless compute
- Cloudflare KV - Key-value storage for configuration
- Cloudflare D1 - SQLite database for backups and logs
- Cloudflare Cron Triggers - Scheduled tasks

**Build Tool:** Wrangler CLI v3.0+

**Dependencies:**
```json
{
  "devDependencies": {
    "wrangler": "^3.0.0"
  }
}
```

**Common Commands:**
```bash
# Install dependencies
npm install

# Local development
npm run dev
wrangler dev

# Deploy to production
npm run deploy
wrangler deploy

# Database operations
npm run d1:create
npm run d1:migrate:remote
wrangler d1 migrations apply cpa-manager-db --remote

# KV namespace operations
npm run kv:create
wrangler kv:namespace create ACCOUNTS

# View logs
npm run tail
wrangler tail

# Manage secrets
wrangler secret put ADMIN_USERNAME
wrangler secret put ADMIN_PASSWORD
```

## Web Version

**Backend:** Flask 3.0.0 (Python)

**Database:** SQLite

**Task Scheduler:** APScheduler 3.10.4

**Dependencies:**
```
Flask==3.0.0
Flask-Login==0.6.3
APScheduler==3.10.4
requests==2.31.0
PyYAML==6.0.1
python-dotenv==1.0.0
Werkzeug==3.0.1
```

**Frontend:** 
- Bootstrap 5
- Vanilla JavaScript (no build step)

**Deployment:** Docker + Docker Compose

**Common Commands:**
```bash
# Docker deployment (recommended)
docker-compose up -d
docker-compose down
docker-compose logs -f

# Local development - Windows
setup.bat
run.bat

# Local development - Linux/macOS
chmod +x setup.sh run.sh
./setup.sh
./run.sh

# Manual setup
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python app.py

# Database operations
# Database auto-initializes on first run
# To reset: delete data/cpa_manager.db and restart
```

## Development Conventions

**Code Style:**
- Python: Follow PEP 8
- JavaScript: ES6+ with async/await for async operations
- Use try-catch for error handling
- Clear, descriptive function names

**API Design:**
- RESTful endpoints
- JSON request/response format
- Token-based authentication
- Standard HTTP status codes

**Error Handling:**
- Graceful degradation
- Detailed error messages in logs
- User-friendly error messages in UI
- Retry logic for network operations (max 3 attempts)

**Concurrency:**
- Default worker pool: 10 threads
- Use `Promise.all()` (JS) or `concurrent.futures` (Python) for batch operations
- Configurable via `max_workers` setting

## Testing

**Cloudflare:**
```bash
# Local testing
wrangler dev
curl http://localhost:8787/api/stats/overview

# Test deployment
wrangler deploy --env dev
```

**Web:**
```bash
# Run Flask in debug mode
FLASK_ENV=development python app.py

# Test endpoints
curl http://localhost:5000/health
```

## Configuration Files

**Shell:** `shell/config.json`
**Cloudflare:** `cf/wrangler.toml` + Wrangler secrets
**Web:** `web/config.json` + `web/.env`

All versions support multi-server configuration with the same JSON structure.
