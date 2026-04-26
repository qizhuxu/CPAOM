# Cloudflare Development Skill

A comprehensive skill for developing applications on the Cloudflare platform, covering Workers, Pages, and all storage solutions.

## What's Included

### Main Skill File
- **SKILL.md** - Quick reference guide with common patterns and examples

### Reference Materials
- **storage-comparison.md** - Detailed comparison of KV, R2, D1, and Durable Objects
- **wrangler-commands.md** - Complete Wrangler CLI command reference
- **troubleshooting.md** - Common issues and solutions
- **index.md** - Navigation to all references

## Quick Start

To use this skill, simply mention Cloudflare-related topics in your conversation:
- "Create a Cloudflare Worker"
- "Deploy to Cloudflare Pages"
- "Use KV storage"
- "Set up R2 bucket"
- "Configure D1 database"

The skill will automatically activate and provide relevant guidance.

## Coverage

### Platforms
- ✅ Cloudflare Workers (serverless functions)
- ✅ Cloudflare Pages (static sites + functions)
- ✅ Wrangler CLI (development and deployment)

### Storage Solutions
- ✅ KV (Key-Value storage)
- ✅ R2 (Object storage)
- ✅ D1 (SQL database)
- ✅ Durable Objects Storage (transactional storage)

### Features
- ✅ Queues (message processing)
- ✅ Caching strategies
- ✅ Authentication patterns
- ✅ Error handling
- ✅ Performance optimization

## Structure

```
cloudflare-development/
├── SKILL.md                          # Main skill file with quick reference
├── README.md                         # This file
└── references/
    ├── index.md                      # Navigation index
    ├── storage-comparison.md         # KV vs R2 vs D1 vs DO comparison
    ├── wrangler-commands.md          # Complete CLI reference
    └── troubleshooting.md            # Common issues and solutions
```

## Maintenance

This skill is based on:
- Official Cloudflare Workers documentation
- Wrangler CLI documentation
- Community best practices
- Real-world usage patterns

Last updated: 2026-04-21

## Contributing

To update this skill:
1. Update the relevant reference files in `references/`
2. Update `SKILL.md` if adding new patterns
3. Update this README if structure changes
4. Update the "Last updated" date in SKILL.md

## Related Skills

This skill pairs well with:
- **chrome-extension-automation** - For building extensions that interact with Cloudflare services
- **documentation-management** - For maintaining Cloudflare project documentation
