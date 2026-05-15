# Design Notes

## Architecture

This service is intentionally small and modular:
- `main.py` contains API routes.
- `models.py` defines database models.
- `schemas.py` defines request/response contracts.
- `auth.py` handles password hashing and JWT creation/validation.
- `crud.py` contains database access logic.
- `deps.py` provides FastAPI dependencies such as database sessions and current-user resolution.

## Database Choice

SQLite was selected because it keeps local setup simple and satisfies the requirement for embedded or relational persistence. For a take-home challenge, this reduces friction for reviewers.

## Authentication and Authorization

JWT bearer tokens are used for authentication. Authorization is enforced at the route level:
- Owners can create, read, update, delete, and share their own notes.
- Shared users can read a shared note.
- Shared users cannot update or delete a shared note.

## Error Handling

The API returns clear HTTP status codes and error messages for:
- Invalid credentials
- Duplicate usernames
- Missing resources
- Unauthorized or forbidden access
- Duplicate sharing attempts

## Testing Strategy

Tests focus on API-level flows and access control:
- Register and login
- Invalid login
- Owner CRUD flow
- One user blocked from reading another user's note
- Shared notes are read-only

## Production Deployment

For production, I would:
- Run behind a reverse proxy or managed ingress
- Use PostgreSQL instead of SQLite
- Store secrets in environment variables or a secret manager
- Add migrations with Alembic
- Use structured logs and metrics
- Add request rate limiting and stronger operational hardening

## Monitoring and Alerting

I would monitor:
- API error rate and latency
- Authentication failures
- Database health
- Container health and restart rate
- Resource usage such as CPU and memory

Alerts would focus on sustained 5xx spikes, latency degradation, auth abuse patterns, and service availability.

## Database Migrations

I would introduce Alembic and keep migrations versioned in the repository. Schema changes would be forward-only, reviewed, and applied through deployment automation.

## Scaling to 10,000 Concurrent Users

To scale further, I would:
- Move from SQLite to PostgreSQL
- Run multiple stateless API instances behind a load balancer
- Tune DB indexes and connection pooling
- Introduce caching for hot reads if needed
- Add pagination and response-size limits
- Separate write-heavy and read-heavy concerns if traffic patterns justify it
