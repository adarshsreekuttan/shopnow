from django.db import models
from seller.models import *

# Create your models here.
class UserProfile(models.Model):
    user_id=models.CharField(max_length=50,primary_key=True)
    username=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=15,unique=True)
    address=models.TextField()
    pincode=models.CharField(max_length=10)
    state=models.CharField(max_length=100)
    city=models.CharField(max_length=100)

class Category(models.Model):
    name=models.CharField()
    is_active=models.BooleanField(default=True)

class SubCategory(models.Model):
    Cateory=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)

class UserImage(models.Model):
    user=models.OneToOneField(UserProfile,on_delete=models.CASCADE)
    user_image=models.ImageField(upload_to="user_images/")    

class Cart(models.Model):
    user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    Cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)   
    
class WishList(models.Model):
    user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

class WishListItem(models.Model):
    wishlist=models.ForeignKey(WishList,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)

class Order(models.Model):
    order_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    totalprice=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=20)
    payment_method=models.CharField(max_length=20)
    ordered_at=models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    rating=models.PositiveIntegerField()
    comment=models.TextField()
    is_active=models.BooleanField(default=True)