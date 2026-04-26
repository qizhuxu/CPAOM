# Minimum Viable Documentation (MVD) Principles

## Core Philosophy

MVD is about creating documentation that is:
- **Essential**: Only what's truly needed
- **Maintainable**: Easy to keep up-to-date
- **Actionable**: Helps people do their job
- **Readable**: Actually gets read and used

Think of it as the Marie Kondo approach to documentation - keep only what sparks understanding.

## The Four Pillars

### 1. Capture the WHY, Not Just the HOW

**Bad Example:**
```markdown
## Database
We use PostgreSQL.
```

**Good Example:**
```markdown
## Database Choice: PostgreSQL

Why PostgreSQL over alternatives:
- ACID compliance required for financial transactions
- JSON support for flexible user metadata
- Mature replication for high availability
- Team has 5+ years PostgreSQL experience

Alternatives considered:
- MongoDB: Rejected due to lack of multi-document transactions
- MySQL: Rejected due to weaker JSON support
```

**Why This Matters:**
- Future developers understand the reasoning
- Prevents "why did we do this?" questions
- Makes it easier to know when to change decisions

### 2. Focus on Fundamentals

Document what changes slowly, skip what changes often.

**Document:**
- Core architecture and design patterns
- Key technology choices and rationale
- Critical workflows and processes
- Security and compliance requirements
- Integration points and contracts

**Don't Document:**
- Implementation details (code is the source of truth)
- Obvious code behavior (self-documenting code)
- Temporary workarounds (add TODO comments instead)
- Every function and parameter (use types/interfaces)

**Example:**
```markdown
# Good: Document the pattern
## Error Handling Strategy
All API errors follow RFC 7807 Problem Details format.

Example:
{
  "type": "https://api.example.com/errors/insufficient-funds",
  "title": "Insufficient Funds",
  "status": 400,
  "detail": "Account balance is $50, transaction requires $100"
}

Why: Standardized format makes client error handling consistent.

# Bad: Document every error
## getUserById Errors
- Returns 404 if user not found
- Returns 500 if database error
- Returns 401 if not authenticated
... (repeated for every function)
```

### 3. Keep It Current

Less documentation = easier to maintain.

**Strategies:**

**Link to Code Instead of Duplicating:**
```markdown
❌ Bad:
## User Model Fields
- id: UUID
- email: string
- name: string
- created_at: timestamp
(Gets out of sync with actual schema)

✅ Good:
## User Model
See [src/models/User.ts](../src/models/User.ts) for schema.

Key design decisions:
- UUID for distributed system compatibility
- Email as unique identifier (not username)
- Soft delete pattern (deleted_at field)
```

**Automate Staleness Detection:**
```javascript
// In CI/CD pipeline
const lastDocUpdate = getLastModified('docs/api.md');
const lastApiChange = getLastModified('src/api/**');

if (lastApiChange > lastDocUpdate) {
  console.warn('⚠️  API changed but docs not updated');
}
```

**Regular Review Schedule:**
```markdown
# Add to quarterly team tasks
- [ ] Review and update architecture.md
- [ ] Verify all code examples still work
- [ ] Remove outdated information
- [ ] Check all links are valid
```

### 4. Make It Actionable

Every piece of documentation should help someone accomplish a task.

**Test: Can Someone Use This?**

**Bad (Not Actionable):**
```markdown
## Deployment
The application is deployed using Docker containers.
```

**Good (Actionable):**
```markdown
## Deploying to Production

1. Build and tag image:
```bash
docker build -t myapp:v1.2.3 .
docker tag myapp:v1.2.3 registry.example.com/myapp:v1.2.3
```

2. Push to registry:
```bash
docker push registry.example.com/myapp:v1.2.3
```

3. Update production:
```bash
kubectl set image deployment/myapp myapp=registry.example.com/myapp:v1.2.3
kubectl rollout status deployment/myapp
```

4. Verify deployment:
```bash
curl https://api.example.com/health
# Should return: {"status": "ok", "version": "1.2.3"}
```

Rollback if needed:
```bash
kubectl rollout undo deployment/myapp
```
```

## Practical Application

### Documentation Hierarchy

**Level 1: README (2-5 minutes to read)**
- What the project does (one sentence)
- Quick start (3-5 commands)
- Links to detailed docs

**Level 2: Core Docs (10-15 minutes each)**
- Architecture overview
- API reference
- Development guide
- Deployment guide

**Level 3: Deep Dives (30+ minutes)**
- Detailed design documents
- Performance optimization guides
- Troubleshooting guides
- Migration guides

### The 80/20 Rule

80% of documentation needs are met by 20% of content:
- README with quick start
- Architecture overview
- API reference
- Development setup

Focus on getting these right before adding more.

### Documentation Debt

Like technical debt, documentation debt compounds:

**Signs of Documentation Debt:**
- Developers ask same questions repeatedly
- Onboarding takes weeks instead of days
- "Tribal knowledge" not written down
- Docs contradict actual behavior
- Multiple docs say different things

**Paying Down Documentation Debt:**
1. Start with most-asked questions
2. Document one thing well, not everything poorly
3. Delete outdated docs (don't just mark as old)
4. Consolidate duplicate information
5. Make docs part of definition of done

## MVD in Practice

### Example: Password Strength Checker

**Traditional Documentation (Too Much):**
```markdown
## Password Strength Checker

### Overview
The password strength checker is a component that validates user passwords.

### Installation
npm install zxcvbn

### Usage
Import the function:
import { checkPasswordStrength } from './utils';

Call the function:
const result = checkPasswordStrength(password);

### Parameters
- password (string): The password to check

### Return Value
Object with score and feedback properties

### Score Values
- 0: Too weak
- 1: Weak
- 2: Fair
- 3: Good
- 4: Strong

### Implementation Details
Uses zxcvbn library internally...
(continues for pages)
```

**MVD Approach (Just Enough):**
```markdown
## Password Strength Checker

### Purpose
Ensure user passwords meet security standards without frustrating users.

### Key Decisions
- Using zxcvbn library (better than regex rules)
- Requiring minimum score of 3/4
- Real-time feedback as user types

### Implementation
```typescript
import zxcvbn from 'zxcvbn';

function checkPasswordStrength(password: string) {
  const result = zxcvbn(password);
  return {
    score: result.score, // 0-4
    feedback: result.feedback.suggestions[0] || ''
  };
}
```

### Why This Approach
- zxcvbn provides nuanced assessment beyond simple rules
- Score 3+ balances security with user experience
- Real-time feedback educates users

### Future Considerations
- Add password breach checking (see ticket SEC-123)
- Consider adjusting threshold based on account type
```

## Common Mistakes

### Mistake 1: Documenting Everything

**Problem:** Trying to document every detail leads to:
- Overwhelming amount of content
- Outdated information
- Nobody reads it

**Solution:** Document decisions and patterns, not implementations.

### Mistake 2: Duplicating Code in Docs

**Problem:** Code examples in docs get out of sync with actual code.

**Solution:** 
- Link to actual code files
- Use tested code snippets (from test files)
- Document behavior, not implementation

### Mistake 3: No Clear Audience

**Problem:** Docs try to serve everyone and serve no one well.

**Solution:** 
- README: New users and evaluators
- Development Guide: Contributors
- Architecture: Technical decision makers
- API Docs: Integrators

### Mistake 4: Writing for Today

**Problem:** Docs assume current context that won't exist in 6 months.

**Solution:**
- Explain why decisions were made
- Document alternatives considered
- Include context about constraints

## Measuring Success

Good documentation should:
- ✅ Reduce repeated questions in chat/email
- ✅ Speed up onboarding (measure time to first PR)
- ✅ Decrease "how do I..." support tickets
- ✅ Enable self-service problem solving
- ✅ Stay current with code changes

Bad documentation:
- ❌ Nobody reads it
- ❌ Contradicts actual behavior
- ❌ Requires constant updates
- ❌ Doesn't answer real questions
- ❌ Duplicates information

## Resources

- [Minimum Viable Documentation](https://trevorlasn.com/blog/minimum-viable-documentation)
- [Google Documentation Best Practices](https://google.github.io/styleguide/docguide/best_practices.html)
- [Agile Documentation](https://deepdocs.dev/documentation-in-agile-development/)
