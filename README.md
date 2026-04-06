# EazyBill

A production-grade REST API backend for a cable operator's billing and customer management system. Handles customer onboarding, billing, agent operations, collections, and reporting. Designed and implemented end-to-end using FastAPI, SQLModel, and PostgreSQL.

---

## Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLModel + SQLAlchemy
- **Database:** PostgreSQL
- **Migrations:** Alembic
- **Auth:** JWT (python-jose) + RBAC
- **Language:** Python 3.10+

---

## Architecture
```
app/
├── api/          # Route layer (entry points)
├── auth/         # JWT token handling
├── core/         # Config, exceptions, security
├── db/           # Session management and DB initialization
├── dependencies/ # Auth and RBAC enforcement (FastAPI Depends)
├── models/       # SQLModel ORM models
├── schemas/      # Request/response validation (Pydantic)
├── services/     # Business logic layer(customer, billing, reports, devices)
└── main.py       # Application entry point
```

### Request Lifecycle
```
Request → Router → Service → Database
               ↑
          Auth + RBAC (Depends)
```

- Routers handle request/response
- Services encapsulate business logic
- Dependencies enforce authentication and authorization
- Models and Schemas separate persistence from validation

---

## Features

- Customer onboarding (single and bulk)
- Bill generation with validation rules
- Same-day bill edit restriction
- Package-based pricing model
- Agent-based access restriction
- Role-based access control (admin / agent)
- Village-level data isolation
- Reports:
     - Billing summaries
     - Collection reports
     - Customer status insights
- UUID-based external identifiers (secure public APIs)

---

## Local Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Git

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/alPuneeth/eazy_bill.git
cd eazy_bill

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Database Setup 
# Open PostgreSQL
psql -U postgres

# Create Database
CREATE DATABASE eazybill;
\q

# 5.  Environment Configuration
# Create a .env file in the project root:
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/eazybill
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENV=development

# 6. Run migrations
alembic upgrade head

# 7. Start the server
uvicorn app.main:app --reload
```

### API Documentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Authentication & Authorization

- JWT-based authentication
- Role-based access control
    - Admin -> full access
    - Agent -> restricted to assigned data
- RBAC enforced via FastAPI dependencies and service-layer checks
- Single-admin constraint enforced at the application level

---

## Design Decisions

- UUIDs over incremental IDs → prevents enumeration attacks
- Service layer abstraction → keeps routers thin and logic testable
- Manual Alembic review → avoids unintended schema changes
- Long-lived JWT tokens → acceptable due to controlled deployment environment

---

## Notes

- `.env`, `venv/` are excluded via `.gitignore`
- PostgreSQL must be running before applying migrations
- All schema changes must go through Alembic