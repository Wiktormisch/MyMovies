"""
URL configuration for MyMovies project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Movies.views import (movie_list, add_movie,
                          movie_detail, movie_delete, movie_edit, register,
                          search_movies_api, add_movie_api)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", movie_list, name="home"),
    path("movies/movie_list/", movie_list, name="movie_list"),
    path("movies/add_movie/", add_movie, name="add_movie"),
    path("movies/<int:pk>/", movie_detail, name="movie_detail"),
    path("movies/<int:pk>/delete", movie_delete, name="movie_delete"),
    path("movies/<int:pk>/edit", movie_edit, name="movie_edit"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page='/login/'), name="logout"),
    path("register/", register, name="register"),
    path("search/", search_movies_api, name="search"),
    path("add_from_api/<int:tmdb_id>/", add_movie_api, name="add_movie_api")
]
