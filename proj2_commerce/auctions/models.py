from django.contrib.auth.models import AbstractUser
from django.db import models


# We’ve started you with a User model that represents each user of the application.
# Because it inherits from AbstractUser, it will already have fields for a username,
# email, password, etc., but you’re welcome to add new fields to the User class if
# there is additional information about a user that you wish to represent.

class User(AbstractUser):
    pass

# Models: Your application should have at least three models in addition to the
# User model: one for auction listings, one for bids, and one for comments made
# on auction listings. It’s up to you to decide what fields each model should
# have, and what the types of those fields should be. You may have additional
# models if you would like.

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=9000)
    image_url = models.URLField(max_length=900)
    is_active = models.BooleanField(default=False)
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2)
    current_bid = models.DecimalField(max_digits=5, decimal_places=2)
    seller = models.ForeignKey('User', on_delete=models.PROTECT)

# bids
# 2 digit decimal
class Bid(models.Model):
    item_number = models.ForeignKey(Listing, on_delete=models.PROTECT)
    bidder = models.ForeignKey(User, on_delete=models.PROTECT)
    bid_amount = models.DecimalField(max_digits=5, decimal_places=2)
    n_bids = models.IntegerField()

# comments
class Comment(models.Model):
    item_number = models.ForeignKey(Listing, on_delete=models.PROTECT)
    commenter = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.CharField(max_length=9000)
