from django.contrib import admin
from .models import user, service, items, items_service_price, order, order_item

# Register your models here.
@admin.register(user)
@admin.register(service)
@admin.register(items)
@admin.register(items_service_price)
@admin.register(order)
@admin.register(order_item)
class DefaultAdmin(admin.ModelAdmin):
	pass