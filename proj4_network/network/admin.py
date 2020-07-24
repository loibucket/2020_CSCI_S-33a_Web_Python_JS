from django.contrib import admin

# Register your models here.

from .models import User
from .models import Post
from .models import Follower
from .models import Like

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Follower)
admin.site.register(Like)
