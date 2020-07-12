from django.contrib import admin

from .models import User
from .models import Listing
from .models import Bid
from .models import Comment
from .models import Watchlist


admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)


# Register your models here.
