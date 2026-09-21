"""Security gate: the repository contains no credentials.

This guards a regression that already happened. `.env.production`, holding a
live SECRET_KEY and TMDB_API_KEY, was committed to a public repo. A plain grep
never surfaced it because the file was saved as UTF-16, so the scanner below
decodes every encoding rather than assuming UTF-8.

Deterministic, local, offline.
"""
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# The only .env file allowed to be tracked.
TEMPLATE = ".env.example"

SENSITIVE_KEYS = ("SECRET_KEY", "TMDB_API_KEY", "API_KEY", "TOKEN", "PASSWORD")

# Values that are obviously stand-ins rather than secrets. The empty case is
# anchored with $: an unanchored empty alternative matches every string and
# would silently turn this whole check into a no-op.
PLACEHOLDER = re.compile(
    r"^(?:$|\"\"$|''$|your_|test[-_]|example|placeholder|dummy|xxx"
    r"|change[-_]this|django-insecure-change)",
    re.IGNORECASE,
)

# A key assigned a value, in a .env file or in Python. [ \t] rather than \s:
# \s swallows the newline, so an empty value would absorb the following line.
ASSIGNMENT = re.compile(
    r"^[ \t]*(?P<key>[A-Z0-9_]*(?:%s))[ \t]*[=:][ \t]*(?P<value>.*)$"
    % "|".join(SENSITIVE_KEYS),
    re.MULTILINE,
)

SIGNATURES = (
    ("TMDB key (32 hex chars)", re.compile(r"\b[0-9a-f]{32}\b")),
    ("generated Django key", re.compile(r"django-insecure-(?!change)[!-~]{20,}")),
)

# Migrations and static files carry hashes; this file necessarily contains the
# patterns themselves.
SKIP = re.compile(r"(^|/)(migrations|staticfiles|\.git)/|test_no_secrets\.py$")


def _read(path: Path) -> str:
    """Decode whatever the encoding is. UTF-16 is how the last leak hid."""
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


@pytest.fixture(scope="module")
def tracked() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True,
    )
    return [p for p in result.stdout.decode("utf-8").split("\0") if p]


def test_only_the_template_env_file_is_tracked(tracked):
    leaked = [
        p for p in tracked
        if Path(p).name.startswith(".env") and p != TEMPLATE
    ]
    assert leaked == [], (
        f"env files with secrets are tracked: {leaked}. "
        "Remove them with: git rm --cached <file>"
    )


@pytest.mark.parametrize(
    "variant", [".env", ".env.production", ".env.local"]
)
def test_gitignore_covers_every_env_variant(variant):
    result = subprocess.run(
        ["git", "check-ignore", "-q", variant], cwd=REPO, capture_output=True,
    )
    assert result.returncode == 0, f"{variant} is not ignored by .gitignore"


def test_the_template_holds_names_but_no_values():
    content = _read(REPO / TEMPLATE)
    filled = [
        (m.group("key"), m.group("value"))
        for m in ASSIGNMENT.finditer(content)
        if not PLACEHOLDER.match(m.group("value").strip().strip("\"'"))
    ]
    assert filled == [], f"{TEMPLATE} contains values: {filled}"


def test_no_tracked_file_contains_a_credential(tracked):
    """Scans every tracked file for both secret signatures and assignments."""
    hits = []
    for relative in tracked:
        if SKIP.search(relative) or not (REPO / relative).is_file():
            continue
        content = _read(REPO / relative)

        for label, pattern in SIGNATURES:
            for match in pattern.finditer(content):
                line = content.count("\n", 0, match.start()) + 1
                hits.append(f"{relative}:{line} -> {label}")

        for m in ASSIGNMENT.finditer(content):
            value = m.group("value").strip().rstrip(",").strip("\"'")
            # Reading from the environment is the correct pattern, not a leak.
            if value.startswith(("os.getenv", "os.environ", "env_", "settings.",
                                 "secrets.", "TEST_PASSWORD")):
                continue
            if PLACEHOLDER.match(value):
                continue
            line = content.count("\n", 0, m.start()) + 1
            hits.append(f"{relative}:{line} -> {m.group('key')}={value!r}")

    assert hits == [], "credentials found in tracked files:\n" + "\n".join(hits)
