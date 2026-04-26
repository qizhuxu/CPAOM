---
name: documentation-management
description: "Minimal viable documentation management: maintain lean, essential docs with README in root and detailed docs in /docs folder. Use when creating or updating project documentation, ensuring quality over quantity, avoiding duplication, and keeping docs synchronized with code changes."
---

# Documentation Management Skill

Maintain minimal, high-quality documentation that developers actually read and use. Focus on essential information, avoid duplication, and keep docs synchronized with code.

## When to Use This Skill

Trigger when:
- Creating new project documentation
- Updating existing documentation after code changes
- Reviewing documentation structure and quality
- Consolidating duplicate or outdated documentation
- Setting up documentation for a new project
- Refactoring documentation to improve clarity
- Ensuring documentation follows best practices

## Not For / Boundaries

This skill does NOT cover:
- API documentation generation tools (Swagger, JSDoc, etc.)
- Documentation hosting platforms (GitBook, Docusaurus, etc.)
- Marketing or user-facing product documentation
- Legal documents (licenses, terms of service)

Required inputs (ask if missing):
- Project type and target audience
- Existing documentation structure (if any)
- Specific documentation needs or pain points

## Quick Reference

### Documentation Structure

**Root Level (Minimal)**
```
project/
├── README.md           # Only essential overview
├── LICENSE             # License file
├── CHANGELOG.md        # Version history (optional)
└── docs/               # All other documentation
    ├── architecture.md
    ├── api.md
    ├── development.md
    └── deployment.md
```

**README.md Template (Keep Under 200 Lines)**
```markdown
# Project Name

One-line description of what this project does.

## Quick Start

```bash
# Installation
npm install

# Run
npm start

# Test
npm test
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Documentation

- [Architecture](docs/architecture.md) - System design and structure
- [API Reference](docs/api.md) - API endpoints and usage
- [Development Guide](docs/development.md) - Setup and contribution
- [Deployment](docs/deployment.md) - Production deployment

## License

MIT
```

### Essential Documentation Files

**1. README.md (Root)**
- What: One-line project description
- Why: Problem it solves
- Quick Start: 3-5 commands to get running
- Features: Bullet list of key capabilities
- Links: Point to detailed docs in /docs folder

**2. docs/architecture.md**
- System overview diagram
- Key design decisions and WHY
- Technology stack with rationale
- Data flow and component interaction

**3. docs/api.md**
- Endpoint list with examples
- Authentication method
- Request/response formats
- Error codes and handling

**4. docs/development.md**
- Development environment setup
- Project structure explanation
- Coding standards and conventions
- Testing strategy
- Contribution guidelines

**5. docs/deployment.md**
- Deployment steps
- Environment variables
- Configuration options
- Monitoring and logging

### Documentation Principles

**1. Capture WHY, Not Just HOW**
```markdown
❌ Bad:
## Authentication
We use JWT tokens.

✅ Good:
## Authentication
We use JWT tokens (not sessions) because:
- Stateless: scales horizontally without shared state
- Mobile-friendly: works across web and native apps
- Microservices: each service can verify tokens independently
```

**2. Keep It Actionable**
```markdown
❌ Bad:
The system uses a microservices architecture.

✅ Good:
## Running Services Locally
```bash
# Start all services
docker-compose up

# Or run individually
npm run service:auth
npm run service:api
```
```

**3. Update With Code Changes**
```markdown
# In pull request template
## Documentation
- [ ] Updated relevant docs in /docs
- [ ] Updated README if public API changed
- [ ] Added migration guide if breaking change
```

**4. Avoid Duplication**
```markdown
❌ Bad:
- README explains API endpoints
- docs/api.md explains same endpoints
- Code comments repeat endpoint docs

✅ Good:
- README: "See [API docs](docs/api.md) for endpoints"
- docs/api.md: Complete API reference
- Code: Only non-obvious implementation details
```

### Documentation Maintenance

**When to Update Docs**
```javascript
// Add to pre-commit hook or CI
const changedFiles = getChangedFiles();
const needsDocUpdate = [
  'src/api/**',      // API changes → update docs/api.md
  'src/config/**',   // Config changes → update docs/deployment.md
  'package.json',    // Dependencies → update docs/development.md
];

if (needsDocUpdate.some(pattern => matches(changedFiles, pattern))) {
  console.warn('⚠️  Consider updating documentation');
}
```

**Documentation Review Checklist**
- [ ] README is under 200 lines
- [ ] No duplicate information across files
- [ ] All links work (no 404s)
- [ ] Code examples are tested and work
- [ ] Outdated information removed
- [ ] "Why" is explained for key decisions
- [ ] Quick start works in clean environment

**Consolidation Pattern**
```markdown
# Before: 5 scattered docs
- setup.md
- installation.md
- getting-started.md
- prerequisites.md
- configuration.md

# After: 1 comprehensive doc
- docs/development.md
  - Prerequisites
  - Installation
  - Configuration
  - Getting Started
```

### Anti-Patterns to Avoid

**❌ Don't: Duplicate Code in Docs**
```markdown
# Bad: Copying code into docs
## User Model
```javascript
class User {
  constructor(name, email) {
    this.name = name;
    this.email = email;
  }
}
```
// This will get out of sync with actual code
```

**✅ Do: Link to Code**
```markdown
# Good: Reference actual code
## User Model
See [src/models/User.js](../src/models/User.js) for implementation.

Key design decisions:
- Email is unique identifier (not username)
- Passwords hashed with bcrypt (cost factor 12)
- Soft delete pattern (deleted_at field)
```

**❌ Don't: Document Every Function**
```markdown
# Bad: Over-documentation
## getUserById(id)
Gets a user by their ID.

Parameters:
- id: The user ID

Returns: User object
```

**✅ Do: Document Non-Obvious Behavior**
```markdown
# Good: Document the WHY
## User Lookup Performance
getUserById() uses Redis cache with 5-minute TTL.
Cache is invalidated on user updates.
Falls back to database if cache miss.

Why: 80% of requests are user lookups, caching reduced
database load by 60%.
```

### Documentation Templates

**Architecture Decision Record (ADR)**
```markdown
# ADR-001: Use PostgreSQL for Primary Database

## Status
Accepted

## Context
Need to choose primary database for user data and transactions.

## Decision
Use PostgreSQL 14+

## Consequences
### Positive
- ACID compliance for financial transactions
- JSON support for flexible schemas
- Mature ecosystem and tooling

### Negative
- More complex than NoSQL for simple queries
- Requires careful index management

## Alternatives Considered
- MongoDB: Rejected due to lack of transactions
- MySQL: Rejected due to weaker JSON support
```

**API Endpoint Documentation**
```markdown
## POST /api/auth/login

Authenticate user and return JWT token.

### Request
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Response (200 OK)
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expiresIn": 3600
}
```

### Errors
- 401: Invalid credentials
- 429: Too many attempts (rate limited)
- 500: Server error

### Rate Limiting
5 attempts per minute per IP address.
```

**Development Setup Guide**
```markdown
## Development Setup

### Prerequisites
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### First-Time Setup
```bash
# 1. Install dependencies
npm install

# 2. Copy environment file
cp .env.example .env

# 3. Start database
docker-compose up -d postgres redis

# 4. Run migrations
npm run migrate

# 5. Seed test data
npm run seed

# 6. Start dev server
npm run dev
```

### Verify Setup
Visit http://localhost:3000/health
Should return: `{"status": "ok"}`

### Troubleshooting
**Port 3000 already in use**
```bash
# Find and kill process
lsof -ti:3000 | xargs kill -9
```

**Database connection failed**
Check PostgreSQL is running: `docker-compose ps`
```

## Examples

### Example 1: New Project Documentation

**Input:** Starting a new Express.js API project

**Steps:**
1. Create minimal README.md with project description and quick start
2. Create docs/ folder with architecture.md, api.md, development.md
3. Document key architectural decisions (why Express, why PostgreSQL)
4. Add API endpoint examples with request/response
5. Write development setup guide with tested commands
6. Link README to detailed docs

**Expected Output:**
- README.md under 150 lines with working quick start
- 3-4 focused docs in /docs folder
- No duplicate information
- All code examples tested and working

### Example 2: Consolidating Scattered Documentation

**Input:** Project has 15+ markdown files with overlapping content

**Steps:**
1. Audit all existing documentation files
2. Identify duplicate and outdated content
3. Merge related docs (setup.md + install.md → development.md)
4. Move detailed docs to /docs folder
5. Update README to be concise overview with links
6. Remove or archive outdated files
7. Update all internal links

**Expected Output:**
- Reduced from 15 files to 5 essential files
- Clear separation: README (overview) + docs/ (details)
- No duplicate information
- All links working

### Example 3: Documentation Update After Feature Addition

**Input:** Added OAuth authentication feature to existing API

**Steps:**
1. Update docs/api.md with new OAuth endpoints
2. Add OAuth flow diagram to docs/architecture.md
3. Explain WHY OAuth was chosen over basic auth
4. Update docs/development.md with OAuth testing setup
5. Add environment variables to docs/deployment.md
6. Update README features list (one line)
7. Add migration guide for existing users

**Expected Output:**
- OAuth fully documented in appropriate files
- No duplication across files
- Clear migration path for existing users
- README remains concise (just mentions OAuth)

## References

- `references/mvd-principles.md`: Minimum Viable Documentation principles
- `references/structure-guide.md`: Folder structure best practices
- `references/writing-guide.md`: Technical writing guidelines
- `references/templates.md`: Documentation templates library

## Maintenance

- Sources: Industry best practices (Google, Agile documentation), folder structure conventions, MVD principles
- Last updated: 2026-04-19
- Known limits: Does not cover auto-generated API docs or documentation hosting platforms
