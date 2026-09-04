# EazyBill

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Tests](https://img.shields.io/badge/Tests-42-success)
![Coverage](https://img.shields.io/badge/Coverage-74%25-yellow)

A containerized REST API backend for a cable operator's billing and customer management system. Built to model realistic operational constraints — billing consistency, concurrency safety, role-based access, and automated deployment.

Repository: https://github.com/alPuneeth/eazy_bill

---

## Tech Stack

| Layer          | Technology                        |
| -------------- | --------------------------------- |
| Framework      | FastAPI                           |
| ORM            | SQLModel + SQLAlchemy             |
| Database       | PostgreSQL                        |
| Migrations     | Alembic                           |
| Auth           | JWT (`python-jose`) + RBAC        |
| Language       | Python 3.13                       |
| Containerization | Docker (multi-stage builds)     |
| CI/CD          | GitHub Actions                    |
| Deployment     | Railway                           |
| Testing        | Pytest                            |

---

## Key Backend Concepts

- Transaction management (`session.begin()` — no partial writes)
- Row-level locking (`SELECT FOR UPDATE` — race-safe billing)
- Device state derived from billing validity (`ACTIVE ⇔ valid bill exists`)
- Service-layer architecture (thin routers, testable business logic)
- RBAC enforced at dependency and service layers
- Multi-stage Docker builds (build tools and test code excluded from production image)
- Containerized CI pipeline (identical environment across local, CI, and production)
- Automated containerized deployment via Railway

---

## Architecture

```text
app/
├── api/          # HTTP route layer
├── auth/         # JWT creation and validation
├── core/         # Config, security, exception handling
├── db/           # Session management
├── dependencies/ # Auth + RBAC (FastAPI Depends)
├── models/       # SQLModel ORM models
├── schemas/      # Request/response validation (Pydantic)
├── services/     # Business logic layer
└── main.py       # Entry point
```

**Request flow:** Router → Dependency (Auth + RBAC) → Service → Database

---

## Features

- Customer onboarding (single and bulk)
- Billing with race-safe overlap prevention and same-day update restriction
- Device lifecycle driven by billing validity
- Package-based pricing model
- Agent-scoped access with village-level data isolation
- Role-based access control (Admin / Agent)
- Billing summaries, collection reports, and customer status reports
- UUID-based public identifiers (enumeration protection)

---

## CI/CD Pipeline

```text
git push → GitHub Actions → Run Tests (Docker) → Deploy to Railway
```

- Tests run inside Docker — identical environment to production
- Deployment is blocked if any test fails
- Deployment only triggers on push to `main`, not pull requests
- `RAILWAY_TOKEN`, `RAILWAY_SERVICE_ID`, and `RAILWAY_PROJECT_ID` stored as GitHub Secrets

---

## Docker

Three-stage Dockerfile:

| Stage   | Purpose                                            |
| ------- | -------------------------------------------------- |
| builder | Compiles psycopg C extension, installs all deps    |
| final   | Lean production image — no build tools or test code|
| test    | Extends final — adds pytest and test dependencies  |

---

## Testing

- **42 endpoint-level integration tests** against an isolated PostgreSQL test database
- **74% code coverage**
- Rollback-based test isolation via pytest fixtures
- Reusable factories for customers, bills, users, and villages

```bash
# Run tests
docker compose run --rm test

# Coverage report
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Authentication & Authorization

- JWT-based authentication with secure password hashing
- Two roles: **Admin** (full access) and **Agent** (village/customer scope)
- RBAC enforced at FastAPI dependency layer and service layer
- Single-admin constraint enforced at application level

---

## Design Decisions

| Decision                  | Reason                                       |
| ------------------------- | -------------------------------------------- |
| UUIDs over sequential IDs | Prevent enumeration attacks on public APIs   |
| Service layer             | Testability and separation of concerns       |
| Multi-stage Docker builds | Lean, secure production images               |
| Manual Alembic review     | Prevent unintended schema changes            |
| Synchronous endpoints     | Simpler operational model for current scale  |
| PostgreSQL only           | Workload is moderate and relational          |
| Long-lived JWTs           | Acceptable in a controlled single-operator environment |

---

## Local Setup

### With Docker

```bash
git clone https://github.com/alPuneeth/eazy_bill.git
cd eazy_bill
cp .env.example .env                 # fill in your values
cp .env.docker.example .env.docker   # fill in your values
docker compose up app                 # starts db, runs migrations, starts server
```

API available at `http://localhost:8000` — docs at `/docs`.

### Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment — create .env with:
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/eazy_bill
TEST_DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/test_db
SECRET_KEY=your-secret-key

# Run migrations and start server
alembic upgrade head
uvicorn app.main:app --reload
```

---

## Notes

- `.env` and `.env.docker` hold local secrets and are excluded via `.gitignore`; `venv/` is also excluded
- `.env.example` and `.env.docker.example` are committed templates — copy and fill in your own values
- All schema changes go through Alembic
