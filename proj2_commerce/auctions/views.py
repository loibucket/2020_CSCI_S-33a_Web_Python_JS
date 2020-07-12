from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

import math

from .models import User
from .models import Listing
from .models import Bid
from .models import Comment
from .models import Watchlist


def index(request):
    """
    renders active listings
    """
    context = {
        "all_listings": Listing.objects.filter(is_active=True),
        "heading": "Active Listings"
    }
    return render(request, "auctions/index.html", context)


def inactive_listings(request):
    """
    renders inactive listings
    """
    context = {
        "all_listings": Listing.objects.filter(is_active=False),
        "heading": "Inactive Listings"
    }
    return render(request, "auctions/index.html", context)


def login_view(request):
    """
    renders user login page, and on POST, logs in user
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


@login_required()
def logout_view(request):
    """
    logs user out
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    renders register user page, and on POST, adds user to database
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
    renders create listing page, and on POST, adds listing to database
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
    renders listing details
    """
    # listing item details
    # get listing id from passed in argument if exists, else get from user request
    if not listing_id: listing_id = request.GET['listing_id']
    listing = get_object_or_404(Listing, id=listing_id)

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
    # update current bid when page is visited
    listing.current_bid = current_bid
    listing.save()

    # allow bid from non-seller
    if str(request.user.username) == str(listing.seller):
        allow_end_item = True
    else:
        allow_end_item = False

    auction_winner = False
    # if user is logged in
    try:
        bidder = request.user
        # add or remove from watchlist
        watch_item = Watchlist.objects.filter(listing_id=listing_id, user_id=bidder.id)
        if watch_item:
            watch_button = "Remove from Watchlist"
        else:
            watch_button = "Add to Watchlist"
        # if the user is winner
        if not listing.is_active and bidder == high_bidder:
            auction_winner = True
    except:
        pass

    # get list of comments
    comments = Comment.objects.filter(listing=listing_id)[::-1]

    # render results
    context = {
        "listing": listing,
        "all_bids": all_bids,
        "n_bids": n_bids,
        "high_bidder": high_bidder,
        "status_message": status_message,
        "current_bid": current_bid,
        "allow_end_item": allow_end_item,
        "watch_button": watch_button,
        "auction_winner": auction_winner,
        "comments": comments
    }
    return render(request, "auctions/listing_details.html", context)


@login_required()
def place_bid(request, listing_id=None, status_message=""):
    """
    attempts update bid data if valid, refreshes page with updated data
    """
    # placing a bid
    bidder = request.user
    bid_amount = request.POST["bid_amount"]
    listing_id = int(request.POST["listing_id"])
    listing = get_object_or_404(Listing, id=listing_id)
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


@login_required()
def watchlist_modify(request):
    """
    renders active listings
    """
    listing_id = int(request.POST["listing_id"])
    user = request.user

    # look for item in watchlist, if not in watchlist, add to watchest
    # if in watchlist, remove from watchlist

    watch_item = Watchlist.objects.filter(listing_id=listing_id, user_id=user.id)

    if watch_item:
        watch_item.delete()
    else:
        watch_item = Watchlist(listing_id=listing_id, user_id=user.id)
        watch_item.save()

    # go back to same listing
    request.method = "GET"
    return listing_details(request, listing_id=listing_id)


@login_required()
def watchlist(request):
    """
    renders watch list
    """
    listing_ids = Watchlist.objects.filter(user_id=request.user.id).values_list('listing')
    listings = Listing.objects.filter(id__in=listing_ids)
    context = {
        "all_listings": listings,
        "heading": "Watch List"
    }
    return render(request, "auctions/index.html", context)


@login_required()
def end_listing(request):
    """
    ends listing in data base, refreshes page with updated data
    """
    # get listing
    listing_id = request.POST['listing_id']
    listing = get_object_or_404(Listing, id=listing_id)
    listing.is_active = False
    listing.save()
    request.method = "GET"
    return listing_details(request, listing_id=listing_id)


@login_required()
def comment(request):
    """
    Adds comment to database, refreshes page with updated data
    """
    # get listing
    listing_id = request.POST['listing_id']
    listing = get_object_or_404(Listing, id=listing_id)
    comment = request.POST['comment']
    user = request.user

    comment_entry = Comment(listing=listing, commenter=user, comment=comment)
    comment_entry.save()

    return listing_details(request, listing_id=listing_id)


def categories(request):
    """
    lists categories, or lists active items in specified category
    """
    all_categories = Listing.objects.filter(is_active=True).order_by().values('category').distinct()
    all_categories = [c['category'] for c in all_categories]

    listings = []

    try:
        # if c is specified, return category results
        c = request.GET['c']
        listings = Listing.objects.filter(category=c, is_active=True)
        c = f"Active Listings for {c}"
        context = {
            "heading": c,
            "all_listings": listings
        }
        return render(request, "auctions/index.html", context)
    except:
        pass

    # list all non-empty categories
    context = {
        "heading": "Active Categories",
        "all_categories": all_categories,
        "all_listings": listings
    }
    return render(request, "auctions/categories.html", context)
