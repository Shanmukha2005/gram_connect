from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.db import transaction, models
from .models import Shopkeeper, Customer, DeliveryPartner, Product, Order, OrderItem


# ---------- Base Admin with Safe Delete ----------
class SafeDeleteAdmin(admin.ModelAdmin):
    """Base admin that cascades deletes to related objects to avoid FK errors."""
    actions = ['safe_delete_selected']

    def get_actions(self, request):
        """Remove default delete and use our safe cascade delete."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        # Ensure our safe delete action is properly registered
        if 'safe_delete_selected' not in actions:
            actions['safe_delete_selected'] = (
                SafeDeleteAdmin.safe_delete_selected,
                'safe_delete_selected',
                "Delete selected safely (cascade)"
            )
        return actions

    def safe_delete_selected(self, request, queryset):
        """Custom admin action to delete with cascade cleanup."""
        self.delete_queryset(request, queryset)

    def delete_queryset(self, request, queryset):
        try:
            with transaction.atomic():
                model_name = self.model.__name__

                if model_name == "Product":
                    # ✅ FIXED: Don't delete OrderItems - let Django handle it with SET_NULL
                    # The OrderItem.product field will be set to NULL automatically
                    # This preserves order history while removing the product reference
                    count = queryset.count()
                    queryset.delete()  # Django will automatically set OrderItem.product to NULL
                    
                    self.message_user(
                        request,
                        f"Deleted {count} Product(s). Order history preserved with product references set to null.",
                        messages.SUCCESS
                    )
                    return  # Early return to avoid duplicate deletion

                elif model_name == "Order":
                    OrderItem.objects.filter(order__in=queryset).delete()

                elif model_name == "Customer":
                    orders = Order.objects.filter(customer__in=queryset)
                    OrderItem.objects.filter(order__in=orders).delete()
                    orders.delete()

                elif model_name == "Shopkeeper":
                    # Delete orders linked directly to shopkeeper
                    direct_orders = Order.objects.filter(shopkeeper__in=queryset)
                    OrderItem.objects.filter(order__in=direct_orders).delete()
                    direct_orders.delete()

                    # For products: let Django handle SET_NULL for OrderItems automatically
                    products = Product.objects.filter(shopkeeper__in=queryset)
                    products.delete()  # OrderItems will have product set to NULL

                elif model_name == "DeliveryPartner":
                    # Unassign delivery partner from orders
                    Order.objects.filter(delivery_partner__in=queryset).update(delivery_partner=None)

                count = queryset.count()
                queryset.delete()
                self.message_user(
                    request,
                    f"Deleted {count} {model_name}(s) and related records successfully.",
                    messages.SUCCESS
                )
        except Exception as e:
            self.message_user(
                request,
                f"Error deleting {self.model.__name__}: {str(e)}",
                messages.ERROR
            )


# ---------- Shopkeeper Admin ----------
class ShopkeeperAdmin(UserAdmin, SafeDeleteAdmin):
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


# ---------- Product Admin ----------
class ProductAdmin(SafeDeleteAdmin):
    list_display = ('name', 'shopkeeper', 'price', 'quantity', 'has_orders')
    list_filter = ('shopkeeper',)
    search_fields = ('name', 'description')
    
    def has_orders(self, obj):
        return obj.has_orders()
    has_orders.boolean = True
    has_orders.short_description = 'Has Orders'


# ---------- Order Admin ----------  
class OrderAdmin(SafeDeleteAdmin):
    list_display = ('id', 'customer', 'shopkeeper', 'status', 'total_amount', 'date')
    list_filter = ('status', 'date', 'shopkeeper')
    search_fields = ('customer__name', 'shopkeeper__name', 'id')


# ---------- OrderItem Admin (Enhanced to show deleted products) ----------
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'product_name', 'quantity', 'price', 'order_status')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')
    
    def order_id(self, obj):
        return f"Order #{obj.order.id}"
    order_id.short_description = 'Order'
    
    def product_name(self, obj):
        return obj.product.name if obj.product else '[Deleted Product]'
    product_name.short_description = 'Product'
    
    def order_status(self, obj):
        return obj.order.status
    order_status.short_description = 'Order Status'


# ---------- Customer Admin ----------
class CustomerAdmin(SafeDeleteAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')


# ---------- Delivery Partner Admin ----------
class DeliveryPartnerAdmin(SafeDeleteAdmin):
    list_display = ('name', 'email', 'vehicle')
    search_fields = ('name', 'email', 'vehicle')


# ---------- Register Admin Classes ----------
admin.site.register(Shopkeeper, ShopkeeperAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(DeliveryPartner, DeliveryPartnerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)