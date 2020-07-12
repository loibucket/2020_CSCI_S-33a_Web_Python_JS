from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("index.html", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing_details", views.listing_details, name="listing_details"),
    path("place_bid", views.place_bid, name="place_bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist_modify", views.watchlist_modify, name="watchlist_modify"),
    path("end_listing", views.end_listing, name="end_listing"),
    path("inactive_listings", views.inactive_listings, name="inactive_listings"),
    path("comment", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
]
