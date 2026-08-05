"""Wspólne fixture'y dla całego zestawu testów."""
import pytest
import requests
from django.contrib.auth.models import User
from django.test import Client

from Movies.models import Movie, Tag

PASSWORD = "test-pass-123"


# --- użytkownicy i klienci HTTP ----------------------------------------

@pytest.fixture
def password():
    return PASSWORD


@pytest.fixture
def user(db):
    """Właściciel filmów - główny bohater większości testów."""
    return User.objects.create_user(username="owner", password=PASSWORD)


@pytest.fixture
def other_user(db):
    """Inny użytkownik - do sprawdzania izolacji danych między kontami."""
    return User.objects.create_user(username="intruder", password=PASSWORD)


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def other_client(other_user):
    c = Client()
    c.force_login(other_user)
    return c


# --- dane domenowe ------------------------------------------------------

@pytest.fixture
def tag(db):
    return Tag.objects.create(name="sci-fi")


@pytest.fixture
def movie(user):
    return Movie.objects.create(
        title="Blade Runner",
        year=1982,
        status="to_watch",
        owner=user,
    )


@pytest.fixture
def make_movie(db):
    """Fabryka filmów: make_movie(user, title="X", status="watched")."""
    counter = {"n": 0}

    def _make(owner, **kwargs):
        counter["n"] += 1
        kwargs.setdefault("title", f"Film {counter['n']}")
        kwargs.setdefault("status", "to_watch")
        return Movie.objects.create(owner=owner, **kwargs)

    return _make


# --- mockowanie TMDB ----------------------------------------------------

class FakeResponse:
    """Minimalny odpowiednik requests.Response na potrzeby testów."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


@pytest.fixture
def mock_tmdb(monkeypatch):
    """Podmienia requests.get w Movies.views i zapisuje wykonane wywołania.

    Użycie:
        calls = mock_tmdb({"results": [...]})
        ...
        assert len(calls) == 1
    """
    def _install(payload, status_code=200):
        calls = []

        def fake_get(url, params=None, **kwargs):
            calls.append({"url": url, "params": params})
            return FakeResponse(payload, status_code)

        monkeypatch.setattr("Movies.views.requests.get", fake_get)
        return calls

    return _install


@pytest.fixture
def no_network(monkeypatch):
    """Wysadza test, jeśli kod mimo wszystko spróbuje wyjść do sieci."""
    def boom(*args, **kwargs):
        raise AssertionError("Test próbował wykonać prawdziwe żądanie HTTP")

    monkeypatch.setattr("Movies.views.requests.get", boom)
