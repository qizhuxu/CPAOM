# Documentation Templates

Ready-to-use templates for common documentation needs.

## README.md Template

```markdown
# Project Name

One-line description of what this project does and the problem it solves.

## Quick Start

```bash
# Install
npm install

# Configure
cp .env.example .env

# Run
npm start
```

Visit http://localhost:3000

## Features

- Feature 1: Brief description
- Feature 2: Brief description
- Feature 3: Brief description

## Documentation

- [Architecture](docs/architecture.md) - System design and decisions
- [API Reference](docs/api.md) - API endpoints and usage
- [Development](docs/development.md) - Setup and contribution guide
- [Deployment](docs/deployment.md) - Production deployment

## Tech Stack

- Node.js 18+
- PostgreSQL 14+
- Redis 6+

## License

MIT - see [LICENSE](LICENSE) file
```

## Architecture Document Template

```markdown
# Architecture

## Overview

High-level description of the system (2-3 sentences).

## System Diagram

```
[Include a simple diagram showing main components]
```

## Components

### Component 1: Name
**Purpose:** What it does
**Technology:** What it's built with
**Why:** Reason for this choice

### Component 2: Name
**Purpose:** What it does
**Technology:** What it's built with
**Why:** Reason for this choice

## Key Decisions

### Decision 1: Database Choice
**What:** PostgreSQL for primary database
**Why:** 
- ACID compliance for transactions
- JSON support for flexible data
- Team expertise

**Alternatives Considered:**
- MongoDB: Rejected due to lack of transactions
- MySQL: Rejected due to weaker JSON support

### Decision 2: Authentication
**What:** JWT tokens with refresh tokens
**Why:**
- Stateless authentication
- Works across web and mobile
- Easy to scale horizontally

## Data Flow

1. User request → API Gateway
2. API Gateway → Authentication Service
3. Authentication Service → Business Logic
4. Business Logic → Database
5. Response back through chain

## Security

- All communication over HTTPS
- JWT tokens expire after 1 hour
- Passwords hashed with bcrypt
- Rate limiting on all endpoints

## Performance

- Redis caching for frequently accessed data
- Database connection pooling
- CDN for static assets

## Future Considerations

- Add message queue for async processing
- Implement event sourcing for audit trail
- Consider microservices split when team grows
```

## API Documentation Template

```markdown
# API Reference

Base URL: `https://api.example.com/v1`

## Authentication

All endpoints require authentication via Bearer token:

```bash
Authorization: Bearer YOUR_TOKEN
```

Get token via `/auth/login` endpoint.

## Endpoints

### POST /auth/login

Authenticate and receive access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expiresIn": 3600
}
```

**Errors:**
- `401`: Invalid credentials
- `429`: Too many attempts

---

### GET /users/:id

Get user by ID.

**Parameters:**
- `id` (path): User ID

**Response (200):**
```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Errors:**
- `404`: User not found
- `401`: Unauthorized

---

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per user

## Error Format

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email is required",
    "details": {}
  }
}
```
```

## Development Guide Template

```markdown
# Development Guide

## Prerequisites

- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)

## First-Time Setup

### 1. Clone and Install

```bash
git clone https://github.com/user/project.git
cd project
npm install
```

### 2. Database Setup

```bash
# Start PostgreSQL (Docker)
docker-compose up -d postgres

# Or install locally
brew install postgresql
brew services start postgresql
```

### 3. Configuration

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
```

### 4. Database Migration

```bash
npm run migrate
npm run seed  # Optional: add test data
```

### 5. Start Development Server

```bash
npm run dev
```

Server runs at http://localhost:3000

## Project Structure

```
project/
├── src/
│   ├── api/          # API routes
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   └── utils/        # Helper functions
├── tests/
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
└── docs/             # Documentation
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

- Write code
- Add tests
- Update docs

### 3. Run Tests

```bash
npm test
npm run lint
```

### 4. Commit

```bash
git add .
git commit -m "feat: add user authentication"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/).

### 5. Push and Create PR

```bash
git push origin feature/my-feature
```

## Testing

### Run All Tests

```bash
npm test
```

### Run Specific Test

```bash
npm test -- users.test.js
```

### Watch Mode

```bash
npm test -- --watch
```

## Code Style

- ESLint enforces style rules
- Prettier formats code
- Run before commit: `npm run lint:fix`

## Troubleshooting

### Port Already in Use

```bash
# Find process
lsof -ti:3000

# Kill process
kill -9 $(lsof -ti:3000)
```

### Database Connection Failed

Check PostgreSQL is running:
```bash
docker-compose ps postgres
```

### Tests Failing

Clear test database:
```bash
npm run test:db:reset
```
```

## Deployment Guide Template

```markdown
# Deployment Guide

## Prerequisites

- Production server with Node.js 18+
- PostgreSQL database
- Redis instance
- Domain with SSL certificate

## Environment Variables

Required variables:

```bash
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
JWT_SECRET=your-production-secret
```

## Deployment Steps

### 1. Build Application

```bash
npm run build
```

### 2. Run Database Migrations

```bash
NODE_ENV=production npm run migrate
```

### 3. Start Application

```bash
NODE_ENV=production npm start
```

Or use PM2:

```bash
pm2 start npm --name "app" -- start
pm2 save
```

## Docker Deployment

### Build Image

```bash
docker build -t myapp:latest .
```

### Run Container

```bash
docker run -d \
  --name myapp \
  -p 3000:3000 \
  --env-file .env.production \
  myapp:latest
```

## Health Checks

Check application health:

```bash
curl https://api.example.com/health
```

Expected response:
```json
{"status": "ok"}
```

## Monitoring

- Logs: `pm2 logs` or `docker logs myapp`
- Metrics: Available at `/metrics` endpoint
- Alerts: Configure via monitoring service

## Rollback

### PM2

```bash
pm2 stop app
git checkout previous-version
npm install
npm run build
pm2 restart app
```

### Docker

```bash
docker stop myapp
docker run -d --name myapp myapp:previous-tag
```

## Backup

### Database Backup

```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restore

```bash
psql $DATABASE_URL < backup.sql
```
```

## Architecture Decision Record Template

```markdown
# ADR-XXX: [Title]

## Status

[Proposed | Accepted | Deprecated | Superseded]

## Context

What is the issue we're facing? What factors are driving this decision?

## Decision

What are we going to do? Be specific.

## Consequences

### Positive

- Benefit 1
- Benefit 2

### Negative

- Drawback 1
- Drawback 2

### Neutral

- Consideration 1

## Alternatives Considered

### Alternative 1: [Name]
- Pros: ...
- Cons: ...
- Why rejected: ...

### Alternative 2: [Name]
- Pros: ...
- Cons: ...
- Why rejected: ...

## References

- [Link to relevant discussion]
- [Link to documentation]
```

## Troubleshooting Guide Template

```markdown
# Troubleshooting Guide

## Common Issues

### Issue: Application Won't Start

**Symptoms:**
- Error: `EADDRINUSE: address already in use`

**Cause:**
Port 3000 is already in use by another process.

**Solution:**

1. Find the process:
```bash
lsof -ti:3000
```

2. Kill the process:
```bash
kill -9 $(lsof -ti:3000)
```

3. Restart application:
```bash
npm start
```

**Prevention:**
Use different port or ensure clean shutdown.

---

### Issue: Database Connection Failed

**Symptoms:**
- Error: `ECONNREFUSED`
- Application crashes on startup

**Cause:**
PostgreSQL is not running or connection string is incorrect.

**Solution:**

1. Check if PostgreSQL is running:
```bash
docker-compose ps postgres
# or
brew services list | grep postgresql
```

2. Verify connection string in `.env`:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

3. Test connection:
```bash
psql $DATABASE_URL -c "SELECT 1"
```

**Prevention:**
Add PostgreSQL to startup services.

---

## Getting Help

1. Check logs: `npm run logs`
2. Search issues: [GitHub Issues](link)
3. Ask in Slack: #dev-help channel
4. Email: dev-team@example.com
```

## CHANGELOG Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- New features in development

### Changed
- Changes to existing features

### Fixed
- Bug fixes

## [1.2.0] - 2024-03-15

### Added
- OAuth authentication support
- Rate limiting middleware
- User profile endpoints

### Changed
- Updated Node.js requirement to 18+
- Improved error messages

### Fixed
- Memory leak in WebSocket connections
- Race condition in user creation

### Security
- Updated dependencies with security patches

## [1.1.0] - 2024-02-01

### Added
- User authentication
- JWT token support

### Fixed
- Database connection pooling issue

## [1.0.0] - 2024-01-15

Initial release

### Added
- Basic API endpoints
- PostgreSQL integration
- Docker support

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

## Contributing Guide Template

```markdown
# Contributing

Thanks for your interest in contributing!

## Getting Started

1. Read the [Development Guide](docs/development.md)
2. Check [open issues](link)
3. Join our [Slack channel](link)

## How to Contribute

### Reporting Bugs

1. Check if bug already reported
2. Create new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

### Suggesting Features

1. Check if feature already requested
2. Create new issue with:
   - Use case description
   - Proposed solution
   - Alternatives considered

### Submitting Code

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Run tests: `npm test`
5. Commit: `git commit -m "feat: add feature"`
6. Push: `git push origin feature/my-feature`
7. Create Pull Request

## Code Standards

- Follow ESLint rules
- Write tests for new features
- Update documentation
- Use Conventional Commits

## Pull Request Process

1. Update README if needed
2. Add tests
3. Ensure CI passes
4. Request review from maintainers
5. Address review feedback

## Code of Conduct

Be respectful and inclusive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Questions?

Ask in #dev-help Slack channel or email dev@example.com
```

## Usage

Copy the relevant template and customize for your project. Remove sections that don't apply and add project-specific details.
