"""Testy listy filmów: izolacja właścicieli i filtry (status, szukajka, tagi)."""
import pytest
from django.urls import reverse

from Movies.models import Tag

pytestmark = pytest.mark.django_db


def tytuly(response):
    return sorted(m.title for m in response.context["movies"])


def test_widac_tylko_wlasne_filmy(auth_client, make_movie, user, other_user):
    make_movie(user, title="Moj film")
    make_movie(other_user, title="Cudzy film")

    response = auth_client.get(reverse("movie_list"))

    assert tytuly(response) == ["Moj film"]


def test_filtr_po_statusie(auth_client, make_movie, user):
    make_movie(user, title="Obejrzany", status="watched")
    make_movie(user, title="Do obejrzenia", status="to_watch")

    response = auth_client.get(reverse("movie_list"), {"status": "watched"})

    assert tytuly(response) == ["Obejrzany"]


def test_brak_filtra_zwraca_wszystko(auth_client, make_movie, user):
    make_movie(user, title="Obejrzany", status="watched")
    make_movie(user, title="Do obejrzenia", status="to_watch")

    response = auth_client.get(reverse("movie_list"))

    assert tytuly(response) == ["Do obejrzenia", "Obejrzany"]


def test_szukajka_ignoruje_wielkosc_liter(auth_client, make_movie, user):
    make_movie(user, title="Blade Runner")
    make_movie(user, title="Diuna")

    response = auth_client.get(reverse("movie_list"), {"search": "blade"})

    assert tytuly(response) == ["Blade Runner"]


def test_szukajka_dopasowuje_fragment(auth_client, make_movie, user):
    make_movie(user, title="Blade Runner")

    response = auth_client.get(reverse("movie_list"), {"search": "Runn"})

    assert tytuly(response) == ["Blade Runner"]


def test_puste_szukanie_nie_filtruje(auth_client, make_movie, user):
    make_movie(user, title="Blade Runner")

    response = auth_client.get(reverse("movie_list"), {"search": "   "})

    assert tytuly(response) == ["Blade Runner"]


def test_filtr_po_tagu(auth_client, make_movie, user):
    sci_fi = Tag.objects.create(name="sci-fi")
    film = make_movie(user, title="Blade Runner")
    film.tags.add(sci_fi)
    make_movie(user, title="Diuna")

    response = auth_client.get(reverse("movie_list"), {"tag": ["sci-fi"]})

    assert tytuly(response) == ["Blade Runner"]


def test_lista_tagow_zawiera_tylko_tagi_wlasnych_filmow(
    auth_client, make_movie, user, other_user
):
    moj = Tag.objects.create(name="moj-tag")
    cudzy = Tag.objects.create(name="cudzy-tag")
    make_movie(user, title="Moj").tags.add(moj)
    make_movie(other_user, title="Cudzy").tags.add(cudzy)

    response = auth_client.get(reverse("movie_list"))

    assert [t.name for t in response.context["tags"]] == ["moj-tag"]


def test_film_z_dwoma_pasujacymi_tagami_nie_duplikuje_sie(
    auth_client, make_movie, user
):
    film = make_movie(user, title="Blade Runner")
    film.tags.add(Tag.objects.create(name="sci-fi"))
    film.tags.add(Tag.objects.create(name="noir"))

    response = auth_client.get(
        reverse("movie_list"), {"tag": ["sci-fi", "noir"]}
    )

    assert len(response.context["movies"]) == 1
