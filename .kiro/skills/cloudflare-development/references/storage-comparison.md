# Cloudflare Storage Solutions Comparison

Detailed comparison of storage options available in Cloudflare Workers ecosystem.

## Overview Table

| Feature | KV | R2 | D1 | Durable Objects Storage |
|---------|----|----|----|-----------------------|
| **Type** | Key-Value | Object Storage | SQL Database | Transactional KV |
| **Consistency** | Eventual | Strong | Strong | Strong |
| **Max Value Size** | 25 MB | 5 TB per object | N/A (row-based) | 128 KB per key |
| **Read Latency** | <10ms | ~50-100ms | ~10-50ms | <1ms (in-memory) |
| **Write Latency** | ~1 second | ~100-200ms | ~10-50ms | <1ms |
| **Best For** | Caching, config | Files, media | Structured data | Real-time state |
| **Pricing Model** | Read/Write ops | Storage + ops | Rows read/written | Duration + requests |

## KV (Workers KV)

### When to Use
- Configuration data that changes infrequently
- Caching API responses or computed results
- User preferences and settings
- Session data (with eventual consistency tolerance)
- Static content distribution
- Feature flags

### Characteristics
- **Eventual consistency**: Writes propagate globally in ~60 seconds
- **High read performance**: Optimized for high read volumes
- **Global replication**: Automatically replicated to all Cloudflare data centers
- **TTL support**: Automatic expiration of keys
- **List operations**: Can list keys with prefix filtering

### Limitations
- Not suitable for data requiring strong consistency
- Write operations are slower (eventual consistency)
- Limited to 25 MB per value
- List operations are eventually consistent
- No transactions or atomic operations across keys

### Pricing (as of 2024)
- **Free tier**: 100,000 reads/day, 1,000 writes/day, 1 GB storage
- **Paid**: $0.50 per million reads, $5.00 per million writes, $0.50/GB/month storage

### Code Example
```javascript
// Write with TTL
await env.MY_KV.put('session:123', JSON.stringify(sessionData), {
  expirationTtl: 3600 // 1 hour
});

// Read
const session = await env.MY_KV.get('session:123', { type: 'json' });

// List with prefix
const sessions = await env.MY_KV.list({ prefix: 'session:' });
```

## R2 (Object Storage)

### When to Use
- File uploads and downloads
- Media storage (images, videos, audio)
- Backup and archival
- Static website hosting
- Large dataset storage
- CDN origin storage

### Characteristics
- **S3-compatible API**: Easy migration from AWS S3
- **Strong consistency**: Immediate read-after-write consistency
- **No egress fees**: Free data transfer to the internet
- **Large objects**: Up to 5 TB per object
- **Metadata support**: Custom and HTTP metadata

### Limitations
- Higher latency than KV for small values
- Not suitable for frequently updated small data
- No built-in search or query capabilities
- Requires separate bucket creation

### Pricing (as of 2024)
- **Storage**: $0.015/GB/month
- **Class A operations** (write, list): $4.50 per million
- **Class B operations** (read): $0.36 per million
- **No egress fees**

### Code Example
```javascript
// Upload with metadata
await env.MY_BUCKET.put('uploads/image.jpg', imageBuffer, {
  httpMetadata: {
    contentType: 'image/jpeg',
    cacheControl: 'public, max-age=31536000',
  },
  customMetadata: {
    userId: '123',
    uploadedAt: new Date().toISOString(),
  }
});

// Download
const object = await env.MY_BUCKET.get('uploads/image.jpg');
const blob = await object.blob();

// List with pagination
let cursor;
do {
  const list = await env.MY_BUCKET.list({ 
    prefix: 'uploads/',
    cursor 
  });
  for (const obj of list.objects) {
    console.log(obj.key, obj.size);
  }
  cursor = list.truncated ? list.cursor : undefined;
} while (cursor);
```

## D1 (SQL Database)

### When to Use
- Structured relational data
- Complex queries with JOINs
- Data requiring ACID transactions
- Analytics and reporting
- User management systems
- Content management

### Characteristics
- **SQLite-based**: Familiar SQL syntax
- **Strong consistency**: ACID transactions
- **Migrations support**: Built-in migration system
- **Query batching**: Execute multiple queries efficiently
- **Global replication**: Read replicas in multiple regions

### Limitations
- Currently in beta (usage limits may apply)
- Not suitable for extremely high write volumes
- Database size limits (check current limits)
- No full-text search (yet)

### Pricing (as of 2024)
- **Free tier**: 5 GB storage, 5 million rows read/day, 100,000 rows written/day
- **Paid**: $0.75 per million rows read, $1.00 per million rows written, $0.75/GB/month storage

### Code Example
```javascript
// Single query with binding
const user = await env.DB.prepare(
  'SELECT * FROM users WHERE email = ?'
).bind(email).first();

// Batch queries (transactional)
const results = await env.DB.batch([
  env.DB.prepare('INSERT INTO users (name, email) VALUES (?, ?)').bind('John', 'john@example.com'),
  env.DB.prepare('INSERT INTO profiles (user_id, bio) VALUES (?, ?)').bind(userId, 'Hello'),
  env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(userId)
]);

// Get all results
const { results: allUsers } = await env.DB.prepare(
  'SELECT * FROM users ORDER BY created_at DESC LIMIT 100'
).all();
```

## Durable Objects Storage

### When to Use
- Real-time collaboration (chat, multiplayer games)
- Counters and rate limiters
- WebSocket connections with state
- Distributed locks
- Session management requiring strong consistency
- Stateful workflows

### Characteristics
- **Strong consistency**: Single-threaded execution per object
- **Transactional storage**: Atomic operations
- **In-memory state**: Fast access to frequently used data
- **Persistent storage**: Automatic persistence to disk
- **Global uniqueness**: Each object ID is globally unique

### Limitations
- More expensive than other storage options
- Limited to 128 KB per key
- Requires Durable Object class implementation
- Cold start latency for inactive objects

### Pricing (as of 2024)
- **Requests**: $0.15 per million requests
- **Duration**: $12.50 per million GB-seconds
- **Minimum**: 5ms duration per request

### Code Example
```javascript
export class Counter {
  constructor(state, env) {
    this.state = state;
    this.value = null;
  }

  async fetch(request) {
    // Lazy load from storage
    if (this.value === null) {
      this.value = (await this.state.storage.get('count')) || 0;
    }

    const url = new URL(request.url);
    
    if (url.pathname === '/increment') {
      this.value++;
      // Transactional write
      await this.state.storage.put('count', this.value);
      return Response.json({ count: this.value });
    }
    
    return Response.json({ count: this.value });
  }
}

// Usage in Worker
export default {
  async fetch(request, env) {
    const id = env.COUNTER.idFromName('user-123');
    const stub = env.COUNTER.get(id);
    return stub.fetch(request);
  }
};
```

## Decision Matrix

### Choose KV when:
- ✅ Data is read frequently, written infrequently
- ✅ Eventual consistency is acceptable
- ✅ Need global low-latency reads
- ✅ Caching or configuration data
- ❌ Need strong consistency
- ❌ Frequent writes to same keys

### Choose R2 when:
- ✅ Storing files or large objects
- ✅ Need S3 compatibility
- ✅ Want to avoid egress fees
- ✅ Backup and archival
- ❌ Need sub-10ms latency
- ❌ Storing small frequently-accessed data

### Choose D1 when:
- ✅ Need relational data with JOINs
- ✅ Complex queries required
- ✅ ACID transactions needed
- ✅ Structured data with relationships
- ❌ Extremely high write volumes
- ❌ Need full-text search

### Choose Durable Objects Storage when:
- ✅ Need strong consistency
- ✅ Real-time state management
- ✅ WebSocket connections
- ✅ Coordination between requests
- ❌ Simple key-value storage (use KV instead)
- ❌ Cost is primary concern

## Hybrid Patterns

### KV + R2
Use KV for metadata and R2 for actual files:
```javascript
// Store file in R2
await env.BUCKET.put(`files/${fileId}`, fileData);

// Store metadata in KV for fast lookup
await env.KV.put(`file:${fileId}`, JSON.stringify({
  name: 'document.pdf',
  size: fileData.length,
  uploadedAt: Date.now(),
  url: `https://files.example.com/${fileId}`
}));
```

### D1 + R2
Use D1 for structured data and R2 for file storage:
```javascript
// Store file in R2
await env.BUCKET.put(`avatars/${userId}.jpg`, imageData);

// Store reference in D1
await env.DB.prepare(
  'UPDATE users SET avatar_url = ? WHERE id = ?'
).bind(`https://cdn.example.com/avatars/${userId}.jpg`, userId).run();
```

### KV + Durable Objects
Use KV for caching and Durable Objects for coordination:
```javascript
// Check cache first
let data = await env.KV.get('expensive-computation', { type: 'json' });

if (!data) {
  // Use Durable Object to coordinate computation
  const id = env.COORDINATOR.idFromName('computation-lock');
  const stub = env.COORDINATOR.get(id);
  data = await stub.fetch('/compute').then(r => r.json());
  
  // Cache result
  await env.KV.put('expensive-computation', JSON.stringify(data), {
    expirationTtl: 3600
  });
}
```

## Migration Considerations

### From AWS S3 to R2
- Use S3-compatible API for easy migration
- Update endpoint URLs
- Test multipart uploads
- Verify metadata handling

### From Redis to KV
- Account for eventual consistency
- Implement retry logic for critical writes
- Consider Durable Objects for strong consistency needs
- Test TTL behavior differences

### From PostgreSQL to D1
- SQLite syntax differences (e.g., no `RETURNING` in some cases)
- Test migration scripts thoroughly
- Consider row read/write pricing
- Plan for database size limits
