from django.urls import path
from . import views

urlpatterns = [
    # Shopkeeper URLs
    path('shopkeeper/login/', views.shopkeeper_login, name='shopkeeper_login'),
    path('shopkeeper/register/', views.shopkeeper_register, name='shopkeeper_register'),
    path('shopkeeper/dashboard/', views.shopkeeper_dashboard, name='shopkeeper_dashboard'),
    path('shopkeeper/add-product/', views.add_product, name='add_product'),
    path('shopkeeper/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('shopkeeper/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('shopkeeper/update-order/<int:order_id>/', views.update_order_status, name='update_order_status'),

    # Customer URLs
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/cart/', views.customer_cart, name='customer_cart'),
    path('customer/orders/', views.customer_orders, name='customer_orders'),
    path('customer/checkout/', views.checkout, name='checkout'),

    # Delivery Partner URLs
    path('delivery/login/', views.delivery_login, name='delivery_login'),
    path('delivery/register/', views.delivery_register, name='delivery_register'),
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/accept-order/<int:order_id>/', views.accept_delivery_order, name='accept_delivery_order'),
    path('delivery/update-status/<int:order_id>/', views.update_delivery_status, name='update_delivery_status'),

    # Logout
    path('logout/', views.logout_view, name='logout'),

    # Test dashboard for debugging
    path('test-dashboard/', views.test_dashboard, name='test_dashboard'),
    path('minimal-dashboard/', views.minimal_dashboard, name='minimal_dashboard'),

    # Home route for root URL
    path('', views.home, name='home'),
]
