from django.contrib import admin
from .models import Category, SubCategory, ProductImage,Attribute,AttributeValues,ProductVarient
from seller.models import SellerProfile

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(ProductImage)
admin.site.register(SellerProfile)
admin.site.register(Attribute)
admin.site.register(AttributeValues)
admin.site.register(ProductVarient)
