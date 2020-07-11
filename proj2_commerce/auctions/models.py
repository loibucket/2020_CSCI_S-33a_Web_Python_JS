from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils import Choices
from django.core.validators import MaxValueValidator, MinValueValidator


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
    CAT = Choices(
        ('Watches', 'Watches'),
        ('Video Games', 'Video Games'),
        ('Everything Else', 'Everything Else'),
    )

    title = models.CharField(max_length=64)
    description = models.CharField(max_length=9000)
    image_url = models.URLField(max_length=900)
    is_active = models.BooleanField(default=False)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    current_bid = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey('User', on_delete=models.PROTECT)
    category = models.CharField(max_length=64, choices=CAT)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Id: {self.id} | Time: {self.created_time} | Title: {self.title} | Seller: {self.seller}"


# bids
# 2 digit decimal
class Bid(models.Model):
    listing = models.ForeignKey("Listing", on_delete=models.PROTECT)
    bidder = models.ForeignKey("User", on_delete=models.PROTECT)
    bid_amount = models.DecimalField(max_digits=5, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Id: {self.id} | Time:{self.bid_time} | Bidder:{self.bidder} | Bid:{self.bid_amount}"


# comments
class Comment(models.Model):
    listing = models.ForeignKey("Listing", on_delete=models.PROTECT)
    commenter = models.ForeignKey("User", on_delete=models.PROTECT)
    comment = models.CharField(max_length=9000)
