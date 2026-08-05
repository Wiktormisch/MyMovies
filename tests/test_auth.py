"""Testy dostępu: ochrona loginem, logowanie/wylogowanie, rejestracja."""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

pytestmark = pytest.mark.django_db

# Wszystkie widoki oznaczone @login_required.
CHRONIONE_WIDOKI = [
    ("movie_list", ()),
    ("add_movie", ()),
    ("movie_detail", (1,)),
    ("movie_delete", (1,)),
    ("movie_edit", (1,)),
    ("search", ()),
    ("add_movie_api", (550,)),
]


@pytest.mark.parametrize("nazwa,args", CHRONIONE_WIDOKI)
def test_anonim_jest_przekierowany_na_login(client, nazwa, args):
    url = reverse(nazwa, args=args)

    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith("/login/")
    assert f"next={url}" in response.url


def test_strona_glowna_wymaga_logowania(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response.url.startswith("/login/")


def test_zalogowany_widzi_liste(auth_client):
    response = auth_client.get(reverse("movie_list"))

    assert response.status_code == 200


def test_logowanie_poprawnymi_danymi(client, user, password):
    response = client.post(
        reverse("login"),
        {"username": user.username, "password": password},
    )

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


def test_logowanie_zlym_haslem_nie_udaje_sie(client, user):
    response = client.post(
        reverse("login"),
        {"username": user.username, "password": "zle-haslo"},
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


def test_wylogowanie_przekierowuje_na_login(auth_client):
    # Django >= 5 przyjmuje wylogowanie wyłącznie metodą POST.
    response = auth_client.post(reverse("logout"))

    assert response.status_code == 302
    assert response.url == "/login/"


# --- rejestracja jest celowo wyłączona w wersji demo --------------------

def test_strona_rejestracji_informuje_o_wylaczeniu(client):
    response = client.get(reverse("register"))

    assert response.status_code == 200
    assert response.context["registration_disabled"] is True


def test_post_na_rejestracje_nie_tworzy_konta(client):
    liczba_przed = User.objects.count()

    response = client.post(
        reverse("register"),
        {
            "username": "nowy",
            "password1": "BardzoTrudneHaslo123",
            "password2": "BardzoTrudneHaslo123",
        },
    )

    assert response.status_code == 200
    assert User.objects.count() == liczba_przed
    assert not User.objects.filter(username="nowy").exists()
