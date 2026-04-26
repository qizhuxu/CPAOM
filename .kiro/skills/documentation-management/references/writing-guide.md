# Technical Writing Guide

## Core Principles

### 1. Write for Your Audience

**Know Who You're Writing For:**
- **New Users**: Need quick start and basic concepts
- **Contributors**: Need development setup and guidelines
- **Integrators**: Need API reference and examples
- **Operators**: Need deployment and troubleshooting

**Adjust Complexity:**
```markdown
❌ Bad (assumes too much):
Configure the ingress controller with TLS termination.

✅ Good (explains terms):
Configure the ingress controller (routes external traffic to services)
with TLS termination (handles HTTPS encryption at the edge).
```

### 2. Be Clear and Concise

**Use Simple Language:**
```markdown
❌ Bad:
Utilize the aforementioned methodology to instantiate the service.

✅ Good:
Use this method to start the service.
```

**Avoid Jargon (or Explain It):**
```markdown
❌ Bad:
The system uses CQRS with event sourcing.

✅ Good:
The system uses CQRS (Command Query Responsibility Segregation):
- Commands: Write operations (create, update, delete)
- Queries: Read operations (get, list, search)

Events are stored and replayed to rebuild state (event sourcing).
```

### 3. Show, Don't Just Tell

**Include Working Examples:**
```markdown
❌ Bad:
The API accepts JSON and returns user data.

✅ Good:
## Get User

```bash
curl -X GET https://api.example.com/users/123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com"
}
```
```

## Structure and Formatting

### Use Headings Effectively

**Create Clear Hierarchy:**
```markdown
# Main Topic (H1 - once per document)

## Major Section (H2)

### Subsection (H3)

#### Detail (H4 - use sparingly)
```

**Make Headings Descriptive:**
```markdown
❌ Bad:
## Overview
## Details
## More Info

✅ Good:
## System Architecture
## API Authentication
## Deployment Process
```

### Use Lists for Clarity

**Bullet Lists for Unordered Items:**
```markdown
## Features
- Real-time notifications
- User authentication
- File uploads
```

**Numbered Lists for Steps:**
```markdown
## Setup Process
1. Install dependencies
2. Configure environment
3. Run migrations
4. Start server
```

**Nested Lists for Hierarchy:**
```markdown
## Project Structure
- src/
  - api/ (API endpoints)
  - models/ (Data models)
  - utils/ (Helper functions)
- tests/
  - unit/
  - integration/
```

### Code Blocks

**Always Specify Language:**
```markdown
❌ Bad:
```
npm install
```

✅ Good:
```bash
npm install
```
```

**Add Context Before Code:**
```markdown
Install dependencies:
```bash
npm install
```

Start the development server:
```bash
npm run dev
```
```

**Show Expected Output:**
```markdown
Check if the server is running:
```bash
curl http://localhost:3000/health
```

Expected output:
```json
{"status": "ok"}
```
```

### Tables for Comparisons

**Use Tables for Structured Data:**
```markdown
## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| PORT | No | 3000 | Server port |
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| JWT_SECRET | Yes | - | Secret for JWT signing |
```

## Writing Patterns

### Quick Start Pattern

**Structure:**
1. Prerequisites (what you need)
2. Installation (how to install)
3. Configuration (minimal setup)
4. Verification (how to test it works)

**Example:**
```markdown
## Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 14+

### Installation
```bash
npm install
```

### Configuration
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and set:
- `DATABASE_URL`: Your PostgreSQL connection string
- `JWT_SECRET`: A random secret key

### Start the Server
```bash
npm start
```

### Verify
Visit http://localhost:3000/health

You should see: `{"status": "ok"}`
```

### API Documentation Pattern

**Structure:**
1. Endpoint and method
2. Description
3. Authentication requirements
4. Request format
5. Response format
6. Error codes
7. Example

**Example:**
```markdown
## POST /api/users

Create a new user account.

### Authentication
Requires admin API key in `X-API-Key` header.

### Request Body
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```

### Response (201 Created)
```json
{
  "id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "createdAt": "2024-03-15T10:30:00Z"
}
```

### Errors
- `400 Bad Request`: Invalid email format
- `401 Unauthorized`: Missing or invalid API key
- `409 Conflict`: Email already exists

### Example
```bash
curl -X POST https://api.example.com/users \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"John Doe","role":"user"}'
```
```

### Troubleshooting Pattern

**Structure:**
1. Symptom (what's wrong)
2. Cause (why it happens)
3. Solution (how to fix)
4. Prevention (how to avoid)

**Example:**
```markdown
## Database Connection Failed

### Symptom
Error: `ECONNREFUSED 127.0.0.1:5432`

### Cause
PostgreSQL is not running or not accessible.

### Solution
1. Check if PostgreSQL is running:
```bash
docker-compose ps postgres
```

2. If not running, start it:
```bash
docker-compose up -d postgres
```

3. Verify connection:
```bash
psql $DATABASE_URL -c "SELECT 1"
```

### Prevention
Add PostgreSQL to startup services or use Docker Compose
to manage dependencies.
```

## Common Mistakes

### Mistake 1: Assuming Knowledge

**Problem:**
```markdown
Configure the reverse proxy with SSL termination.
```

**Solution:**
```markdown
Configure nginx (reverse proxy) to handle HTTPS:
1. Install SSL certificate
2. Update nginx.conf with SSL settings
3. Restart nginx

See [nginx-ssl-setup.md](nginx-ssl-setup.md) for details.
```

### Mistake 2: Outdated Examples

**Problem:**
```markdown
Install version 1.2.3:
```bash
npm install package@1.2.3
```
```

**Solution:**
```markdown
Install the latest version:
```bash
npm install package
```

Or install a specific version:
```bash
npm install package@1.2.3
```
```

### Mistake 3: No Context

**Problem:**
```markdown
Run: `npm run migrate`
```

**Solution:**
```markdown
Apply database migrations to create tables:
```bash
npm run migrate
```

This creates the `users`, `posts`, and `comments` tables.
```

### Mistake 4: Walls of Text

**Problem:**
```markdown
The authentication system uses JWT tokens which are generated when a user logs in with valid credentials and the token contains the user ID and role and expires after 1 hour and can be refreshed using the refresh token endpoint and tokens are signed with HS256 algorithm using a secret key stored in environment variables.
```

**Solution:**
```markdown
## Authentication

The system uses JWT tokens for authentication:

**Token Generation:**
- User logs in with valid credentials
- Server generates JWT containing user ID and role
- Token expires after 1 hour

**Token Refresh:**
- Use `/api/auth/refresh` endpoint
- Provide refresh token to get new access token

**Security:**
- Tokens signed with HS256 algorithm
- Secret key stored in `JWT_SECRET` environment variable
```

## Style Guidelines

### Voice and Tone

**Use Active Voice:**
```markdown
❌ Passive: The database is queried by the API.
✅ Active: The API queries the database.
```

**Be Direct:**
```markdown
❌ Indirect: You might want to consider installing...
✅ Direct: Install the dependencies:
```

**Use Second Person (You):**
```markdown
❌ Third person: The developer should configure...
✅ Second person: Configure your environment:
```

### Consistency

**Be Consistent With:**
- Terminology (pick one term and stick with it)
- Code style (use same formatting)
- Structure (use same patterns)

**Example:**
```markdown
❌ Inconsistent:
- Login endpoint
- Authentication API
- Sign-in service

✅ Consistent:
- Authentication endpoint
- Authorization endpoint
- Token refresh endpoint
```

### Links and References

**Use Descriptive Link Text:**
```markdown
❌ Bad:
Click [here](link) for more info.

✅ Good:
See the [API Reference](link) for endpoint details.
```

**Use Relative Links:**
```markdown
❌ Bad:
[Setup](https://github.com/user/repo/blob/main/docs/setup.md)

✅ Good:
[Setup](setup.md)
```

## Documentation Review Checklist

Before publishing documentation:

**Content:**
- [ ] Accurate and up-to-date
- [ ] No outdated information
- [ ] Code examples tested and working
- [ ] All links valid (no 404s)

**Clarity:**
- [ ] Clear and concise language
- [ ] Technical terms explained
- [ ] Appropriate for target audience
- [ ] Examples provided where helpful

**Structure:**
- [ ] Logical organization
- [ ] Clear headings
- [ ] Proper formatting
- [ ] Consistent style

**Completeness:**
- [ ] Covers essential information
- [ ] No critical gaps
- [ ] Prerequisites listed
- [ ] Troubleshooting included

## Tools and Automation

### Markdown Linting

```bash
# Install markdownlint
npm install -g markdownlint-cli

# Lint documentation
markdownlint docs/**/*.md
```

### Link Checking

```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check links
markdown-link-check docs/**/*.md
```

### Spell Checking

```bash
# Install cspell
npm install -g cspell

# Check spelling
cspell docs/**/*.md
```

### Documentation Testing

```javascript
// Test code examples in docs
const { execSync } = require('child_process');
const fs = require('fs');

// Extract code blocks from markdown
const markdown = fs.readFileSync('docs/api.md', 'utf8');
const codeBlocks = markdown.match(/```bash\n([\s\S]*?)```/g);

// Test each code block
codeBlocks.forEach(block => {
  const code = block.replace(/```bash\n|```/g, '');
  try {
    execSync(code);
    console.log('✓ Code block works');
  } catch (error) {
    console.error('✗ Code block failed:', code);
  }
});
```

## Resources

- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://docs.microsoft.com/en-us/style-guide/)
- [Write the Docs](https://www.writethedocs.org/)
- [Markdown Guide](https://www.markdownguide.org/)
