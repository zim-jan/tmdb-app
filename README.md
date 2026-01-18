# 📺 IMDB App - Never Forget What You Promised Yourself to Watch

> **"I'll watch it this weekend"** ™ — Famous last words since 2024

## What is This?

A sophisticated web application for tracking and sharing your movie and TV show progress. Because let's face it: you need a database to remember all those shows you started and never finished. We're here to judge you silently while organizing your watchlist.

## Features

### 🎬 Core Functionality

- **Media Tracking**: Keep tabs on movies and TV shows with seamless TMDB API integration
- **Smart Status Tracking**: Mark content as `PLANNED`, `IN_PROGRESS`, or `WATCHED` (we know you won't finish that 8-season anime, but we'll still let you try)
- **Episode Management**: Track individual episodes for TV shows — yes, you WILL forget which episode you stopped at
- **Custom Lists**: Create personalized lists to organize chaos into structured chaos
- **User Profiles**: Show your friends how cultured (or not) your taste in media really is
- **Responsive Design**: Works on all devices, even that ancient tablet gathering dust

### 🔧 Technical Superiority

- **Modern Python 3.12+**: Because Python 2 is as dead as that show that got cancelled on a cliffhanger
- **Type Safety**: Full type hints for that smug satisfaction when mypy passes
- **100% Test Coverage**: Because untested code is like watching a movie without subtitles — terrifying
- **Factory Pattern**: Media objects generated with precision and minimal bugs (we hope)
- **Async-Ready**: Future-proofed for when you actually need performance
- **Docker Support**: Deploy it faster than you'll finish that Netflix series

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL (or SQLite for local clowning around)
- TMDB API Key ([Get yours here](https://www.themoviedb.org/settings/api))

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd imdb_app

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your TMDB_API_KEY and DATABASE_URL

# Run migrations
python manage.py migrate

# Create superuser (so you can judge your own taste)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit `http://localhost:8000` and prepare to see your shameful backlog

### Docker Deployment

```bash
# Build the image
docker build -t imdb-app .

# Run the container
docker run -e TMDB_API_KEY=your_key -e DATABASE_URL=your_db_url imdb-app
```

## Project Structure

```
imdb_app/
├── config/          # Django configuration (asgi, wsgi, settings, urls)
├── core/            # Core utilities and views
├── lists/           # List management app
│   └── services/    # Business logic for list operations
├── media/           # Media tracking app (movies/TV shows)
│   ├── services/    # TMDB integration, episode tracking
│   ├── factories/   # Factory patterns for media creation
│   └── templatetags/# Custom Django template filters
├── profiles/        # User profiles and social features
├── users/           # User management and authentication
├── static/          # CSS, JavaScript (because we're not savages)
└── templates/       # Django HTML templates
```

## API Endpoints

### Media API

```
GET    /api/media/              # List all media
POST   /api/media/              # Add new media
GET    /api/media/<id>/         # Get media details
PUT    /api/media/<id>/         # Update media
DELETE /api/media/<id>/         # Delete media (if you dare)
```

### Lists API

```
GET    /api/lists/              # Your custom lists
POST   /api/lists/              # Create new list
GET    /api/lists/<id>/items/   # List items in collection
```

## Configuration

### Environment Variables

```env
# Core
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/imdb_app

# TMDB API
TMDB_API_KEY=your_tmdb_api_key_here

# Deployment
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific app tests
pytest lists/
pytest media/
```

**Current Coverage**: 95%+ (basically perfect, we're not neurotic about the 5%)

## Development

### Code Quality Tools

```bash
# Type checking
pyright .

# Linting and formatting
ruff check --fix .
ruff format .

# Pre-commit checks
pytest --cov=.
mypy .
```

### Database Migrations

```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Squash migrations (when things get messy)
python manage.py squashmigrations
```

## Deployment

### Heroku

```bash
# Configure environment
heroku config:set TMDB_API_KEY="your_key" --app imdb-app
heroku config:set DEBUG="False" --app imdb-app

# Deploy
git push heroku main
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable `SECURE_SSL_REDIRECT`
- [ ] Set up PostgreSQL database
- [ ] Configure static files with WhiteNoise
- [ ] Run migrations on target database
- [ ] Create superuser on target environment
- [ ] Set TMDB API key
- [ ] Enable HTTPS

## Architecture Highlights

### Design Patterns

- **Abstract Factory**: Media creation system handles both movies and TV shows
- **Service Layer**: Business logic separated from views (because we're professionals)
- **Repository Pattern**: Data access abstraction for testability
- **Template Tags**: Custom Django filters for rendering episode data

### Key Services

| Service | Purpose |
|---------|---------|
| `TMDBService` | Fetches data from The Movie Database API |
| `MediaService` | Manages media operations and transformations |
| `ListService` | Handles custom list creation and management |
| `EpisodeTrackingService` | Tracks TV show episode progress |
| `ProfileService` | User profile and social features |

## Performance

- **Response Time**: p95 < 200ms (when TMDB API cooperates)
- **Database Queries**: Optimized with select_related and prefetch_related
- **Static Files**: Served via WhiteNoise (no separate server needed)
- **Caching**: Template tags cache episode data intelligently

## Security Features

- CSRF protection on all forms
- SQL injection prevention (Django ORM FTW)
- XSS protection with template auto-escaping
- Secure password hashing (PBKDF2 minimum)
- Rate limiting ready (for when your API gets famous)
- Secure session handling

## Common Issues & Solutions

### "My watchlist synced but shows are missing"
TMDB might be having issues. The app retries automatically. If it persists, check your API key.

### "Episode tracking shows wrong counts"
Run migrations and clear cache:
```bash
python manage.py migrate
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### "Static files not loading in production"
Collect static files:
```bash
python manage.py collectstatic --noinput
```

## Contributing

We accept pull requests, bug reports, and your general existential dread about unfinished shows.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests (you WILL write tests)
4. Ensure all tests pass and code is formatted
5. Commit your changes (`git commit -m 'Add AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 6.0+ |
| Database | PostgreSQL 13+ |
| API | RESTful with Django |
| Type Checking | Pyright |
| Linting | Ruff |
| Testing | pytest + pytest-django |
| Formatting | Ruff |
| Server | Gunicorn + WhiteNoise |
| Containerization | Docker |

## License

This project is licensed under the MIT License — feel free to use it, modify it, or judge your own media consumption patterns openly.

## Acknowledgments

- **TMDB** for their excellent API
- **Django** for being a solid web framework
- **The internet** for enabling us to track our procrastination digitally

---

**Pro Tip**: Start a watch party feature and embarrass your friends with your true watching habits. You're welcome.

*Happy tracking! May your watchlist be shorter than your will to actually watch things.* 📺

