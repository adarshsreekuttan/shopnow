from django.db import models
from django.utils.text import slugify
from core.models import User

class SellerProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,related_name='seller_profile')
    shop_name=models.CharField(max_length=100)
    address=models.TextField()
    pincode=models.CharField(max_length=6)
    state=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    gst_number=models.CharField(max_length=100,blank=True,null=True)
    is_verified=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    approved=models.BooleanField(default=False)
    shop_logo=models.ImageField(upload_to="seller_profile_pic/",null=True)

class Category(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True, blank=True)
    image=models.ImageField(upload_to="category_icons/", null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Attribute(models.Model):
    name=models.CharField(max_length=100)
  
    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey('seller.Category', on_delete=models.CASCADE)
    is_active = models.BooleanField(default= True)
    slug = models.SlugField(unique=True, blank=True)
    attributes = models.ManyToManyField(Attribute,related_name='subcategories', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey('core.Product',on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/")
    is_primary = models.BooleanField(default=False)   

class SellerNotification(models.Model):
    TYPE_CHOICES = (
        ('order', 'Order Update'),
        ('stock', 'Stock Alert'),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.seller.username} - {self.title}"
