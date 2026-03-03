from django.db import models
from django.contrib.auth.models import AbstractUser

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
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,null=True,blank=True)

    price = models.IntegerField()
    discount_price = models.IntegerField()

    description = models.CharField(max_length=200)
    stock = models.PositiveIntegerField(default=1)
    available = models.BooleanField(default=True)
    
    sub_category = models.ForeignKey('seller.SubCategory', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    
