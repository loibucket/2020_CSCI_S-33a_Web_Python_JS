from django.contrib.auth.models import AbstractUser
from django.db import models

# We’ve started you with a User model that represents each user of the application.
# Because it inherits from AbstractUser, it will already have fields for a username,
# email, password, etc., but you’re welcome to add new fields to the User class if
# there is additional information about a user that you wish to represent.
class User(AbstractUser):
    first_name = models.IntegerField(null=True)
    last_name = models.IntegerField(null=True)

# Models: Your application should have at least three models in addition to the
# User model: one for auction listings, one for bids, and one for comments made
# on auction listings. It’s up to you to decide what fields each model should
# have, and what the types of those fields should be. You may have additional
# models if you would like.

class Listing(models.Model):
    auction_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=300)
    image = models.URLField(max_length=200)

# bids
# 2 digit decimal
class Bid(models.Model):
    auction_id = models.AutoField(primary_key=True)
    start_bid = models.DecimalField(max_digits=9, decimal_places=2)
    curr_bid = models.DecimalField(max_digits=9, decimal_places=2)
    n_bids = models.IntegerField()

# comments
class Comment(models.Model):
    auction_id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=300)