# Documentation Structure Guide

## Standard Project Structure

### Minimal Structure (Small Projects)

```
project/
├── README.md           # Project overview and quick start
├── LICENSE             # License information
└── docs/               # All detailed documentation
    ├── api.md         # API reference
    └── development.md # Development guide
```

### Standard Structure (Most Projects)

```
project/
├── README.md           # Project overview and quick start
├── LICENSE             # License information
├── CHANGELOG.md        # Version history (optional)
└── docs/               # All detailed documentation
    ├── architecture.md # System design and decisions
    ├── api.md         # API reference
    ├── development.md # Development setup and guidelines
    └── deployment.md  # Deployment and operations
```

### Comprehensive Structure (Large Projects)

```
project/
├── README.md           # Project overview and quick start
├── LICENSE             # License information
├── CHANGELOG.md        # Version history
├── CONTRIBUTING.md     # Contribution guidelines (if open source)
└── docs/
    ├── README.md       # Documentation index
    ├── architecture/   # Architecture documentation
    │   ├── overview.md
    │   ├── decisions/  # Architecture Decision Records
    │   │   ├── 001-database-choice.md
    │   │   └── 002-authentication.md
    │   └── diagrams/
    ├── api/            # API documentation
    │   ├── rest.md
    │   ├── websocket.md
    │   └── examples/
    ├── guides/         # How-to guides
    │   ├── development.md
    │   ├── deployment.md
    │   ├── testing.md
    │   └── troubleshooting.md
    └── reference/      # Reference material
        ├── configuration.md
        ├── environment-variables.md
        └── error-codes.md
```

## File Naming Conventions

### Use Lowercase with Hyphens

```
✅ Good:
- architecture.md
- api-reference.md
- getting-started.md
- deployment-guide.md

❌ Bad:
- Architecture.md
- API_Reference.md
- GettingStarted.md
- deployment guide.md
```

### Be Descriptive but Concise

```
✅ Good:
- authentication.md
- database-schema.md
- error-handling.md

❌ Bad:
- auth.md (too vague)
- database-schema-and-migration-strategy-guide.md (too long)
- stuff.md (meaningless)
```

## Root Level Files

### README.md (Required)

**Purpose:** First impression and quick start

**Keep Under 200 Lines**

**Must Include:**
- One-line project description
- Quick start (3-5 commands)
- Key features (bullet list)
- Links to detailed docs
- License information

**Should NOT Include:**
- Detailed API documentation
- Complete setup instructions
- Architecture details
- Deployment procedures

**Template:**
```markdown
# Project Name

One-line description of what this project does.

## Quick Start

```bash
npm install
npm start
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Development Guide](docs/development.md)

## License

MIT
```

### LICENSE (Required for Open Source)

Standard license file, no modifications needed.

### CHANGELOG.md (Optional)

**When to Include:**
- Versioned releases
- Public API or library
- Need to track breaking changes

**Format:** Follow [Keep a Changelog](https://keepachangelog.com/)

```markdown
# Changelog

## [1.2.0] - 2024-03-15

### Added
- OAuth authentication support
- Rate limiting middleware

### Changed
- Updated Node.js requirement to 18+

### Fixed
- Memory leak in WebSocket connections

## [1.1.0] - 2024-02-01
...
```

### CONTRIBUTING.md (Optional)

**When to Include:**
- Open source project
- Accepting external contributions
- Specific contribution workflow

**Keep Brief:** Link to detailed development guide

```markdown
# Contributing

Thanks for your interest! Please:

1. Read our [Development Guide](docs/development.md)
2. Check existing issues before creating new ones
3. Follow our code style (enforced by ESLint)
4. Add tests for new features
5. Update documentation

See [Development Guide](docs/development.md) for setup instructions.
```

## docs/ Folder Organization

### Core Documentation Files

#### architecture.md

**Purpose:** System design and key decisions

**Contents:**
- High-level system overview
- Component diagram
- Technology stack with rationale
- Key architectural decisions (ADRs)
- Data flow
- Security considerations

**Length:** 500-1000 lines

#### api.md

**Purpose:** API reference for integrators

**Contents:**
- Authentication method
- Base URL and versioning
- Endpoint list with examples
- Request/response formats
- Error codes
- Rate limiting

**Length:** Varies by API size

#### development.md

**Purpose:** Setup and contribution guide

**Contents:**
- Prerequisites
- First-time setup steps
- Project structure explanation
- Development workflow
- Testing strategy
- Code style guidelines
- Troubleshooting

**Length:** 300-500 lines

#### deployment.md

**Purpose:** Production deployment guide

**Contents:**
- Deployment steps
- Environment variables
- Configuration options
- Monitoring setup
- Backup procedures
- Rollback process

**Length:** 200-400 lines

### When to Split Documentation

**Split When:**
- Single file exceeds 1000 lines
- Multiple distinct topics in one file
- Different audiences need different docs
- File becomes hard to navigate

**Example: Splitting development.md**

```
Before:
docs/development.md (1500 lines)
- Setup
- Testing
- Debugging
- Contributing
- Code style
- Git workflow

After:
docs/
├── development.md (300 lines - setup and overview)
├── testing.md (200 lines)
├── debugging.md (150 lines)
└── contributing.md (200 lines)
```

### When to Merge Documentation

**Merge When:**
- Multiple files cover related topics
- Files are very short (< 100 lines each)
- Constant cross-referencing between files
- Duplication across files

**Example: Merging setup docs**

```
Before:
docs/
├── prerequisites.md (50 lines)
├── installation.md (80 lines)
├── configuration.md (60 lines)
└── first-run.md (40 lines)

After:
docs/development.md (230 lines)
- Prerequisites
- Installation
- Configuration
- First Run
```

## Subdirectory Organization

### When to Use Subdirectories

Use subdirectories when you have:
- 5+ files in a category
- Clear logical grouping
- Different audiences for different sections

### Common Subdirectory Patterns

#### Architecture Decision Records (ADRs)

```
docs/
└── architecture/
    └── decisions/
        ├── 001-database-choice.md
        ├── 002-authentication-strategy.md
        └── 003-caching-layer.md
```

**Template:**
```markdown
# ADR-001: Database Choice

## Status
Accepted

## Context
Need to choose primary database for user data.

## Decision
Use PostgreSQL 14+

## Consequences
- ACID compliance for transactions
- JSON support for flexible schemas
- Requires careful index management

## Alternatives Considered
- MongoDB: Rejected due to lack of transactions
```

#### API Documentation by Version

```
docs/
└── api/
    ├── v1/
    │   ├── authentication.md
    │   └── endpoints.md
    └── v2/
        ├── authentication.md
        └── endpoints.md
```

#### Guides by Topic

```
docs/
└── guides/
    ├── getting-started.md
    ├── authentication.md
    ├── deployment.md
    └── troubleshooting.md
```

## Documentation Index

### When to Add docs/README.md

Add when:
- More than 5 documentation files
- Complex subdirectory structure
- Need to guide readers to right doc

**Template:**
```markdown
# Documentation Index

## Getting Started
- [Quick Start](../README.md) - Get up and running in 5 minutes
- [Development Guide](guides/development.md) - Full setup instructions

## Architecture
- [System Overview](architecture/overview.md)
- [Design Decisions](architecture/decisions/)

## API Reference
- [REST API](api/rest.md)
- [WebSocket API](api/websocket.md)

## Operations
- [Deployment](guides/deployment.md)
- [Monitoring](guides/monitoring.md)
- [Troubleshooting](guides/troubleshooting.md)
```

## Special Cases

### Monorepo Structure

```
monorepo/
├── README.md           # Monorepo overview
├── docs/               # Shared documentation
│   └── architecture.md
└── packages/
    ├── api/
    │   ├── README.md   # API package overview
    │   └── docs/       # API-specific docs
    └── web/
        ├── README.md   # Web package overview
        └── docs/       # Web-specific docs
```

### Multi-Language Projects

```
project/
├── README.md           # English (default)
├── README.zh-CN.md     # Chinese
├── README.ja.md        # Japanese
└── docs/
    ├── en/             # English docs
    ├── zh-CN/          # Chinese docs
    └── ja/             # Japanese docs
```

### Documentation with Code Examples

```
docs/
├── api.md
└── examples/           # Runnable code examples
    ├── authentication.js
    ├── pagination.js
    └── error-handling.js
```

Reference in docs:
```markdown
## Authentication Example

See [examples/authentication.js](examples/authentication.js) for a complete example.
```

## Anti-Patterns

### ❌ Don't: Scatter Docs Everywhere

```
Bad:
project/
├── README.md
├── SETUP.md
├── API.md
├── DEPLOY.md
├── docs/
│   ├── guide.md
│   └── more-docs.md
└── documentation/
    └── other-stuff.md
```

### ❌ Don't: Use Unclear Names

```
Bad:
docs/
├── doc1.md
├── notes.md
├── stuff.md
└── misc.md
```

### ❌ Don't: Create Deep Hierarchies

```
Bad:
docs/
└── guides/
    └── development/
        └── setup/
            └── prerequisites/
                └── software.md
```

### ❌ Don't: Mix Documentation with Code

```
Bad:
src/
├── api/
│   ├── users.js
│   └── API_DOCS.md    # Should be in docs/
└── models/
    ├── User.js
    └── SCHEMA.md       # Should be in docs/
```

## Migration Guide

### Consolidating Scattered Docs

**Step 1: Audit**
```bash
# Find all markdown files
find . -name "*.md" -not -path "./node_modules/*"
```

**Step 2: Categorize**
- Overview → README.md
- Architecture → docs/architecture.md
- API → docs/api.md
- Setup → docs/development.md
- Deployment → docs/deployment.md

**Step 3: Merge and Move**
```bash
# Create docs folder
mkdir -p docs

# Move and merge files
cat SETUP.md INSTALL.md > docs/development.md
mv API_DOCS.md docs/api.md
mv ARCHITECTURE.md docs/architecture.md
```

**Step 4: Update Links**
```bash
# Find and update all internal links
grep -r "\[.*\](.*\.md)" docs/
```

**Step 5: Clean Up**
```bash
# Remove old files
rm SETUP.md INSTALL.md API_DOCS.md
```

## Resources

- [Folder Structure Conventions](https://github.com/kriasoft/Folder-Structure-Conventions)
- [Keep a Changelog](https://keepachangelog.com/)
- [Architecture Decision Records](https://adr.github.io/)
