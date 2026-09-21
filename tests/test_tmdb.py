"""TMDB integration. requests is always mocked, so no test touches the network."""
import pytest
from django.urls import reverse

from Movies.models import Movie

pytestmark = [pytest.mark.django_db, pytest.mark.tmdb]

SEARCH_RESULT = {
    "results": [
        {"id": 78, "title": "Blade Runner", "release_date": "1982-06-25"},
        {"id": 335984, "title": "Blade Runner 2049",
         "release_date": "2017-10-04"},
    ]
}

MOVIE_DETAILS = {
    "title": "Blade Runner",
    "overview": "Rick Deckard hunts replicants.",
    "release_date": "1982-06-25",
    "poster_path": "/abc123.jpg",
}


def test_an_empty_query_does_not_call_the_api(auth_client, no_network):
    response = auth_client.get(reverse("search"))

    assert response.status_code == 200
    assert response.context["results"] == []


def test_search_passes_the_query_through_and_returns_results(
    auth_client, mock_tmdb
):
    calls = mock_tmdb(SEARCH_RESULT)

    response = auth_client.get(reverse("search"), {"q": "blade"})

    assert response.status_code == 200
    assert len(response.context["results"]) == 2
    assert calls[0]["params"]["query"] == "blade"


def test_an_api_error_does_not_break_the_page(auth_client, mock_tmdb):
    mock_tmdb({"status_message": "Not found"}, status_code=404)

    response = auth_client.get(reverse("search"), {"q": "blade"})

    assert response.status_code == 200
    assert response.context["results"] == []


def test_adding_from_the_api_creates_the_movie(auth_client, mock_tmdb, user):
    mock_tmdb(MOVIE_DETAILS)

    response = auth_client.get(reverse("add_movie_api", args=[78]))

    created = Movie.objects.get(title="Blade Runner")
    assert created.owner == user
    assert created.year == 1982
    assert created.poster_path == "/abc123.jpg"
    assert response.url == reverse("movie_detail", args=[created.pk])


def test_adding_the_same_film_twice_does_not_duplicate_it(
    auth_client, mock_tmdb, user
):
    mock_tmdb(MOVIE_DETAILS)
    Movie.objects.create(title="Blade Runner", owner=user)

    response = auth_client.get(reverse("add_movie_api", args=[78]))

    assert Movie.objects.filter(title="Blade Runner").count() == 1
    assert response.url == reverse("movie_list")
