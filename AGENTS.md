# Guindex — local development setup (Cursor / AI agent context)

This file helps new contributors (and Cursor agents) mirror a working local environment. The Django project lives under `GuindexProject/`; run commands from there unless noted.

## Stack

- **Python:** Use **Python 3.10+** (e.g. 3.12). Install dependencies from the repo root: `pip install -r requirements.txt` (ideally in a virtualenv).
- **Django:** 4.x per `requirements.txt`. The **production server may still run older Python** in some deployments; **local dev should match `requirements.txt` and Python 3**, not legacy Python 2.

## One-time setup

1. **Clone** the repo and open the **repository root** in Cursor (the folder that contains `GuindexProject/` and `requirements.txt`).

2. **Virtual environment** (recommended):
   ```bash
   cd /path/to/Guindex
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Secrets:** `GuindexProject/GuindexProject/settings.py` imports `secrets` (e.g. `KEY`, `EMAIL`, API keys). Create `GuindexProject/GuindexProject/secrets.py` from your teammate’s template or copy — it is usually **gitignored** and must not be committed.

4. **Database:** Uses **SQLite only** — no PostgreSQL/MySQL install, host, or password for normal local work. Django chooses the file automatically: **`Guindex.db` at the repo root** (next to `GuindexProject/`) if it exists, otherwise **`GuindexProject/Guindex.db`**. Override with `GUINDEX_DATABASE_PATH` only if you want the file elsewhere. Then:
   ```bash
   cd GuindexProject
   python manage.py migrate
   ```
   That creates or updates the schema. Optionally copy a teammate’s `Guindex.db` for real data; otherwise the DB starts empty after migrate.

## Environment variables (local dev)

| Variable | Purpose |
|----------|---------|
| **`DJANGO_DEBUG=1`** | **Required for `runserver` to serve CSS/JS/images** from app static folders. If unset, `DEBUG` defaults to off and `/static/...` returns 404 in development. |
| `GUINDEX_DATABASE_PATH` | Optional override for SQLite file location. |
| `GUINDEX_LOG_DIR` | Optional; defaults to `GuindexProject/logs/`. |
| `GUINDEX_USE_DB_CACHE` | Optional production-style DB cache; see `settings.py`. |

**Typical local run:**

```bash
cd GuindexProject
export DJANGO_DEBUG=1
python manage.py runserver
```

Or: `DJANGO_DEBUG=1 python manage.py runserver`

## Static files and templates

- With **`DJANGO_DEBUG=1`**, Django’s dev server serves static files from installed apps (e.g. `GuindexWebClient/static/`).
- **`collectstatic`** copies into `STATIC_ROOT` (`GuindexProject/CDN/`). Use that when testing production-like static layout or nginx; it is not required for everyday `runserver` with `DJANGO_DEBUG=1`.

### Production JavaScript (`DJANGO_DEBUG` unset / `DEBUG=False`)

[`guindex_web_client.html`](GuindexProject/GuindexWebClient/templates/guindex_web_client.html) loads **`.min.js`** versions of several Guindex scripts (e.g. `guindex_login.min.js`, `guindex_tabs.min.js`, `guindex_main.min.js`, `guindex_web_client_utils.min.js`). When you change the non-minified `.js` sources, **sync or regenerate** the corresponding `.min.js` files before deploying without debug, or production will serve **stale** login/logout and tab behavior.

- At minimum, after editing [`guindex_login.js`](GuindexProject/GuindexWebClient/static/javascript/guindex_login.js), update [`guindex_login.min.js`](GuindexProject/GuindexWebClient/static/javascript/guindex_login.min.js) (copy for parity, or run `npx terser` / your bundler for a true minified build).
- The same applies to any other `guindex_*.min.js` files referenced in that template that your pipeline does not auto-generate.

## DataTables / API (smoke check)

The pubs table loads from **`/api/pubs/?format=datatables`** (see `guindex_table.js`). If the table is empty or broken locally, check the browser Network tab for that request and run `python manage.py check`.

## Production deployment (high level — not local)

- Restart the **WSGI app** (e.g. Gunicorn), not only nginx, after code changes.
- Ensure **`collectstatic`** output matches what nginx serves from `STATIC_ROOT`.

## Quick troubleshooting

| Symptom | Likely cause |
|--------|----------------|
| No CSS/JS, 404 on `/static/...` | **`DJANGO_DEBUG` not set to `1`** → `DEBUG` false → dev server does not serve static. |
| `ModuleNotFoundError: secrets` | Missing `GuindexProject/GuindexProject/secrets.py`. |
| Migration errors | Run `migrate`; ensure DB path is writable. |

---

*Share this file with teammates using Cursor; it doubles as onboarding for humans and agents.*
