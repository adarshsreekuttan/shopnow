from django.db import models
from core.models import User, Product
from decimal import Decimal

class Address(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    house_name = models.CharField(max_length=150)
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    created_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.cartitem_set.all())
    
    @property
    def tax(self):
        return self.total_price * 0.18

    @property
    def grand_total(self):
        return round(self.total_price + self.tax, 2)

    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.quantity * self.price

class WishList(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.CASCADE)
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

class Reviews(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.CASCADE)
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE)
    rating = models.IntegerField(null=True)
    comment = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        total = sum(item.subtotal for item in self.orderitem_set.all())
        return total or Decimal("0")

    @property
    def tax(self):
        return (self.total_price * Decimal("0.18")).quantize(Decimal("0.00"))

    @property
    def grand_total(self):
        return round(self.total_price + self.tax, 2)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price
    