"""Shared fixtures for the test suite."""
import secrets

import pytest
import requests
from django.contrib.auth.models import User
from django.test import Client

from Movies.models import Movie, Tag

# Generated per run rather than hardcoded. A literal password here is a real
# credential as far as any secret scanner is concerned, and this one has no
# reason to be stable across runs.
TEST_PASSWORD = secrets.token_urlsafe(16)


# --- users and HTTP clients ---------------------------------------------

@pytest.fixture
def password():
    return TEST_PASSWORD


@pytest.fixture
def user(db):
    """Owner of the movies, the subject of most tests."""
    return User.objects.create_user(username="owner", password=TEST_PASSWORD)


@pytest.fixture
def other_user(db):
    """A second account, used to prove data is isolated per owner."""
    return User.objects.create_user(username="intruder", password=TEST_PASSWORD)


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def other_client(other_user):
    c = Client()
    c.force_login(other_user)
    return c


# --- domain data --------------------------------------------------------

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
    """Movie factory: make_movie(user, title="X", status="watched")."""
    counter = {"n": 0}

    def _make(owner, **kwargs):
        counter["n"] += 1
        kwargs.setdefault("title", f"Movie {counter['n']}")
        kwargs.setdefault("status", "to_watch")
        return Movie.objects.create(owner=owner, **kwargs)

    return _make


# --- TMDB mocking -------------------------------------------------------

class FakeResponse:
    """Minimal stand-in for requests.Response."""

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
    """Replace requests.get in Movies.views and record the calls made.

    Usage:
        calls = mock_tmdb({"results": [...]})
        ...
        assert calls[0]["params"]["query"] == "blade"
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
    """Fail the test if the code tries to reach the network anyway."""
    def boom(*args, **kwargs):
        raise AssertionError("the test attempted a real HTTP request")

    monkeypatch.setattr("Movies.views.requests.get", boom)
