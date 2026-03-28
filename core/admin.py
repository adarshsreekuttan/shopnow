from django.contrib import admin
from .models import User, Product, ProductAttribute


admin.site.register(User)
admin.site.register(Product)
admin.site.register(ProductAttribute)
