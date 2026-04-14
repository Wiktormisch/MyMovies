from django.db import models
from django.contrib.auth.models import User


class Movie (models.Model):

    STATUS_CHOICES = [("watched", "Watched"),
                      ("to_watch", "To Watch")]

    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="to_watch")
    created_at = models.DateField(auto_now_add=True, blank=True)
    updated_at = models.DateField(auto_now=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):

        return f"{self.title} - {self.year}"
