from django.shortcuts import render
from .models import Movie, Tag
from .forms import MovieForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings


@login_required
def movie_list(request):
    status = request.GET.get("status")
    movies = Movie.objects.filter(owner=request.user)
    search = request.GET.get("search", "").strip()
    tag_list = request.GET.getlist("tag")
    tags = Tag.objects.filter(movie__owner=request.user).distinct()

    if status:
        movies = movies.filter(status=status)

    if search:
        movies = movies.filter(title__icontains=search)

    if tag_list:
        movies = movies.filter(tags__name__in=tag_list)

    return render(request, "movies/movie_list.html", {
        "movies": movies,
        "tags": tags})


@login_required
def add_movie(request):
    # Sprawdź limit filmów (max 50 per użytkownik)
    movie_count = Movie.objects.filter(owner=request.user).count()
    if movie_count >= 50:
        return render(request, "movies/add_movie.html", {
            "form": MovieForm(),
            "error": "Osiągnąłeś limit 50 filmów. Usuń niektóre filmy, aby dodać nowe."
        })

    if request.method == "POST":
        form = MovieForm(request.POST)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.owner = request.user
            movie.save()
            return redirect("movie_list")
    else:
        form = MovieForm()

    return render(request, "movies/add_movie.html", {"form": form})


@login_required
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if movie.owner == request.user:
        return render(request, "movies/movie_detail.html", {"movie": movie})

    return redirect("movie_list")


@login_required
def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if movie.owner == request.user:
        if request.method == "POST":
            movie.delete()
            return redirect("movie_list")
    return redirect("movie_detail", pk=pk)


@login_required
def movie_edit(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if movie.owner == request.user:

        if request.method == "POST":
            form = MovieForm(request.POST, instance=movie)
            if form.is_valid():
                form.save()
                return redirect("movie_detail", pk=pk)
        else:
            form = MovieForm(instance=movie)

        return render(request, "movies/edit_movie.html", {
            "form": form,
            "movie": movie
        })
    return redirect("movie_list")


def register(request):
    # Rejestracja jest wyłączona w wersji demo.
    form = UserCreationForm()
    registration_disabled = True
    registration_message = (
        "Rejestracja jest tymczasowo wyłączona. "
        "Użyj istniejącego konta demo, aby się zalogować."
    )

    if request.method == "POST":
        # Jeśli ktoś wysyła formularz ręcznie, zawsze pokażemy komunikat.
        return render(request, "registration/register.html", {
            "form": form,
            "registration_disabled": registration_disabled,
            "registration_message": registration_message,
        })

    return render(request, "registration/register.html", {
        "form": form,
        "registration_disabled": registration_disabled,
        "registration_message": registration_message,
    })


@login_required
def search_movies_api(request):
    results = []
    query = request.GET.get("q", "").strip()

    if query:
        api_key = settings.TMDB_API_KEY
        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": api_key,
            "query": query,
            "language": "pl-PL"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json()["results"]
        except Exception as e:
            print(f"Bląd API: {e}")

    return render(request, "movies/search_api.html", {
        "results": results,
        "query": query
    })


@login_required
def add_movie_api(request, tmdb_id):
    api_key = settings.TMDB_API_KEY
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"

    params = {
        "api_key": api_key,
        "language": "pl-PL"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        movie, created = Movie.objects.get_or_create(
            title=data["title"],
            owner=request.user,
            defaults={
                "description": data.get("overview", ""),
                "year": int((data.get("release_date") or "0000")[:4]),
                "status": "to_watch",
                "poster_path": data.get("poster_path", "")
            }
        )
        if created:
            return redirect("movie_detail", pk=movie.pk)
        else:
            return redirect("movie_list")

    except Exception as e:
        print(f"Blad dodawnia filmu: {e}")
        return redirect("movie_list")
