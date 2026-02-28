# Fynity Platform — Architecture

## Stack

| Layer     | Technology                                      |
|-----------|-------------------------------------------------|
| Backend   | Django 5, Django REST Framework, MySQL          |
| Frontend  | Next.js 14 (App Router), TypeScript, Tailwind   |
| Auth      | TBD (Session / JWT / OAuth)                     |

## Directory Structure

```
fynity-platform/
├── backend/
│   ├── apps/               ← Django applications (one dir per app)
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py     ← Shared settings
│   │   │   ├── local.py    ← Dev overrides
│   │   │   └── production.py
│   │   ├── api_router.py   ← Central DRF URL router
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── local.txt
│   │   └── production.txt
│   └── manage.py
├── frontend/
│   ├── app/                ← Next.js App Router pages & layouts
│   ├── components/         ← Shared React components
│   ├── lib/                ← Utilities, API clients, hooks
│   ├── types/              ← TypeScript type definitions
│   └── public/
├── docs/
└── scripts/
    ├── setup.sh            ← Bootstrap local dev
    ├── db.sh               ← MySQL + Django migration helpers
    └── deploy.sh           ← Production deployment
```

## API Convention

All API routes are prefixed with `/api/v1/`.
The frontend proxies these via `next.config.ts` rewrites to `NEXT_PUBLIC_API_URL`.

## Adding a New Django App

```bash
cd backend
source .venv/bin/activate
python manage.py startapp <app_name> apps/<app_name>
```

Then register `apps.<app_name>` in `config/settings/base.py → LOCAL_APPS`
and add its URLs in `config/api_router.py`.
