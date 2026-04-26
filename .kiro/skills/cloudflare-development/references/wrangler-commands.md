# Wrangler CLI Commands Reference

Comprehensive reference for Wrangler CLI commands and options.

## Installation

```bash
# Install globally
npm install -g wrangler

# Install as dev dependency
npm install --save-dev wrangler

# Check version
wrangler --version

# Update to latest
npm update -g wrangler
```

## Authentication

```bash
# Login to Cloudflare account
wrangler login

# Login with API token
wrangler login --api-token YOUR_API_TOKEN

# Logout
wrangler logout

# Check current user
wrangler whoami
```

## Project Management

### Initialize

```bash
# Create new project (interactive)
wrangler init

# Create with specific name
wrangler init my-worker

# Create from template
npm create cloudflare@latest my-worker

# Initialize in existing directory
wrangler init --yes
```

### Development

```bash
# Start local development server
wrangler dev

# Dev server with remote resources (KV, R2, D1)
wrangler dev --remote

# Dev server on specific port
wrangler dev --port 8787

# Dev server with local protocol
wrangler dev --local-protocol https

# Dev server with specific compatibility date
wrangler dev --compatibility-date 2024-01-01

# Enable inspector for debugging
wrangler dev --inspector-port 9229
```

### Deployment

```bash
# Deploy to production
wrangler deploy

# Deploy with specific name
wrangler deploy --name my-worker

# Deploy to specific environment
wrangler deploy --env production

# Dry run (validate without deploying)
wrangler deploy --dry-run

# Deploy with compatibility flags
wrangler deploy --compatibility-date 2024-01-01

# Deploy specific script
wrangler deploy src/index.js
```

### Publishing

```bash
# Publish (alias for deploy)
wrangler publish

# Publish with minification
wrangler publish --minify

# Publish without minification
wrangler publish --no-bundle
```

## Worker Management

### List Workers

```bash
# List all workers
wrangler list

# List workers in specific account
wrangler list --account-id YOUR_ACCOUNT_ID
```

### Delete Worker

```bash
# Delete worker
wrangler delete

# Delete specific worker
wrangler delete my-worker

# Delete without confirmation
wrangler delete --force
```

### Tail Logs

```bash
# Tail live logs
wrangler tail

# Tail specific worker
wrangler tail my-worker

# Tail with filters
wrangler tail --status error
wrangler tail --status ok
wrangler tail --method POST
wrangler tail --header "User-Agent: *Chrome*"

# Tail with sampling rate
wrangler tail --sampling-rate 0.5

# Output as JSON
wrangler tail --format json
```

## KV Namespace Management

### Create Namespace

```bash
# Create KV namespace
wrangler kv:namespace create MY_KV

# Create preview namespace
wrangler kv:namespace create MY_KV --preview

# Create in specific environment
wrangler kv:namespace create MY_KV --env production
```

### List Namespaces

```bash
# List all KV namespaces
wrangler kv:namespace list
```

### Delete Namespace

```bash
# Delete KV namespace
wrangler kv:namespace delete --namespace-id YOUR_NAMESPACE_ID

# Delete with binding name
wrangler kv:namespace delete --binding MY_KV
```

### KV Key Operations

```bash
# Put key-value
wrangler kv:key put "my-key" "my-value" --namespace-id YOUR_NAMESPACE_ID

# Put from file
wrangler kv:key put "config" --path ./config.json --namespace-id YOUR_NAMESPACE_ID

# Put with TTL (seconds)
wrangler kv:key put "session" "data" --ttl 3600 --namespace-id YOUR_NAMESPACE_ID

# Put with expiration timestamp
wrangler kv:key put "temp" "data" --expiration 1735689600 --namespace-id YOUR_NAMESPACE_ID

# Get key
wrangler kv:key get "my-key" --namespace-id YOUR_NAMESPACE_ID

# Get and save to file
wrangler kv:key get "config" --namespace-id YOUR_NAMESPACE_ID > config.json

# Delete key
wrangler kv:key delete "my-key" --namespace-id YOUR_NAMESPACE_ID

# List keys
wrangler kv:key list --namespace-id YOUR_NAMESPACE_ID

# List with prefix
wrangler kv:key list --prefix "user:" --namespace-id YOUR_NAMESPACE_ID

# List with limit
wrangler kv:key list --limit 100 --namespace-id YOUR_NAMESPACE_ID
```

### Bulk Operations

```bash
# Bulk put from JSON file
wrangler kv:bulk put data.json --namespace-id YOUR_NAMESPACE_ID

# Bulk delete from JSON file
wrangler kv:bulk delete keys.json --namespace-id YOUR_NAMESPACE_ID

# JSON format for bulk put:
# [
#   {"key": "key1", "value": "value1"},
#   {"key": "key2", "value": "value2", "expiration_ttl": 3600}
# ]

# JSON format for bulk delete:
# ["key1", "key2", "key3"]
```

## R2 Bucket Management

### Create Bucket

```bash
# Create R2 bucket
wrangler r2 bucket create my-bucket

# Create in specific jurisdiction
wrangler r2 bucket create my-bucket --jurisdiction eu
```

### List Buckets

```bash
# List all R2 buckets
wrangler r2 bucket list
```

### Delete Bucket

```bash
# Delete R2 bucket
wrangler r2 bucket delete my-bucket

# Delete without confirmation
wrangler r2 bucket delete my-bucket --force
```

### R2 Object Operations

```bash
# Upload object
wrangler r2 object put my-bucket/file.txt --file ./local-file.txt

# Upload with content type
wrangler r2 object put my-bucket/image.jpg --file ./image.jpg --content-type image/jpeg

# Upload from stdin
echo "Hello World" | wrangler r2 object put my-bucket/hello.txt

# Download object
wrangler r2 object get my-bucket/file.txt

# Download to file
wrangler r2 object get my-bucket/file.txt --file ./downloaded.txt

# Delete object
wrangler r2 object delete my-bucket/file.txt

# List objects
wrangler r2 object list my-bucket

# List with prefix
wrangler r2 object list my-bucket --prefix uploads/

# List with limit
wrangler r2 object list my-bucket --limit 100
```

## D1 Database Management

### Create Database

```bash
# Create D1 database
wrangler d1 create my-database

# Create with specific name
wrangler d1 create my-database --name "My Database"
```

### List Databases

```bash
# List all D1 databases
wrangler d1 list
```

### Delete Database

```bash
# Delete D1 database
wrangler d1 delete my-database

# Delete without confirmation
wrangler d1 delete my-database --force
```

### Execute SQL

```bash
# Execute SQL command (local)
wrangler d1 execute my-database --local --command "SELECT * FROM users"

# Execute SQL command (remote)
wrangler d1 execute my-database --remote --command "SELECT * FROM users"

# Execute SQL from file
wrangler d1 execute my-database --local --file ./schema.sql

# Execute with JSON output
wrangler d1 execute my-database --remote --command "SELECT * FROM users" --json
```

### Migrations

```bash
# Create migration
wrangler d1 migrations create my-database create_users_table

# List migrations
wrangler d1 migrations list my-database

# Apply migrations (local)
wrangler d1 migrations apply my-database --local

# Apply migrations (remote)
wrangler d1 migrations apply my-database --remote

# Apply specific migration
wrangler d1 migrations apply my-database --local --batch-size 1
```

### Backup and Export

```bash
# Export database
wrangler d1 export my-database --local --output backup.sql
wrangler d1 export my-database --remote --output backup.sql
```

## Secrets Management

```bash
# Put secret (interactive)
wrangler secret put SECRET_NAME

# Put secret from value
echo "secret-value" | wrangler secret put SECRET_NAME

# Put secret for specific environment
wrangler secret put SECRET_NAME --env production

# List secrets
wrangler secret list

# Delete secret
wrangler secret delete SECRET_NAME

# Delete without confirmation
wrangler secret delete SECRET_NAME --force
```

## Pages Management

### Create Project

```bash
# Create Pages project
wrangler pages project create my-site

# Create with production branch
wrangler pages project create my-site --production-branch main
```

### List Projects

```bash
# List all Pages projects
wrangler pages project list
```

### Delete Project

```bash
# Delete Pages project
wrangler pages project delete my-site
```

### Deploy

```bash
# Deploy directory
wrangler pages deploy ./dist

# Deploy with project name
wrangler pages deploy ./dist --project-name my-site

# Deploy with branch
wrangler pages deploy ./dist --branch preview

# Deploy with commit message
wrangler pages deploy ./dist --commit-message "Deploy v1.2.3"
```

### Deployments

```bash
# List deployments
wrangler pages deployment list --project-name my-site

# Tail deployment logs
wrangler pages deployment tail --project-name my-site
```

### Functions

```bash
# Build Pages Functions
wrangler pages functions build

# Optimize Functions
wrangler pages functions optimize
```

## Queue Management

### Create Queue

```bash
# Create queue
wrangler queues create my-queue

# Create with specific settings
wrangler queues create my-queue --max-batch-size 10 --max-batch-timeout 30
```

### List Queues

```bash
# List all queues
wrangler queues list
```

### Delete Queue

```bash
# Delete queue
wrangler queues delete my-queue
```

### Consumer Management

```bash
# Add consumer
wrangler queues consumer add my-queue my-worker

# Remove consumer
wrangler queues consumer remove my-queue my-worker

# List consumers
wrangler queues consumer list my-queue
```

## Configuration

### Generate Types

```bash
# Generate TypeScript types from wrangler.toml
wrangler types

# Generate with specific output
wrangler types --output-file worker-configuration.d.ts
```

### Validate Configuration

```bash
# Validate wrangler.toml
wrangler deploy --dry-run
```

## Debugging and Diagnostics

### Inspector

```bash
# Start dev server with inspector
wrangler dev --inspector-port 9229

# Then connect Chrome DevTools to chrome://inspect
```

### Logs

```bash
# View recent logs
wrangler tail

# View logs with filters
wrangler tail --status error --method POST

# View logs as JSON
wrangler tail --format json
```

### Metrics

```bash
# View worker metrics (via dashboard)
# No CLI command available yet
```

## Environment Management

### Using Environments

```bash
# Deploy to specific environment
wrangler deploy --env production
wrangler deploy --env staging

# Dev with specific environment
wrangler dev --env production

# Tail logs for specific environment
wrangler tail --env production

# Manage secrets per environment
wrangler secret put API_KEY --env production
```

### wrangler.toml Environment Configuration

```toml
name = "my-worker"
main = "src/index.js"

[env.production]
name = "my-worker-production"
vars = { ENVIRONMENT = "production" }

[env.staging]
name = "my-worker-staging"
vars = { ENVIRONMENT = "staging" }
```

## Advanced Options

### Compatibility Flags

```bash
# Deploy with specific compatibility date
wrangler deploy --compatibility-date 2024-01-01

# Deploy with compatibility flags
wrangler deploy --compatibility-flags nodejs_compat
```

### Custom Builds

```bash
# Deploy with custom build command
wrangler deploy --build-command "npm run build"

# Deploy with custom watch paths
wrangler dev --watch-paths "src/**/*.js"
```

### Proxy

```bash
# Use HTTP proxy
wrangler deploy --proxy http://proxy.example.com:8080

# Use HTTPS proxy
wrangler deploy --proxy https://proxy.example.com:8080
```

## Global Options

```bash
# Specify config file
wrangler deploy --config ./custom-wrangler.toml

# Specify account ID
wrangler deploy --account-id YOUR_ACCOUNT_ID

# Enable verbose logging
wrangler deploy --verbose

# Disable colors
wrangler deploy --no-color

# Output as JSON
wrangler list --json
```

## Troubleshooting Commands

```bash
# Check Wrangler version
wrangler --version

# Check for updates
npm outdated -g wrangler

# Clear cache
rm -rf ~/.wrangler

# Reinstall Wrangler
npm uninstall -g wrangler && npm install -g wrangler

# Check authentication status
wrangler whoami

# Re-authenticate
wrangler logout && wrangler login
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Worker

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npx wrangler deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

### GitLab CI Example

```yaml
deploy:
  image: node:18
  script:
    - npm ci
    - npx wrangler deploy
  only:
    - main
  variables:
    CLOUDFLARE_API_TOKEN: ${{ CLOUDFLARE_API_TOKEN }}
```

## Tips and Best Practices

1. **Use `wrangler dev --remote`** for testing with actual KV/R2/D1 resources
2. **Always use `--dry-run`** before deploying to production
3. **Use environments** for staging and production separation
4. **Store API tokens securely** in CI/CD secrets
5. **Use `wrangler tail`** for real-time debugging
6. **Generate types** with `wrangler types` for TypeScript projects
7. **Version control `wrangler.toml`** but not secrets
8. **Use `--json` flag** for scripting and automation
