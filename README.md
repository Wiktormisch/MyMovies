# 🎬 MyMovies

MyMovies is a simple web application built with Django that helps users organize, track, and get recommendations for movies they want to watch or have already watched.

The main goal of the project is to eliminate the frustration of endlessly scrolling through streaming platforms and instead provide a personal, structured movie library with smart suggestions.

---

## 🚀 Features (MVP)

- 👤 User authentication (register/login/logout)
- 🎬 Add movies to personal library
- 📌 Mark movies as:
  - Watched
  - To Watch
- ⭐ Rate movies
- 🏷️ Add tags (e.g. "comedy", "action", "relax")
- 📋 Filter movies by status and tags
- 💡 Simple recommendation system based on ratings and tags

---

## 🧠 Future Ideas

- 🎯 Smarter recommendation engine (based on similarity)
- 🎞️ Integration with external movie APIs (e.g. TMDB)
- 📱 Mobile-friendly UI improvements
- 👥 Social features (sharing lists with friends)
- 🎥 Trailer previews inside app

---

## 🏗️ Tech Stack

- Python 3.x
- Django
- SQLite (development)
- HTML / CSS (basic frontend)
- Bootstrap (optional styling)

---

## 🌳 Git Workflow

This project follows a **Feature Branch Workflow**:

## 🐳 Docker deployment

The app is prepared to run in Docker with environment variables from `.env`.

1. Copy `.env.example` to `.env` and set your values.
2. Build the image:
   ```bash
   docker compose build
   ```
3. Run the container:
   ```bash
   docker compose up
   ```
4. Open the app at `http://localhost:8000`.

For production on your VPS, make sure `.env` contains:
- `SECRET_KEY`
- `TMDB_API_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=jack165.mikrus.xyz`
- `CSRF_TRUSTED_ORIGINS=http://jack165.mikrus.xyz:20165`
