---
name: cloudflare-development
description: "Cloudflare platform development: includes Workers, Pages, R2, KV, D1, Durable Objects, Queues, and Wrangler CLI. Use when building serverless applications, edge functions, static sites, or managing Cloudflare infrastructure."
---

# Cloudflare Development Skill

Comprehensive guide for developing and deploying applications on the Cloudflare platform, covering Workers (serverless functions), Pages (static sites), storage solutions (R2, KV, D1), and infrastructure management.

## When to Use This Skill

Trigger when any of these applies:
- Building serverless functions or edge computing applications
- Deploying static sites or JAMstack applications
- Working with Cloudflare Workers, Pages, or Wrangler CLI
- Implementing object storage (R2), key-value storage (KV), or SQL databases (D1)
- Setting up Durable Objects for stateful applications
- Configuring Cloudflare Queues for message processing
- Managing Cloudflare infrastructure as code
- Debugging or optimizing edge function performance
- Implementing authentication, caching, or routing at the edge

## Not For / Boundaries

This skill does NOT cover:
- Cloudflare DNS management (use Cloudflare API skill)
- Cloudflare CDN configuration (use Cloudflare dashboard or API)
- Non-Cloudflare serverless platforms (AWS Lambda, Azure Functions, etc.)
- Full-stack frameworks unless specifically deployed to Cloudflare

Required inputs:
- Cloudflare account with appropriate permissions
- Wrangler CLI installed (for local development)
- Node.js environment (v16.13.0 or later)

## Quick Reference

### Wrangler CLI Basics

**Initialize new Worker project:**
```bash
npm create cloudflare@latest my-worker
# or
wrangler init my-worker
```

**Start local development server:**
```bash
wrangler dev
# With remote resources
wrangler dev --remote
```

**Deploy to Cloudflare:**
```bash
wrangler deploy
```

**Tail live logs:**
```bash
wrangler tail
```

**Manage secrets:**
```bash
wrangler secret put SECRET_NAME
wrangler secret list
wrangler secret delete SECRET_NAME
```

### Workers Patterns

**Basic Worker (Fetch Handler):**
```javascript
export default {
  async fetch(request, env, ctx) {
    return new Response('Hello World!', {
      headers: { 'Content-Type': 'text/plain' }
    });
  }
};
```

**Router Pattern:**
```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    if (url.pathname === '/api/users') {
      return handleUsers(request, env);
    }
    
    if (url.pathname.startsWith('/api/posts')) {
      return handlePosts(request, env);
    }
    
    return new Response('Not Found', { status: 404 });
  }
};
```

**CORS Headers:**
```javascript
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    const response = await handleRequest(request, env);
    return new Response(response.body, {
      ...response,
      headers: { ...response.headers, ...corsHeaders }
    });
  }
};
```

### KV Storage

**wrangler.toml configuration:**
```toml
[[kv_namespaces]]
binding = "MY_KV"
id = "your-kv-namespace-id"
```

**Basic operations:**
```javascript
// Write
await env.MY_KV.put('key', 'value');
await env.MY_KV.put('key', JSON.stringify({ data: 'value' }));

// Read
const value = await env.MY_KV.get('key');
const json = await env.MY_KV.get('key', { type: 'json' });

// Delete
await env.MY_KV.delete('key');

// List keys
const keys = await env.MY_KV.list({ prefix: 'user:' });
```

**With expiration:**
```javascript
// Expire in 60 seconds
await env.MY_KV.put('key', 'value', { expirationTtl: 60 });

// Expire at specific time
await env.MY_KV.put('key', 'value', { expiration: Math.floor(Date.now() / 1000) + 3600 });
```

### R2 Storage

**wrangler.toml configuration:**
```toml
[[r2_buckets]]
binding = "MY_BUCKET"
bucket_name = "my-bucket"
```

**Upload object:**
```javascript
await env.MY_BUCKET.put('file.txt', 'Hello World', {
  httpMetadata: {
    contentType: 'text/plain',
  },
  customMetadata: {
    userId: '123',
  }
});
```

**Download object:**
```javascript
const object = await env.MY_BUCKET.get('file.txt');
if (object === null) {
  return new Response('Not Found', { status: 404 });
}

return new Response(object.body, {
  headers: {
    'Content-Type': object.httpMetadata.contentType,
  }
});
```

**List objects:**
```javascript
const list = await env.MY_BUCKET.list({ prefix: 'uploads/' });
for (const object of list.objects) {
  console.log(object.key, object.size);
}
```

**Delete object:**
```javascript
await env.MY_BUCKET.delete('file.txt');
```

### D1 Database

**wrangler.toml configuration:**
```toml
[[d1_databases]]
binding = "DB"
database_name = "my-database"
database_id = "your-database-id"
```

**Execute queries:**
```javascript
// Single query
const result = await env.DB.prepare('SELECT * FROM users WHERE id = ?')
  .bind(userId)
  .first();

// Multiple queries in batch
const results = await env.DB.batch([
  env.DB.prepare('INSERT INTO users (name, email) VALUES (?, ?)').bind('John', 'john@example.com'),
  env.DB.prepare('SELECT * FROM users WHERE email = ?').bind('john@example.com')
]);

// Get all results
const { results } = await env.DB.prepare('SELECT * FROM users').all();
```

**Migrations:**
```bash
# Create migration
wrangler d1 migrations create my-database create_users_table

# Apply migrations
wrangler d1 migrations apply my-database --local
wrangler d1 migrations apply my-database --remote
```

### Durable Objects

**wrangler.toml configuration:**
```toml
[[durable_objects.bindings]]
name = "COUNTER"
class_name = "Counter"
script_name = "my-worker"

[[migrations]]
tag = "v1"
new_classes = ["Counter"]
```

**Durable Object class:**
```javascript
export class Counter {
  constructor(state, env) {
    this.state = state;
  }

  async fetch(request) {
    let count = (await this.state.storage.get('count')) || 0;
    count++;
    await this.state.storage.put('count', count);
    return new Response(count.toString());
  }
}
```

**Using Durable Objects:**
```javascript
export default {
  async fetch(request, env, ctx) {
    const id = env.COUNTER.idFromName('global-counter');
    const stub = env.COUNTER.get(id);
    return stub.fetch(request);
  }
};
```

### Cloudflare Pages

**Deploy via Wrangler:**
```bash
wrangler pages deploy ./dist --project-name=my-site
```

**Pages Functions (_worker.js):**
```javascript
// functions/_middleware.js
export async function onRequest(context) {
  const response = await context.next();
  response.headers.set('X-Custom-Header', 'value');
  return response;
}

// functions/api/hello.js
export async function onRequestGet(context) {
  return new Response('Hello from Pages Function!');
}
```

**Environment variables:**
```bash
wrangler pages secret put SECRET_NAME --project-name=my-site
```

### Queues

**wrangler.toml configuration:**
```toml
[[queues.producers]]
binding = "MY_QUEUE"
queue = "my-queue"

[[queues.consumers]]
queue = "my-queue"
max_batch_size = 10
max_batch_timeout = 30
```

**Send messages:**
```javascript
await env.MY_QUEUE.send({
  userId: '123',
  action: 'process',
  timestamp: Date.now()
});

// Batch send
await env.MY_QUEUE.sendBatch([
  { body: { id: 1 } },
  { body: { id: 2 } },
  { body: { id: 3 } }
]);
```

**Consume messages:**
```javascript
export default {
  async queue(batch, env) {
    for (const message of batch.messages) {
      console.log('Processing:', message.body);
      // Process message
      message.ack(); // Acknowledge successful processing
    }
  }
};
```

### Environment Variables

**wrangler.toml:**
```toml
[env.production]
vars = { ENVIRONMENT = "production" }

[env.staging]
vars = { ENVIRONMENT = "staging" }
```

**Access in Worker:**
```javascript
export default {
  async fetch(request, env, ctx) {
    const environment = env.ENVIRONMENT;
    return new Response(`Running in ${environment}`);
  }
};
```

### Caching

**Cache API:**
```javascript
export default {
  async fetch(request, env, ctx) {
    const cache = caches.default;
    let response = await cache.match(request);
    
    if (!response) {
      response = await fetch(request);
      // Cache for 1 hour
      response = new Response(response.body, response);
      response.headers.set('Cache-Control', 'max-age=3600');
      ctx.waitUntil(cache.put(request, response.clone()));
    }
    
    return response;
  }
};
```

**Custom cache key:**
```javascript
const cacheKey = new Request(url.toString(), request);
const response = await cache.match(cacheKey);
```

### Error Handling

**Try-catch pattern:**
```javascript
export default {
  async fetch(request, env, ctx) {
    try {
      return await handleRequest(request, env);
    } catch (error) {
      console.error('Error:', error);
      return new Response('Internal Server Error', { status: 500 });
    }
  }
};
```

**Custom error responses:**
```javascript
class APIError extends Error {
  constructor(message, status = 500) {
    super(message);
    this.status = status;
  }
}

async function handleRequest(request, env) {
  if (!request.headers.get('Authorization')) {
    throw new APIError('Unauthorized', 401);
  }
  // ... handle request
}
```

## Examples

### Example 1: REST API with KV Storage

**Input:** Build a simple REST API for managing user data with KV storage

**Steps:**
1. Initialize project: `wrangler init user-api`
2. Configure KV namespace in `wrangler.toml`:
```toml
name = "user-api"
main = "src/index.js"
compatibility_date = "2024-01-01"

[[kv_namespaces]]
binding = "USERS"
id = "your-kv-namespace-id"
```

3. Implement Worker:
```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const userId = url.pathname.split('/')[2];
    
    // GET /users/:id
    if (request.method === 'GET' && userId) {
      const user = await env.USERS.get(`user:${userId}`, { type: 'json' });
      if (!user) {
        return new Response('User not found', { status: 404 });
      }
      return Response.json(user);
    }
    
    // POST /users
    if (request.method === 'POST' && url.pathname === '/users') {
      const user = await request.json();
      const id = crypto.randomUUID();
      await env.USERS.put(`user:${id}`, JSON.stringify({ id, ...user }));
      return Response.json({ id, ...user }, { status: 201 });
    }
    
    // DELETE /users/:id
    if (request.method === 'DELETE' && userId) {
      await env.USERS.delete(`user:${userId}`);
      return new Response(null, { status: 204 });
    }
    
    return new Response('Not Found', { status: 404 });
  }
};
```

4. Deploy: `wrangler deploy`

**Expected output:** Functional REST API accessible at `https://user-api.your-subdomain.workers.dev`

### Example 2: Image Resizing with R2

**Input:** Create a Worker that resizes images stored in R2

**Steps:**
1. Configure R2 bucket in `wrangler.toml`:
```toml
[[r2_buckets]]
binding = "IMAGES"
bucket_name = "my-images"
```

2. Implement Worker with image resizing:
```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const key = url.pathname.slice(1);
    const width = url.searchParams.get('width');
    
    // Get image from R2
    const object = await env.IMAGES.get(key);
    if (!object) {
      return new Response('Image not found', { status: 404 });
    }
    
    // If no resize requested, return original
    if (!width) {
      return new Response(object.body, {
        headers: {
          'Content-Type': object.httpMetadata.contentType,
          'Cache-Control': 'public, max-age=31536000',
        }
      });
    }
    
    // Resize using Cloudflare Image Resizing
    const resizeRequest = new Request(request.url, {
      cf: {
        image: {
          width: parseInt(width),
          quality: 85,
        }
      }
    });
    
    return fetch(resizeRequest);
  }
};
```

3. Upload images: `wrangler r2 object put IMAGES/photo.jpg --file=./photo.jpg`
4. Deploy: `wrangler deploy`

**Expected output:** Image resizing service at `https://images.your-subdomain.workers.dev/photo.jpg?width=300`

### Example 3: Real-time Counter with Durable Objects

**Input:** Build a real-time visitor counter using Durable Objects

**Steps:**
1. Configure Durable Objects in `wrangler.toml`:
```toml
[[durable_objects.bindings]]
name = "COUNTER"
class_name = "Counter"

[[migrations]]
tag = "v1"
new_classes = ["Counter"]
```

2. Implement Durable Object:
```javascript
export class Counter {
  constructor(state, env) {
    this.state = state;
    this.sessions = new Set();
  }

  async fetch(request) {
    const url = new URL(request.url);
    
    if (url.pathname === '/increment') {
      let count = (await this.state.storage.get('count')) || 0;
      count++;
      await this.state.storage.put('count', count);
      return Response.json({ count });
    }
    
    if (url.pathname === '/get') {
      const count = (await this.state.storage.get('count')) || 0;
      return Response.json({ count });
    }
    
    if (url.pathname === '/reset') {
      await this.state.storage.put('count', 0);
      return Response.json({ count: 0 });
    }
    
    return new Response('Not Found', { status: 404 });
  }
}

export default {
  async fetch(request, env, ctx) {
    const id = env.COUNTER.idFromName('global-counter');
    const stub = env.COUNTER.get(id);
    return stub.fetch(request);
  }
};
```

3. Deploy: `wrangler deploy`

**Expected output:** Persistent counter accessible at `https://counter.your-subdomain.workers.dev/get`

## References

- `references/index.md`: Navigation to all reference materials
- `references/workers-api.md`: Complete Workers API reference
- `references/storage-comparison.md`: KV vs R2 vs D1 comparison
- `references/wrangler-commands.md`: Comprehensive Wrangler CLI reference
- `references/deployment-strategies.md`: Production deployment patterns
- `references/performance-optimization.md`: Edge performance best practices
- `references/troubleshooting.md`: Common issues and solutions

## Maintenance

- Sources: Official Cloudflare documentation, Wrangler CLI docs, Workers examples
- Last updated: 2026-04-21
- Known limits: 
  - Workers CPU time limit (10ms on free plan, 50ms on paid)
  - KV eventual consistency (not suitable for strong consistency requirements)
  - R2 pricing based on operations and storage
  - D1 currently in beta with usage limits
