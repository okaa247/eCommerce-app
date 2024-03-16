from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Registration)
class Useradmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'otp', 'is_email_verified', 'first_name', 'last_name', 'is_vendor')

