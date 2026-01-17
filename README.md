# TMDb App

Aplikacja webowa do śledzenia i udostępniania postępów w oglądaniu filmów i seriali TV.

## Technologie

- **Backend**: Django 6.0
- **Database**: SQLite
- **Python**: 3.12
- **Dependency Manager**: uv
- **Linter**: Ruff
- **Type Checker**: PyRight
- **API Integration**: The Movie Database (TMDb)

## Architektura

Projekt wykorzystuje czystą architekturę z podziałem na warstwy:

- **Models**: Modele biznesowe reprezentujące obiekty domenowe
- **Services**: Warstwa logiki biznesowej
- **Views**: Warstwa prezentacji (do implementacji)
- **Factories**: Wzorzec Abstract Factory dla obiektów Media

### Aplikacje Django

- `users` - Zarządzanie użytkownikami i autoryzacja
- `lists` - Listy użytkowników z filmami i serialami
- `media` - Filmy, seriale TV i śledzenie oglądanych odcinków
- `profiles` - Profile publiczne użytkowników
- `core` - Wspólne narzędzia i konfiguracja

## Modele Biznesowe

### User
- Niestandardowy model użytkownika rozszerzający Django AbstractUser
- Pola: username, email, nickname, is_2fa_enabled
- Relacje: 1:N z List, 1:N z WatchedEpisode, 1:1 z PublicProfile

### List
- Listy użytkowników (domyślnie prywatne)
- Pola: name, user, is_public
- Relacje: N:1 z User, 1:N z ListItem

### ListItem
- Element listy zawierający media
- Pola: list, media, position
- Relacje: N:1 z List, N:1 z Media

### Media (klasa abstrakcyjna)
- Bazowa klasa dla Movie i TVShow
- Pola: tmdb_id, title, original_title, overview, poster_path, backdrop_path, release_date, popularity, vote_average, vote_count, original_language, media_type

### Movie
- Rozszerza Media
- Dodatkowe pola: runtime, budget, revenue

### TVShow
- Rozszerza Media
- Dodatkowe pola: number_of_seasons, number_of_episodes, episode_run_time, status, first_air_date, last_air_date

### WatchedEpisode
- Śledzenie oglądanych odcinków seriali
- Pola: user, tv_show, season_number, episode_number, watched_at
- Relacje: N:1 z User, N:1 z TVShow

### PublicProfile
- Publiczny profil użytkownika
- Pola: user, bio, avatar_url, is_visible, show_watched_episodes, show_lists
- Relacje: 1:1 z User

## Wzorce Projektowe

### Abstract Factory
Implementacja dla tworzenia obiektów Media:
- `MediaFactory` - abstrakcyjna fabryka
- `MovieFactory` - konkretna fabryka dla filmów
- `TVShowFactory` - konkretna fabryka dla seriali
- `MediaFactoryProvider` - dostawca odpowiedniej fabryki

## Warstwa Serwisów

### UserService
- Rejestracja użytkowników
- Autoryzacja
- Zarządzanie profilem
- Włączanie/wyłączanie 2FA

### ListService
- Tworzenie, aktualizacja, usuwanie list
- Dodawanie/usuwanie mediów z list
- Przenoszenie elementów między listami
- Zmiana kolejności elementów

### MediaService
- Tworzenie obiektów Media z danych TMDb
- Wyszukiwanie mediów
- Aktualizacja metadanych z TMDb
- Integracja z TMDb API

### EpisodeTrackingService
- Oznaczanie odcinków jako obejrzane
- Usuwanie oznaczeń
- Pobieranie historii oglądania
- Obliczanie postępu oglądania serialu

### ProfileService
- Tworzenie i aktualizacja profili publicznych
- Zarządzanie ustawieniami prywatności
- Pobieranie profili po nickname

### TMDbService
- Komunikacja z TMDb API
- Wyszukiwanie filmów i seriali
- Pobieranie szczegółowych informacji
- Obsługa błędów API

## Instalacja

### Wymagania wstępne
- Python 3.12
- uv (dependency manager)

### Kroki instalacji

1. Klonowanie repozytorium:
```bash
cd /home/zim-jan/abc123/imdb_app
```

2. Utworzenie środowiska wirtualnego:
```bash
uv venv
source .venv/bin/activate
```

3. Instalacja zależności:
```bash
uv pip install django requests python-dotenv ruff pyright
```

4. Konfiguracja zmiennych środowiskowych:
```bash
cp .env.example .env
# Edytuj .env i dodaj swój klucz API TMDb
```

5. Migracje bazy danych:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Utworzenie superużytkownika:
```bash
python manage.py createsuperuser
```

7. Uruchomienie serwera deweloperskiego:
```bash
python manage.py runserver
```

## Konfiguracja

### Zmienne środowiskowe (.env)

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

TMDB_API_KEY=your-tmdb-api-key-here
TMDB_BASE_URL=https://api.themoviedb.org/3
```

### TMDb API
Zarejestruj się na [https://www.themoviedb.org/](https://www.themoviedb.org/) i uzyskaj klucz API.

## Deployment

Projekt jest gotowy do wdrożenia w produkcji z Dockerem, Gunicornem i WhiteNoise.

- **Zmienne środowiskowe:**
	- `SECRET_KEY`: klucz aplikacji Django.
	- `DEBUG`: `False` w produkcji.
	- `ALLOWED_HOSTS`: lista hostów rozdzielona przecinkami (np. `example.com,127.0.0.1`).
	- `CSRF_TRUSTED_ORIGINS`: lista originów (np. `https://example.com`).
	- `DATABASE_URL`: opcjonalnie, np. `postgres://user:pass@host:5432/dbname`.

### Heroku (bez Dockera)

1. Utwórz aplikację i bazę Postgres:

```bash
heroku create your-app-name
heroku stack:set heroku-22
heroku addons:create heroku-postgresql:hobby-dev
```

2. Skonfiguruj zmienne środowiskowe:

```bash
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
```

3. Wypchnij kod:

```bash
git push heroku main
```

4. Migracje uruchomią się automatycznie (faza `release`). Jeśli potrzeba ręcznie:

```bash
heroku run python manage.py migrate
```

5. Opcjonalnie:
```bash
heroku config:set DISABLE_COLLECTSTATIC=1  # jeśli budowa statyk sprawia problemy
```

### Docker

Budowa i uruchomienie:

```bash
docker build -t imdb-app .
docker run --env SECRET_KEY=change-me \
	--env DEBUG=False \
	--env ALLOWED_HOSTS=localhost,127.0.0.1 \
	-p 8000:8000 imdb-app
```

Kontener podczas startu wykona migracje i uruchomi aplikację przez Gunicorn na porcie 8000.

### Procfile (Heroku/Fly.io)

Platformy wykorzystujące Procfile mogą użyć dołączonego pliku `Procfile`:

```
web: gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

Upewnij się, że zmienne środowiskowe są ustawione oraz uruchom `python manage.py collectstatic --noinput` w trakcie budowy.

### Pliki statyczne

WhiteNoise serwuje pliki statyczne w produkcji. `collectstatic` wykonywane jest podczas budowania obrazu Dockera.

### Baza danych

Domyślnie używany jest SQLite. Jeśli obecny jest `DATABASE_URL`, konfiguracja aplikowana jest przez `dj-database-url` z włączonym SSL, gdy `DEBUG=False`.

## Jakość kodu

### Linting z Ruff
```bash
ruff check .
ruff check --fix .  # Automatyczna naprawa
```

### Type checking z PyRight
```bash
pyright
```

## Struktura projektu

```
imdb_app/
├── config/              # Konfiguracja Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/               # Aplikacja użytkowników
│   ├── models.py
│   ├── services/
│   │   └── user_service.py
│   └── admin.py
├── lists/               # Aplikacja list
│   ├── models.py
│   ├── services/
│   │   └── list_service.py
│   └── admin.py
├── media/               # Aplikacja mediów
│   ├── models.py
│   ├── factories/
│   │   └── media_factory.py
│   ├── services/
│   │   ├── media_service.py
│   │   ├── episode_tracking_service.py
│   │   └── tmdb_service.py
│   └── admin.py
├── profiles/            # Aplikacja profili
│   ├── models.py
│   ├── services/
│   │   └── profile_service.py
│   └── admin.py
├── core/                # Wspólne narzędzia
├── static/              # Pliki statyczne
├── manage.py
├── pyproject.toml       # Konfiguracja projektu
├── ruff.toml           # Konfiguracja Ruff
├── pyrightconfig.json  # Konfiguracja PyRight
└── .env                # Zmienne środowiskowe
```

## Wymagania Funkcjonalne

1. Rejestracja i logowanie użytkowników
2. Tworzenie i zarządzanie spersonalizowanymi listami
3. Dodawanie tytułów z TMDb lub ręcznie
4. Automatyczne pobieranie metadanych
5. Przenoszenie elementów między listami
6. Oznaczanie odcinków seriali jako obejrzane
7. Listy domyślnie prywatne
8. Udostępnianie profilu publicznego przez `/u/<nickname>`
9. Kontrola prywatności profilu
10. Edycja profilu użytkownika
11. Historia oglądanych odcinków
12. Monitoring dla administratorów
13. Okresowa aktualizacja metadanych

## Wymagania Niefunkcjonalne

- Obsługa 1000 równoczesnych użytkowników
- Czas odpowiedzi ≤ 10 sekund w 95% żądań
- Komunikacja HTTPS
- Szyfrowane hasła
- Opcjonalna 2FA
- Dostępność ≥ 99%
- Skalowalność do 2000 aktywnych użytkowników
- Kompatybilność z nowoczesnymi przeglądarkami

## Standardy Kodu

- **Type hints**: Wszystkie funkcje i metody w pełni typowane
- **Docstrings**: NumPy style dla wszystkich klas i funkcji
- **PEP8**: Zgodność ze standardem Python
- **Linting**: Kod przechodzi testy Ruff
- **Type checking**: Kod przechodzi testy PyRight strict mode
- **Język**: Angielski dla kodu, komentarzy i docstringów

## Licencja

Projekt prywatny.

## Kontakt

Dla pytań i sugestii, skontaktuj się z zespołem deweloperskim.
