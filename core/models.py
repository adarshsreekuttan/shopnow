from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
 
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Product(models.Model):

    seller_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(unique=True,null=True,blank=True)

    price = models.IntegerField()
    discount_price = models.IntegerField()
    STATS_CHOICES=(
        ('pending','PENDING'),
        ('apporved','APPORVED'),
        ('rejected','REJECTED'),
        
    )
    status=models.CharField(max_length=10,null=True)
    description = models.CharField(max_length=200)
    stock = models.PositiveIntegerField(default=1)
    available = models.BooleanField(default=True)
    
    sub_category = models.ForeignKey('core.SubCategory', on_delete=models.CASCADE,null=True,blank=True)
    image=models.ImageField(upload_to='products_image/',null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_activate = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SubCategory(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
