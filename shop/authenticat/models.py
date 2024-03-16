from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.
from django.utils.translation import gettext_lazy as _


class Registration(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, default='000', null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(max_length=254, blank=False, unique=True)
    vendor_application_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved')],
        default='pending'
    )

     # New fields for vendor application
    business_name = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    registration_no = models.CharField(max_length=50, default=00)
    registering_body = models.CharField(max_length=100, null=True, blank=True)
    business_description = models.TextField(null=True, blank=True)
    website_url = models.URLField(blank=True)  # website is optional

    def __str__(self):
        return self.email
    

    def save(self, *args, **kwargs):
        if self.vendor_application_status == 'approved' and not self.is_vendor:
            self.is_vendor = True
        super().save(*args, **kwargs)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Set custom related_name attributes
    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     related_name='registration_groups',
    #     related_query_name='registration_group',
    #     blank=True,
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     related_name='registration_user_permissions',
    #     related_query_name='registration_user_permission',
    #     blank=True,
    # )


# class Registration(AbstractUser):
#     is_email_verified = models.BooleanField(default=False)
#     is_vendor = models.BooleanField(default=False)
#     otp = models.CharField(max_length=6, default=000, null=True)
#     email = models.EmailField(max_length=254, blank=False, unique=True)
#     vendor_application_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), 
#                                                                          ('approved', 'Approved')], 
#                                                                          default='pending')

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']


# class CustomUserManager(BaseUserManager):
#     # Custom user model manager where email is the unique identifiers
#     # for authentication instead of usernames.

#     def create_user(self, email, password, **extra_fields):
#         # Create and save a user with the given email and password.
       
#         if not email:
#             raise ValueError(_("The Email must be set"))
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save()
#         return user
#     def create_superuser(self, email, password, **extra_fields):
#         # Create and save a SuperUser with the given email and password.
        
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         extra_fields.setdefault("is_active", True)
#         if extra_fields.get("is_staff") is not True:
#             raise ValueError(_("Superuser must have is_staff=True."))
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError(_("Superuser must have is_superuser=True."))
#         return self.create_user(email, password, **extra_fields)
# class CustomUser(AbstractUser):
#     username = None
#     first_name = models.CharField(max_length=40, blank=True)
#     email = models.CharField(max_length=60, blank=False, unique=True)
#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = []
#     objects = CustomUserManager()
#     def __str__(self):
#         return self.email    


