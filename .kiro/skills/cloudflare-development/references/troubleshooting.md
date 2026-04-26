# Cloudflare Workers Troubleshooting Guide

Common issues, error messages, and solutions for Cloudflare Workers development.

## CPU Time Limit Exceeded

### Error Message
```
Error: Script exceeded CPU time limit
```

### Causes
- Infinite loops or recursive functions
- Heavy computation in request handler
- Large data processing without streaming
- Synchronous operations blocking execution

### Solutions

**1. Use async/await properly:**
```javascript
// ❌ Bad: Blocking synchronous loop
for (let i = 0; i < 1000000; i++) {
  // Heavy computation
}

// ✅ Good: Break into chunks with await
async function processInChunks(data) {
  const chunkSize = 1000;
  for (let i = 0; i < data.length; i += chunkSize) {
    const chunk = data.slice(i, i + chunkSize);
    await processChunk(chunk);
  }
}
```

**2. Use streaming for large responses:**
```javascript
// ✅ Stream large data instead of buffering
const { readable, writable } = new TransformStream();
const writer = writable.getWriter();

// Process and write in chunks
(async () => {
  for (const chunk of largeData) {
    await writer.write(chunk);
  }
  await writer.close();
})();

return new Response(readable);
```

**3. Move heavy computation to background:**
```javascript
export default {
  async fetch(request, env, ctx) {
    // Return response immediately
    const response = new Response('Processing started');
    
    // Continue processing in background
    ctx.waitUntil(heavyComputation(request, env));
    
    return response;
  }
};
```

**4. Optimize algorithms:**
```javascript
// ❌ Bad: O(n²) complexity
for (let i = 0; i < items.length; i++) {
  for (let j = 0; j < items.length; j++) {
    // ...
  }
}

// ✅ Good: Use Map for O(1) lookups
const itemMap = new Map(items.map(item => [item.id, item]));
const result = itemMap.get(targetId);
```

## Memory Limit Exceeded

### Error Message
```
Error: Worker exceeded memory limit
```

### Causes
- Loading large files into memory
- Accumulating data in arrays/objects
- Memory leaks in long-running operations
- Large JSON parsing

### Solutions

**1. Stream instead of buffering:**
```javascript
// ❌ Bad: Load entire file into memory
const object = await env.BUCKET.get('large-file.json');
const data = await object.json(); // Loads entire file

// ✅ Good: Stream the response
const object = await env.BUCKET.get('large-file.json');
return new Response(object.body);
```

**2. Process data in chunks:**
```javascript
// ✅ Process line by line
async function processLargeFile(stream) {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line
    
    for (const line of lines) {
      await processLine(line);
    }
  }
}
```

**3. Limit data accumulation:**
```javascript
// ❌ Bad: Accumulate all results
const results = [];
for (const item of items) {
  results.push(await process(item));
}

// ✅ Good: Process and discard
for (const item of items) {
  const result = await process(item);
  await saveResult(result); // Save immediately
}
```

## Network/Fetch Errors

### Error: `fetch failed`

**Causes:**
- Target server is down or unreachable
- DNS resolution failure
- SSL/TLS certificate issues
- Timeout

**Solutions:**

```javascript
// Add retry logic with exponential backoff
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, {
        ...options,
        signal: AbortSignal.timeout(10000), // 10s timeout
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return response;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Exponential backoff
      await new Promise(resolve => 
        setTimeout(resolve, Math.pow(2, i) * 1000)
      );
    }
  }
}
```

### Error: `Too many subrequests`

**Cause:** Exceeded limit of 50 subrequests per Worker invocation

**Solutions:**

```javascript
// ❌ Bad: Making requests in loop
for (const url of urls) {
  await fetch(url);
}

// ✅ Good: Batch requests with Promise.all
const batchSize = 10;
for (let i = 0; i < urls.length; i += batchSize) {
  const batch = urls.slice(i, i + batchSize);
  await Promise.all(batch.map(url => fetch(url)));
}

// ✅ Better: Use a queue or background task
ctx.waitUntil(processUrlsInBackground(urls, env));
```

## KV Issues

### Error: `KV GET operation failed`

**Causes:**
- Namespace not bound correctly
- Key doesn't exist
- Network issues

**Solutions:**

```javascript
// Always check for null
const value = await env.MY_KV.get('key');
if (value === null) {
  return new Response('Not found', { status: 404 });
}

// Add error handling
try {
  const value = await env.MY_KV.get('key');
  return Response.json({ value });
} catch (error) {
  console.error('KV error:', error);
  return new Response('Service unavailable', { status: 503 });
}
```

### Issue: Stale data after write

**Cause:** KV is eventually consistent

**Solutions:**

```javascript
// Use cache headers to control freshness
await env.MY_KV.put('key', 'value');

// For critical data, use Durable Objects instead
const id = env.COUNTER.idFromName('critical-data');
const stub = env.COUNTER.get(id);
await stub.fetch('/update');
```

## R2 Issues

### Error: `R2 bucket not found`

**Causes:**
- Bucket doesn't exist
- Incorrect binding configuration
- Wrong bucket name

**Solutions:**

```javascript
// Check wrangler.toml
[[r2_buckets]]
binding = "MY_BUCKET"  // Must match env.MY_BUCKET
bucket_name = "my-bucket"  // Actual bucket name

// Verify bucket exists
try {
  const object = await env.MY_BUCKET.get('test');
} catch (error) {
  console.error('Bucket error:', error);
  return new Response('Storage unavailable', { status: 503 });
}
```

### Issue: Large file upload fails

**Cause:** Trying to upload files larger than Worker memory limit

**Solutions:**

```javascript
// ✅ Stream uploads for large files
async function uploadLargeFile(request, env) {
  const contentLength = request.headers.get('content-length');
  
  if (contentLength && parseInt(contentLength) > 100 * 1024 * 1024) {
    // For files > 100MB, use multipart upload
    return await multipartUpload(request, env);
  }
  
  // Stream directly to R2
  await env.MY_BUCKET.put('file', request.body);
  return new Response('Uploaded', { status: 201 });
}
```

## D1 Issues

### Error: `D1_ERROR: no such table`

**Causes:**
- Migrations not applied
- Wrong database binding
- Table doesn't exist

**Solutions:**

```bash
# Apply migrations locally
wrangler d1 migrations apply my-database --local

# Apply migrations remotely
wrangler d1 migrations apply my-database --remote

# Verify tables exist
wrangler d1 execute my-database --remote --command "SELECT name FROM sqlite_master WHERE type='table'"
```

### Error: `D1_ERROR: database is locked`

**Cause:** Concurrent writes to same database

**Solutions:**

```javascript
// Use transactions for multiple writes
const results = await env.DB.batch([
  env.DB.prepare('INSERT INTO users (name) VALUES (?)').bind('John'),
  env.DB.prepare('INSERT INTO profiles (user_id) VALUES (?)').bind(1)
]);

// Add retry logic for locked database
async function executeWithRetry(statement, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await statement.run();
    } catch (error) {
      if (error.message.includes('locked') && i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, 100 * (i + 1)));
        continue;
      }
      throw error;
    }
  }
}
```

## Durable Objects Issues

### Error: `Durable Object not found`

**Causes:**
- Migration not applied
- Incorrect binding configuration
- Class name mismatch

**Solutions:**

```toml
# Verify wrangler.toml configuration
[[durable_objects.bindings]]
name = "COUNTER"  # Must match env.COUNTER
class_name = "Counter"  # Must match export class Counter

[[migrations]]
tag = "v1"
new_classes = ["Counter"]  # Must match class_name
```

```javascript
// Verify export
export class Counter {  // Must be exported
  constructor(state, env) {
    this.state = state;
  }
  
  async fetch(request) {
    // ...
  }
}
```

### Issue: Cold start latency

**Cause:** Durable Object hasn't been accessed recently

**Solutions:**

```javascript
// Implement lazy loading
export class Counter {
  constructor(state, env) {
    this.state = state;
    this.initialized = false;
  }

  async initialize() {
    if (!this.initialized) {
      this.value = (await this.state.storage.get('count')) || 0;
      this.initialized = true;
    }
  }

  async fetch(request) {
    await this.initialize();
    // Handle request
  }
}
```

## Deployment Issues

### Error: `Authentication error`

**Solutions:**

```bash
# Re-authenticate
wrangler logout
wrangler login

# Or use API token
wrangler login --api-token YOUR_API_TOKEN

# Verify authentication
wrangler whoami
```

### Error: `Script validation failed`

**Causes:**
- Syntax errors in code
- Missing dependencies
- Incompatible Node.js APIs

**Solutions:**

```bash
# Check for syntax errors
npm run build  # If using build step

# Test locally first
wrangler dev

# Deploy with dry-run
wrangler deploy --dry-run

# Check compatibility
wrangler deploy --compatibility-date 2024-01-01
```

### Issue: Environment variables not working

**Solutions:**

```toml
# Verify wrangler.toml
[vars]
ENVIRONMENT = "production"
API_URL = "https://api.example.com"

# For secrets, use wrangler secret
# wrangler secret put API_KEY
```

```javascript
// Access in Worker
export default {
  async fetch(request, env, ctx) {
    console.log(env.ENVIRONMENT);  // "production"
    console.log(env.API_KEY);  // Secret value
    return new Response('OK');
  }
};
```

## Debugging Techniques

### Enable Verbose Logging

```javascript
// Add detailed logging
export default {
  async fetch(request, env, ctx) {
    console.log('Request:', {
      method: request.method,
      url: request.url,
      headers: Object.fromEntries(request.headers),
    });
    
    try {
      const response = await handleRequest(request, env);
      console.log('Response:', response.status);
      return response;
    } catch (error) {
      console.error('Error:', error.message, error.stack);
      throw error;
    }
  }
};
```

### Use Wrangler Tail

```bash
# Tail all logs
wrangler tail

# Filter by status
wrangler tail --status error

# Filter by method
wrangler tail --method POST

# Output as JSON for processing
wrangler tail --format json | jq '.logs[]'
```

### Local Debugging with Inspector

```bash
# Start dev server with inspector
wrangler dev --inspector-port 9229

# Open Chrome DevTools
# Navigate to chrome://inspect
# Click "inspect" under Remote Target
```

### Test with curl

```bash
# Test Worker endpoint
curl -X POST https://my-worker.example.workers.dev/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John"}'

# Test with verbose output
curl -v https://my-worker.example.workers.dev

# Test with specific headers
curl -H "Authorization: Bearer token" \
     -H "X-Custom-Header: value" \
     https://my-worker.example.workers.dev
```

## Performance Issues

### Issue: Slow response times

**Diagnosis:**

```javascript
// Add timing measurements
export default {
  async fetch(request, env, ctx) {
    const start = Date.now();
    
    const kvStart = Date.now();
    const data = await env.MY_KV.get('key');
    console.log('KV time:', Date.now() - kvStart, 'ms');
    
    const fetchStart = Date.now();
    const response = await fetch('https://api.example.com');
    console.log('Fetch time:', Date.now() - fetchStart, 'ms');
    
    console.log('Total time:', Date.now() - start, 'ms');
    return new Response('OK');
  }
};
```

**Solutions:**

```javascript
// 1. Use Promise.all for parallel requests
const [kvData, apiData] = await Promise.all([
  env.MY_KV.get('key'),
  fetch('https://api.example.com')
]);

// 2. Implement caching
const cache = caches.default;
let response = await cache.match(request);
if (!response) {
  response = await fetch(request);
  ctx.waitUntil(cache.put(request, response.clone()));
}

// 3. Use edge caching
return new Response(data, {
  headers: {
    'Cache-Control': 'public, max-age=3600',
    'CDN-Cache-Control': 'max-age=86400',
  }
});
```

## Common Pitfalls

### 1. Not handling errors

```javascript
// ❌ Bad
const data = await env.MY_KV.get('key');
const parsed = JSON.parse(data);

// ✅ Good
try {
  const data = await env.MY_KV.get('key');
  if (!data) {
    return new Response('Not found', { status: 404 });
  }
  const parsed = JSON.parse(data);
} catch (error) {
  console.error('Error:', error);
  return new Response('Internal error', { status: 500 });
}
```

### 2. Blocking the event loop

```javascript
// ❌ Bad: Synchronous heavy computation
function heavyComputation() {
  let result = 0;
  for (let i = 0; i < 10000000; i++) {
    result += Math.sqrt(i);
  }
  return result;
}

// ✅ Good: Break into async chunks
async function heavyComputation() {
  let result = 0;
  const chunkSize = 10000;
  for (let i = 0; i < 10000000; i += chunkSize) {
    for (let j = 0; j < chunkSize && i + j < 10000000; j++) {
      result += Math.sqrt(i + j);
    }
    await new Promise(resolve => setTimeout(resolve, 0));
  }
  return result;
}
```

### 3. Not using ctx.waitUntil

```javascript
// ❌ Bad: Background task may not complete
export default {
  async fetch(request, env, ctx) {
    logToAnalytics(request); // May not complete
    return new Response('OK');
  }
};

// ✅ Good: Ensure background task completes
export default {
  async fetch(request, env, ctx) {
    ctx.waitUntil(logToAnalytics(request));
    return new Response('OK');
  }
};
```

## Getting Help

### Check Status

- [Cloudflare Status](https://www.cloudflarestatus.com/)
- [Workers Status](https://www.cloudflarestatus.com/incidents)

### Community Resources

- [Cloudflare Community](https://community.cloudflare.com/)
- [Workers Discord](https://discord.gg/cloudflaredev)
- [GitHub Discussions](https://github.com/cloudflare/workers-sdk/discussions)

### Support Channels

- [Cloudflare Support](https://support.cloudflare.com/)
- [Workers Documentation](https://developers.cloudflare.com/workers/)
- [API Documentation](https://developers.cloudflare.com/api/)
