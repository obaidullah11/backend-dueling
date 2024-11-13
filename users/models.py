from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, AbstractUser
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import uuid
from django.utils.crypto import get_random_string

from django.contrib.auth.base_user import BaseUserManager

class MyUserManager(BaseUserManager):
    def create_user(self, email, contact, username , password=None, **extra_fields):
        """
        Creates and saves a User with the given email, contact, name, and password.
        """
        if not contact:
            raise ValueError('The Contact field must be set')
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, contact=contact, username=username , **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, contact, username , password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, contact, name, and password.
        """
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        # extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, contact, username , password, **extra_fields)
class CustomUserIDField(models.CharField):
    def pre_save(self, model_instance, add):
        # Generate a 6-digit ID if it's a new instance
        if add:
            return get_random_string(length=6, allowed_chars='0123456789')
        else:
            return super().pre_save(model_instance, add)
# Create your models here.
class User(AbstractUser):
    full_name = models.CharField(max_length=150, null=True, blank=True)
    
    address = models.TextField(null=True, blank=True)
    id = CustomUserIDField(primary_key=True, max_length=6, editable=False)
    
    USER_TYPE_CHOICES = (
        ('client', 'client'),
        ('admin', 'admin'),
        ('super_admin', 'Super Admin'),
    )
    
    contact = models.CharField(max_length=255, blank=True)
    device_token = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    Trade_radius = models.CharField(max_length=6, null=True, blank=True)
    is_registered = models.BooleanField(default=False)
    verify = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    username = models.CharField(max_length=200)  # This is your "name" field in forms
    user_type = models.CharField(max_length=255, default='client', choices=USER_TYPE_CHOICES)
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True)
     
    origin = models.CharField(max_length=200,null=True, blank=True)     
    uid = models.CharField(max_length=200,null=True, blank=True)     
    
       
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    visible_to_user = models.BooleanField(default=True)  # Determines if the user profile is visible
    twitter_url = models.URLField(max_length=255, null=True, blank=True)  # Twitter profile link
    instagram_url = models.URLField(max_length=255, null=True, blank=True)  # Instagram profile link
    facebook_url = models.URLField(max_length=255, null=True, blank=True)  # Facebook profile link

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['contact', 'username']  # Include 'username' for superuser creation

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "User"
