from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max

from .models import User, Auction
from django import forms

from slugify import slugify

class CreateListingForm(forms.Form):
    name = forms.CharField(max_length=64, label="Listing name")
    url = forms.URLField(max_length=500, label="Image URL")
    CHOICES = [
        ('', "-------"),
        ('FA', 'Fashion'),
        ('HG', 'Home & Garden'),
        ('EL', 'Electronics'),
        ('HE', 'Home Entertainment'),
        ('TO', 'Toys'),
        ('CO', 'Collectables')
    ]
    categories = forms.ChoiceField(choices=CHOICES, label="Category")
    description = forms.CharField(max_length=500, widget=forms.Textarea, label="Description")

def index(request):
    auctions=Auction.objects.annotate(high_bid=Max('highestbid__bidvalue'))
    return render(request, "auctions/index.html", {
        "auctions" : auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# def listingview(request, slug):
#     pass

def createlisting(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]
            slug=slugify(name)
            url=form.cleaned_data["url"]
            description=form.cleaned_data["description"]
            category=form.cleaned_data["categories"]
            if request.user.is_authenticated:
                user=request.user.username
            newlisting = Auction(name=name, slug=slug, url=url, description=description, categories=category, auctionauthor=user)
            newlisting.save()
            return HttpResponseRedirect("index.html")
    else:
        return render(request, "auctions/createlisting.html", {
            "form" : CreateListingForm()
        })
