# Secure Notes Vault API
# Kumar Sankaralingam

A small backend service for a take-home challenge that demonstrates REST API design, token-based authentication, access control, persistence, testing, and documentation.

## Overview

This service allows users to:
- Register and log in
- Create, read, update, and delete their own notes
- Share a note with another user as read-only
- Prevent unauthorized access to other users' notes

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy ORM
- SQLite
- JWT authentication
- pytest
- Uvicorn

## Project Structure

```text
secure-notes-vault/
├── app/
├── tests/
├── requirements.txt
├── README.md
├── DESIGN.md
├── Dockerfile
└── .github/workflows/ci.yml
```

## How to Run Locally

### Option 1: Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will start at:
- http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

### Option 2: Docker

```bash
docker build -t secure-notes-vault .
docker run --rm -p 8000:8000 secure-notes-vault
```

## How to Run Tests

```bash
pytest
```

## Example API Usage

### Register

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'
```

Copy the `access_token` from the response and export it:

```bash
export TOKEN="paste-token-here"
```

### Create a note

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"my first note"}'
```

### List notes

```bash
curl -X GET http://127.0.0.1:8000/notes \
  -H "Authorization: Bearer $TOKEN"
```

## Security Considerations

- Passwords are stored as hashes, not plaintext.
- Authentication uses signed JWT bearer tokens.
- Authorization enforces owner-only mutation of notes.
- Shared notes are read-only for recipients.
- The hard-coded secret key is acceptable for a take-home, but must be moved to environment variables in production.

## What is Covered

- Registration and login
- Token-based authentication
- CRUD for notes
- Sharing notes as read-only
- Access-control enforcement
- Automated API tests
- Docker support
- GitHub Actions CI

## Future Improvements

- Move configuration to environment variables
- Add Alembic for schema migrations
- Add pagination and note metadata
- Add rate limiting and audit logs
- Switch to PostgreSQL for production
- Add structured logging and observability

Tested locally with Python 3.14; some remaining deprecation warnings come from upstream framework dependencies and do not affect functional correctness.

