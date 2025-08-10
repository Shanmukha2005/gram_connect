from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Shopkeeper, Customer, DeliveryPartner, Product, Order

# Custom admin for Shopkeeper (our custom user model)
class ShopkeeperAdmin(UserAdmin):
    model = Shopkeeper
    list_display = ('email', 'name', 'address', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'address', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)

# Register models with admin
admin.site.register(Shopkeeper, ShopkeeperAdmin)
admin.site.register(Customer)
admin.site.register(DeliveryPartner)
admin.site.register(Product)
admin.site.register(Order)