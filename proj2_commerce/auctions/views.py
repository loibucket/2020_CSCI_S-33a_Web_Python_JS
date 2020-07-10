from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from .models import User
from .models import Listing


def index(request):
    return render(request, "auctions/index.html")


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


@login_required()
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        starting_bid = request.POST["starting_bid"]
        seller = request.user
        print(title, description, starting_bid, image_url, seller)

        #listing = Listing(title=title, description=description, image_url=image_url,
        #                  is_active=True, starting_bid=starting_bid, current_bid=starting_bid, seller=seller)

        #listing.save()

        # Attempt to create new listing
        try:
            listing = Listing(title=title, description=description, image_url=image_url,
                              is_active=True, starting_bid=starting_bid, current_bid=starting_bid, seller=seller)
            listing.save()
            return render(request, "auctions/create_listing.html", {
                "message": "Listing created",
            })
        except:
            return render(request, "auctions/create_listing.html", {
                "message": "Input Error: Please check fields again",
                "title": title,
                "description": description,
                "image_url": image_url,
                "starting_bid": starting_bid
            })

        return render(request, "auctions/create_listing.html")
    else:
        return render(request, "auctions/create_listing.html")
