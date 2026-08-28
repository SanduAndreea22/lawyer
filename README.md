# Cassian & Voicu — Law Firm Website

A portfolio project: a Django website and booking system for a fictional law
firm, "Cassian & Voicu". Public marketing site + a functional consultation
booking flow backed by a database, plus an internal staff dashboard for
managing appointments and cases — no client accounts, no client portal.

## Screenshots

| Homepage | Booking flow |
|---|---|
| ![Homepage](docs/screenshots/home.png) | ![Booking](docs/screenshots/booking.png) |

| Team | Staff dashboard |
|---|---|
| ![Team](docs/screenshots/team.png) | ![Dashboard](docs/screenshots/dashboard.png) |

## Stack

Django 5, server-rendered templates (no SPA). SQLite for local dev,
Postgres in production (via `DATABASE_URL`). Static files served through
WhiteNoise; deploys to Render via the included `render.yaml`.

## Structure

- `pages` — homepage, contact page and message form
- `practice_areas` — the four practice areas (list + detail pages)
- `team` — lawyer profiles, each optionally linked to a staff login
- `booking` — the public consultation booking flow (practice area → lawyer →
  time slot → confirmation), with `transaction.atomic()` + `select_for_update()`
  and a database-level unique constraint to prevent double-booking the same
  lawyer and time slot
- `dashboard` — internal, login-only area for lawyers/staff: an overview of
  upcoming appointments, active cases and unpaid invoices; confirming,
  cancelling and rescheduling appointments (same double-booking protection as
  public booking); opening a case from a confirmed appointment; updating case
  status and uploading documents. A lawyer only sees their own appointments
  and cases — a superuser account sees everything.

## Getting started

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the public site, `/dashboard/` for the
staff area, and `/admin/` for the Django admin.

### Demo data

Data migrations automatically seed the four practice areas, one lawyer per
area, and one demo case with an invoice, so the site isn't empty on first
run. This part always runs on `migrate`, in any environment — it's just
content, not credentials.

Staff **logins** for the dashboard are a separate, deliberate step — `migrate`
alone never creates them, including in production. For local development or
a demo deployment, create them explicitly:

```bash
python manage.py seed_demo_users
```

This links each seeded lawyer to a login, all sharing one password (printed
by the command; `demo12345` unless you pass `--password`):

| Username | Lawyer |
|---|---|
| `mihai.cassian` | Commercial Law |
| `delia.voicu` | Family Law |
| `radu.stoian` | Real Estate Law |
| `ana.petrescu` | Civil Litigation |

Don't run this against a deployment with real client data — use
`createsuperuser` and/or the Django admin to create real staff accounts
instead. For full visibility across every lawyer's appointments and cases,
use a superuser account.

## Configuration / deployment

Settings are read from environment variables (via a local `.env` file in
development, or real environment variables from the host in production).
Copy `.env.example` to `.env` and fill it in:

- `DJANGO_SECRET_KEY` — generate one with
  `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DJANGO_DEBUG` — `True` locally, `False` in any real deployment
- `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` — required once
  `DJANGO_DEBUG=False`

With `DJANGO_DEBUG=False`, HTTPS-only cookie and HSTS settings turn on
automatically — see `config/settings.py`. The demo staff password above is
fine for a portfolio demo but is public (it's in this README, and it's the
`seed_demo_users` default) — don't use it anywhere real client data lives.

Uploaded media (lawyer photos, case documents) is served directly by Django
in every environment, since no object storage (S3/Cloudinary/etc.) is wired
up yet — fine for a small, low-traffic deployment, but note that anyone with
a media URL can fetch it with no login check. Move to `django-storages` +
S3 (or similar, with access control) before there's meaningful traffic or
before case documents contain anything genuinely sensitive.

Static files (CSS/JS/images) are served via
[WhiteNoise](https://whitenoise.readthedocs.io/) with hashed, cache-busted
filenames in production (`STORAGES["staticfiles"]`, only active when
`DJANGO_DEBUG=False` — local dev keeps using Django's plain static handling,
no `collectstatic` needed).

The database is picked up from `DATABASE_URL` when set (any standard
Postgres connection string — Neon, Render Postgres, etc.), falling back to
local SQLite otherwise. This matters beyond just persistence: the
double-booking protection's `select_for_update()` only actually locks rows
on Postgres — on SQLite it's a silent no-op, and the DB-level unique
constraint is doing all the real work there. Use Postgres for any real
deployment.

### Deploying to Render

This repo includes a `render.yaml` [Blueprint](https://render.com/docs/blueprint-spec)
for a one-command deploy.

1. **Create a Postgres database** — e.g. on [Neon](https://neon.tech) (free
   tier, no expiry, unlike Render's own free Postgres which is deleted after
   30 days). Copy the connection string it gives you (starts with
   `postgres://` or `postgresql://`).
2. On Render: **New → Blueprint**, point it at this repo. Render reads
   `render.yaml` and provisions the web service with sensible defaults
   (`DJANGO_DEBUG=False`, a generated `DJANGO_SECRET_KEY`, etc.).
3. In the service's **Environment** tab, paste the Neon connection string as
   `DATABASE_URL` (left blank in the Blueprint on purpose — it's a secret,
   `sync: false` means Render won't try to manage it).
4. Once deployed, check the actual URL Render assigned the service (it may
   differ from the `cassian-voicu.onrender.com` placeholder in `render.yaml`
   if that name is taken) and update `DJANGO_ALLOWED_HOSTS` /
   `DJANGO_CSRF_TRUSTED_ORIGINS` to match if needed — then redeploy.
5. Create a real staff account via Render's **Shell** tab:
   `python manage.py createsuperuser` (don't run `seed_demo_users` against
   a deployment anyone else can reach — see above).

The build step runs `collectstatic` and `migrate` automatically
(`render.yaml`'s `buildCommand`); the app itself runs under `gunicorn`.

Render's free web service disk is ephemeral — uploaded lawyer photos and
case documents won't survive a redeploy or a scale-to-zero restart, even
with Postgres handling the actual data. That's an accepted tradeoff for a
portfolio deployment; revisit with S3/Cloudinary if that ever matters.
