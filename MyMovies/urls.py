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
from Movies.views import movie_list, add_movie, movie_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path("movies/movie_list/", movie_list, name="movie_list"),
    path("movies/add_movie/", add_movie, name="add_movie"),
    path("movies/<int:pk>/", movie_detail, name="movie_detail"),
]
