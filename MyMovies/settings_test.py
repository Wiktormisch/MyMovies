"""Settings used by the test suite only.

Imports the real settings and overrides what has to be deterministic and fast
under test, so that the suite:
  * never touches the real db.sqlite3 (the database is in memory),
  * does not depend on a .env file being present (SECRET_KEY / TMDB_API_KEY
    are fixed here),
  * never calls the real TMDB API (the key is a dummy, and requests is mocked
    anyway).
"""
from .settings import *  # noqa: F401,F403

SECRET_KEY = "test-secret-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# The default hasher (PBKDF2) is deliberately slow; in tests that is dead cost.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# A dummy: no test should ever reach the network.
TMDB_API_KEY = "test-api-key"
