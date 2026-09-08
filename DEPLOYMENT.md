# Deploying DevFlow

This covers taking DevFlow from local development to a live deployment:
**Render** for the Django API + PostgreSQL database, and **Vercel** for the
React frontend. Both have free tiers sufficient for this project's scale.

Everything below assumes your code is already pushed to GitHub (it is) and
that you're comfortable creating free accounts on Render and Vercel.

---

## 1. Backend: Render

### 1.1 Create the database first

1. Render dashboard → **New** → **PostgreSQL**
2. Name it (e.g. `devflow-db`), choose the free tier, create it
3. Once created, copy its **Internal Database URL** — you'll need it in step 1.3

### 1.2 Create the web service

1. Render dashboard → **New** → **Web Service**
2. Connect your GitHub repo, select the `devflow` repo
3. Set **Root Directory** to `devflow-api`
4. Render should auto-detect Python. Confirm:
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command:** `gunicorn config.wsgi --log-file -` (matches the `Procfile`)

### 1.3 Set environment variables

In the web service's **Environment** tab, add:

| Key | Value |
|---|---|
| `SECRET_KEY` | Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` — use a fresh one, don't reuse your local dev key |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | Your Render service's domain, e.g. `devflow-api.onrender.com` (Render shows you this once the service is created — you may need to add it after the first deploy) |
| `CORS_ALLOWED_ORIGINS` | Your Vercel frontend's domain, e.g. `https://devflow.vercel.app` (set this after step 2, once you know the real URL) |
| `DATABASE_URL` | The Internal Database URL from step 1.1 |

### 1.4 Migrations

The `Procfile` includes a `release: python manage.py migrate --noinput` line. If your Render plan runs release commands automatically, migrations happen on every deploy with no extra step. If not, run it manually once from Render's **Shell** tab:

```bash
python manage.py migrate
```

### 1.5 Create a superuser (optional, for `/admin/`)

From Render's Shell tab:

```bash
python manage.py createsuperuser
```

### 1.6 Verify

Visit `https://<your-render-domain>/api/docs/` — you should see the Swagger UI. If you get a 400 "Bad Request," double check `ALLOWED_HOSTS` matches the domain exactly.

---

## 2. Frontend: Vercel

1. Vercel dashboard → **Add New** → **Project**
2. Import the same GitHub repo
3. Set **Root Directory** to `devflow-frontend`
4. Framework preset: Vercel should auto-detect Vite
5. Add an environment variable:

   | Key | Value |
   |---|---|
   | `VITE_API_URL` | `https://<your-render-domain>/api` |

6. Deploy

Once deployed, Vercel gives you a URL like `https://devflow.vercel.app`. Go back to Render and update `CORS_ALLOWED_ORIGINS` to that exact URL (step 1.3), then redeploy the backend so the new CORS setting takes effect.

---

## 3. Post-deploy checklist

- [ ] Visit the Vercel URL, register a new account, confirm login works
- [ ] Create a project, add a member, create a task — confirms the full request chain (frontend → CORS → API → database) works end to end
- [ ] Check the browser's Network tab for any CORS errors — if you see one, the frontend URL in `CORS_ALLOWED_ORIGINS` doesn't match exactly (check for trailing slashes, http vs https)
- [ ] Confirm `DEBUG=False` on the backend — visiting a broken URL should show a generic error page, not a Django debug traceback
- [ ] Run `python manage.py check --deploy` from Render's shell — should report no issues (this is already verified to pass with the settings in this repo, but re-check after any future settings changes)

---

## 4. Continuous Integration

`.github/workflows/ci.yml` runs automatically on every push and pull request to `main`:

- **Backend job:** installs dependencies, runs migrations, runs the full test suite (71 tests), and verifies the OpenAPI schema generates without warnings
- **Frontend job:** installs dependencies, lints, and builds

Both must pass before merging is a sensible habit to adopt, even working solo — it catches regressions immediately rather than after they've been deployed. Render/Vercel deploy independently of this workflow (they redeploy on push regardless of CI status by default) — if you want deploys blocked on CI passing, that's configurable in each platform's settings, not something this repo controls.

---

## 5. What's intentionally not covered here

- **Custom domains** — both Render and Vercel support attaching your own domain; it's a few clicks in each platform's settings once you own one
- **Email sending** — nothing in DevFlow sends real email yet (see `EMAIL_BACKEND` in `settings.py`); if that changes, you'll need a transactional email provider (e.g. SendGrid, Postmark) and corresponding env vars
- **Media/file uploads** — DevFlow doesn't currently accept file uploads (avatars, attachments); if that's added later, static-file storage (S3 or similar) would need to be introduced separately from the static-asset serving (whitenoise) already configured