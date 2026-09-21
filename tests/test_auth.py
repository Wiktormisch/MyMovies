"""Access control: every view is behind a login, and registration is off."""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

pytestmark = pytest.mark.django_db

# Every view decorated with @login_required.
PROTECTED_VIEWS = [
    ("movie_list", ()),
    ("add_movie", ()),
    ("movie_detail", (1,)),
    ("movie_delete", (1,)),
    ("movie_edit", (1,)),
    ("search", ()),
    ("add_movie_api", (550,)),
]


@pytest.mark.parametrize("name,args", PROTECTED_VIEWS)
def test_anonymous_is_redirected_to_login(client, name, args):
    url = reverse(name, args=args)

    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith("/login/")
    assert f"next={url}" in response.url


def test_login_with_correct_credentials(client, user, password):
    response = client.post(
        reverse("login"),
        {"username": user.username, "password": password},
    )

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


def test_login_with_wrong_password_is_rejected(client, user, password):
    response = client.post(
        reverse("login"),
        {"username": user.username, "password": password + "-wrong"},
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


def test_registration_is_disabled(client, password):
    """The demo advertises registration but must never create an account."""
    page = client.get(reverse("register"))
    assert page.status_code == 200
    assert page.context["registration_disabled"] is True

    response = client.post(
        reverse("register"),
        {
            "username": "newcomer",
            "password1": password,
            "password2": password,
        },
    )

    assert response.status_code == 200
    assert not User.objects.filter(username="newcomer").exists()
