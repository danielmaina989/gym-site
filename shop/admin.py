# shop/admin.py
from django.contrib import admin
from .models import Category, Product, Order, OrderItem
from .models import Refferral, Affilliate

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {"slug": ("name",)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created', 'updated', 'paid']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]

class RefferralInline(admin.TabularInline):
    model = Refferral
    extra = 0  # Don't show extra empty forms

class AffilliateAdmin(admin.ModelAdmin):
    list_display = ['user', 'referral_code', 'total_earnings', 'created_at']
    inlines = [RefferralInline]

admin.site.register(Affilliate, AffilliateAdmin)
admin.site.register(Refferral)