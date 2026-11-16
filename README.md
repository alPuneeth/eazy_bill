# EazyBill

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Tests](https://img.shields.io/badge/Tests-46-success)
![Coverage](https://img.shields.io/badge/Coverage-76%25-yellow)

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

## API Endpoints

Interactive documentation is served at `/docs`.

**Conventions**

- Resource paths are plural nouns in kebab-case (`/customers`, `/customer-types`); actions are expressed by the HTTP method, not the path
- `201 Created` for resource creation, `204 No Content` for deletion, `200 OK` otherwise
- `404` not found, `409` conflict, `422` validation error, `403` forbidden

| Method | Path | Description | Success |
|--------|------|-------------|---------|
| GET | `/` | Service root | 200 |
| GET | `/db_check` | Database health check | 200 |
| POST | `/auth/` | Log in and receive a JWT | 200 |
| GET | `/users/` | List users | 200 |
| POST | `/users/` | Create a user | 201 |
| GET | `/users/me` | Get the authenticated user | 200 |
| GET | `/users/{user_public_id}` | Get a user | 200 |
| PATCH | `/users/{user_public_id}` | Update a user | 200 |
| POST | `/agents/{agent_public_id}/villages` | Assign villages to an agent | 200 |
| PUT | `/agents/{agent_public_id}/villages` | Replace an agent's villages | 200 |
| GET | `/customers/` | List active and inactive customers | 200 |
| POST | `/customers/` | Create a customer | 201 |
| POST | `/customers/bulk` | Create customers in bulk | 200 |
| GET | `/customers/all` | List all customers | 200 |
| GET | `/customers/archived` | List archived customers | 200 |
| GET | `/customers/{customer_public_id}` | Get a customer | 200 |
| PATCH | `/customers/{customer_public_id}` | Update a customer | 200 |
| DELETE | `/customers/{customer_public_id}` | Soft-delete (archive) a customer | 204 |
| GET | `/devices/` | List devices | 200 |
| GET | `/devices/{device_info_public_id}` | Get a device | 200 |
| PATCH | `/devices/{device_info_public_id}` | Update a device | 200 |
| GET | `/bills/` | List bills | 200 |
| POST | `/bills/` | Create a bill | 201 |
| GET | `/bills/{bill_public_id}` | Get a bill | 200 |
| PATCH | `/bills/{bill_public_id}` | Update a bill | 200 |
| GET | `/bills/customers/{customer_public_id}` | List a customer's bills (paginated) | 200 |
| GET | `/bills/villages/{village_code}/next-bill-code` | Get the next bill code for a village | 200 |
| GET | `/villages/` | List villages | 200 |
| POST | `/villages/` | Create a village | 201 |
| GET | `/villages/{village_id}` | Get a village | 200 |
| PATCH | `/villages/{village_id}` | Update a village | 200 |
| GET | `/packages/` | List packages | 200 |
| POST | `/packages/` | Create a package | 201 |
| GET | `/packages/{package_id}` | Get a package | 200 |
| PATCH | `/packages/{package_id}` | Update a package | 200 |
| GET | `/statuses/` | List statuses | 200 |
| POST | `/statuses/` | Create a status | 201 |
| GET | `/statuses/{status_id}` | Get a status | 200 |
| PATCH | `/statuses/{status_id}` | Update a status | 200 |
| GET | `/customer-types/` | List customer types | 200 |
| POST | `/customer-types/` | Create a customer type | 201 |
| GET | `/customer-types/{customer_type_public_id}` | Get a customer type | 200 |
| PATCH | `/customer-types/{customer_type_public_id}` | Update a customer type | 200 |
| GET | `/tv-types/` | List TV types | 200 |
| POST | `/tv-types/` | Create a TV type | 201 |
| GET | `/tv-types/{tv_type_id}` | Get a TV type | 200 |
| PATCH | `/tv-types/{tv_type_id}` | Update a TV type | 200 |
| GET | `/ftth64/` | List FTTH64 entries | 200 |
| POST | `/ftth64/` | Create an FTTH64 entry | 201 |
| GET | `/ftth64/{ftth64_id}` | Get an FTTH64 entry | 200 |
| PATCH | `/ftth64/{ftth64_id}` | Update an FTTH64 entry | 200 |
| GET | `/reports/bills-by-agent/{agent_public_id}` | Bills collected by an agent | 200 |
| POST | `/reports/bills-with-optional-filters` | Bills filtered by optional criteria | 200 |
| GET | `/reports/collections-summary` | Collections summary | 200 |
| GET | `/reports/customer-status-summary-by-village` | Customer status summary per village | 200 |

**Known deviations**

- `GET /bills/customers/{customer_public_id}` lists a customer's bills under the bills resource; a nested `/customers/{id}/bills` would be more conventional
- `GET /bills/villages/{village_code}/next-bill-code` lives in the bills router for the same reason
- `POST /customers/bulk` returns `200` with `success` and `failed` lists, because a request can partly succeed
- Reference-data resources (`/villages`, `/packages`, `/statuses`, `/tv-types`, `/ftth64`) are addressed by integer id; they are admin-managed lookup data, whereas customers, bills, users and devices use UUID public ids
- `GET /db_check` keeps its underscore because the Docker `HEALTHCHECK` depends on it

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

- **46 endpoint-level integration tests** against an isolated PostgreSQL test database
- **76% code coverage**
- Rollback-based test isolation via pytest fixtures
- Reusable factories for customers, bills, users, and villages

```bash
# Run tests
docker compose run --rm --build test

# Coverage report
docker compose run --rm --build test pytest tests/ --cov=app --cov-report=term-missing
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
