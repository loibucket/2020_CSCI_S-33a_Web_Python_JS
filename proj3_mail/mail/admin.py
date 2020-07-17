from django.contrib import admin

from .models import User
from .models import Email

admin.site.register(User)
admin.site.register(Email)

# Register your models here.
