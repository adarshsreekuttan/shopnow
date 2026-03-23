from django.db import models

# Create your models here.

class AdminLogin(models.Model):   
    email = models.EmailField()
    password = models.CharField(max_length=10,unique=True)


class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="brands/")
    is_active = models.BooleanField(default=True)


class ProductApproval(models.Model):
    product = models.ForeignKey('core.Product',on_delete=models.CASCADE)
    approved_by = models.ForeignKey('core.User',on_delete=models.SET_NULL,null=True) 
    status = models.CharField(max_length=20) 
    reviewed_at = models.DateTimeField(auto_now_add=True)


class Coupon(models.Model):
    DISCOUNT_TYPE=(
        ('percentage','Precentage'),
        ('fixed','Fixed Amount')
    )
    seller=models.ForeignKey('seller.sellerprofile',on_delete=models.CASCADE,null=True)
    code = models.CharField(max_length=20,unique=True)
    discount_type=models.CharField(max_length=10,choices=DISCOUNT_TYPE,null=True)
    discount_value = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    min_purchase=models.DecimalField(max_digits=10,decimal_places=2,default=0,null=True)
    usage_limit=models.IntegerField(default=1,null=True)
    used_count=models.IntegerField(default=0,null=True)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True)
    valid_to =  models.DateTimeField(null=True)
    approved=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.code}- {self.seller.shop_name}"


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200)
    support_email = models.EmailField()
    contact_number = models.CharField(max_length=20)
    mainrenance_mode = models.BooleanField(default=False)


class Commission(models.Model):
    seller = models.ForeignKey('seller.SellerProfile',on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5,decimal_places=2)          

