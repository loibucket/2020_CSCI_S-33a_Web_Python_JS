from django.urls import path

from . import views, util

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("new_page", views.new_page, name="new_page"),
    path("edit_page", views.edit_page, name="edit_page"),
    path("make", views.make, name="make"),
    path("random_page", views.random_page, name="random_page"),

    # this must be last in list
    path("<str:title>", views.wiki, name="get_entry")
]
