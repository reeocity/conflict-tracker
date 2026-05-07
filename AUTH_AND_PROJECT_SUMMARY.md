# Conflict Tracker — What I Did (Simple Explanation)

This file explains, in plain language, what was changed and why. It covers the frontend, backend, database, data pipeline, tests, and the new authentication system. No code is included — just clear descriptions you can read or copy.

---

## High-level summary

- I connected the frontend dashboard to a real backend API instead of static sample data.
- I connected the project to a PostgreSQL database (Neon) so events persist between runs.
- I built a secure backend authentication system so users can register, log in, and save alert preferences.
- I updated the frontend to use the backend login and to store a JWT token instead of only using the browser's localStorage mock.
- I added database tables for users and their alert subscriptions and made sure the scraper keeps events up-to-date in the database.
- I added tests and documentation and kept secrets (database credentials) out of the code by using a `.env` file.

---

## Files and what I changed (simple, part-by-part)

- `tutorial_Selenium/index.html`
  - This is the frontend dashboard users see in the browser.
  - What I changed: Rewrote the auth flow so it talks to the backend. Instead of pretending someone is "signed in" only in the browser, the UI now calls the real `/auth/register` and `/auth/login` API endpoints. It stores a server-issued token (JWT) and includes it in API requests.
  - Effect: The UI now shows/hides the alert preferences panel based on whether the server considers the user logged in. Clicking "Get notified like this" prompts the real sign-up when needed.

- `tutorial_Selenium/main.py` (FastAPI backend)
  - This file runs the API server. It provides endpoints to return events, statistics, and now authentication routes.
  - What I changed: I registered the new auth routes with the app and added a startup step that creates or updates the database tables (events, users, subscriptions) automatically when the server starts.
  - Effect: The backend can now handle user registration, login, and subscription management in addition to serving events.

- `tutorial_Selenium/db.py`
  - This is the shared database helper used by the scraper and the API.
  - What I changed: Added database setup for the new authentication-related tables (`users` and `user_alert_subscriptions`). I kept the scraper's event persistence and query helpers.
  - Effect: The database now holds events plus user accounts and user alert preferences.

- `tutorial_Selenium/sql.py` (RSS scraper)
  - This module fetches the Al Jazeera RSS feed, extracts articles, detects country and category, and saves results.
  - What I changed: The scraper already upserts (insert or update) events into the `events` table. No functional change was needed to connect it to auth, but I ensured the database schema is consistent with what the scraper expects.
  - Effect: The scraper keeps the `events` table in Neon updated; the API and frontend read from the same persistent store.

- `tutorial_Selenium/auth.py`
  - This is the core authentication helper module (server-side logic) that handles user creation, password hashing, token creation, and subscriptions.
  - What I changed / added: Implemented secure password hashing with `bcrypt`, functions to create and look up users, functions to create JSON Web Tokens (JWTs) to represent a logged-in session, and functions to save and list user alert subscriptions.
  - Effect: Passwords are never stored in plain text, and the server can issue secure, signed tokens that the frontend uses to make authenticated API requests.

- `tutorial_Selenium/routes/auth.py`
  - This is the HTTP layer for authentication: the register/login endpoints, and the subscription endpoints.
  - What I changed / added: Implemented `/auth/register`, `/auth/login`, `/auth/me`, `/auth/subscriptions` (create and list), and `DELETE /auth/subscriptions/{id}`. The endpoints validate input, call the auth helpers, and return a JWT token on successful register/login.
  - Effect: The frontend can now register users, log them in, and save user-specific alert rules in the database.

- `requirements.txt`
  - What I changed: Added `bcrypt` and `PyJWT` so the project can hash passwords and create/verify tokens.
  - Effect: These are required packages for the new server-side auth features.

- `.env.example`
  - What I changed: Added a `JWT_SECRET_KEY` placeholder and left database placeholders.
  - Effect: New contributors see which environment variables they must set locally (and understand not to commit real secrets).

- Miscellaneous small updates
  - Fixed database connection cleanup to avoid crashes if the connection failed to open.
  - Added small UI changes so logged-in vs logged-out states are clearer and the sign-out button works.

---

## What the new authentication system does (simple terms)

- Registration
  - A user types an email and password in the frontend.
  - The frontend sends that to the backend `/auth/register` endpoint.
  - The server checks the email isn't already used, hashes the password (so it can't be read by anyone), stores the user, and returns a signed token (JWT).
  - The frontend stores that token and uses it to prove who the user is on future requests.

- Login
  - A user provides email and password to `/auth/login`.
  - The server checks the password against the hashed version on file.
  - If correct, the server returns a fresh JWT token and the user is considered logged-in.

- Token-based authentication (JWT)
  - The token is a signed string that shows the server issued it — the frontend includes it in an HTTP header on API requests.
  - The server verifies the token signature and expiration before it executes protected operations (like saving alert preferences).

- Subscriptions (alert preferences)
  - When logged in, the user can save a set of rules (which countries and categories they want alerts for).
  - Each rule is stored in the `user_alert_subscriptions` table associated with that user's database record.

---

## How everything fits together now (simplified)

- The scraper writes events into the shared database.
- The backend reads events from the database and returns them to the frontend API consumers.
- Users register and log in via the backend; their passwords are hashed and their subscription rules are saved to the same database.
- The frontend uses the returned JWT token to make authenticated requests (for example, to save subscriptions).

This means the entire system is now working end-to-end: scrape → DB → API → frontend → user saves preferences → DB.

---

## Short README: How to run locally (for convenience)

1. Create a `.env` file in the repository root, based on `.env.example`. Fill in the real `DATABASE_URL` (or DB_HOST/DB_NAME/DB_USER/DB_PASSWORD) and set a long `JWT_SECRET_KEY`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the backend: `cd tutorial_Selenium` then `python -m uvicorn main:app --reload --port 8000`.
4. Open the frontend: open `tutorial_Selenium/index.html` in a browser (or serve the folder with a simple static server).
5. Register a user in the UI and save subscriptions; verify rows appear in the `users` and `user_alert_subscriptions` tables.

---

## Security notes (what I took care of)

- Secrets are not stored in the repository: the `.env` file is used and `.env` is ignored by git.
- Passwords are hashed with `bcrypt`; the cleartext password is never stored.
- Tokens are signed with a secret (`JWT_SECRET_KEY`) and expire after 7 days.
- DB schema uses `UNIQUE` on event links to prevent event duplicates and `ON DELETE CASCADE` for subscriptions so cleaning up users is safe.

---

## Next suggested steps you might want to do

- Wire an email provider (SendGrid, SMTP, or similar) so the server can send email alerts when new matching events are scraped.
- Add an endpoint or background job to scan new events and notify subscribed users.
- Add rate limiting and stronger email validation if you plan public signups.
- Add tests for the auth endpoints if you want automated verification of register/login flows.

---

## If you want the short commit history I made (very short list)

- Added secure DB configuration and `.env` handling
- Implemented persistent database-backed events (scraper → DB)
- Built frontend dashboard and connected it to `/api/news`
- Implemented backend authentication (bcrypt + JWT)
- Wired frontend to call backend register/login and save subscriptions

---

If you want any part of this explanation expanded (for example: a one-page README focused only on auth, or a short guide showing exactly what to check in the database), tell me which part and I’ll add it as another .md file.
