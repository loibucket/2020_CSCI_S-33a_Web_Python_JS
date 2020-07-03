from django.http import HttpResponse
from django.shortcuts import render

from . import util

import markdown2
import os
from pathlib import Path
from django.template import RequestContext
import time
import uuid
import random


def index(request):
    """
    renders index page
    """
    linked_entries = []
    for entry in util.list_entries():
        linked_entries.append("<a href='" + entry + "'>" + entry + "</a>")

    return render(request, "encyclopedia/index.html", {
        "heading": "All Pages",
        "entries": linked_entries
    })


def search(request):
    """
    renders search results
    """
    q = request.GET['q'].lower()
    entries = {}
    for entry in util.list_entries():
        entries[entry.lower()] = entry

    # go to page, don't check if exists
    if q in entries:
        return wiki(None, q, check=False)

    # list partial results
    partial_results = [entries[title] for title in entries if q in title]
    if partial_results:
        links = [
            "<a href='" +
            nonlink +
            "'>" +
            nonlink +
            "</a>" for nonlink in partial_results]
        return render(request, "encyclopedia/index.html", {
            "heading": "Search Results",
            "entries": links
        })

    # no results found
    return render(request, "encyclopedia/entry.html", {
        "title": "Not Found",
        "entry": "<h2>No Matches Found</h2>"
    }, content_type='text/html')


def wiki(request, title, check=True):
    """
    renders specific entry result, error if not found
    """
    entries = {}
    for entry in util.list_entries():
        entries[entry.lower()] = entry

    if check:
        # check if entry exists
        if title.lower() not in entries:  # filenames:
            return render(request, "encyclopedia/entry.html", {
                "title": "Not Found",
                "entry": "<h2>Requested Page Not Found</h2>"
            }, content_type='text/html')

    valid_title = entries[title.lower()]
    md = markdown2.markdown((util.get_entry(valid_title)))
    return render(request, "encyclopedia/entry.html", {
        "title": valid_title,
        "entry": md,
        "option": f"""
            <form action="edit_page">
            <input type="hidden" name="page_title" value="{valid_title}">
            <input type="submit" value="Edit Page">
            </form>
        """
    }, content_type='text/html')


def new_page(request):
    """
    render page to create new entry
    """
    return render(request, "encyclopedia/newedit.html", {
        "title": "New Page",
        "heading": "Create New Page",
    }, content_type='text/html')


def make(request):
    """
    create the new entry
    """
    page_title = request.GET['page_title'].strip()
    # check if title exists
    if page_title == "":
        return render(
            request,
            "encyclopedia/entry.html",
            {
                "title": "Error",
                "entry": "<h2>Error: Title is not specified</h2>"
            },
            content_type='text/html')

    page_contents = request.GET['page_contents'].strip()
    page_contents = ('\n'.join(page_contents.splitlines()))

    edit_page_token = request.GET['edit_page_token']

    # check for edit session
    edit_token_entry = page_title.lower(
    ) + "_5ea36f7a-bcde-11ea-b3de-0242ac130004_" + edit_page_token
    if edit_token_entry in util.list_edits():
        f = open(os.path.join("entries", page_title + ".md"), "w")
        f.write(page_contents)
        f.close()
        os.remove(os.path.join("entries", edit_token_entry + ".edit"))
        return wiki(None, page_title)

    # check if file exists
    if page_title.lower() in [e.lower() for e in util.list_entries()]:
        return render(
            request,
            "encyclopedia/entry.html",
            {
                "title": "Error",
                "entry": "<h2>Error: The page <b><a href=" +
                page_title +
                ">" +
                page_title +
                "</a></b> already exists</h2>"},
            content_type='text/html')

    f = open(os.path.join("entries", page_title + ".md"), "w")
    f.write(page_contents)
    f.close()
    return wiki(None, page_title)


def edit_page(request):
    """
    render page to edit entry
    """
    page_title = request.GET['page_title'].strip()
    page_contents = util.get_entry(page_title)

    edit_page_token = str(uuid.uuid4())
    f = open(
        os.path.join(
            "entries",
            page_title.lower() +
            "_5ea36f7a-bcde-11ea-b3de-0242ac130004_" +
            edit_page_token +
            ".edit"),
        "w")
    f.close()

    return render(request, "encyclopedia/newedit.html", {
        "title": "Edit Page",
        "heading": "Edit Page",
        "page_title": page_title,
        "page_contents": page_contents,
        "edit_page_token": edit_page_token
    }, content_type='text/html')


def random_page(request):
    """
    random page
    """
    chosen = random.choice(util.list_entries())
    return wiki(None, chosen)
