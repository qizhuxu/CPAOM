# Cloudflare Development References

Navigation index for all reference materials.

## Core References

### [Workers API Reference](./workers-api.md)
Complete API documentation for Cloudflare Workers including:
- Request/Response objects
- Runtime APIs (crypto, encoding, streams)
- Web Standards APIs
- Cloudflare-specific APIs

### [Storage Comparison](./storage-comparison.md)
Detailed comparison of Cloudflare storage solutions:
- KV (Key-Value) - When to use, limitations, pricing
- R2 (Object Storage) - S3-compatible API, use cases
- D1 (SQL Database) - SQLite at the edge
- Durable Objects Storage - Transactional storage

### [Wrangler Commands](./wrangler-commands.md)
Comprehensive Wrangler CLI reference:
- Project management commands
- Deployment and publishing
- Development and testing
- Resource management (KV, R2, D1, Queues)
- Secret and environment variable management

### [Deployment Strategies](./deployment-strategies.md)
Production deployment patterns:
- Environment management (dev, staging, production)
- CI/CD integration (GitHub Actions, GitLab CI)
- Rollback strategies
- Blue-green deployments
- Canary releases

### [Performance Optimization](./performance-optimization.md)
Edge performance best practices:
- Caching strategies
- Request coalescing
- Streaming responses
- Worker-to-Worker communication
- Cold start optimization

### [Troubleshooting](./troubleshooting.md)
Common issues and solutions:
- Debugging techniques
- Error handling patterns
- Logging and monitoring
- CPU time limit errors
- Memory issues
- Network and fetch errors

## Additional Resources

### [Authentication Patterns](./authentication.md)
- JWT validation at the edge
- OAuth flows
- API key management
- Session management with KV

### [Routing Patterns](./routing.md)
- URL routing strategies
- Middleware patterns
- Request transformation
- Response modification

### [Testing Strategies](./testing.md)
- Unit testing Workers
- Integration testing
- Local development with Miniflare
- Mocking external services

### [Security Best Practices](./security.md)
- Input validation
- Rate limiting
- CORS configuration
- Secret management
- Content Security Policy

## External Links

- [Official Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [Workers Examples Repository](https://github.com/cloudflare/workers-sdk/tree/main/templates)
- [Cloudflare Community](https://community.cloudflare.com/)
- [Workers Discord](https://discord.gg/cloudflaredev)
