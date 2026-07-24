# Backend — Guest House Website

## Tech Stack

- Language: Python 3.14
- Framework: Flask 3.0
- ORM/DB: SQLAlchemy 2.0 + Flask-SQLAlchemy, PostgreSQL (via `psycopg`/`psycopg2-binary`)
- Migrations: Flask-Migrate (Alembic)
- Auth: PyJWT + bcrypt (admin panel JWT auth)
- Mail: Flask-Mail (SMTP, default Gmail)
- Rate limiting: Flask-Limiter
- CORS: Flask-CORS
- WSGI server: Gunicorn (production)
- Env management: python-dotenv
- Dependency tooling: both `Pipfile`/`Pipfile.lock` and `requirements.txt` are present in this repo

## Structure

```
app/
  models/     — SQLAlchemy models
  routes/     — Flask blueprints / route handlers
  services/   — business logic, kept out of route handlers
  utils/      — shared helpers
```

Keep route handlers thin — request parsing, calling into `services/`, returning a response. Business logic (booking rules, availability checks, email templating, etc.) belongs in `services/`, not inline in a route.

## Rules

- Do not add features, endpoints, or fields not requested. If a change implies a new field, ask before adding it to a model.
- Match existing patterns in the codebase (naming, blueprint registration style, error response shape) rather than introducing a new convention for one feature.
- Every model change goes through a Flask-Migrate migration — never hand-edit the DB schema or skip generating a migration.
- Any endpoint that mutates data (POST/PUT/PATCH/DELETE) needs to consider: auth (is this admin-only via JWT?), rate limiting, and input validation.
- Secrets and config (DB URL, JWT secret, SMTP creds) come from environment variables via python-dotenv — never hardcode credentials, even for local testing.
- CORS config should stay scoped to the actual frontend origin(s), not left wide open, unless explicitly testing.

## Dependency Management

Both `Pipfile` and `requirements.txt` exist in this repo — pick one source of truth going forward (recommend `Pipfile`/pipenv since it locks versions) and keep the other in sync or regenerate it from the primary, rather than editing both independently. Flag this to the user rather than silently deciding.

## Testing & Workflow

Follow this loop for non-trivial changes:

1. Write/edit the code.
2. If a `code-reviewer` or `qa` subagent pattern is in use, run it against the changed file(s) before merging.
3. Run any existing test suite; add tests for new routes/services where none exist.
4. Run a migration check (`flask db migrate` / `flask db upgrade` against a dev DB) if models changed.
5. Ship only after checks pass.

## Technical Defaults

- New endpoints follow REST conventions consistent with existing routes (check `app/routes/` for the current pattern before adding).
- Passwords: bcrypt only, never store plaintext or use a weaker hash.
- JWTs: short-lived where reasonable, verified via PyJWT on every protected route — don't roll a custom auth check.
- Production runs via Gunicorn, not the Flask dev server — don't add dev-only code paths that would break under Gunicorn.
