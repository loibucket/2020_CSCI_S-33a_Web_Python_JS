from django.contrib import admin

from .models import User
from .models import Listing
from .models import Bid
from .models import Comment

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)

# Register your models here.
