from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def natural_key(self):
        return (self.username)


class Game(models.Model):
    player = models.ForeignKey("User", on_delete=models.PROTECT)
    duration = models.DecimalField(
        max_digits=3, decimal_places=1, blank=False)  # seconds played
    # on 1P, player is first mover
    first_mover = models.CharField(blank=False, max_length=10)
    mode = models.CharField(blank=False, max_length=10)  # 1P or 2P
    timestamp = models.DateTimeField(auto_now_add=True)
    winner = models.CharField(blank=False, max_length=10)  # X or O or D
