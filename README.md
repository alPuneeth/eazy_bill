**EazyBill** — Local Development Setup (README)

This document explains how to set up and run EazyBill locally on a new device from scratch.
Follow the steps in order. Do not skip steps.

--------------------------------------------------
STEP 1 — INSTALL SYSTEM PREREQUISITES
--------------------------------------------------

Install the following software:

- Python 3.10 or higher
- Git
- PostgreSQL 13 or higher

1.1 Install Python
Download from: https://www.python.org/downloads/

During installation:
- Enable “Add Python to PATH”
- Use default options

Verify:
python --version

1.2 Install Git
Download from: https://git-scm.com/downloads/

Verify:
git --version

1.3 Install PostgreSQL
Download from: https://www.postgresql.org/download/

During installation:
- Set password for postgres user
- Keep port 5432
- Install pgAdmin (recommended)

Verify:
psql --version

--------------------------------------------------
STEP 2 — CLONE THE REPOSITORY
--------------------------------------------------

git clone https://github.com/alPuneeth/eazy_bill.git

cd eazy_bill

--------------------------------------------------
STEP 3 — CREATE AND ACTIVATE VIRTUAL ENVIRONMENT
--------------------------------------------------

Windows:
python -m venv venv
venv\Scripts\activate

Linux / macOS:
python3 -m venv venv
source venv/bin/activate

--------------------------------------------------
STEP 4 — INSTALL PYTHON DEPENDENCIES
--------------------------------------------------

pip install --upgrade pip
pip install -r requirements.txt

--------------------------------------------------
STEP 5 — CREATE POSTGRESQL DATABASE
--------------------------------------------------

psql -U postgres

CREATE DATABASE eazybill;
\q

--------------------------------------------------
STEP 6 — CONFIGURE ENVIRONMENT VARIABLES
--------------------------------------------------

Create a .env file in the project root:

DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/eazybill

SECRET_KEY=dev-password-change-this-later

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30 or 60

ENV=development


Do NOT commit .env to Git.

--------------------------------------------------
STEP 7 — VERIFY ALEMBIC CONFIGURATION
--------------------------------------------------

Open alembic.ini and ensure:

sqlalchemy.url = %(DATABASE_URL)s

--------------------------------------------------
STEP 8 — RUN DATABASE MIGRATIONS
--------------------------------------------------

alembic upgrade head

Verify tables:

psql -U postgres -d eazybill

\dt

--------------------------------------------------
STEP 9 — START THE APPLICATION
--------------------------------------------------

uvicorn app.main:app --reload

Server runs at:
http://127.0.0.1:8000

--------------------------------------------------
STEP 10 — API DOCUMENTATION
--------------------------------------------------

Swagger UI:
http://127.0.0.1:8000/docs

ReDoc:
http://127.0.0.1:8000/redoc

--------------------------------------------------
STEP 11 — AUTHENTICATION FLOW
--------------------------------------------------

1. Create admin/test user
2. Login and obtain JWT token
3. Authorize via Swagger
4. Access protected endpoints

--------------------------------------------------
STEP 12 — CREATE LOOKUP / MASTER DATA
--------------------------------------------------

Create required lookup data:
- Status
- Village
- Customer Type
- Package
- Device / FTTH lookups

--------------------------------------------------
STEP 13 — ONBOARD CUSTOMER
--------------------------------------------------

Create customer with village, package, and device info.

--------------------------------------------------
STEP 14 — CREATE BILL
--------------------------------------------------

- Monthly rate is sourced from Package.price
- Bill amount is validated
- Bill date is stored

--------------------------------------------------
STEP 15 — UPDATE BILL (SAME-DAY RULE)
--------------------------------------------------

Bills can only be updated on the day they are created.

--------------------------------------------------
STEP 16 — VERIFY END-TO-END FLOW
--------------------------------------------------

Confirm:
- Customer listing works
- Bill details are correct
- Pricing matches package
- Validations are enforced

--------------------------------------------------
STEP 17 — STOP APPLICATION
--------------------------------------------------

CTRL + C
deactivate

--------------------------------------------------
STEP 18 — CLEAN RESET (OPTIONAL)
--------------------------------------------------

dropdb eazybill

createdb eazybill

alembic upgrade head
