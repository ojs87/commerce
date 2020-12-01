from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from django.contrib.auth.decorators import login_required

from .models import User, Auction, Bid, Comment
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

    #create query sets for the view, filtering by the slug name of the auction and annotating the highestbid.

    a = Auction.objects.annotate(high_bid = Max("highestbid__bidvalue"))
    auction = a.filter(slug=slug)
    b = Auction.objects.filter(slug=slug)
    c = Bid.objects.filter(auction__slug=slug)
    d = c.aggregate(Max('bidvalue'))
    e = c.filter(bidvalue = d['bidvalue__max'])
    comments = Comment.objects.filter(auction__slug=slug)

    #get the watchlist for the current user
    if not request.user.is_authenticated:
        return render(request, "auctions/listing.html", {
            "auctions" : auction,
            "comments" : comments
        })

    users = User.objects.get(username=request.user.username)
    watchlist = users.watchlist.all()

    if request.method == "POST":

        #close the auction if the button is pressed

        if request.POST["close"] == "close":
            if len(e) != 0:
                b.update(auctionclosed=True)
                b.update(auctionwinner=e[0].user.username)
                return HttpResponseRedirect(reverse("listingview", args=(slug, )))

            else:
                b.update(auctionclosed=True)
                return HttpResponseRedirect(reverse("listingview", args=(slug, )))

        #remove the auction from the watchlist if the button is pressed

        elif request.POST["close"] == "removefromwatchlist":

            auctions = Auction.objects.get(slug=slug)
            users.watchlist.remove(auctions)
            return HttpResponseRedirect(reverse("listingview", args=(slug, )))

        #add the auction to the watchlist if the button is pressed

        elif request.POST["close"] == "addtowatchlist":

            auctions = Auction.objects.get(slug=slug)
            users.watchlist.add(auctions)
            return HttpResponseRedirect(reverse("listingview", args=(slug, )))

        elif request.POST["close"] == "comment":

            comment = request.POST["comment"]
            newcomment = Comment(user=request.user, auction=b[0], comment=comment)
            newcomment.save()
            return HttpResponseRedirect(reverse("listingview", args=(slug, )))

        else:

        #check if a bid is higher than the minimumbid

            bid = request.POST["Bid"]

            if float(bid) < auction[0].minimumbid:

                return render(request, "auctions/listing.html", {
                    "auctions" : auction,
                    "watchlist" : watchlist,
                    "message" : "Your bid must be at least equal to the minimumbid",
                    "comments" : comments
                })

            #check if a high bid exists
            if auction[0].high_bid != None:

                #check if the bid is higher than the highest bid and return a message

                if float(bid) > auction[0].high_bid:

                    newbid = Bid(auction = b[0], user=request.user, bidvalue=bid)
                    newbid.save()
                    return render(request, "auctions/listing.html", {
                        "auctions" : auction,
                        "watchlist" : watchlist,
                        "message" : "Your bid has been accepted",
                        "comments" : comments
                    })

                else:

                    return render(request, "auctions/listing.html", {
                        "auctions" : auction,
                        "watchlist" : watchlist,
                        "message" : "Your bid is too low",
                        "comments" : comments
                    })

            #accept the bid if a high bid doesn't exist

            else:

                newbid = Bid(auction = b[0], user=request.user, bidvalue=bid)
                newbid.save()
                return render(request, "auctions/listing.html", {
                    "auctions" : auction,
                    "watchlist" : watchlist,
                    "message" : "Your bid has been accepted",
                    "comments" : comments
                })


    return render(request, "auctions/listing.html", {
        "auctions" : auction,
        "watchlist" : watchlist,
        "comments" : comments
    })

#View for creating a new auction
@login_required
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

            #save the new auction

            if request.user.is_authenticated:
                user=request.user.username
            newlisting = Auction(name=name, slug=slug, url=url, description=description, categories=category, auctionauthor=user, minimumbid=minimumbid)
            newlisting.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/createlisting.html", {
            "form" : CreateListingForm()
        })

@login_required
def watchlist(request):
    if request.method == "POST":
        users = User.objects.get(username=request.user.username)
        auctions = Auction.objects.get(slug=request.POST["close"])
        users.watchlist.remove(auctions)
        return HttpResponseRedirect(reverse("watchlist"))
    a = User.objects.get(username=request.user.username)
    watchlist = a.watchlist.annotate(high_bid=Max("highestbid__bidvalue"))
    return render(request, "auctions/watchlist.html", {
        "watchlist" : watchlist
    })

def categories(request, category):
    #check if the nav link was pressed
    if category == "allcats":
        return render(request, "auctions/categories.html")

    cat = Auction.objects.annotate(high_bid = Max("highestbid__bidvalue")).filter(categories=category).filter(auctionclosed=False)
    return render(request, "auctions/categories.html", {
        "cats" : cat,
        "message" : "There are no auctions for this category"
    })
