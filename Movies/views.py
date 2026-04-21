from django.shortcuts import render
from .models import Movie, Tag
from .forms import MovieForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


@login_required
def movie_list(request):
    status = request.GET.get("status")
    movies = Movie.objects.filter(owner=request.user)
    search = request.GET.get("search", "").strip()

    if status:
        movies = movies.filter(status=status)

    if search:
        movies = movies.filter(title__icontains=search)

    return render(request, "movies/movie_list.html", {"movies": movies})


@login_required
def add_movie(request):
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


def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if movie.owner == request.user:
        if request.method == "POST":
            movie.delete()
            return redirect("movie_list")
    return redirect("movie_detail", pk=pk)


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

        return render(request, "movies/edit_movie.html", {"form": form})
    return redirect("movie_list")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm
    return render(request, "registration/register.html", {"form": form})
