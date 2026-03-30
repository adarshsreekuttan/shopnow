from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.db.models import Avg


class User(AbstractUser):

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class Product(models.Model):
    seller = models.ForeignKey('seller.SellerProfile', on_delete=models.CASCADE, null=True, blank=True)
    name=models.CharField(max_length=100,null=True)
    slug = models.SlugField(unique=True,null=True,blank=True)
    price = models.IntegerField()
    discount_price = models.IntegerField()

    STATUS_CHOICES = (
        ('pending', 'PENDING'),
        ('approved', 'APPROVED'),
        ('rejected', 'REJECTED'),
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved=models.BooleanField(default=False)

    description = models.CharField(max_length=200)

    stock = models.PositiveIntegerField(default=1)

    available = models.BooleanField(default=True)    
    category = models.ForeignKey('seller.Category', on_delete=models.CASCADE,null=True,blank=True)
    sub_category = models.ForeignKey('seller.SubCategory', on_delete=models.CASCADE,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_primary_image(self):
        primary=self.productimage_set.filter(is_primary=True).first()        
        return primary or self.productimage_set.first()
    
    def avg_rating(self):
        return round(self.reviews_set.aggregate(Avg('rating'))['rating__avg'] or 0, 1)

    def review_count(self):
        return self.reviews_set.count()