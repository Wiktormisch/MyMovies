"""Movies: model rules, CRUD, ownership isolation and list filtering."""
import pytest
from django.db import IntegrityError
from django.urls import reverse

from Movies.models import Movie, Tag

pytestmark = pytest.mark.django_db


def form(**overrides):
    data = {
        "title": "Inception",
        "description": "A dream within a dream",
        "director": "Christopher Nolan",
        "year": 2010,
        "rating": 9,
        "status": "watched",
    }
    data.update(overrides)
    return data


def titles(response):
    return sorted(m.title for m in response.context["movies"])


# --- model rules --------------------------------------------------------

def test_str_shows_title_and_year(movie):
    assert str(movie) == "Blade Runner - 1982"


def test_new_movie_defaults_to_unwatched_and_unrated(user):
    m = Movie.objects.create(title="Dune", owner=user)

    assert m.status == "to_watch"
    assert m.rating is None
    assert m.director is None
    assert m.tags.count() == 0


def test_titles_are_unique_per_owner_not_globally(user, other_user):
    """Two people may both track Matrix; one person may not track it twice."""
    Movie.objects.create(title="Matrix", owner=user)
    Movie.objects.create(title="Matrix", owner=other_user)

    assert Movie.objects.filter(title="Matrix").count() == 2

    with pytest.raises(IntegrityError):
        Movie.objects.create(title="Matrix", owner=user)


# --- creating -----------------------------------------------------------

def test_adding_a_movie_assigns_the_logged_in_owner(auth_client, user):
    response = auth_client.post(reverse("add_movie"), form())

    assert response.status_code == 302
    created = Movie.objects.get(title="Inception")
    assert created.owner == user
    assert created.year == 2010


def test_a_movie_without_a_title_is_not_created(auth_client):
    response = auth_client.post(reverse("add_movie"), form(title=""))

    assert response.status_code == 200
    assert Movie.objects.count() == 0


@pytest.mark.parametrize(
    "existing,blocked", [(49, False), (50, True)],
    ids=["under-the-limit", "at-the-limit"],
)
def test_the_fifty_movie_limit_blocks_adding(auth_client, user, existing, blocked):
    Movie.objects.bulk_create(
        Movie(title=f"Movie {i}", owner=user) for i in range(existing)
    )

    response = auth_client.get(reverse("add_movie"))

    assert response.status_code == 200
    assert ("error" in response.context) is blocked


# --- ownership ----------------------------------------------------------

def test_the_owner_can_view_and_edit_their_movie(auth_client, movie):
    assert auth_client.get(
        reverse("movie_detail", args=[movie.pk])
    ).context["movie"] == movie

    response = auth_client.post(
        reverse("movie_edit", args=[movie.pk]),
        form(title="Blade Runner 2049", year=2017),
    )

    assert response.status_code == 302
    movie.refresh_from_db()
    assert movie.title == "Blade Runner 2049"
    assert movie.year == 2017


@pytest.mark.parametrize(
    "view,method", [
        ("movie_detail", "get"),
        ("movie_edit", "post"),
        ("movie_delete", "post"),
    ],
)
def test_a_stranger_cannot_reach_someone_elses_movie(
    other_client, movie, view, method
):
    """The one property that actually matters: accounts are sealed off."""
    response = getattr(other_client, method)(
        reverse(view, args=[movie.pk]), form(title="Hijacked")
    )

    assert response.status_code == 302
    movie.refresh_from_db()
    assert movie.title == "Blade Runner"
    assert Movie.objects.filter(pk=movie.pk).exists()


# --- deleting -----------------------------------------------------------

def test_deleting_requires_post(auth_client, movie):
    assert auth_client.get(
        reverse("movie_delete", args=[movie.pk])
    ).status_code == 302
    assert Movie.objects.filter(pk=movie.pk).exists()

    auth_client.post(reverse("movie_delete", args=[movie.pk]))

    assert not Movie.objects.filter(pk=movie.pk).exists()


# --- the list -----------------------------------------------------------

def test_the_list_shows_only_your_own_movies(
    auth_client, make_movie, user, other_user
):
    make_movie(user, title="Mine")
    make_movie(other_user, title="Theirs")

    response = auth_client.get(reverse("movie_list"))

    assert titles(response) == ["Mine"]


def test_the_list_filters_by_status(auth_client, make_movie, user):
    make_movie(user, title="Seen", status="watched")
    make_movie(user, title="Queued", status="to_watch")

    response = auth_client.get(reverse("movie_list"), {"status": "watched"})

    assert titles(response) == ["Seen"]


def test_search_matches_a_fragment_ignoring_case(auth_client, make_movie, user):
    make_movie(user, title="Blade Runner")
    make_movie(user, title="Dune")

    response = auth_client.get(reverse("movie_list"), {"search": "blade"})

    assert titles(response) == ["Blade Runner"]


def test_filtering_by_two_tags_does_not_duplicate_a_movie(
    auth_client, make_movie, user
):
    """A join across two matching tags would otherwise return the row twice."""
    tagged = make_movie(user, title="Blade Runner")
    tagged.tags.add(Tag.objects.create(name="sci-fi"))
    tagged.tags.add(Tag.objects.create(name="noir"))
    make_movie(user, title="Dune")

    response = auth_client.get(
        reverse("movie_list"), {"tag": ["sci-fi", "noir"]}
    )

    assert len(response.context["movies"]) == 1


def test_the_tag_sidebar_does_not_leak_other_peoples_tags(
    auth_client, make_movie, user, other_user
):
    make_movie(user, title="Mine").tags.add(Tag.objects.create(name="my-tag"))
    make_movie(other_user, title="Theirs").tags.add(
        Tag.objects.create(name="their-tag")
    )

    response = auth_client.get(reverse("movie_list"))

    # str() rather than .name: that is what the template actually renders.
    assert [str(t) for t in response.context["tags"]] == ["my-tag"]
