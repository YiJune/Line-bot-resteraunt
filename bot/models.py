# models.py

from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    rating = models.FloatField()
    opening_hours = models.BinaryField(models.CharField(max_length=255))
    price = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    categories = models.BinaryField(models.CharField(max_length=255))




# Create your models here.
