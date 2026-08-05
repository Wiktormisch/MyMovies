"""Testy integracji z TMDB - requests jest zawsze mockowany, zero sieci."""
import pytest
from django.urls import reverse

from Movies.models import Movie

pytestmark = [pytest.mark.django_db, pytest.mark.tmdb]

WYNIK_WYSZUKIWANIA = {
    "results": [
        {"id": 78, "title": "Blade Runner", "release_date": "1982-06-25"},
        {"id": 335984, "title": "Blade Runner 2049",
         "release_date": "2017-10-04"},
    ]
}

SZCZEGOLY_FILMU = {
    "title": "Blade Runner",
    "overview": "Rick Deckard tropi replikantów.",
    "release_date": "1982-06-25",
    "poster_path": "/abc123.jpg",
}


# --- wyszukiwanie -------------------------------------------------------

def test_puste_zapytanie_nie_wola_api(auth_client, no_network):
    response = auth_client.get(reverse("search"))

    assert response.status_code == 200
    assert response.context["results"] == []


def test_wyszukiwanie_zwraca_wyniki(auth_client, mock_tmdb):
    calls = mock_tmdb(WYNIK_WYSZUKIWANIA)

    response = auth_client.get(reverse("search"), {"q": "blade"})

    assert response.status_code == 200
    assert len(response.context["results"]) == 2
    assert response.context["query"] == "blade"
    assert calls[0]["params"]["query"] == "blade"


def test_blad_api_nie_wywraca_strony(auth_client, mock_tmdb):
    mock_tmdb({"status_message": "Not found"}, status_code=404)

    response = auth_client.get(reverse("search"), {"q": "blade"})

    assert response.status_code == 200
    assert response.context["results"] == []


# --- dodawanie z API ----------------------------------------------------

def test_dodanie_z_api_tworzy_film(auth_client, mock_tmdb, user):
    mock_tmdb(SZCZEGOLY_FILMU)

    response = auth_client.get(reverse("add_movie_api", args=[78]))

    film = Movie.objects.get(title="Blade Runner")
    assert film.owner == user
    assert film.year == 1982
    assert film.status == "to_watch"
    assert film.poster_path == "/abc123.jpg"
    assert response.url == reverse("movie_detail", args=[film.pk])


def test_ponowne_dodanie_nie_duplikuje(auth_client, mock_tmdb, user):
    mock_tmdb(SZCZEGOLY_FILMU)
    Movie.objects.create(title="Blade Runner", owner=user)

    response = auth_client.get(reverse("add_movie_api", args=[78]))

    assert Movie.objects.filter(title="Blade Runner").count() == 1
    assert response.url == reverse("movie_list")


def test_brak_daty_premiery_daje_rok_zero(auth_client, mock_tmdb):
    mock_tmdb({"title": "Bez daty", "overview": "", "release_date": None})

    auth_client.get(reverse("add_movie_api", args=[999]))

    assert Movie.objects.get(title="Bez daty").year == 0


def test_ten_sam_tytul_u_innego_uzytkownika_jest_dodawany(
    auth_client, other_client, mock_tmdb, user, other_user
):
    mock_tmdb(SZCZEGOLY_FILMU)

    auth_client.get(reverse("add_movie_api", args=[78]))
    other_client.get(reverse("add_movie_api", args=[78]))

    assert Movie.objects.filter(title="Blade Runner").count() == 2
    assert Movie.objects.filter(owner=user).count() == 1
    assert Movie.objects.filter(owner=other_user).count() == 1
