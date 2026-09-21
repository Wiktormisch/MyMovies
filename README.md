# 🎬 MyMovies

A personal movie library built with Django. Add movies by hand or from the TMDB database, mark them as watched or to-watch, rate and tag them, then filter your collection.

**Live demo:** [wiktormischker.dev/app](https://wiktormischker.dev/app) (login: `demo`, password: `demo1`, registration disabled)

**Author:** Wiktor Mischker · [GitHub](https://github.com/Wiktormisch)

---

## What this project shows

- **Working, deployed app.** Runs on a VPS in Docker behind Gunicorn, not just on localhost.
- **Tested.** A pytest suite that runs in under a second. Views, access control, forms, the TMDB integration (mocked, no network) and a secret-scanning gate are all covered.
- **Secure by default.** Secrets live in `.env`, never in the repo. A test fails the build if a real key or a committed `.env` shows up. Every view requires login and users only ever see their own data.
- **Git discipline.** 80+ commits, feature branches merged into `dev`, then `main` through pull requests. Most commit messages use `feat:`, `fix:`, `test:`, `docs:` prefixes.
- **Third-party API integration.** Movie search and import from [TMDB](https://www.themoviedb.org/), with error handling so an API outage never breaks the page.

---

## Features

- 👤 Login / logout (Django auth)
- 🎬 Add, edit and delete movies in a personal library
- 🔍 Search TMDB and import a movie with one click (title, overview, year, poster)
- 📌 Status: **Watched** / **To Watch**
- ⭐ Rating 1 to 10
- 🏷️ Tags, many per movie
- 📋 Filter by status, tags and title search
- 🔒 Per-user data isolation, 50 movies per account (demo limit)

---

## Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.13 |
| Framework | Django 6.0 |
| Database | SQLite (demo scale; swap for PostgreSQL via `DATABASES`) |
| Frontend | Django templates, Bootstrap 5, Font Awesome |
| External API | TMDB (via `requests`) |
| Testing | pytest, pytest-django, pytest-cov |
| Deployment | Docker, Docker Compose, Gunicorn, WhiteNoise |

---

## Run it locally

Requires Python 3.13+ and a free [TMDB API key](https://www.themoviedb.org/settings/api).

```bash
git clone https://github.com/Wiktormisch/MyMovies.git
cd MyMovies
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then set SECRET_KEY, TMDB_API_KEY and DEBUG=True
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000 and log in with the superuser you created.

### With Docker

```bash
cp .env.example .env           # fill in SECRET_KEY and TMDB_API_KEY
docker compose up --build
```

The app listens on http://localhost:20165.

---

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

All tests are offline and deterministic. The TMDB client is mocked, so the suite never touches the network.

---

## Project structure

```
MyMovies/
├── Movies/                 # The app: models, views, forms, templates, static files
│   ├── models.py          # Movie, Tag
│   ├── views.py           # Library CRUD, filtering, TMDB search and import
│   └── templates/         # Bootstrap 5 UI
├── MyMovies/              # Django project: settings, urls, wsgi
├── tests/                 # pytest suite (auth, movies, TMDB, secret scan)
├── conftest.py            # Shared fixtures, TMDB mock
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Git workflow

- `main`: what runs on the demo server
- `dev`: integration branch
- `feature/*`: one branch per feature, merged through a pull request

---

## Roadmap

- Registration behind a feature flag (currently off for the demo)
- Password reset by email
- PostgreSQL in production
- Recommendations based on ratings and tags

---

## License

MIT
