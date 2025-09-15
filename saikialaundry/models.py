from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class user(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    user_type = models.CharField(max_length=50, choices=[('Customer', 'Customer'), ('DeliveryPerson', 'DeliveryPerson'), ('Manager', 'Manager')], default='Customer')
    is_staff = models.BooleanField(default=False)
    def __str__(self):
        return self.username

class service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.service_name
class items(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=100)
    def __str__(self):
        return self.item_name
    
class items_service_price(models.Model):
    item_id = models.ForeignKey(items, on_delete=models.CASCADE)
    service_id = models.ForeignKey(service, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.item_id.item_name} - {self.service_id.service_name} : {self.price}"
    
class order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    pickup_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)
    order_status = models.CharField(max_length=50, default='Pending', choices=[('Order Confirmed', 'Order Confirmed'), ('Out for pickup', 'Out for pickup'), ('Picked Up', 'Picked Up'),('In Progress', 'In Progress'),('Out for Delivery', 'Out for Delivery'), ('Cancelled', 'Cancelled')])
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transection_id = models.CharField(max_length=100, null=True, blank=True)
    payment_mode = models.CharField(max_length=50, choices=[('Cash', 'Cash'), ('Online', 'Online')])
    payment_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    delivery_otp = models.CharField(max_length=6, null=True, blank=True)
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
class order_item(models.Model):
    order = models.ForeignKey(order, on_delete=models.CASCADE, related_name='order_items') # added related_name
    item = models.CharField(max_length=100) # This correctly stores the item name as a snapshot
    service_name = models.CharField(max_length=100) # Changed from service_name to match your intent
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Changed name to price and removed editable=False

    def __str__(self):
        # Updated to reflect the new field names
        return f"{self.quantity} x {self.item} ({self.service_name}) for Order {self.order.order_id}"
