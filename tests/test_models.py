"""Testy warstwy modeli: reprezentacje tekstowe, wartości domyślne, ograniczenia."""
import pytest
from django.db import IntegrityError

from Movies.models import Movie, Tag

pytestmark = pytest.mark.django_db


def test_tag_str_zwraca_nazwe():
    assert str(Tag.objects.create(name="horror")) == "horror"


def test_movie_str_zawiera_tytul_i_rok(movie):
    assert str(movie) == "Blade Runner - 1982"


def test_domyslny_status_to_to_watch(user):
    m = Movie.objects.create(title="Diuna", owner=user)
    assert m.status == "to_watch"


def test_pola_opcjonalne_domyslnie_puste(user):
    m = Movie.objects.create(title="Diuna", owner=user)
    assert m.rating is None
    assert m.director is None
    assert m.tags.count() == 0


def test_created_at_ustawiane_automatycznie(movie):
    assert movie.created_at is not None
    assert movie.updated_at is not None


def test_ten_sam_tytul_u_roznych_wlascicieli_jest_dozwolony(user, other_user):
    Movie.objects.create(title="Matrix", owner=user)
    Movie.objects.create(title="Matrix", owner=other_user)

    assert Movie.objects.filter(title="Matrix").count() == 2


def test_duplikat_tytulu_u_tego_samego_wlasciciela_jest_odrzucany(user):
    Movie.objects.create(title="Matrix", owner=user)

    with pytest.raises(IntegrityError):
        Movie.objects.create(title="Matrix", owner=user)


def test_nazwa_taga_jest_unikalna():
    Tag.objects.create(name="sci-fi")

    with pytest.raises(IntegrityError):
        Tag.objects.create(name="sci-fi")
