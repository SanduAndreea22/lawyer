# Cassian & Voicu — Law Firm Website

A portfolio project: a Django website and booking system for a fictional law
firm, "Cassian & Voicu". Public marketing site + a functional consultation
booking flow backed by a database — no client accounts, no client portal
(staff manage everything through the Django admin).

## Stack

Django 5, SQLite (default dev database), server-rendered templates (no SPA).

## Structure

- `pages` — homepage, contact page and message form
- `practice_areas` — the four practice areas (list + detail pages)
- `team` — lawyer profiles
- `booking` — the consultation booking flow (practice area → lawyer → time
  slot → confirmation), with `transaction.atomic()` + `select_for_update()`
  and a database-level unique constraint to prevent double-booking the same
  lawyer and time slot

## Getting started

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the site and `/admin/` to manage practice
areas, lawyers, and appointments.

Seed data for the four practice areas and one lawyer per area is loaded
automatically by data migrations.
