from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from .models import Shopkeeper, Customer, DeliveryPartner, Product, Order

# --- Shopkeeper Views ---

def home(request):
    return render(request, 'home.html')

def shopkeeper_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            shopkeeper = Shopkeeper.objects.get(email=email)
            if shopkeeper.check_password(password):
                # Store shopkeeper info in session
                request.session['shopkeeper_id'] = shopkeeper.id
                request.session['user_type'] = 'shopkeeper'
                messages.success(request, 'Login successful!')
                return redirect('shopkeeper_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except Shopkeeper.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'shopkeeper/login.html')

def shopkeeper_register(request):
    if request.method == 'POST':
        shop_name = request.POST.get('shop_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        
        # Check if shopkeeper already exists
        if Shopkeeper.objects.filter(email=email).exists():
            messages.error(request, 'A shop with this email already exists.')
            return render(request, 'shopkeeper/register.html')
        
        # Create new shopkeeper
        shopkeeper = Shopkeeper.objects.create_user(
            email=email,
            name=shop_name,
            address=address,
            password=password
        )
        
        messages.success(request, 'Shop registered successfully! Please login.')
        return redirect('shopkeeper_login')
    
    return render(request, 'shopkeeper/register.html')

def shopkeeper_dashboard(request):
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login to access dashboard.')
        return redirect('shopkeeper_login')
    
    try:
        shopkeeper_id = request.session['shopkeeper_id']
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
        
        # Fetch products and orders for this shopkeeper
        products = Product.objects.filter(shopkeeper=shopkeeper)
        orders = Order.objects.filter(shopkeeper=shopkeeper).order_by('-date')
        
        # Count pending orders specifically
        pending_orders_count = orders.filter(status='pending').count()
        
        context = {
            'shopkeeper': shopkeeper,
            'products': products,
            'orders': orders,
            'pending_orders_count': pending_orders_count,
        }
        
        return render(request, 'shopkeeper/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Dashboard error: {str(e)}')
        return redirect('shopkeeper_login')

def add_product(request):
    """Handle product creation for shopkeepers"""
    
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to add products.')
        return redirect('shopkeeper_login')
    
    if request.method == 'POST':
        try:
            shopkeeper_id = request.session['shopkeeper_id']
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            
            # Get form data
            name = request.POST.get('name')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            image = request.POST.get('image')
            description = request.POST.get('description')
            
            # Validate required fields
            if not name or not price or not quantity:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('shopkeeper_dashboard')
            
            # Create new product
            product = Product.objects.create(
                shopkeeper=shopkeeper,
                name=name,
                price=float(price),
                quantity=quantity,
                image=image if image else '',
                description=description if description else ''
            )
            
            messages.success(request, f'Product "{name}" added successfully!')
            
        except ValueError as e:
            messages.error(request, 'Please enter a valid price.')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    return redirect('shopkeeper_dashboard')

def edit_product(request, product_id):
    """Handle product editing for shopkeepers"""
    
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to edit products.')
        return redirect('shopkeeper_login')
    
    if request.method == 'POST':
        try:
            shopkeeper_id = request.session['shopkeeper_id']
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            
            # Get the product and verify ownership
            product = Product.objects.get(id=product_id, shopkeeper=shopkeeper)
            
            # Get form data
            name = request.POST.get('name')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            image = request.POST.get('image')
            description = request.POST.get('description')
            
            # Validate required fields
            if not name or not price or not quantity:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('shopkeeper_dashboard')
            
            # Update product
            product.name = name
            product.price = float(price)
            product.quantity = quantity
            product.image = image if image else ''
            product.description = description if description else ''
            product.save()
            
            messages.success(request, f'Product "{name}" updated successfully!')
            
        except Product.DoesNotExist:
            messages.error(request, 'Product not found or you do not have permission to edit it.')
        except ValueError as e:
            messages.error(request, 'Please enter a valid price.')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    return redirect('shopkeeper_dashboard')

def delete_product(request, product_id):
    """Handle product deletion for shopkeepers"""
    
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to delete products.')
        return redirect('shopkeeper_login')
    
    if request.method == 'POST':
        try:
            shopkeeper_id = request.session['shopkeeper_id']
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            
            # Get the product and verify ownership
            product = Product.objects.get(id=product_id, shopkeeper=shopkeeper)
            product_name = product.name
            
            # Delete the product
            product.delete()
            
            messages.success(request, f'Product "{product_name}" deleted successfully!')
            
        except Product.DoesNotExist:
            messages.error(request, 'Product not found or you do not have permission to delete it.')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
    
    return redirect('shopkeeper_dashboard')

def update_order_status(request, order_id):
    """Handle order status updates for shopkeepers"""
    
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to update orders.')
        return redirect('shopkeeper_login')
    
    if request.method == 'POST':
        try:
            shopkeeper_id = request.session['shopkeeper_id']
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            
            # Get the order and verify ownership
            order = Order.objects.get(id=order_id, shopkeeper=shopkeeper)
            new_status = request.POST.get('status')
            
            # Validate the new status
            valid_statuses = ['pending', 'confirmed', 'ready', 'assigned', 'out_for_delivery', 'delivered', 'cancelled']
            if new_status not in valid_statuses:
                messages.error(request, 'Invalid order status.')
                return redirect('shopkeeper_dashboard')
            
            # Update the order status
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Provide appropriate success message
            if new_status == 'confirmed':
                messages.success(request, f'Order #{order_id} confirmed successfully!')
            elif new_status == 'ready':
                messages.success(request, f'Order #{order_id} marked as ready for pickup!')
            elif new_status == 'cancelled':
                messages.success(request, f'Order #{order_id} cancelled successfully.')
            else:
                messages.success(request, f'Order #{order_id} status updated to {new_status.title()}.')
            
        except Order.DoesNotExist:
            messages.error(request, 'Order not found or you do not have permission to update it.')
        except Exception as e:
            messages.error(request, f'Error updating order status: {str(e)}')
    
    return redirect('shopkeeper_dashboard')

# --- Customer Views ---

def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password):
                # Store customer info in session
                request.session['customer_id'] = customer.id
                request.session['user_type'] = 'customer'
                messages.success(request, 'Login successful!')
                return redirect('customer_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'customer/login.html')

def customer_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        
        # Check if customer already exists
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'customer/register.html')
        
        # Create new customer
        customer = Customer.objects.create(
            name=full_name,
            email=email,
            phone=phone,
            password=make_password(password)
        )
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('home')
    
    return render(request, 'customer/register.html')

def customer_dashboard(request):
    # Check if logged in as customer
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to access dashboard.')
        return redirect('customer_login')
    
    try:
        customer_id = request.session['customer_id']
        customer = Customer.objects.get(id=customer_id)
        
        # Fetch all products from all shopkeepers
        products = Product.objects.all().order_by('-id')
        
        # Fetch orders for this customer
        orders = Order.objects.filter(customer=customer).order_by('-date')
        
        context = {
            'customer': customer,
            'products': products,
            'orders': orders,
        }
        
        return render(request, 'customer/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Dashboard error: {str(e)}')
        return redirect('customer_login')

def customer_cart(request):
    # Check if logged in as customer
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to access cart.')
        return redirect('customer_login')
    
    context = {
        'cart_items': [],  # TODO: Implement cart functionality
    }
    return render(request, 'customer/cart.html', context)

def customer_orders(request):
    # Check if logged in as customer
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to access orders.')
        return redirect('customer_login')
    
    customer_id = request.session['customer_id']
    orders = Order.objects.filter(customer_id=customer_id).order_by('-date')
    
    context = {
        'orders': orders,
    }
    return render(request, 'customer/orders.html', context)

def checkout(request):
    """Handle checkout process and create orders"""
    
    # Check if logged in as customer
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to place orders.')
        return redirect('customer_login')
    
    if request.method == 'POST':
        try:
            import json
            from datetime import datetime
            
            customer_id = request.session['customer_id']
            customer = Customer.objects.get(id=customer_id)
            
            # Get form data
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            payment_method = request.POST.get('payment_method')
            instructions = request.POST.get('instructions', '')
            cart_data = request.POST.get('cart_data')
            
            # Validate required fields
            if not all([full_name, phone, address, payment_method, cart_data]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('customer_dashboard')
            
            # Parse cart data
            try:
                cart_items = json.loads(cart_data)
                if not cart_items:
                    messages.error(request, 'Your cart is empty.')
                    return redirect('customer_dashboard')
            except json.JSONDecodeError:
                messages.error(request, 'Invalid cart data.')
                return redirect('customer_dashboard')
            
            # Group items by shopkeeper to create separate orders
            orders_by_shop = {}
            for item in cart_items:
                try:
                    product = Product.objects.get(id=item['id'])
                    shopkeeper = product.shopkeeper
                    
                    if shopkeeper.id not in orders_by_shop:
                        orders_by_shop[shopkeeper.id] = {
                            'shopkeeper': shopkeeper,
                            'items': [],
                            'total': 0
                        }
                    
                    item_total = float(item['price']) * int(item['quantity'])
                    orders_by_shop[shopkeeper.id]['items'].append({
                        'product': product,
                        'quantity': int(item['quantity']),
                        'price': float(item['price']),
                        'total': item_total
                    })
                    orders_by_shop[shopkeeper.id]['total'] += item_total
                    
                except Product.DoesNotExist:
                    continue
            
            # Create orders for each shopkeeper
            created_orders = []
            for shop_data in orders_by_shop.values():
                # Create the order
                order = Order.objects.create(
                    customer=customer,
                    shopkeeper=shop_data['shopkeeper'],
                    delivery_name=full_name,
                    delivery_phone=phone,
                    delivery_address=address,
                    payment_method=payment_method,
                    special_instructions=instructions,
                    total_amount=shop_data['total'],
                    status='pending',
                    date=datetime.now()
                )
                
                # Create order items
                for item_data in shop_data['items']:
                    # Check if OrderItem model exists, if not we'll create it
                    try:
                        from .models import OrderItem
                        OrderItem.objects.create(
                            order=order,
                            product=item_data['product'],
                            quantity=item_data['quantity'],
                            price=item_data['total']
                        )
                    except ImportError:
                        # If OrderItem doesn't exist, we'll store items as a simple field
                        # This is a fallback - ideally OrderItem model should exist
                        pass
                
                created_orders.append(order)
            
            # Clear the cart (this will be done via JavaScript)
            order_count = len(created_orders)
            total_amount = sum(order.total_amount for order in created_orders)
            
            if order_count == 1:
                messages.success(request, f'Order placed successfully! Order total: ₹{total_amount:.2f}')
            else:
                messages.success(request, f'{order_count} orders placed successfully! Total: ₹{total_amount:.2f}')
            
            # Redirect back to dashboard
            return redirect('customer_dashboard')
            
        except Customer.DoesNotExist:
            messages.error(request, 'Customer account not found.')
            return redirect('customer_login')
        except Exception as e:
            messages.error(request, f'Error processing checkout: {str(e)}')
            return redirect('customer_dashboard')
    
    # If not POST, redirect to dashboard
    return redirect('customer_dashboard')

# --- Minimal Test Dashboard (for debugging) ---
def minimal_dashboard(request):
    """Minimal dashboard with no session checks or database queries"""
    context = {
        'test_message': 'Minimal dashboard is working!',
        'customer': {'name': 'Test User', 'email': 'test@example.com', 'id': 1},
        'products': []
    }
    return render(request, 'customer/dashboard_simple.html', context)

# --- Delivery Partner Views ---

def delivery_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            delivery_partner = DeliveryPartner.objects.get(email=email)
            if check_password(password, delivery_partner.password):
                # Store delivery partner info in session
                request.session['delivery_id'] = delivery_partner.id
                request.session['user_type'] = 'delivery'
                messages.success(request, 'Login successful!')
                return redirect('delivery_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except DeliveryPartner.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'delivery/login.html')

def delivery_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        vehicle_type = request.POST.get('vehicle_type')
        
        # Check if delivery partner already exists
        if DeliveryPartner.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'delivery/register.html')
        
        # Create new delivery partner
        delivery_partner = DeliveryPartner.objects.create(
            name=full_name,
            email=email,
            vehicle=vehicle_type,
            password=make_password(password)
        )
        
        messages.success(request, 'Application submitted successfully! Please login.')
        return redirect('home')
    
    return render(request, 'delivery/register.html')

def delivery_dashboard(request):
    # Check if logged in as delivery partner
    if 'delivery_id' not in request.session or request.session.get('user_type') != 'delivery':
        messages.error(request, 'Please login to access dashboard.')
        return redirect('delivery_login')
    
    try:
        delivery_id = request.session['delivery_id']
        delivery_partner = DeliveryPartner.objects.get(id=delivery_id)
        
        # Fetch available orders for delivery (orders that are ready or confirmed)
        available_orders = Order.objects.filter(
            status__in=['confirmed', 'ready']
        ).order_by('-date')
        
        # Fetch orders assigned to this delivery partner
        assigned_orders = Order.objects.filter(
            delivery_partner=delivery_partner
        ).order_by('-date')
        
        context = {
            'delivery_partner': delivery_partner,
            'available_orders': available_orders,
            'assigned_orders': assigned_orders,
        }
        
        return render(request, 'delivery/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Dashboard error: {str(e)}')
        return redirect('delivery_login')

def accept_delivery_order(request, order_id):
    """Handle delivery partner accepting an order for delivery"""
    
    # Check if logged in as delivery partner
    if 'delivery_id' not in request.session or request.session.get('user_type') != 'delivery':
        messages.error(request, 'Please login as delivery partner to accept orders.')
        return redirect('delivery_login')
    
    if request.method == 'POST':
        try:
            delivery_id = request.session['delivery_id']
            delivery_partner = DeliveryPartner.objects.get(id=delivery_id)
            
            # Get the order and verify it's available for delivery
            order = Order.objects.get(id=order_id)
            
            # Check if order is available for delivery
            if order.status not in ['ready']:
                messages.error(request, 'This order is not available for delivery.')
                return redirect('delivery_dashboard')
            
            # Check if order is already assigned to another delivery partner
            if order.delivery_partner and order.delivery_partner != delivery_partner:
                messages.error(request, 'This order is already assigned to another delivery partner.')
                return redirect('delivery_dashboard')
            
            # Assign the order to this delivery partner
            order.delivery_partner = delivery_partner
            order.status = 'assigned'
            order.save()
            
            messages.success(request, f'Order #{order_id} accepted successfully! You can now start the delivery.')
            
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
        except DeliveryPartner.DoesNotExist:
            messages.error(request, 'Delivery partner account not found.')
        except Exception as e:
            messages.error(request, f'Error accepting order: {str(e)}')
    
    return redirect('delivery_dashboard')

def update_delivery_status(request, order_id):
    """Handle delivery status updates (start delivery, mark delivered)"""
    
    # Check if logged in as delivery partner
    if 'delivery_id' not in request.session or request.session.get('user_type') != 'delivery':
        messages.error(request, 'Please login as delivery partner to update delivery status.')
        return redirect('delivery_login')
    
    if request.method == 'POST':
        try:
            delivery_id = request.session['delivery_id']
            delivery_partner = DeliveryPartner.objects.get(id=delivery_id)
            
            # Get the order and verify it's assigned to this delivery partner
            order = Order.objects.get(id=order_id, delivery_partner=delivery_partner)
            new_status = request.POST.get('status')
            
            # Validate the new status
            valid_delivery_statuses = ['assigned', 'out_for_delivery', 'delivered']
            if new_status not in valid_delivery_statuses:
                messages.error(request, 'Invalid delivery status.')
                return redirect('delivery_dashboard')
            
            # Update the order status
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Provide appropriate success message
            if new_status == 'out_for_delivery':
                messages.success(request, f'Order #{order_id} marked as out for delivery!')
            elif new_status == 'delivered':
                messages.success(request, f'Order #{order_id} marked as delivered successfully!')
            else:
                messages.success(request, f'Order #{order_id} status updated to {new_status.title()}.')
            
        except Order.DoesNotExist:
            messages.error(request, 'Order not found or not assigned to you.')
        except Exception as e:
            messages.error(request, f'Error updating delivery status: {str(e)}')
    
    return redirect('delivery_dashboard')

# --- Test Dashboard (for debugging) ---
def test_dashboard(request):
    """Simple test dashboard to check if template rendering works"""
    context = {
        'test_message': 'Dashboard is working!',
        'user_session': dict(request.session),
    }
    return render(request, 'test_dashboard.html', context)

# --- Logout view (shared) ---

from django.contrib.auth import logout

def logout_view(request):
    # Clear all session data
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
