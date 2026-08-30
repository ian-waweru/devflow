# DevFlow

**A collaborative multi-user project & task management platform.**

> Backend is feature-complete for v1. Frontend currently provides authentication and a protected dashboard shell.

---

## Status

| Layer        | Status                          |
|--------------|---------------------------------|
| **Backend**  | Complete (projects, tasks, comments, notifications, activity log, JWT auth) |
| **Frontend** | Minimal — login + protected route + placeholder dashboard |
| **Tests**    | Solid API coverage with permission boundary checks |
| **Docs**     | OpenAPI / Swagger available at `/api/docs/` |

---

## Features

### Already working (API)

- **User accounts** — registration, login, profile (`/me/`)
- **Projects** — create, list, update, delete; multi-member collaboration
- **Membership roles** — Owner (full control) vs Member (read + limited task actions)
- **Tasks** — status (`todo` → `in_progress` → `completed` / `archived`), priority, assignment
- **Comments** on tasks
- **Notifications** — assignment and project invitation alerts
- **Activity log** per project
- **JWT authentication** (access + refresh tokens)
- **Filtering, search & pagination** on projects and tasks
- **Interactive API docs** (Swagger UI)

### Frontend (current)

- Login page
- JWT storage + automatic Bearer token attachment
- Session restore
- Protected routes
- Basic dashboard placeholder

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Backend    | Django 6.1, Django REST Framework, SimpleJWT    |
| Frontend   | React 19, Vite 8, Tailwind CSS, React Router 7  |
| Database   | SQLite (development) — PostgreSQL-ready         |
| API Docs   | drf-spectacular (OpenAPI 3 + Swagger UI)        |

---

## Project Structure

```
devflow/
├── devflow-api/          # Django REST API
│   ├── accounts/         # Custom User + Notifications
│   ├── projects/         # Projects, Membership, ActivityLog
│   ├── tasks/            # Tasks + Comments
│   └── config/           # Settings, URLs
└── devflow-frontend/     # React SPA
    └── src/
        ├── api/          # Axios client
        ├── context/      # AuthContext
        ├── components/   # ProtectedRoute
        └── pages/        # Login + Dashboard placeholder
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- npm (or pnpm/yarn)

### 1. Backend

```bash
cd devflow-api
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set a real SECRET_KEY

python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver
```

- API: http://127.0.0.1:8000  
- Swagger UI: http://127.0.0.1:8000/api/docs/  
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

### 2. Frontend

```bash
cd devflow-frontend
npm install
npm run dev
```

- App: http://localhost:5173 (typical Vite port)

> **Note:** The frontend currently expects the API at `http://127.0.0.1:8000/api`.  
> CORS is not fully configured yet — you may need to allow the Vite origin in Django settings before the browser will accept responses.

---

## API Overview

Base path: `/api/`

| Area            | Prefix                  | Key endpoints                                      |
|-----------------|-------------------------|----------------------------------------------------|
| Auth            | `/api/auth/`            | `register/`, `login/`, `token/refresh/`, `me/`     |
| Notifications   | `/api/auth/notifications/` | list, mark read, mark all read                  |
| Projects        | `/api/projects/`        | CRUD + `add-member/`, `remove-member/`, `activity/` |
| Tasks           | `/api/tasks/`           | CRUD + `complete/`, `archive/`                     |
| Comments        | `/api/tasks/comments/`  | full CRUD                                          |

All endpoints except registration and login require a valid JWT (`Authorization: Bearer <access_token>`).

---

## Permission Model (Summary)

| Resource  | Owner                    | Member / Assignee                          | Non-member |
|-----------|--------------------------|--------------------------------------------|------------|
| Project   | Full CRUD + manage members | Read-only                                | No access  |
| Task      | Full access              | Read + limited status changes + complete/archive if assigned | No access |
| Comment   | —                        | Read; only author can edit/delete          | No access  |

---

## Environment Variables

Create `devflow-api/.env` from the example:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

---

## Running Tests

```bash
cd devflow-api
source venv/bin/activate
python manage.py test
```

Tests cover authentication, project membership, task lifecycle, comments, notifications, and permission boundaries.

---

## Roadmap (Next Steps)

1. Configure CORS for the frontend origin
2. Registration UI
3. Projects list + create + detail views
4. Task board / list with status & priority controls
5. Task detail + comments UI
6. Notifications UI
7. Token refresh handling on the frontend
8. Environment-based API base URL
9. Production hardening (PostgreSQL, `DEBUG=False`, proper `ALLOWED_HOSTS`, etc.)

---

## License

No license file is present yet. Add one when you decide how the project should be shared.

---

## Author

[Ian Waweru](https://github.com/ian-waweru)
