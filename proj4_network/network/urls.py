
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),

    path("follow", views.follow, name="follow"),  # post
    path("follow_stats/<str:username>", views.follow_stats, name="follow_stats"),

    path("like", views.like, name="like"),  # post
    path("like_stats/<int:post_id>", views.like_stats, name="like_stats"),

    path("all_posts/<int:page_num>//",
         views.all_posts, name="all_posts"),
    path("all_posts/<int:page_num>//<int:following>",
         views.all_posts, name="all_posts"),
    path("all_posts/<int:page_num>/<str:username>/",
         views.all_posts, name="all_posts"),
    path("all_posts/<int:page_num>/<str:username>/<int:following>",
         views.all_posts, name="all_posts"),
]
