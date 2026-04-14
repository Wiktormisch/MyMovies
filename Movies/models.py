from django.db import models


class Movie (models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    director = models.TextField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title
