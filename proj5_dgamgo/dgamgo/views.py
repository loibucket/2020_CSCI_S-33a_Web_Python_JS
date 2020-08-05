from django.db.models import Q, F
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
from .models import Game


def index(request):
    """
    show index page
    """
    return render(request, "dgamgo/index.html")


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
            return render(request, "dgamgo/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "dgamgo/login.html")


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
            return render(request, "dgamgo/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "dgamgo/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "dgamgo/register.html")


def result(request):
    """
    record game results to database
    """
    if request.method == "POST":

        data = json.loads(request.body)
        mode = data.get("mode", "")
        duration = data.get("duration", "")
        winner = data.get("winner", "")
        first_mover = data.get("first_mover", "")

        duration = round(duration/1000.0, 1)

        Game(player=request.user, mode=mode, duration=duration,
             winner=winner, first_mover=first_mover).save()
        return JsonResponse({"message": "game recorded successfully."}, status=201)

    return JsonResponse({"error": "not a post request"}, status=400)


def history(request, mode="1P"):
    """
    show player history
    """
    context = {
        "games": Game.objects.filter(player=request.user, mode=mode).order_by("-timestamp")[:50],
        "mode": mode
    }
    return render(request, "dgamgo/history.html", context)


def leaderboard(request, type="draw"):
    """
    leaderboard
    """
    if type == "win":
        context = {
            "games": Game.objects.filter(mode="1P").filter(Q(winner=F("first_mover"))).order_by("duration")[:50],
            "type": type
        }

    elif type == "draw":
        context = {
            "games": Game.objects.filter(mode="1P").filter(Q(winner="draw")).order_by("duration")[:50],
            "type": type
        }

    return render(request, "dgamgo/leaderboard.html", context)
