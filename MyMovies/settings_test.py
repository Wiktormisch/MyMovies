"""Ustawienia używane wyłącznie przez testy.

Importuje produkcyjne settings i nadpisuje to, co w testach musi być
deterministyczne i szybkie. Dzięki temu testy:
  * nie dotykają prawdziwego db.sqlite3 (baza w pamięci),
  * nie zależą od obecności pliku .env (SECRET_KEY / TMDB_API_KEY na sztywno),
  * nie wołają prawdziwego API TMDB (klucz jest atrapą, a requests i tak mockujemy).
"""
from .settings import *  # noqa: F401,F403

SECRET_KEY = "test-secret-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Domyślny hasher (PBKDF2) celowo spowalnia logowanie - w testach to zbędny koszt.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Atrapa - żaden test nie powinien wyjść do sieci.
TMDB_API_KEY = "test-api-key"
