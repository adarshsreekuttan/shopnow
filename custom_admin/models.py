from django.db import models
from seller.models import *
from customer.models import *

# Create your models here.

class AdminLogin(models.Model):   
    email = models.EmailField()
    password = models.CharField(max_length=10,unique=True)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_activate = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SubCategory(models.Model):
    Category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="brands/")
    is_active = models.BooleanField(default=True)


class ProductApproval(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE) 
    approved_by = models.ForeignKey(UserProfile,on_delete=models.SET_NULL,null=True) 
    status = models.CharField(max_length=20) 
    reviewed_at = models.DateTimeField(auto_now_add=True)


class Coupon(models.Model):
    code = models.CharField(max_length=20,unique=True)
    discount_percentage = models.DecimalField(max_digits=5,decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to =  models.DateTimeField()


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200)
    support_email = models.EmailField()
    contact_number = models.CharField(max_length=20)
    mainrenance_mode = models.BooleanField(default=False)


class Commission(models.Model):
    seller = models.ForeignKey(SellerProfile,on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5,decimal_places=2)          


