from django.db import models
from core.models import User

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    house_name = models.CharField(max_length=150)
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    created_at = models.DateTimeField(auto_now_add=True)


# class CustomerProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)

# class Category(models.Model):
#     name=models.CharField()
#     is_active=models.BooleanField(default=True)

# class SubCategory(models.Model):
#     Cateory=models.ForeignKey(Category,on_delete=models.CASCADE)
#     name=models.CharField(max_length=100)

# class UserImage(models.Model):
#     user=models.OneToOneField(UserProfile,on_delete=models.CASCADE)
#     user_image=models.ImageField(upload_to="user_images/")    

# class Cart(models.Model):
#     user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
#     created_at=models.DateTimeField(auto_now_add=True)

# class CartItem(models.Model):
#     Cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
#     product=models.ForeignKey(Addproduct,on_delete=models.CASCADE)
#     quantity=models.PositiveIntegerField(default=1)   
    
# class WishList(models.Model):
#     user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
#     created_at=models.DateTimeField(auto_now_add=True)

# class WishListItem(models.Model):
#     wishlist=models.ForeignKey(WishList,on_delete=models.CASCADE)
#     product=models.ForeignKey(Addproduct,on_delete=models.CASCADE)

# class Order(models.Model):
#     order_id=models.AutoField(primary_key=True)
#     user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
#     totalprice=models.CharField(max_digit=10,decimal_place=2)
#     status=models.CharField(max_length=20)
#     payment_method=models.CharField(max_length=20)
#     ordered_at=models.DateTimeField(auto_now_add=True)

# class Review(models.Model):
#     user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
#     product=models.ForeignKey(Addproduct,on_delete=models.CASCADE)
#     rating=models.PositiveIntegerField()
#     comment=models.TextField()
#     is_active=models.BooleanField(default=True)

