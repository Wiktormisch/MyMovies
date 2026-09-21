"""The app speaks one language: English in templates, views, settings and TMDB calls."""
import re
import subprocess
from pathlib import Path

import pytest
from django.urls import reverse

from Movies.models import Movie

ROOT = Path(__file__).resolve().parent.parent
POLISH_LETTERS = re.compile(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]")
# Source files that end up in front of a user or a reviewer.
SOURCE_SUFFIXES = {".py", ".html", ".js", ".css"}


def tracked_source_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    return [
        ROOT / name
        for name in out.decode("utf-8").split("\0")
        if name and Path(name).suffix in SOURCE_SUFFIXES
    ]


def test_no_polish_text_in_tracked_source():
    offenders = []
    for path in tracked_source_files():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if POLISH_LETTERS.search(line):
                offenders.append(f"{path.relative_to(ROOT)}:{lineno}: {line.strip()}")
    assert not offenders, "Polish text found:\n" + "\n".join(offenders)


@pytest.mark.django_db
def test_html_declares_english(auth_client):
    response = auth_client.get(reverse("movie_list"))
    assert b'<html lang="en">' in response.content


@pytest.mark.django_db
def test_movie_limit_message_is_english(auth_client, user):
    for i in range(50):
        Movie.objects.create(title=f"Movie {i}", owner=user)
    response = auth_client.get(reverse("add_movie"))
    assert response.context["error"] == (
        "You have reached the limit of 50 movies. Delete some movies to add new ones."
    )


@pytest.mark.django_db
@pytest.mark.tmdb
def test_tmdb_is_queried_in_english(auth_client, mock_tmdb):
    calls = mock_tmdb({"results": []})
    auth_client.get(reverse("search"), {"q": "blade"})
    assert calls[0]["params"]["language"] == "en-US"
