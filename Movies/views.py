from django.shortcuts import render
from .models import Movie
from .forms import MovieForm


def movie_list(request):
    status = request.GET.get("status")
    movies = Movie.objects.all()

    if status:
        movies = movies.filter(status=status)

    return render(request, "movies/movie_list.html", {"movies": movies})


def add_movie(request):
    if request.method == "POST":
        form = MovieForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = MovieForm()

    return render(request, "movies/add_movie.html", {"form": form})
