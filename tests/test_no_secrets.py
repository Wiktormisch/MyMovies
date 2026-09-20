"""Bramka bezpieczeństwa: w repozytorium nie ma sekretów.

Testy pilnują regresji, która już się wydarzyła: plik `.env.production`
z prawdziwym SECRET_KEY i TMDB_API_KEY trafił na publicznego GitHuba.
Zwykły `grep` go nie znalazł, bo plik był zapisany w UTF-16 - dlatego
skaner poniżej dekoduje każdy wariant kodowania, a nie tylko UTF-8.

Testy są deterministyczne, lokalne i nie wychodzą do sieci.
"""
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# Jedyny plik .env, który wolno śledzić w gicie.
DOZWOLONY_SZABLON = ".env.example"

# Klucze, których wartość nigdy nie może być zacommitowana.
WRAZLIWE_KLUCZE = ("SECRET_KEY", "TMDB_API_KEY", "API_KEY", "TOKEN", "PASSWORD")

# Wartości, które są oczywistymi atrapami, a nie sekretami.
# Uwaga: puste alternatywy typu r"^(|...)" pasują do KAŻDEGO ciągu i czynią
# test bezużytecznym - pustą wartość dopuszczamy wyłącznie jako pełne dopasowanie.
ATRAPY = re.compile(
    r"^(?:$|\"\"$|''$|your_|test[-_]|example|placeholder|dummy|xxx"
    r"|change[-_]this|django-insecure-change)",
    re.IGNORECASE,
)

# Przypisanie klucza do wartości w pliku .env albo w kodzie Pythona.
PRZYPISANIE = re.compile(
    # [ 	] a nie \s: \s pochłania znak nowej linii, przez co pusta wartość
    # "zjadłaby" następny wiersz pliku i test stałby się ślepy.
    r"^[ 	]*(?P<klucz>[A-Z0-9_]*(?:%s))[ 	]*[=:][ 	]*(?P<wartosc>.*)$"
    % "|".join(WRAZLIWE_KLUCZE),
    re.MULTILINE,
)

# Sygnatury konkretnych sekretów tego projektu.
SYGNATURY = (
    ("klucz TMDB (32 znaki hex)", re.compile(r"\b[0-9a-f]{32}\b")),
    (
        "wygenerowany klucz Django",
        re.compile(r"django-insecure-(?!change)[!-~]{20,}"),
    ),
)

# Ścieżki, których nie skanujemy: migracje i statyki zawierają hashe,
# a ten plik z definicji zawiera wzorce sekretów.
POMIJANE = re.compile(r"(^|/)(migrations|staticfiles|\.git)/|test_no_secrets\.py$")


def _sledzone_pliki() -> list[str]:
    wynik = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO, capture_output=True, check=True,
    )
    return [p for p in wynik.stdout.decode("utf-8").split("\0") if p]


def _odczytaj(sciezka: Path) -> str:
    """Dekoduje plik niezależnie od kodowania - UTF-16 ukrył poprzedni wyciek."""
    surowe = sciezka.read_bytes()
    for kodowanie in ("utf-8-sig", "utf-16", "utf-8", "latin-1"):
        try:
            return surowe.decode(kodowanie)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


@pytest.fixture(scope="module")
def sledzone() -> list[str]:
    return _sledzone_pliki()


def test_tylko_szablon_env_jest_sledzony(sledzone):
    """Żaden plik .env poza szablonem nie może być w indeksie gita."""
    pliki_env = [
        p for p in sledzone
        if Path(p).name.startswith(".env") and p != DOZWOLONY_SZABLON
    ]
    assert pliki_env == [], (
        "Pliki .env z sekretami są śledzone przez gita: %s. "
        "Usuń je: git rm --cached <plik>" % pliki_env
    )


@pytest.mark.parametrize("wariant", [".env", ".env.production", ".env.local", ".env.prod"])
def test_gitignore_blokuje_warianty_env(wariant):
    """.gitignore musi ignorować każdy wariant .env."""
    wynik = subprocess.run(
        ["git", "check-ignore", "-q", wariant], cwd=REPO, capture_output=True,
    )
    assert wynik.returncode == 0, f"{wariant} nie jest ignorowany przez .gitignore"


def test_szablon_env_nie_ma_wartosci():
    """.env.example jest pusty - same nazwy zmiennych, zero wartości."""
    tresc = _odczytaj(REPO / DOZWOLONY_SZABLON)
    winne = [
        (m.group("klucz"), m.group("wartosc"))
        for m in PRZYPISANIE.finditer(tresc)
        if not ATRAPY.match(m.group("wartosc").strip().strip("\"'"))
    ]
    assert winne == [], f"{DOZWOLONY_SZABLON} zawiera wartości: {winne}"


def test_szablon_env_wymienia_wszystkie_wymagane_zmienne():
    """Szablon musi pokrywać to, czego settings.py naprawdę szuka w środowisku."""
    tresc = _odczytaj(REPO / DOZWOLONY_SZABLON)
    ustawienia = _odczytaj(REPO / "MyMovies" / "settings.py")
    wymagane = set(re.findall(r"getenv\(\s*[\"']([A-Z0-9_]+)[\"']", ustawienia))
    wymagane |= set(re.findall(r"env_(?:bool|list)\(\s*[\"']([A-Z0-9_]+)[\"']", ustawienia))
    brakujace = sorted(
        n for n in wymagane
        if not re.search(r"^\s*%s\s*=" % re.escape(n), tresc, re.MULTILINE)
    )
    assert brakujace == [], f"{DOZWOLONY_SZABLON} nie wymienia: {brakujace}"


def test_zaden_sledzony_plik_nie_zawiera_sekretu(sledzone):
    """Skan wszystkich śledzonych plików pod kątem sygnatur sekretów."""
    trafienia = []
    for wzgledna in sledzone:
        if POMIJANE.search(wzgledna):
            continue
        plik = REPO / wzgledna
        if not plik.is_file():
            continue
        tresc = _odczytaj(plik)
        for opis, wzorzec in SYGNATURY:
            for dopasowanie in wzorzec.finditer(tresc):
                numer = tresc.count("\n", 0, dopasowanie.start()) + 1
                trafienia.append(f"{wzgledna}:{numer} -> {opis}")

    assert trafienia == [], "Sekrety w śledzonych plikach:\n" + "\n".join(trafienia)


def test_sledzone_pliki_nie_przypisuja_wrazliwych_kluczy(sledzone):
    """Wrażliwy klucz w śledzonym pliku może mieć tylko wartość-atrapę."""
    trafienia = []
    for wzgledna in sledzone:
        if POMIJANE.search(wzgledna) or not (REPO / wzgledna).is_file():
            continue
        tresc = _odczytaj(REPO / wzgledna)
        for m in PRZYPISANIE.finditer(tresc):
            wartosc = m.group("wartosc").strip().rstrip(",").strip("\"'")
            # Odczyt ze środowiska nie jest sekretem, tylko poprawnym wzorcem.
            if wartosc.startswith(("os.getenv", "os.environ", "env_", "settings.")):
                continue
            if ATRAPY.match(wartosc):
                continue
            numer = tresc.count("\n", 0, m.start()) + 1
            trafienia.append(f"{wzgledna}:{numer} -> {m.group('klucz')}={wartosc!r}")

    assert trafienia == [], "Zakodowane sekrety:\n" + "\n".join(trafienia)
