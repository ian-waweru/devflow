# DevFlow

### A modern collaborative project & task management platform

DevFlow is a full-stack project management platform designed to help teams organize projects, manage tasks, collaborate with team members, and keep track of project activity from a centralized workspace.

The project is built around a **decoupled Django REST Framework API**, with a React client consuming the API. This architecture also makes the backend reusable for future clients, including a planned React Native mobile application.

> **Project status:** 🚧 Actively developed  
> **Backend:** 🟢 Feature-rich REST API  
> **Frontend:** 🟡 In active development  
> **Mobile:** 🔵 Planned

---

## ✨ Why DevFlow?

Many project management applications hide the complexity of collaboration, permissions, authentication, and state management behind a polished interface.

DevFlow is being built with a different objective:

**to demonstrate how a production-style collaborative application can be designed from the backend API through to the user interface.**

The project focuses on:

- REST API design
- Authentication and authorization
- Role-based permissions
- Relational data modeling
- Project collaboration
- Task lifecycle management
- API filtering, searching and pagination
- Notifications
- Activity auditing
- Automated testing
- API documentation
- Decoupled frontend architecture

---

# 🎯 Core Features

### 🔐 Authentication

DevFlow uses JWT authentication to secure API access.

- User registration
- User login
- JWT access tokens
- Refresh tokens
- Authenticated user profile
- Protected API endpoints
- Protected React routes

---

### 📁 Project Management

Users can create and manage collaborative projects.

```text
Create Project
      │
      ▼
Add Members
      │
      ▼
Create Tasks
      │
      ▼
Assign Tasks
      │
      ▼
Collaborate
      │
      ▼
Track Activity
```

Projects support:

- Creation
- Updating
- Deletion
- Member management
- Project-specific permissions
- Activity history

---

### 👥 Team Collaboration

Projects are not isolated workspaces.

Users can collaborate by:

- Adding members to projects
- Removing members
- Assigning tasks
- Communicating through task comments
- Receiving notifications about important events

---

### ✅ Task Management

Tasks form the core of project execution.

Each task can contain:

- Title
- Description
- Status
- Priority
- Assignee
- Project
- Timestamps
- Comments

Tasks follow a simple lifecycle:

```text
┌──────┐
│ TODO │
└──┬───┘
   │
   ▼
┌─────────────┐
│ IN PROGRESS │
└──────┬──────┘
       │
       ▼
┌───────────┐
│ COMPLETED │
└─────┬─────┘
      │
      ▼
┌──────────┐
│ ARCHIVED │
└──────────┘
```

---

### 💬 Task Comments

Team members can communicate directly through task comments.

Comments support:

- Creation
- Editing
- Deletion
- Permission-based access

This provides a basic collaboration layer without requiring an external communication service.

---

### 🔔 Notifications

DevFlow keeps users informed about important events.

Examples include:

- Task assignments
- Project invitations
- Other project-related events

Users can:

- View notifications
- Mark individual notifications as read
- Mark all notifications as read

---

### 📜 Activity Tracking

Important project actions are recorded in an activity log.

This creates an audit trail that allows users to understand:

> **Who did what, and when?**

This becomes particularly useful in collaborative environments where several users are modifying the same project.

---

### 🔎 Search, Filtering & Pagination

The API supports server-side:

- Searching
- Filtering
- Pagination

This allows clients to request only the information they need instead of downloading an entire dataset.

For example:

```http
GET /api/tasks/?search=backend
```

The frontend can therefore remain lightweight while the API handles data retrieval efficiently.

---

# 🏗️ Architecture

DevFlow follows a **decoupled client-server architecture**.

```text
                         ┌─────────────────────┐
                         │       Database      │
                         │   SQLite / Postgres │
                         └──────────▲──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         │   Django REST API   │
                         │                     │
                         │  Authentication     │
                         │  Business Logic     │
                         │  Permissions        │
                         │  Validation         │
                         │  Serializers        │
                         │  API Documentation  │
                         └──────────┬──────────┘
                                    │
                              REST / JSON
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
              ┌──────▼───────┐             ┌──────▼───────┐
              │ React Web App │             │ React Native │
              │               │             │ Mobile App   │
              │   Current     │             │   Planned    │
              └───────────────┘             └──────────────┘
```

### Why this architecture?

The backend does not depend on the React application.

Instead:

```text
Django
   │
   └── REST API
          │
          ├── React
          ├── React Native
          ├── Mobile clients
          └── Other future clients
```

This allows the API to serve multiple applications without duplicating backend logic.

---

# 🧠 Backend Design

The backend is divided into focused Django applications.

```text
devflow-api/
│
├── accounts/
│   ├── authentication
│   ├── users
│   └── notifications
│
├── projects/
│   ├── projects
│   ├── memberships
│   └── activity logs
│
├── tasks/
│   ├── tasks
│   └── comments
│
└── config/
    ├── settings
    └── URL configuration
```

This separation keeps application responsibilities clear and makes the backend easier to extend.

---

# 🔒 Permission Architecture

Authorization is handled by the API rather than relying solely on frontend restrictions.

For example:

```text
                    Project
                       │
              ┌────────┴────────┐
              │                 │
            Owner             Member
              │                 │
       Full project        Restricted access
          control
```

The backend determines whether a user is allowed to perform an action.

This is important because hiding a button in React is **not security**.

A malicious client could simply send the HTTP request manually.

DevFlow therefore enforces authorization at the API level.

---

# 🧰 Technology Stack

## Backend

| Technology | Purpose |
|---|---|
| Python | Core backend language |
| Django | Web framework |
| Django REST Framework | REST API |
| Simple JWT | Authentication |
| drf-spectacular | OpenAPI documentation |
| SQLite | Development database |
| PostgreSQL | Production-ready database option |

## Frontend

| Technology | Purpose |
|---|---|
| React | UI |
| Vite | Development/build tooling |
| React Router | Client-side routing |
| Axios | HTTP communication |
| Tailwind CSS | UI styling |

## Planned

| Technology | Purpose |
|---|---|
| React Native | Mobile application |
| Expo | Mobile development workflow |
| PostgreSQL | Production database |
| Docker | Containerized deployment |

---

# 📂 Repository Structure

```text
devflow/
│
├── devflow-api/
│   │
│   ├── accounts/
│   ├── projects/
│   ├── tasks/
│   ├── config/
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
│
├── devflow-frontend/
│   │
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   └── pages/
│   ├── package.json
│   └── .env.example
│
├── .gitignore
└── README.md
```

---

# 📡 API

The API is the foundation of DevFlow.

## Main Resources

| Resource | Endpoint | Description |
|---|---|---|
| Authentication | `/api/auth/` | User authentication |
| Notifications | `/api/auth/notifications/` | User notifications |
| Projects | `/api/projects/` | Project management |
| Tasks | `/api/tasks/` | Task management |
| Comments | `/api/tasks/comments/` | Task discussions |

---

## Authentication

```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/token/refresh/
GET  /api/auth/me/
```

Authenticated requests use:

```http
Authorization: Bearer <access_token>
```

---

## Projects

```http
GET    /api/projects/
POST   /api/projects/
GET    /api/projects/<id>/
PUT    /api/projects/<id>/
PATCH  /api/projects/<id>/
DELETE /api/projects/<id>/
```

Project-specific functionality includes member management and activity history.

---

## Tasks

```http
GET    /api/tasks/
POST   /api/tasks/
GET    /api/tasks/<id>/
PUT    /api/tasks/<id>/
PATCH  /api/tasks/<id>/
DELETE /api/tasks/<id>/
```

Tasks also expose lifecycle actions such as completion and archiving.

---

# 📚 API Documentation

DevFlow uses OpenAPI documentation generated through `drf-spectacular`.

Once the backend is running:

### Swagger UI

```text
http://127.0.0.1:8000/api/docs/
```

### OpenAPI Schema

```text
http://127.0.0.1:8000/api/schema/
```

Swagger provides an interactive way to:

- Explore endpoints
- Inspect schemas
- Authenticate
- Send requests
- Inspect responses
- Test permissions

---

# 🚀 Getting Started

## Requirements

Before running DevFlow, install:

- Python 3.12+
- Node.js 20+
- npm
- Git

Verify:

```bash
python --version
node --version
npm --version
git --version
```

---

## 1. Clone

```bash
git clone https://github.com/ian-waweru/devflow.git
cd devflow
```

---

# 2. Backend Setup

```bash
cd devflow-api
```

Create a virtual environment.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create your environment file.

### Windows

```powershell
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Configure the required variables in `.env`.

For local development:

```env
DEBUG=True
SECRET_KEY=your-secret-key
```

> Never commit production secrets to Git.

---

## Database

Run migrations:

```bash
python manage.py migrate
```

Optionally create an administrator:

```bash
python manage.py createsuperuser
```

Start the API:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

# 3. Frontend Setup

Open another terminal.

```bash
cd devflow-frontend
```

Install dependencies:

```bash
npm install
```

Create the environment file:

```bash
copy .env.example .env
```

or:

```bash
cp .env.example .env
```

Configure the API URL for your local backend.

Then start React:

```bash
npm run dev
```

Vite will provide the frontend URL, normally:

```text
http://localhost:5173/
```

---

# 🧪 Running Tests

From the backend directory:

```bash
python manage.py test
```

The test suite covers important backend behavior including:

- Authentication
- Permissions
- Project membership
- Tasks
- Comments
- Notifications
- Project functionality

Run the tests before submitting changes to ensure existing functionality remains intact.

---

# 🖥️ Screenshots

> Screenshots will be added as the React frontend reaches its major UI milestones.

Recommended screenshots:

### Dashboard

![DevFlow Dashboard](docs/screenshots/dashboard.png)

### Project Workspace

![DevFlow Project](docs/screenshots/project.png)

### Task Management

![DevFlow Tasks](docs/screenshots/tasks.png)

### API Documentation

![DevFlow API](docs/screenshots/swagger.png)

> If you add the screenshots to the repository, keep them under `docs/screenshots/` and update the paths above.

---

# 🗺️ Roadmap

## Backend

- [x] Custom user authentication
- [x] JWT authentication
- [x] Project CRUD
- [x] Project membership
- [x] Permission system
- [x] Task CRUD
- [x] Task assignment
- [x] Task lifecycle
- [x] Comments
- [x] Notifications
- [x] Activity logging
- [x] Searching
- [x] Filtering
- [x] Pagination
- [x] Automated tests
- [x] OpenAPI documentation

## React Frontend

- [x] React/Vite setup
- [x] Authentication
- [x] JWT handling
- [x] Protected routes
- [x] Dashboard foundation
- [ ] Registration UI
- [ ] Project dashboard
- [ ] Project creation/editing
- [ ] Member management
- [ ] Task board
- [ ] Task creation/editing
- [ ] Task details
- [ ] Comments interface
- [ ] Notifications
- [ ] Improved loading/error states
- [ ] Responsive/mobile-first refinement

## Mobile

- [ ] React Native application
- [ ] Expo setup
- [ ] Mobile authentication
- [ ] Project management
- [ ] Task management
- [ ] Comments
- [ ] Notifications
- [ ] Offline support
- [ ] Push notifications

## Deployment

- [ ] PostgreSQL production database
- [ ] Docker configuration
- [ ] Production environment configuration
- [ ] CI/CD
- [ ] Backend deployment
- [ ] Frontend deployment
- [ ] API monitoring
- [ ] Production documentation

---

# 🔄 Development Workflow

DevFlow is developed in layers.

```text
        DATABASE
           │
           ▼
       DJANGO MODELS
           │
           ▼
       DRF SERIALIZERS
           │
           ▼
       API / VIEWSETS
           │
           ▼
       PERMISSIONS
           │
           ▼
       REST / JSON
           │
           ▼
      REACT API CLIENT
           │
           ▼
       REACT COMPONENTS
           │
           ▼
           UI
```

This approach keeps responsibilities separated and makes it possible to develop and test each layer independently.

---

# 🌐 Future Architecture

The long-term goal is for DevFlow to support multiple clients using the same API.

```text
                         ┌─────────────────────┐
                         │    DevFlow API      │
                         │                     │
                         │ Django + DRF        │
                         │ JWT Authentication  │
                         │ PostgreSQL          │
                         └──────────┬──────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               │                    │                    │
               ▼                    ▼                    ▼
        ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
        │ React Web   │      │ React Native│      │ Future      │
        │             │      │ Mobile      │      │ Clients     │
        └─────────────┘      └─────────────┘      └─────────────┘
```

The backend therefore remains independent of any particular interface.

---

# 🔐 Production Checklist

Before deploying DevFlow:

- [ ] `DEBUG=False`
- [ ] Strong production `SECRET_KEY`
- [ ] PostgreSQL configured
- [ ] HTTPS enabled
- [ ] Production `ALLOWED_HOSTS`
- [ ] Production CORS configuration
- [ ] CSRF configuration reviewed
- [ ] Secure JWT configuration
- [ ] Static/media files configured
- [ ] Logging configured
- [ ] Rate limiting considered
- [ ] Environment secrets secured
- [ ] Database backups configured
- [ ] CI/CD configured

---

# 📖 What This Project Demonstrates

DevFlow is intended to demonstrate practical full-stack development skills, including:

### Backend Engineering

- Django
- Django REST Framework
- REST API architecture
- JWT authentication
- Authorization
- Permission classes
- Serializers
- ViewSets
- Database relationships
- Query optimization
- Filtering
- Searching
- Pagination
- Validation
- Automated testing
- OpenAPI documentation

### Frontend Engineering

- React
- Component architecture
- React Router
- API integration
- Authentication state
- Protected routes
- Responsive UI
- Client-side state management

### Software Engineering

- Separation of concerns
- Client-server architecture
- API-first development
- Security-conscious authorization
- Testing
- Documentation
- Version control
- Incremental development

---

# 👨‍💻 Author

**Ian Waweru**

Full-stack developer focused on building practical applications with Python, Django, Django REST Framework, React and modern web technologies.

**GitHub:**  
https://github.com/ian-waweru

---

# ⭐ Support

If you find the project useful or interesting, consider giving the repository a ⭐ on GitHub.

---

## License

This project currently does not include a license.

If you intend to distribute or open-source DevFlow, add an appropriate `LICENSE` file to the repository.
