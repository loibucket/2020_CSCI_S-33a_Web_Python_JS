from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def natural_key(self):
        return (self.username)


class Post(models.Model):
    poster = models.ForeignKey("User", on_delete=models.PROTECT)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Follower(models.Model):
    followee = models.ForeignKey("User", on_delete=models.PROTECT)
    follower = models.ForeignKey(
        "User", on_delete=models.PROTECT, related_name="Follower_follower")


class Like(models.Model):
    post = models.ForeignKey("Post", on_delete=models.PROTECT)
    liker = models.ForeignKey("User", on_delete=models.PROTECT)
