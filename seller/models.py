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
        return f"{self.attributes} - {self.name}"
    
class ProductImage(models.Model):
    product = models.ForeignKey('core.Product',on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/")
    is_primary = models.BooleanField(default=False)


      
class AttributeValues(models.Model):
    attribute=models.ForeignKey(Attribute,on_delete=models.CASCADE)
    value=models.CharField(max_length=100)
    def __str__(self):
        return f"{self.attribute.name}-{self.value}"
     
class ProductVarient(models.Model):
     product=models.ForeignKey('core.Product',on_delete=models.CASCADE)
     price=models.DecimalField(max_digits=10,decimal_places=2)    
     stock=models.IntegerField()  
     attribute_values=models.ManyToManyField(AttributeValues)  
     
     def __str__(self):
         return f"{self.product.name} Variant"
     
class VariantImage(models.Model):
    variant=models.ForeignKey(ProductVarient,on_delete=models.CASCADE) 
    image=models.ImageField(upload_to="variants/")    

# class Notification(models.Model):
#     seller=models.ForeignKey(SellerProfile,on_delete=models.CASCADE)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

# class Discount(models.Model):
#     code=models.CharField(max_length=50, unique=True)
#     percentage=models.DecimalField()
#     valid_from=models.DecimalField()
#     valid_to = models.DateTimeField()
#     is_active = models.BooleanField(default=True)