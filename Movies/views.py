from django.shortcuts import render
from .models import Movie
from .forms import MovieForm


def movie_list(request):
    movies = Movie.objects.all()
    return render(request, "movies/movie_list.html", {"movies": movies})


def add_movie(request):
    if request.method == "POST":
        form = MovieForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = MovieForm()

    return render(request, "movies/add_movie.html", {"form": form})
