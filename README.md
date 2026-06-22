# Mechanic Shop API — Deployment & CI/CD

The production-ready version of the Mechanic Shop REST API, deployed to Render with a hosted PostgreSQL database and an automated CI/CD pipeline.

## Live Service

- API: `https://<service-name>.onrender.com`
- Documentation: `https://<service-name>.onrender.com/apidocs/`

## Features

Builds on the documented and tested version and adds:

- **Hosted PostgreSQL database** on Render (psycopg2)
- **Environment-based configuration** (`config.py` with Development, Testing, and Production classes); sensitive values (database URI and secret key) read from environment variables, kept out of version control via `.gitignore`
- **Production server** (gunicorn) with `flask_app.py` as the entry point using the production config; the development server call removed
- **CI/CD pipeline** (GitHub Actions): on every push to `main`, a build job installs dependencies, a test job runs the full unit-test suite, and a deploy job triggers a Render deployment — the deploy job runs only if the tests pass

## Tech Stack

- Flask, Flask-SQLAlchemy, gunicorn, psycopg2
- python-dotenv (local environment variables)
- Render (PostgreSQL database + web service hosting)
- GitHub Actions (CI/CD)

## Configuration

Local development uses a `.env` file (excluded from Git) containing:

```
SQLALCHEMY_DATABASE_URI=postgresql://<user>:<password>@<host>/<database>
SECRET_KEY=<random-secret-string>
```

In production, these same variables are supplied through the Render dashboard.

## Local Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Deployment (Render)

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn flask_app:app`
- Environment variables: `SQLALCHEMY_DATABASE_URI` (internal database URL), `SECRET_KEY`

## CI/CD Pipeline

Defined in `.github/workflows/main.yaml`:

```
build  →  test  →  deploy
```

The deploy job depends on the test job (`needs: test`) and calls the Render deploy API using two repository secrets: `SERVICE_ID` and `RENDER_API_KEY`.

## Testing

```bash
python -m unittest discover tests
```
