<div align="center">

# 🎓 EdTech Learning Platform

**A full-featured online learning platform built with Django**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

[Features](#-features) · [Tech Stack](#-tech-stack) · [Getting Started](#-getting-started) · [Project Structure](#-project-structure) · [API](#-api) · [Deployment](#-deployment)

---

</div>

## 📸 Overview

EdTech is a modern, dark-themed online learning platform where **teachers** can create and publish courses, **students** can enroll and track their progress, and **admins** can manage the entire platform — all from a clean, GitHub-inspired UI with dark/light mode support.

---

## ✨ Features

### 👩‍🎓 Students
- Browse and enroll in published courses
- Watch video lessons with progress tracking
- Take timed quizzes with instant results
- Submit assignments and receive grades
- Solve coding practice problems (Easy / Medium / Hard)
- View personal dashboard with progress overview
- Compete on the global leaderboard

### 👨‍🏫 Teachers
- Create and manage courses (Draft → Pending → Published)
- Add video lessons with file upload or URL
- Build quizzes with multiple-choice questions
- Create and grade assignments
- Add coding problems with hidden test cases
- View course analytics and enrollment stats

### 🛡️ Admins
- Full Django admin panel at `/admin/`
- Manage all users with role badges and login activity
- Approve/publish courses
- Bulk actions: activate/deactivate users, change roles
- View enrollment data and progress across all courses

### 🎨 UI / UX
- GitHub-inspired dark theme (default)
- One-click dark / light mode toggle (persisted via `localStorage`)
- Fully responsive — works on mobile, tablet, and desktop
- Split-panel login and registration pages
- Password strength meter on signup
- Show/hide password toggle

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 4.2, Django REST Framework |
| **Auth** | django-allauth (username + email login, password reset) |
| **Database** | PostgreSQL 16 |
| **Cache / Queue** | Redis 7, Celery |
| **Frontend** | Tailwind CSS (CDN), Vanilla JS |
| **Media Storage** | Local (dev) / AWS S3 (production) |
| **Static Files** | WhiteNoise |
| **Web Server** | Gunicorn + Nginx |
| **Containerisation** | Docker |
| **CI / CD** | GitHub Actions (SSH deploy) |

---

## 📁 Project Structure

```
learning_platform/
├── apps/
│   ├── users/          # Custom user model, auth views, dashboard, leaderboard
│   ├── courses/        # Courses, lessons, enrollments, progress tracking
│   ├── quizzes/        # Quizzes, questions, choices, attempts
│   ├── assignments/    # Assignments, submissions, grading
│   └── practice/       # Coding problems, test cases, code submissions
│
├── edtech_platform/
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── development.py  # Local dev overrides
│   │   └── production.py   # Production overrides
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
│
├── templates/
│   ├── base.html           # Base layout with navbar + sidebar
│   ├── home.html           # Landing page
│   ├── partials/           # navbar, sidebar, footer
│   └── users/              # login, register, profile, dashboard
│
├── static/
│   ├── css/custom.css      # Dark/light mode overrides
│   └── js/main.js          # Theme toggle, sidebar, flash messages
│
├── nginx/edtech.conf        # Nginx reverse proxy config
├── Dockerfile
├── .github/workflows/       # CI/CD deploy pipeline
├── requirements.txt
└── .env.example
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 16
- Redis 7
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Abhayks29/learning_platform.git
cd learning_platform
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=edtech_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0
```

### 5. Create the database

```bash
psql -U postgres -c "CREATE DATABASE edtech_db;"
```

### 6. Run migrations

```bash
python manage.py migrate --settings=edtech_platform.settings.development
```

### 7. Create a superuser

```bash
python manage.py createsuperuser --settings=edtech_platform.settings.development
```

### 8. Run the development server

```bash
python manage.py runserver --settings=edtech_platform.settings.development
```

Visit **http://127.0.0.1:8000** in your browser.
Admin panel at **http://127.0.0.1:8000/admin/**

---

## 🔑 User Roles

| Role | Access |
|---|---|
| **Admin** | Full access — manage users, courses, everything via `/admin/` |
| **Teacher** | Create courses, lessons, quizzes, assignments, problems |
| **Student** | Enroll in courses, take quizzes, submit assignments, solve problems |

Roles are assigned at registration and can be changed by an admin.

---

## 🗄️ Data Models

```
User (AbstractUser)
├── role: admin | teacher | student
├── avatar: ImageField
└── bio: TextField

Course
├── teacher → User
├── category → Category
├── status: draft | pending | published
└── lessons → Lesson[]
    └── progress → LessonProgress[]

Enrollment
├── student → User
└── course → Course

Quiz
├── course → Course
├── questions → Question[]
│   └── choices → Choice[]
└── attempts → QuizAttempt[]
    └── answers → QuizAnswer[]

Assignment
├── course → Course
└── submissions → Submission[]

PracticeProblem
├── difficulty: easy | medium | hard
├── test_cases → TestCase[]
└── submissions → CodeSubmission[]
```

---

## 🌐 URL Routes

| URL | Description |
|---|---|
| `/` | Landing page |
| `/accounts/login/` | Sign in |
| `/accounts/signup/` | Register |
| `/accounts/password/reset/` | Password reset |
| `/dashboard/` | Student dashboard |
| `/courses/` | Browse all courses |
| `/courses/<slug>/` | Course detail |
| `/quizzes/` | Quiz list |
| `/assignments/` | Assignment list |
| `/practice/` | Coding problems |
| `/leaderboard/` | Global leaderboard |
| `/admin/` | Admin panel |

---

## 📡 API

The platform exposes a REST API via Django REST Framework.

**Authentication:** Session-based (login required)

```
GET  /api/courses/         # List courses
GET  /api/courses/<id>/    # Course detail
POST /api/enrollments/     # Enroll in a course
GET  /api/progress/        # Student progress
```

---

## 🚢 Deployment

### Docker

```bash
docker build -t edtech .
docker run -p 8000:8000 --env-file .env edtech
```

### Production (Gunicorn + Nginx)

1. Set up environment variables on the server
2. Configure `nginx/edtech.conf` with your domain
3. Run with Gunicorn:

```bash
gunicorn --workers 3 --bind 0.0.0.0:8000 edtech_platform.wsgi:application \
  --settings=edtech_platform.settings.production
```

### CI/CD (GitHub Actions)

On every push to `main`, the workflow:
1. SSH into your server
2. `git pull`
3. Install dependencies, run migrations, collect static files
4. Restart Gunicorn, Nginx, and Celery

Add these **repository secrets** in GitHub → Settings → Secrets:

| Secret | Value |
|---|---|
| `SERVER_HOST` | Your server IP or domain |
| `SERVER_USER` | SSH username |
| `SERVER_SSH_KEY` | Your private SSH key |

---

## ⚙️ Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key |
| `DEBUG` | ✅ | `True` for dev, `False` for prod |
| `ALLOWED_HOSTS` | ✅ | Comma-separated hostnames |
| `DB_NAME` | ✅ | PostgreSQL database name |
| `DB_USER` | ✅ | PostgreSQL username |
| `DB_PASSWORD` | ✅ | PostgreSQL password |
| `DB_HOST` | ✅ | PostgreSQL host |
| `DB_PORT` | ✅ | PostgreSQL port (default: 5432) |
| `REDIS_URL` | ✅ | Redis connection URL |
| `AWS_ACCESS_KEY_ID` | ⚙️ Production | AWS S3 key |
| `AWS_SECRET_ACCESS_KEY` | ⚙️ Production | AWS S3 secret |
| `AWS_STORAGE_BUCKET_NAME` | ⚙️ Production | S3 bucket name |
| `EMAIL_HOST_USER` | ⚙️ Production | SMTP email address |
| `EMAIL_HOST_PASSWORD` | ⚙️ Production | SMTP email password |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ by [Abhay](https://github.com/Abhayks29)

</div>
