from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from django.core.serializers import serialize

from .models import User
from .models import Post
from .models import Follower
from .models import Like

from itertools import chain


def index(request):
    """
    show index page
    """
    return render(request, "network/index.html")


def login_view(request):
    """
    show login screen, or logs in user
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    """
    show logout view
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    show registration page, or register user to database
    """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required
def new_post(request):
    """
    given post message
    record post to database and return results as json
    """
    # must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # add post to database
    data = json.loads(request.body)
    body = data.get("body", "")
    post = Post(poster=request.user, body=body)
    post.save()

    return JsonResponse({"message": "post created successfully."}, status=201)


def all_posts(request, page_num=1, username="", following=""):
    """
    given page number and username
    get all posts from page made by username
    if no username, get posts from all users
    if following is True
    return as json
    """
    # show all posts
    if username == "":
        post = Post.objects.filter().order_by("-timestamp")
    # show post for one user only
    elif following == "":
        post = Post.objects.filter(
            poster__username=username).order_by("-timestamp")
    # show post for all followers
    else:
        following = Follower.objects.filter(
            follower__username=username).values()
        follow_list = [f['followee_id'] for f in following]
        post = Post.objects.filter(
            poster_id__in=follow_list).order_by("-timestamp")

    p = Paginator(post, 10)

    # build posts
    post_list = []
    for entry in p.page(page_num):
        post_list.append([entry.id, entry.poster.username,
                          entry.body, entry.timestamp])
    # return posts and number of pages available
    return JsonResponse([page_num, p.num_pages, post_list], safe=False)


@ csrf_exempt
@ login_required
def follow(request):
    """
    adds or removes following pair from database
    """
    data = json.loads(request.body)
    followee = data.get("followee")  # followee is the profile person
    follower = request.user
    toggle = data.get("toggle")

    pair_exists = Follower.objects.filter(
        followee__username=followee, follower__username=follower)

    # only check for follow
    if not toggle:
        num_followers = len(Follower.objects.filter(
            followee__username=followee))
        num_following = len(Follower.objects.filter(
            follower__username=followee))
        if pair_exists:
            return JsonResponse(["pair exists", num_followers, num_following], safe=False)
        else:
            return JsonResponse(["pair not found", num_followers, num_following], safe=False)

    followee_obj = User.objects.get(username=followee)
    follower_obj = User.objects.get(username=follower)

    # toggle follow
    if not pair_exists:
        pair = Follower(followee=followee_obj, follower=follower_obj)
        pair.save()
        return JsonResponse(["pair created"], safe=False)
    else:
        pair_exists.delete()
        return JsonResponse(["pair deleted"], safe=False)


@ csrf_exempt
@ login_required
def like(request):

    data = json.loads(request.body)
    post_id = data.get("post_id")
    user = request.user
    toggle = data.get("toggle")

    user_like = Like.objects.filter(post__id=post_id, liker__username=user)

    if not toggle:
        num_likes = len(Like.objects.filter(post__id=post_id))
        print(num_likes, user_like)
        return JsonResponse([num_likes, bool(user_like)], safe=False)

    post_obj = Post.objects.get(id=post_id)
    liker_obj = User.objects.get(username=user)

    # toggle like
    if not user_like:
        like = Like(post=post_obj, liker=liker_obj)
        like.save()
        return JsonResponse(["like created", None], safe=False)
    else:
        user_like.delete()
        return JsonResponse(["like deleted", None], safe=False)
