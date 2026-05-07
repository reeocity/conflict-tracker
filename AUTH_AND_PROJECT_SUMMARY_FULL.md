# Conflict Tracker — Full Implementation Summary

This document is a deep, presentation-ready explanation of everything implemented for backend authentication, subscription persistence, and frontend integration in the "conflict-tracker" project. It's structured so you can use it as slides or speaker notes.

---

## 1) Executive summary

- Goal: convert a frontend-only mock auth flow into a secure backend authentication system, persist user alert subscriptions, and integrate the frontend to use real authenticated API calls.
- Result: A FastAPI backend implementing secure user registration and login (bcrypt-hashed passwords + JWT access tokens), database schema additions for `users` and `user_alert_subscriptions`, endpoints to manage subscriptions, and frontend changes to register/login and to send Bearer tokens with API requests.

This file explains design decisions, implementation details, how components interact, testing, security considerations, and next steps.

---

## 2) High-level architecture

- Frontend: `tutorial_Selenium/index.html` (static single-page UI) — now performs register/login to backend, stores token + user info in `localStorage`, and sends `Authorization: Bearer <token>` on API requests.
- Backend: FastAPI app (served with `uvicorn`) — exposes:
  - Public endpoints: news/events retrieval
  - Auth endpoints: register, login, whoami (`/auth/me`)
  - Subscription endpoints: create/list/delete subscriptions (protected by Bearer JWT auth)
- Database: PostgreSQL (Neon) storing events, users, and user subscriptions. All DB access done via helper functions in `db.py` and `auth.py`.
- Scraper: existing script persists news/events into `events` table. Alerts are matched against user subscriptions.

Diagram (text):

Frontend <--> FastAPI (auth + api routes) <--> PostgreSQL (events, users, subscriptions)

---

## 3) Goals & requirements (as implemented)

- Provide secure account creation and authentication.
- Never store plaintext passwords; use strong hashing.
- Issue compact session tokens that can be validated by the server (JWT).
- Provide endpoints for storing user alert preferences (country/category) and retrieving them.
- Replace frontend's localStorage-only gating with server-validated auth flows.
- Keep secrets out of repo via `.env`.

---

## 4) Tech stack & packages

- Python 3.x
- FastAPI for HTTP API
- uvicorn for ASGI server
- psycopg2 for PostgreSQL access
- python-dotenv for `.env` loading
- bcrypt for password hashing
- PyJWT for JSON Web Tokens

Important files changed/added:
- `tutorial_Selenium/main.py` — FastAPI app and router registration
- `tutorial_Selenium/db.py` — DB helpers and `setup_auth_db()`
- `tutorial_Selenium/auth.py` — hashing, token creation/verification and subscription helpers
- `tutorial_Selenium/routes/auth.py` — HTTP endpoints for register/login/me/subscriptions
- `tutorial_Selenium/index.html` — frontend integration for register/login & subscription posting
- `.env.example` — JWT secret placeholder
- `requirements.txt` — added `bcrypt`, `PyJWT` (and updates reflected)

---

## 5) Database schema & rationale

### Existing: `events`
- Stores scraped news items. Scraper uses `ON CONFLICT` upsert to avoid duplicates.

### Added: `users` table
- Columns:
  - `id` (primary key)
  - `email` (unique, indexed)
  - `password_hash` (bcrypt hash)
  - `created_at`
- Rationale: email as login key and unique constraint ensures idempotent registration checks.

### Added: `user_alert_subscriptions` table
- Columns:
  - `id` (pk)
  - `user_id` (foreign key -> `users.id`)
  - `country` (nullable/text)
  - `category` (nullable/text)
  - `created_at`
- Rationale: keeps multiple alert preferences per user; used by alert-dispatch worker (future work).

Notes about DDL in `setup_auth_db(conn)`:
- Creates tables with `IF NOT EXISTS` guards so server startup is idempotent.
- Adds indices for common lookups (`email` on `users` and `user_id` on subscriptions).

---

## 6) Password security (bcrypt)

Why bcrypt:
- Adaptive hashing algorithm that is computationally expensive and tunable via a cost factor (work factor).
- Resists brute-force/GPU cracking better than plain hashes.

Implementation details:
- On register: call `hash_password(plain_password)` -> `bcrypt.hashpw(..., bcrypt.gensalt())`.
- Store the resulting bytes (or decoded string) into `users.password_hash`.
- On login: call `verify_password(plain, stored_hash)` -> `bcrypt.checkpw(... )`.

Notes and recommendations:
- Keep the `bcrypt` work factor moderate for your deployment VM; raise it for higher security if CPU budget allows.
- No salts stored separately — bcrypt embeds salt into the hash.

---

## 7) Session management: JWT access tokens

Design choices:
- Use short-to-medium lived JWT access tokens for stateless session validation.
- Token payload includes `sub` (user id) and `exp` (expiry timestamp).
- Signed using server secret `JWT_SECRET_KEY` from `.env`.

Why JWT:
- Fast stateless validation on each request without DB lookup (unless you need revocation support).
- Compact and portable (used easily in Authorization header).

Implementation details:
- `create_access_token(user_id)` builds a payload with `sub` and `exp` and signs with `HS256`.
- Token lifetime: set (in the implementation) to 7 days; adjust per security needs.
- `verify_token(token)` decodes and validates `exp` and signature; returns user id.
- `get_current_user()` (route helper) parses `Authorization: Bearer <token>`, verifies token, then fetches the user row by id from DB. This approach provides final check that user still exists.

Token revocation & refresh notes (not implemented but recommended):
- Stateless JWTs are fast but cannot be trivially revoked. To support logout or revocation, consider:
  - Shorter access tokens + server-side refresh tokens (stored in DB or Redis) and a refresh endpoint.
  - Keep a revocation list (blacklist) in DB/Redis checked on each token (costly).

---

## 8) HTTP API endpoints (what was added)

All endpoints are under `/auth` for auth-related routes.

1) POST `/auth/register`
- Purpose: create an account.
- Input: JSON { "email": "...", "password": "..." }
- Server-side checks:
  - Validate email format (basic check) and password length/strength.
  - Ensure the email does not already exist (unique constraint will also protect against races).
  - Hash password with bcrypt and insert new `users` row.
- Output: `{ "access_token": "<jwt>", "user": { id, email, created_at } }` on success.

2) POST `/auth/login`
- Purpose: authenticate existing user.
- Input: JSON { "email": "...", "password": "..." }
- Server-side steps:
  - Fetch user by email, verify password with bcrypt.
  - If valid, create JWT and return as in register.
- Failure: 401 Unauthorized with a concise message.

3) GET `/auth/me` (protected)
- Purpose: return current authenticated user info.
- Header: `Authorization: Bearer <token>`
- Steps: verify token -> fetch user -> return user fields.

4) POST `/auth/subscriptions` (protected)
- Purpose: create a user alert subscription (e.g., country/category preference)
- Input: JSON { "country": "...", "category": "..." }
- Steps: insert row in `user_alert_subscriptions` referencing `user_id`.
- Output: created subscription record.

5) GET `/auth/subscriptions` (protected)
- Purpose: list user's subscriptions
- Returns: array of subscription records for authenticated user.

6) DELETE `/auth/subscriptions/{id}` (protected)
- Purpose: remove a subscription (ensures it belongs to authenticated user first).

Implementation notes:
- `get_current_user()` is a thin middleware helper used by protected endpoints.
- Each protected route verifies token then does minimal DB reads/writes.

---

## 9) Frontend integration (what changed in `index.html`)

Key changes:
- Replaced localStorage-only gating with calls to backend `/auth/register` and `/auth/login`.
- On successful register/login, the frontend stores an object in `localStorage` under the key `conflict-tracker-auth`.
  - Stored object: `{ token: '<jwt>', user: { id, email, created_at } }`.
- `getAuthHeaders()` helper returns `Authorization: Bearer <token>` for fetch requests.
- Subscription form now `POST`s to `/auth/subscriptions` using `getAuthHeaders()`.
- UI behavior: when user is signed out, alerts are hidden; after sign-in, alerts are shown and persisted via backend.

Example JS flow (conceptual):

- User submits login form -> call `/auth/login` -> on success save `token` to localStorage -> update UI.
- When making API calls (e.g., GET `/api/news`), include the `Authorization` header so backend can apply user-specific logic later.

Security note on storing token in localStorage:
- Storing tokens in localStorage is simple and commonly used, but it is vulnerable to XSS. Mitigations:
  - Harden frontend to avoid XSS vectors (Content Security Policy, sanitize outputs).
  - Consider storing tokens in an HttpOnly secure cookie for production to reduce XSS risk.

---

## 10) Where secrets live

- `.env` file is used locally and loaded with `python-dotenv`.
- Required secret: `JWT_SECRET_KEY` (used to sign tokens).
- `DATABASE_URL` remains in `.env` (already migrated earlier) and not committed.
- `.env.example` contains placeholders so others can replicate the setup.

---

## 11) Implementation details & key code paths

A. Server start & DB setup
- `main.py` registers the `auth` router and installs startup hook calling `setup_db(conn)` and `setup_auth_db(conn)`.
- `setup_auth_db(conn)` executes DDL to create `users` and `user_alert_subscriptions` with indexes.

B. Register flow (server-side)
- Endpoint receives payload -> validate -> call `create_user(email, password)` in `auth.py` -> `hash_password()` -> DB insert -> `create_access_token(user_id)` -> return token + user JSON.

C. Login flow (server-side)
- Endpoint receives payload -> lookup user by email -> `verify_password()` -> `create_access_token()` -> return.

D. Token validation
- `verify_token()` tries to decode token using `JWT_SECRET_KEY` and `HS256`. If decode fails (invalid signature or expired), return 401.
- Successful decode: extract `sub` -> use `get_user_by_id()` to fetch DB record and attach to request.

E. Subscription storage
- `save_user_subscription(user_id, country, category)` inserts a record into `user_alert_subscriptions`.
- `get_user_subscriptions(user_id)` returns list for the user.
- `delete_user_subscription(user_id, sub_id)` removes only when the subscription belongs to the user.

---

## 12) Testing, validation & run instructions

Run server locally (example):

```bash
# create .env based on .env.example and set JWT_SECRET_KEY and DATABASE_URL
pip install -r requirements.txt
uvicorn tutorial_Selenium.main:app --reload --host 0.0.0.0 --port 8000
```

Test register/login with `curl` or PowerShell (examples):

```bash
# Register
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"email":"you@example.com","password":"Secret123!"}'

# Login
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"you@example.com","password":"Secret123!"}'

# Get profile (replace <token>)
curl -H "Authorization: Bearer <token>" http://localhost:8000/auth/me
```

Unit & integration tests:
- The project includes pytest-based tests (unit & integration). Some integration tests had failures during initial runs (12/15 passing).
- To run tests locally (example):

```bash
pytest tests/
```

If tests break due to environment (e.g., DB not present), ensure `.env` provides a working `DATABASE_URL` pointing to a test DB.

---

## 13) Security review & recommendations

What we did well:
- Password hashing with `bcrypt` (no plaintext storage).
- Tokens signed with secret loaded from `.env`, not hard-coded.
- Database schema created idempotently at startup.

Further improvements for production:
- Use HTTPS everywhere (TLS termination on server/proxy).
- Use short-lived access tokens and implement refresh tokens.
- Store refresh tokens server-side (DB or Redis) to allow revocation.
- Consider storing tokens in HttpOnly secure cookies to reduce XSS exposure.
- Add rate-limiting on auth endpoints to mitigate brute-force.
- Add email verification flows (confirm email before allowing subscriptions).
- Add unit tests targeting auth edge-cases (duplicate register, invalid token, expired token).

---

## 14) How this integrates with alerts & next features

The subscription model persists user preferences; the next major steps are:
- Implement an alert dispatcher that runs periodically (cron/worker) and:
  - Joins `events` with `user_alert_subscriptions` to find matches
  - Sends email notifications or push notifications to matching users
- Recommended stack for alerts:
  - Use a scheduler (APScheduler) or a queue worker (Celery/RQ) to perform dispatch.
  - Use a transactional email provider (SendGrid, SES) with templated messages.
- Add per-user unsubscribe links and audit logging for email deliveries.

---

## 15) Troubleshooting & common errors

- Token invalid/expired: Ensure `JWT_SECRET_KEY` matches the one used to sign tokens. Check `exp` claim and server clock.
- DB connection failures: Verify `DATABASE_URL` in `.env` and network access to Neon DB.
- Duplicate email on register: Unique constraint in `users.email` — catch the DB error and return a friendly message.
- XSS leaking tokens: Audit any dynamic HTML produced by the frontend and sanitize content. Prefer HttpOnly cookies in production.

---

## 16) Suggested presentation outline (slide-by-slide)

1) Title: Conflict Tracker — backend auth & subscriptions
2) Motivation: Why backend auth & persistent subscriptions
3) Architecture diagram (one-line diagram shown here)
4) Data model: `users`, `user_alert_subscriptions`, `events`
5) Auth design: bcrypt + JWT (explain why)
6) API routes: register/login/me + subscriptions
7) Frontend integration: token flow & localStorage
8) Security mitigations & next steps (refresh tokens, HTTPS, rate limiting)
9) Demo steps (how to register/login and add a subscription)
10) Roadmap: email delivery, background dispatch, tests
11) Q&A and appendix with run commands & test commands

Speaker notes: use the earlier detailed sections as per-slide notes.

---

## 17) Appendix — quick reference code snippets

Create token (conceptual):

```python
import jwt, time
payload = {"sub": user_id, "exp": int(time.time()) + 60*60*24*7}
token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
```

Verify token (conceptual):

```python
payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
user_id = payload.get("sub")
```

Hash password with bcrypt (conceptual):

```python
import bcrypt
hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
# Verify with bcrypt.checkpw(plaintext.encode('utf-8'), stored_hash)
```

---

## 18) Where to find the code (paths)

- App entry & router: `tutorial_Selenium/main.py`
- DB helpers: `tutorial_Selenium/db.py`
- Auth helpers: `tutorial_Selenium/auth.py`
- Auth routes: `tutorial_Selenium/routes/auth.py`
- Frontend single page: `tutorial_Selenium/index.html`
- Summary (short): `AUTH_AND_PROJECT_SUMMARY.md`
- This detailed summary: `AUTH_AND_PROJECT_SUMMARY_FULL.md`

---

## 19) Final notes & next suggested actions

- If you'd like, I can implement an email-alert dispatch worker next (two common approaches: scheduled job vs. queue-based worker). Tell me which you prefer and I will scaffold the worker and email integration.
- I can also add refresh-token support for safer long-term sessions and add tests for the auth endpoints.

---

If you want the file shortened into a slide deck or to convert sections into separate Markdown files (slides + speaker notes), tell me the desired output and I will generate it next.