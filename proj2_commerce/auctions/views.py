from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from .models import User
from .models import Listing
from .models import Bid
from .models import Comment
import math


def index(request):
    """
    renders active listings
    """
    context = {
        "all_listings": Listing.objects.filter(is_active=True)
    }

    return render(request, "auctions/index.html", context)


def login_view(request):
    """
    renders user login page, and logs in user
    """
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
    """
    logs user out
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    renders register user page, and adds user to database
    """
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

    # else show registration page
    else:
        return render(request, "auctions/register.html")


@login_required()
def create_listing(request):
    """
    renders create listing page, and adds listing to database
    """
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        starting_bid = request.POST["starting_bid"]
        category = request.POST["category"]
        seller = request.user

        # Attempt to create new listing
        try:
            current_bid = starting_bid
            listing = Listing(title=title, description=description, image_url=image_url,
                              is_active=True, starting_bid=starting_bid, seller=seller, current_bid=current_bid,
                              category=category)
            listing.save()
            request.method = "GET"
            return listing_details(request, str(listing.id))
        except:
            return render(request, "auctions/create_listing.html", {
                "message": "Input Error: Please check fields again",
                "category": category,
                "title": title,
                "description": description,
                "image_url": image_url,
                "starting_bid": starting_bid
            })

    # show create listing page
    else:
        return render(request, "auctions/create_listing.html")


def listing_details(request, listing_id=None, status_message=""):
    """
    renders listing details, or place bid if post
    """
    # placing a bid
    if request.method == "POST":
        bidder = request.user
        bid_amount = request.POST["bid_amount"]
        listing_id = int(request.POST["listing_id"])
        listing = Listing.objects.get(id=listing_id)
        request.method = "GET"

        # attempt to get last bid, or use starting bid as highest
        try:
            highest_bid = Bid.objects.filter(listing_id=listing_id).latest('bid_time').bid_amount
        except:
            highest_bid = float(listing.starting_bid) - 0.01  # minus 1 cent so first bid can equal to starting bid

        # error if not signed in
        if str(bidder) == "AnonymousUser":
            return listing_details(request, listing_id,
                                   status_message=f"<i style='color:red'> Bid Error: Not Signed in</i>")

        # error user does not exist, or in case if keyword AnonymousUser is not used
        if User.objects.filter(username=str(bidder)).count() == 0:
            return listing_details(request, listing_id,
                                   status_message=f"<i style='color:red'> Bid Error: User Does Not Exist</i>")

        # error if user is same as seller:
        if str(bidder) == str(listing.seller):
            return listing_details(request, listing_id,
                                   status_message=f"<i style='color:red'> Bid Error: Cannot Bid On Your Own Items</i>")

        # attempt to place bid, gives user error if unable
        try:
            bid_amount = math.floor(float(bid_amount) * 100) / 100  # floor to cent, errors if not convertible to number
            if bid_amount <= highest_bid:
                return listing_details(request, listing_id,
                                       status_message=f"<i style='color:red'> Error: ${bid_amount} is Lower than Current</i>")
            # attempt to save bid to model
            bid = Bid(listing=listing, bid_amount=bid_amount, bidder=bidder)
            bid.save()
            return listing_details(request, listing_id, status_message=f"<i> Bid Placed: ${bid_amount}</i>")
        except:
            return listing_details(request, listing_id,
                                   status_message=f"<i style='color:red'> Bid Error: {bid_amount}</i>")

    else:  # listing item details
        # get listing id from passed in argument if exists, else get from user request
        if not listing_id: listing_id = request.GET['listing_id']
        listing = Listing.objects.get(id=listing_id)

        # try to get bid history
        try:
            all_bids = Bid.objects.filter(listing_id=listing_id)[::-1]
            n_bids = len(all_bids)
            latest_bid = Bid.objects.filter(listing_id=listing_id).latest('bid_time')
            high_bidder = latest_bid.bidder
            current_bid = latest_bid.bid_amount
        # if history is not found, start with no bids
        except:
            all_bids = []
            n_bids = 0
            high_bidder = "None"
            current_bid = listing.starting_bid
        #update current bid when page is visited
        listing.current_bid = current_bid
        listing.save()
        #render results
        context = {
            "listing": listing,
            "all_bids": all_bids,
            "n_bids": n_bids,
            "high_bidder": high_bidder,
            "status_message": status_message,
            "current_bid": current_bid
        }
        return render(request, "auctions/listing_details.html", context)
