# 🎬 MyMovies

MyMovies is a simple web application built with Django that helps users organize and track.

The main goal of the project is to eliminate the frustration of endlessly scrolling through streaming platforms and instead provide a personal, structured movie library.

---

## 🌐 Live Demo

**Try the application now:** [MyMovies Demo](http://jack165.mikrus.xyz:20165/)

> **Demo Account**
> - Username: `demo`
> - Password: `demo1`
> - Note: This is a demo version with limited functionality. Registration is disabled.

---

## 🚀 Features

- 👤 User authentication (login/logout)
- 🎬 Add movies to personal library
- 📌 Mark movies as:
  - Watched
  - To Watch
- ⭐ Rate movies (1-10 scale)
- 🏷️ Add and organize movies with tags
- 📋 Filter movies by status and tags
- 🔍 Search movies using TMDB API
- 📊 Personal movie statistics and collection management

---

## 🏗️ Tech Stack

### Backend
- **Python 3.14** - Programming language
- **Django 6.0.4** - Web framework
- **SQLite 3** - Database (can be upgraded to PostgreSQL for production)
- **Gunicorn 21.2.0** - WSGI application server
- **WhiteNoise 6.5.0** - Static files serving

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling
- **Bootstrap 5** - UI framework (via django-bootstrap5 26.2)
- **JavaScript** - Client-side interactivity

### APIs & Libraries
- **TMDB API** - Movie data and search
- **Requests 2.33.1** - HTTP library
- **Django REST Framework 3.17.1** - REST API toolkit
- **python-dotenv 1.2.2** - Environment variables management

### Deployment & DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Git** - Version control

---

## 🎯 Key Features Implementation

### Security
- User authentication with Django's built-in system
- CSRF protection enabled
- Secure session handling
- Environment variables for sensitive data

### Performance
- WhiteNoise middleware for efficient static file serving
- Compressed static files in production
- Optimized database queries with Django ORM
- Connection pooling support

### Scalability
- Movie limit (50 per user) to prevent abuse
- User-based data isolation
- Ready for PostgreSQL upgrade
- Docker-based deployment for easy scaling

---

## 🌳 Git Workflow

This project follows a **Feature Branch Workflow**:
- `main` - Production-ready code
- `dev` - Development branch
- Feature branches for new features

---

## 🐳 Docker Deployment

The app is production-ready and containerized for easy deployment.

### Local Development
1. Copy `.env.example` to `.env` (will use local defaults)
2. Build the image:
   ```bash
   docker compose build
   ```
3. Run the container:
   ```bash
   docker compose up
   ```
4. Open the app at `http://localhost:8000`

### Production on VPS
1. Upload your project files to the VPS
2. Copy `.env.production` to `.env` on the server
3. Configure your environment:
   ```bash
   cp .env.production .env
   ```
4. Build and start:
   ```bash
   docker compose build
   docker compose up -d
   ```
5. Access the app at `http://jack165.mikrus.xyz:20165`

### Environment Variables
- `SECRET_KEY` - Django secret key for cryptographic operations
- `TMDB_API_KEY` - API key for TMDB movie data
- `DEBUG` - Django debug mode (False for production)
- `ALLOWED_HOSTS` - Comma-separated allowed hostnames
- `CSRF_TRUSTED_ORIGINS` - CSRF-trusted origins

### Limits & Constraints
- Maximum 50 movies per user
- Registration is disabled for demo purposes
- SQLite database (suitable for demo; upgrade to PostgreSQL for production)

---

## 🚀 Running Locally (Without Docker)

### Prerequisites
- Python 3.14+
- pip

### Setup
1. Create and activate virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with DEBUG=True for local development
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Start development server:
   ```bash
   python manage.py runserver
   ```

---

## 📦 Project Structure

```
MyMovies/
├── Movies/                 # Main app
│   ├── models.py          # Movie, Tag models
│   ├── views.py           # Request handlers
│   ├── forms.py           # Django forms
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JavaScript
│   └── migrations/        # Database migrations
├── MyMovies/              # Project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI application
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
└── manage.py              # Django management
```

---

## 📝 License

This project is open source. Feel free to use, modify, and distribute as needed.

---

## 👨‍💻 Author

Created by **Wiktor**

---

**Happy Movie Tracking!** 🎬🍿

