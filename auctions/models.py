from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms


class User(AbstractUser):
    watchlist = models.ManyToManyField('Auction')

class Auction(models.Model):
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=128)
    url = models.URLField(max_length=500)
    CHOICES = [
        ('FA', 'Fashion'),
        ('HG', 'Home & Garden'),
        ('EL', 'Electronics'),
        ('HE', 'Home Entertainment'),
        ('TO', 'Toys'),
        ('CO', 'Collectables')
    ]
    categories = models.CharField(choices=CHOICES, max_length=2)
    description = models.CharField(max_length=500)
    auctionauthor = models.CharField(max_length=64)
    minimumbid = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.name}"

class Bid(models.Model):
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name="highestbid")
    user=models.ForeignKey('User', on_delete=models.CASCADE, related_name="bidowner")
    bidvalue=models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.auction}, {self.bidvalue}"
