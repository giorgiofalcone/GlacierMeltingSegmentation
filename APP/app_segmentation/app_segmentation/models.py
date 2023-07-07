from django.db import models

class Image(models.Model):
    date = models.DateField()
    location = models.TextField()
    name = models.TextField()