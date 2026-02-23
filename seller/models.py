from django.db import models

# Create your models here.
class SellerProfile(models.Model):
    sellerid=models.AutoField(primary_key=True)
    shopname=models.CharField(max_length=100)
    onwername=models.CharField(max_length=100)
    password=models.CharField(max_length=150)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=100,unique=True)
    address=models.TextField()
    pincode=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    gst_number=models.CharField(max_length=100,blank=True,null=True)
    is_verified=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
class Product(models.Model):
    product_id=models.AutoField(primary_key=True)
    product_name=models.CharField(max_length=100)
    product_price=models.DecimalField(max_digits=100,decimal_places=2)
    product_description=models.TextField(max_length=100)
    product_review=models.TextField(null=True)
    product_rating=models.DecimalField(decimal_place=1,max_digit=2,default=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="product_images/")
  
class Notification(models.Model):
    seller=models.ForeignKey(SellerProfile,on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Discount(models.Model):
    code=models.CharField(max_length=50, unique=True)
    percentage=models.DecimalField()
    valid_from=models.DecimalField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)