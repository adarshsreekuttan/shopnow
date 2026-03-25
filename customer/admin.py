from django.contrib import admin
from .models import Order, OrderItem, Reviews

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Reviews)