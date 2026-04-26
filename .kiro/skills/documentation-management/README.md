# Documentation Management Skill

A practical skill for maintaining minimal, high-quality documentation that developers actually read and use.

## Philosophy

**Quality over Quantity**: Focus on essential information, avoid duplication, keep docs synchronized with code.

**Minimum Viable Documentation (MVD)**: Document what matters, skip what doesn't. Capture WHY, not just HOW.

**Structure**: README in root (overview), detailed docs in /docs folder.

## What This Skill Covers

- **Documentation Structure**: Root files vs /docs folder organization
- **MVD Principles**: Essential information only, no over-documentation
- **Writing Guidelines**: Clear, concise technical writing
- **Templates**: Ready-to-use templates for common docs
- **Maintenance**: Keeping docs current with code changes
- **Consolidation**: Merging duplicate and scattered docs

## When to Use This Skill

Activate when:
- Creating new project documentation
- Updating docs after code changes
- Reviewing documentation quality
- Consolidating scattered or duplicate docs
- Setting up documentation for new project
- Ensuring docs follow best practices

## Structure

```
documentation-management/
├── SKILL.md                    # Main skill with quick reference
├── README.md                   # This file
└── references/                 # Detailed guides
    ├── index.md               # Navigation
    ├── mvd-principles.md      # Minimum Viable Documentation
    ├── structure-guide.md     # Folder structure best practices
    ├── writing-guide.md       # Technical writing guidelines
    └── templates.md           # Ready-to-use templates
```

## Quick Start

### For New Projects

1. Use README template from `references/templates.md`
2. Create /docs folder with 3-4 core files:
   - architecture.md
   - api.md
   - development.md
   - deployment.md
3. Keep README under 200 lines
4. Link README to detailed docs

### For Existing Projects

1. Audit current documentation
2. Consolidate duplicate content
3. Move detailed docs to /docs folder
4. Simplify README to overview + links
5. Remove outdated information

## Key Principles

### 1. Capture WHY, Not Just HOW

```markdown
❌ Bad: We use PostgreSQL.

✅ Good: We use PostgreSQL because:
- ACID compliance for transactions
- JSON support for flexible data
- Team has 5+ years experience
```

### 2. Keep README Minimal

- One-line project description
- Quick start (3-5 commands)
- Feature list
- Links to /docs folder
- Under 200 lines total

### 3. Avoid Duplication

- Don't repeat code in docs (link to code)
- Don't duplicate info across files
- Single source of truth for each topic

### 4. Update With Code

- Update docs in same PR as code changes
- Add doc updates to PR checklist
- Review docs regularly (quarterly)

## Documentation Structure

### Root Level (Minimal)

```
project/
├── README.md           # Overview only
├── LICENSE
└── docs/               # All detailed docs
    ├── architecture.md
    ├── api.md
    ├── development.md
    └── deployment.md
```

### What Goes Where

**README.md:**
- Project description (1 line)
- Quick start (3-5 commands)
- Features (bullet list)
- Links to docs

**docs/architecture.md:**
- System design
- Key decisions and WHY
- Technology stack rationale

**docs/api.md:**
- Endpoint reference
- Request/response examples
- Authentication

**docs/development.md:**
- Setup instructions
- Project structure
- Testing guide
- Contribution guidelines

**docs/deployment.md:**
- Deployment steps
- Environment variables
- Monitoring

## Common Patterns

### Consolidating Scattered Docs

```
Before: 15 files
- README.md
- SETUP.md
- INSTALL.md
- API_DOCS.md
- DEPLOY.md
- ...

After: 5 files
- README.md (overview)
- docs/architecture.md
- docs/api.md
- docs/development.md
- docs/deployment.md
```

### Updating After Feature Addition

1. Update relevant doc in /docs
2. Add one-line mention in README (if public-facing)
3. No duplication across files

## Anti-Patterns to Avoid

❌ **Don't:**
- Document every function
- Duplicate code in docs
- Scatter docs across project
- Let docs get out of sync
- Write walls of text

✅ **Do:**
- Document key decisions
- Link to code instead of copying
- Centralize docs in /docs folder
- Update docs with code changes
- Use clear, concise language

## Examples Included

1. **New Project Setup**: Creating docs from scratch
2. **Consolidation**: Merging 15 files into 5
3. **Feature Update**: Documenting new OAuth feature

## Resources

- `references/mvd-principles.md`: Minimum Viable Documentation
- `references/structure-guide.md`: Folder organization
- `references/writing-guide.md`: Technical writing
- `references/templates.md`: Ready-to-use templates

## Maintenance

- **Sources**: Industry best practices, MVD principles, folder structure conventions
- **Created**: 2026-04-19
- **Philosophy**: Quality over quantity, essential information only

## Quick Reference

### Documentation Checklist

- [ ] README under 200 lines
- [ ] No duplicate information
- [ ] All links work
- [ ] Code examples tested
- [ ] Outdated info removed
- [ ] WHY explained for key decisions
- [ ] Quick start works in clean environment

### File Limits

- README.md: < 200 lines
- Core docs: 300-1000 lines each
- Split if > 1000 lines
- Merge if < 100 lines each

### Update Triggers

Update docs when:
- API changes → docs/api.md
- Config changes → docs/deployment.md
- Setup changes → docs/development.md
- Architecture changes → docs/architecture.md
