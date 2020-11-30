from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max

from .models import User, Auction, Bid
from django import forms

from slugify import slugify

class CreateListingForm(forms.Form):
    name = forms.CharField(max_length=64, label="Listing name")
    url = forms.URLField(max_length=500, label="Image URL", required=False)
    CHOICES = [
        ('', "-------"),
        ('FA', 'Fashion'),
        ('HG', 'Home & Garden'),
        ('EL', 'Electronics'),
        ('HE', 'Home Entertainment'),
        ('TO', 'Toys'),
        ('CO', 'Collectables')
    ]
    categories = forms.ChoiceField(choices=CHOICES, label="Category", required=False)
    minimumbid = forms.DecimalField(max_digits=7, decimal_places=2)
    description = forms.CharField(max_length=500, widget=forms.Textarea, label="Description")

class PlaceBid(forms.Form):
    Bid = forms.DecimalField(max_digits=7, decimal_places=2, label="Place Bid")


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

def listingview(request, slug):
    a = Auction.objects.annotate(high_bid = Max("highestbid__bidvalue"))
    auction = a.filter(slug=slug)
    b=Auction.objects.filter(slug=slug)
    if request.method == "POST":
        bid = request.POST["Bid"]
        if float(bid) > auction[0].high_bid:
            newbid = Bid(auction = b[0], user=request.user, bidvalue=bid)
            newbid.save()
            return render(request, "auctions/listing.html", {
                "auctions" : auction,
                "message" : "Your bid has been accepted"
            })
        else:
            return render(request, "auctions/listing.html", {
                "auctions" : auction,
                "message" : "Your bid is too low"
            })
    return render(request, "auctions/listing.html", {
        "auctions" : auction
    })


def createlisting(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]
            slug=slugify(name)
            url=form.cleaned_data["url"]
            description=form.cleaned_data["description"]
            category=form.cleaned_data["categories"]
            minimumbid=form.cleaned_data["minimumbid"]

            if category == "" and url == "":
                return render(request, "auctions/createlisting.html", {
                    "message" : "You must choose either an Image URL or a Category",
                    "form" : form
                })
            else:

                if request.user.is_authenticated:
                    user=request.user.username
                newlisting = Auction(name=name, slug=slug, url=url, description=description, categories=category, auctionauthor=user, minimumbid=minimumbid)
                newlisting.save()
                return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/createlisting.html", {
            "form" : CreateListingForm()
        })
