"""Testy CRUD filmów wraz z kontrolą własności (owner)."""
import pytest
from django.urls import reverse

from Movies.models import Movie

pytestmark = pytest.mark.django_db


def poprawny_formularz(**nadpisania):
    dane = {
        "title": "Incepcja",
        "description": "Sen w śnie",
        "director": "Christopher Nolan",
        "year": 2010,
        "rating": 9,
        "status": "watched",
    }
    dane.update(nadpisania)
    return dane


# --- dodawanie ----------------------------------------------------------

def test_dodanie_filmu_przypisuje_zalogowanego_wlasciciela(auth_client, user):
    response = auth_client.post(reverse("add_movie"), poprawny_formularz())

    assert response.status_code == 302
    film = Movie.objects.get(title="Incepcja")
    assert film.owner == user
    assert film.year == 2010


def test_formularz_bez_tytulu_nie_tworzy_filmu(auth_client):
    response = auth_client.post(
        reverse("add_movie"), poprawny_formularz(title="")
    )

    assert response.status_code == 200
    assert Movie.objects.count() == 0


def test_limit_50_filmow_blokuje_dodawanie(auth_client, user):
    Movie.objects.bulk_create(
        Movie(title=f"Film {i}", owner=user) for i in range(50)
    )

    response = auth_client.get(reverse("add_movie"))

    assert response.status_code == 200
    assert "limit 50" in response.context["error"]


def test_ponizej_limitu_dodawanie_dziala(auth_client, user):
    Movie.objects.bulk_create(
        Movie(title=f"Film {i}", owner=user) for i in range(49)
    )

    response = auth_client.get(reverse("add_movie"))

    assert response.status_code == 200
    assert "error" not in response.context


# --- szczegóły ----------------------------------------------------------

def test_wlasciciel_widzi_szczegoly(auth_client, movie):
    response = auth_client.get(reverse("movie_detail", args=[movie.pk]))

    assert response.status_code == 200
    assert response.context["movie"] == movie


def test_obcy_uzytkownik_nie_widzi_szczegolow(other_client, movie):
    response = other_client.get(reverse("movie_detail", args=[movie.pk]))

    assert response.status_code == 302
    assert response.url == reverse("movie_list")


def test_nieistniejacy_film_zwraca_404(auth_client):
    response = auth_client.get(reverse("movie_detail", args=[99999]))

    assert response.status_code == 404


# --- edycja -------------------------------------------------------------

def test_wlasciciel_moze_edytowac(auth_client, movie):
    response = auth_client.post(
        reverse("movie_edit", args=[movie.pk]),
        poprawny_formularz(title="Blade Runner 2049", year=2017),
    )

    assert response.status_code == 302
    movie.refresh_from_db()
    assert movie.title == "Blade Runner 2049"
    assert movie.year == 2017


def test_obcy_uzytkownik_nie_moze_edytowac(other_client, movie):
    response = other_client.post(
        reverse("movie_edit", args=[movie.pk]),
        poprawny_formularz(title="Przejęte"),
    )

    assert response.status_code == 302
    movie.refresh_from_db()
    assert movie.title == "Blade Runner"


# --- usuwanie -----------------------------------------------------------

def test_post_usuwa_film(auth_client, movie):
    response = auth_client.post(reverse("movie_delete", args=[movie.pk]))

    assert response.status_code == 302
    assert not Movie.objects.filter(pk=movie.pk).exists()


def test_get_nie_usuwa_filmu(auth_client, movie):
    """Usuwanie musi wymagać POST - GET tylko przekierowuje na szczegóły."""
    response = auth_client.get(reverse("movie_delete", args=[movie.pk]))

    assert response.status_code == 302
    assert Movie.objects.filter(pk=movie.pk).exists()


def test_obcy_uzytkownik_nie_moze_usunac(other_client, movie):
    response = other_client.post(reverse("movie_delete", args=[movie.pk]))

    assert response.status_code == 302
    assert Movie.objects.filter(pk=movie.pk).exists()
