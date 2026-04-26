# Project Structure

## Repository Layout

```
CPAOM/
├── shell/              # Command-line version
├── cf/                 # Cloudflare Workers version
├── web/                # Flask web version
├── README.md           # Main documentation with version comparison
└── DEPLOYMENT_SUMMARY.md
```

## Shell Version Structure

```
shell/
├── manage_accounts.py          # Main CLI tool (recommended)
├── config.json                 # Multi-server configuration
├── pool/                       # Downloaded account backups (*.zip)
├── .venv/                      # Python virtual environment
└── README.md
```

**Key Concepts:**
- Single-file CLI tool with interactive menu
- No persistent storage (stateless)
- Downloads saved to `pool/` directory with format `YYYYMMDD-count.zip`
- Supports both single-server and multi-server config formats

## Cloudflare Version Structure

```
cf/
├── src/
│   ├── index.js                # Worker entry point
│   ├── static.js               # Static file serving
│   ├── api/                    # API layer (modular)
│   │   ├── router.js           # Route dispatcher + auth middleware
│   │   ├── auth.js             # Login/logout endpoints
│   │   ├── servers.js          # Server CRUD operations
│   │   ├── accounts.js         # Account management
│   │   ├── operations.js       # Batch operations
│   │   ├── stats.js            # Statistics endpoints
│   │   ├── sync.js             # Data sync/backup
│   │   └── scheduled.js        # Cron job handlers
│   ├── utils/                  # Utility modules
│   │   ├── cors.js             # CORS configuration
│   │   ├── cpa-client.js       # CPA API client wrapper
│   │   ├── oauth.js            # OAuth token refresh logic
│   │   ├── db-service.js       # D1 database operations
│   │   └── cron-parser.js      # Cron expression parser
│   └── frontend/
│       └── index.html.js       # SPA embedded in Worker
├── migrations/
│   └── 0001_initial_schema.sql # D1 database schema
├── docs/                       # Comprehensive documentation
├── wrangler.toml               # Cloudflare configuration
├── package.json
├── setup.sh / setup.bat        # Automated deployment scripts
└── README.md
```

**Key Concepts:**
- Single Worker handles all routes (API + static files)
- Frontend is embedded as JavaScript string (no build step)
- KV stores: server configs, sessions, temporary data
- D1 stores: operation logs, backups, statistics
- Modular API design - each endpoint in separate file

## Web Version Structure

```
web/
├── app.py                      # Flask application entry point
├── requirements.txt            # Python dependencies
├── config.json.example         # Configuration template
├── .env.example                # Environment variables template
├── Dockerfile                  # Container image definition
├── docker-compose.yml          # Multi-container orchestration
├── setup.sh / setup.bat        # Setup scripts
├── run.sh / run.bat            # Run scripts
├── utils/                      # Business logic modules
│   ├── __init__.py
│   ├── db_service.py           # SQLite operations
│   ├── cpa_client.py           # CPA API client
│   ├── config_manager.py       # Config file management
│   └── scheduler.py            # APScheduler setup
├── routes/                     # Flask blueprints (one per feature)
│   ├── __init__.py
│   ├── auth.py                 # Authentication routes
│   ├── servers.py              # Server management
│   ├── accounts.py             # Account operations
│   ├── operations.py           # Batch operations
│   ├── stats.py                # Statistics
│   ├── sync.py                 # Sync/backup
│   └── tasks.py                # Scheduled tasks
├── templates/                  # Jinja2 templates
│   ├── base.html               # Base layout with sidebar
│   ├── dashboard.html          # Main dashboard
│   ├── 404.html / 500.html     # Error pages
│   └── auth/
│       └── login.html          # Login page
├── data/                       # Runtime data (created on first run)
│   └── cpa_manager.db          # SQLite database
└── pool/                       # Temporary files (created on first run)
```

**Key Concepts:**
- Blueprint-based routing (modular design)
- SQLite for all persistent data
- Templates use Jinja2 + Bootstrap 5
- APScheduler for background tasks
- Flask-Login for session management

## Shared Patterns Across Versions

### Configuration Format

All versions use the same multi-server config structure:

```json
{
  "cpa_servers": [
    {
      "id": "server1",
      "name": "Display Name",
      "base_url": "https://cpa-server.com",
      "token": "mgt-xxx",
      "enable_token_revive": true
    }
  ],
  "settings": {
    "max_workers": 10
  }
}
```

### API Client Pattern

Each version has a `cpa-client` or `cpa_client` module that wraps CPA server API calls:
- `GET /v0/management/auth-files` - List accounts
- `GET /v0/management/auth-files/{filename}` - Download auth file
- `POST /v0/management/auth-files` - Upload auth file
- `PATCH /v0/management/auth-files/status` - Enable/disable account
- `GET /v0/management/stats/usage` - Usage statistics

### Token Revival Flow

Consistent across all versions:
1. Detect 401 error when checking account
2. Download auth file from CPA server
3. Extract `refresh_token` from JSON
4. Call OAuth endpoint to get new tokens
5. Update auth file with new tokens
6. Upload updated file back to CPA server
7. Verify new token works
8. If fails 3 times, disable account

### Directory Conventions

- `pool/` - Downloaded account backups (Shell & Web)
- `data/` - Persistent database files (Web only)
- `migrations/` - Database schema versions (Cloudflare only)
- `docs/` - Detailed documentation (Cloudflare has most comprehensive)

## Module Responsibilities

### API Layer (all versions)
- **auth**: User authentication (login/logout/session)
- **servers**: CPA server CRUD operations
- **accounts**: Individual account operations
- **operations**: Batch operations (download/upload/revive)
- **stats**: Statistics and reporting
- **sync**: Data synchronization and backup
- **scheduled/tasks**: Automated maintenance jobs

### Utils Layer (all versions)
- **cpa-client/cpa_client**: CPA API wrapper
- **oauth**: Token refresh logic
- **db-service/db_service**: Database operations
- **config-manager/config_manager**: Configuration management
- **cors**: CORS headers (Cloudflare only)
- **scheduler**: Task scheduling (Web only)

## File Naming Conventions

**Python (Shell & Web):**
- `snake_case.py` for modules
- `snake_case` for functions and variables
- Classes use `PascalCase`

**JavaScript (Cloudflare):**
- `kebab-case.js` for modules
- `camelCase` for functions and variables
- Classes use `PascalCase`

**Configuration:**
- `config.json` - Application configuration
- `.env` - Environment variables (Web only)
- `wrangler.toml` - Cloudflare configuration
- Secrets via Wrangler CLI (Cloudflare only)

## Adding New Features

### Cloudflare
1. Create new file in `src/api/feature.js`
2. Export handler function
3. Add route in `src/api/router.js`
4. Update frontend in `src/frontend/index.html.js`

### Web
1. Create new blueprint in `routes/feature.py`
2. Register blueprint in `app.py`
3. Add template in `templates/feature.html`
4. Add database methods in `utils/db_service.py` if needed

### Shell
1. Add new function in `manage_accounts.py`
2. Add menu option in main loop
3. Update README with usage instructions
