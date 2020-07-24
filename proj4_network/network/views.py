import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.utils import timezone

from .models import User
from .models import Post
from .models import Follower
from .models import Like


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

    # add post to database, or edit existing post
    data = json.loads(request.body)
    body = data.get("body", "")
    existing_post = data.get("existing_post", "")
    if existing_post == -1:
        Post(poster=request.user, body=body).save()
    else:
        # for security, check if user owns the post
        edit_post = get_object_or_404(Post, pk=existing_post)
        if str(edit_post.poster.username) == str(request.user):
            edit_post.body = body
            edit_post.save()
        else:
            return JsonResponse({"error": "user does not match post creator"}, status=400)

    return JsonResponse({"message": "post created successfully."}, status=201)


def all_posts(request, page_num=1, username="", following=""):
    """
    gets post from all, specific user, or followed users
    """
    # show post for all followers of login user
    if following == 1:
        following = Follower.objects.filter(
            follower__username=request.user).values()
        follow_list = [f['followee_id'] for f in following]
        post = Post.objects.filter(
            poster_id__in=follow_list).order_by("-timestamp")
    # show post for one user
    elif username != "":
        post = Post.objects.filter(
            poster__username=username).order_by("-timestamp")
    # show all posts
    else:
        post = Post.objects.filter().order_by("-timestamp")

    p = Paginator(post, 10)

    # build posts
    post_list = []
    for entry in p.page(page_num):
        post_list.append([entry.id, entry.poster.username,
                          entry.body, entry.timestamp])
    return JsonResponse({"message": "ok", "data": [page_num, p.num_pages, post_list]}, status=201)


@ csrf_exempt
@ login_required
def follow(request):
    """
    check and toggle follow status
    """
    # must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    followee = data.get("followee")  # followee is the profile person
    toggle = data.get("toggle")
    follower = request.user

    pair_exists = Follower.objects.filter(
        followee__username=followee, follower__username=follower)

    # check status only
    if not toggle:
        if pair_exists:
            return JsonResponse({"message": "pair exists"}, status=201)
        else:
            return JsonResponse({"message": "pair not found"}, status=201)

    # toggle follow
    if pair_exists:
        pair_exists.delete()
        return JsonResponse({"message": "pair deleted"}, status=201)
    else:
        followee_obj = User.objects.get(username=followee)
        follower_obj = User.objects.get(username=follower)
        Follower(followee=followee_obj, follower=follower_obj).save()
        return JsonResponse({"message": "pair created"}, status=201)


def follow_stats(request, username):
    """
    get num followers following for user
    """
    num_followers = len(Follower.objects.filter(followee__username=username))
    num_following = len(Follower.objects.filter(follower__username=username))
    return JsonResponse({"num_followers": num_followers, "num_following": num_following}, status=201)


@ csrf_exempt
@ login_required
def like(request):
    """
    check and toggle like status
    """
    # must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    post_id = data.get("post_id")
    toggle = data.get("toggle")
    user = request.user
    user_like = Like.objects.filter(post__id=post_id, liker__username=user)

    # check status only
    if not toggle:
        return JsonResponse({"user_like": len(user_like) > 0}, status=201)

    # toggle like
    if not user_like:
        post_obj = Post.objects.get(id=post_id)
        liker_obj = User.objects.get(username=user)
        Like(post=post_obj, liker=liker_obj).save()
        return JsonResponse({"message": "like created"}, status=201)
    else:
        user_like.delete()
        return JsonResponse({"message": "like deleted"}, status=201)


def like_stats(request, post_id):
    """
    get num likes for a post
    """
    num_likes = len(Like.objects.filter(post__id=post_id))
    return JsonResponse({"num_likes": num_likes}, status=201)
