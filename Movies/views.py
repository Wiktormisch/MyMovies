from django.shortcuts import render
from .models import Movie
from .forms import MovieForm
from django.shortcuts import get_object_or_404, redirect


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
            return redirect("movie_list")
    else:
        form = MovieForm()

    return render(request, "movies/add_movie.html", {"form": form})


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    return render(request, "movies/movie_detail.html", {"movie": movie})


def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        movie.delete()
        return redirect("movie_list")
    return redirect("movie_detail", pk=pk)


def movie_edit(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    if request.method == "POST":
        form = MovieForm(request.POST, instance=movie)
        if form.is_valid():
            form.save()
            return redirect("movie_detail", pk=pk)
    else:
        form = MovieForm(instance=movie)

    return render(request, "movies/edit_movie.html", {"form": form})
