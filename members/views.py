from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Shopkeeper, Customer, DeliveryPartner, Product, Order, OrderItem
import json
from datetime import datetime
from .ai_bot import generate_ai_reply

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
            image = request.FILES.get('image')
            description = request.POST.get('description', '')
            
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
                image=image,
                description=description
            )
            
            messages.success(request, f'Product "{name}" added successfully!')
            
        except ValueError as e:
            messages.error(request, 'Please enter a valid price.')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    return redirect('shopkeeper_dashboard')

def edit_product(request, product_id):
    
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to edit products.')
        return redirect('shopkeeper_login')
    
    # Get the product and verify ownership
    shopkeeper_id = request.session['shopkeeper_id']
    shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    product = get_object_or_404(Product, id=product_id, shopkeeper=shopkeeper)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            description = request.POST.get('description', '')
            image = request.FILES.get('image')
            
            # Validate required fields
            if not name or not price or not quantity:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('edit_product', product_id=product_id)
            
            # Update product
            product.name = name
            product.price = float(price)
            product.quantity = quantity
            product.description = description
            if image:  # Only update image if a new one was provided
                product.image = image
            product.save()
            
            messages.success(request, f'Product "{name}" updated successfully!')
            return redirect('shopkeeper_dashboard')
            
        except ValueError:
            messages.error(request, 'Please enter a valid price.')
            return redirect('edit_product', product_id=product_id)
    
    # For GET request, show the edit form
    return render(request, 'shopkeeper/edit_product.html', {'product': product})

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
            product = get_object_or_404(Product, id=product_id, shopkeeper=shopkeeper)
            product_name = product.name
            
            # Delete the product
            product.delete()
            
            messages.success(request, f'Product "{product_name}" deleted successfully!')
            
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
            order = get_object_or_404(Order, id=order_id, shopkeeper=shopkeeper)
            new_status = request.POST.get('status')
            
            # Validate the new status
            valid_statuses = ['pending', 'confirmed', 'ready', 'assigned', 'out_for_delivery', 'delivered', 'cancelled']
            if new_status not in valid_statuses:
                messages.error(request, 'Invalid order status.')
                return redirect('shopkeeper_dashboard')
            
            # Update the order status
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
    
    try:
        customer = Customer.objects.get(id=request.session['customer_id'])
    except Customer.DoesNotExist:
        messages.error(request, 'Customer account not found.')
        return redirect('customer_login')

    context = {
        'cart_items': [],  # kept for compatibility, items are client-side
        'customer': customer,
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
                    OrderItem.objects.create(
                        order=order,
                        product=item_data['product'],  # can be null later if deleted
                        product_name=item_data['product'].name,  # store name permanently
                        quantity=item_data['quantity'],
                        price=item_data['product'].price  # store price at time of order
                    )

                
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

# --- Lightweight JSON APIs for Bot ---

@csrf_exempt
def api_customer_login(request):
    """JSON login for customers; establishes session on success."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        if not email or not password:
            return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)
        customer = Customer.objects.get(email=email)
        if not check_password(password, customer.password):
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
        request.session['customer_id'] = customer.id
        request.session['user_type'] = 'customer'
        return JsonResponse({'success': True, 'customer': {'id': customer.id, 'name': customer.name, 'email': customer.email}})
    except Customer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Account not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_customer_register(request):
    """JSON register for customers; creates account and logs in."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        phone = (data.get('phone') or '').strip()
        password = data.get('password') or ''
        if not all([name, email, phone, password]):
            return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
        if Customer.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already in use'}, status=409)
        customer = Customer.objects.create(name=name, email=email, phone=phone, password=make_password(password))
        request.session['customer_id'] = customer.id
        request.session['user_type'] = 'customer'
        return JsonResponse({'success': True, 'customer': {'id': customer.id, 'name': customer.name, 'email': customer.email}})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def api_products(request):
    """Public JSON products API. Supports alphabetical list or shop-wise grouping and a simple search query."""
    mode = (request.GET.get('mode') or 'alphabetical').lower()
    query = (request.GET.get('q') or '').strip()
    try:
        products_qs = Product.objects.select_related('shopkeeper')
        if query:
            # Simple contains search on product name and shop name
            products_qs = products_qs.filter(Q(name__icontains=query) | Q(shopkeeper__name__icontains=query))
        if mode == 'shopwise':
            # Group by shop; each group sorted by product name
            response_payload = []
            by_shop = {}
            for p in products_qs:
                shop_name = p.shopkeeper.name if p.shopkeeper else 'Unknown Shop'
                by_shop.setdefault(shop_name, []).append(p)
            for shop_name, shop_products in by_shop.items():
                shop_products_sorted = sorted(shop_products, key=lambda x: x.name.lower())
                response_payload.append({
                    'shop': shop_name,
                    'products': [
                        {
                            'id': sp.id,
                            'name': sp.name,
                            'price': float(sp.price),
                            'quantity': sp.quantity,
                            'description': sp.description,
                            'image_url': (sp.image.url if sp.image else ''),
                        }
                        for sp in shop_products_sorted
                    ]
                })
            # Sort groups by shop name for consistency
            response_payload.sort(key=lambda g: g['shop'].lower())
            return JsonResponse({'success': True, 'mode': 'shopwise', 'groups': response_payload})
        else:
            # Alphabetical list by product name
            products_sorted = products_qs.order_by('name')
            items = []
            for p in products_sorted:
                items.append({
                    'id': p.id,
                    'name': p.name,
                    'price': float(p.price),
                    'quantity': p.quantity,
                    'description': p.description,
                    'shop': (p.shopkeeper.name if p.shopkeeper else 'Unknown Shop'),
                    'image_url': (p.image.url if p.image else ''),
                })
            return JsonResponse({'success': True, 'mode': 'alphabetical', 'products': items})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def ai_chat(request):
    """AI Chat endpoint for the generative AI bot."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '').strip()
        history = data.get('history') or []  # optional chat history array of {role, content}
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
        
        # Build minimal messages for the generator
        messages = []
        for item in history[-5:]:  # keep it short
            role = item.get('role')
            content = (item.get('content') or '').strip()
            if role in ('user','assistant') and content:
                messages.append({'role': role, 'content': content})
        messages.append({'role': 'user', 'content': user_message})
        
        # Try model-based generation first
        bot_reply = generate_ai_reply(messages)
        if not bot_reply:
            bot_reply = generate_ai_response(user_message)
        
        return JsonResponse({
            'success': True,
            'response': bot_reply,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def generate_ai_response(user_message):
    """Generate AI response based on user query."""
    message_lower = user_message.lower()
    
    # E-commerce specific responses with more context
    if any(word in message_lower for word in ['order', 'track', 'delivery', 'shipping']):
        if 'track' in message_lower:
            return "To track your order, go to your dashboard and click on 'Orders'. You'll see all your orders with their current status. For real-time delivery updates, our delivery partners will also contact you directly."
        elif 'delivery' in message_lower or 'shipping' in message_lower:
            return "We offer multiple delivery options: Standard delivery (2-3 days), Express delivery (same day/next day), and Scheduled delivery (choose your preferred time). Delivery fees vary by location and speed. Where are you located?"
        else:
            return "I can help you with order tracking and delivery information. You can check your order status in the Orders section of your dashboard. For delivery updates, please contact our delivery partners."
    
    elif any(word in message_lower for word in ['product', 'item', 'goods', 'merchandise']):
        if 'find' in message_lower or 'search' in message_lower:
            return "I can help you find products! You can browse our catalog by category, search for specific items, or view products by shop. What type of product are you looking for? I can suggest categories like electronics, clothing, food, home & kitchen, etc."
        else:
            return "Our platform has thousands of products across various categories. You can browse by category, search by name, or explore shops. What interests you today?"
    
    elif any(word in message_lower for word in ['price', 'cost', 'expensive', 'cheap', 'budget']):
        if 'budget' in message_lower:
            return "We have products for every budget! You can filter by price range, look for deals and discounts, or check out our budget-friendly categories. What's your budget range?"
        else:
            return "Our prices are competitive and vary by product and shop. You can view prices on individual product pages, and many shops offer discounts and deals. Is there a specific product you'd like to know about?"
    
    elif any(word in message_lower for word in ['payment', 'pay', 'card', 'cash', 'online']):
        if 'secure' in message_lower or 'safe' in message_lower:
            return "All our online payments are completely secure! We use industry-standard encryption and never store your payment details. We support credit/debit cards, UPI, net banking, and digital wallets."
        else:
            return "We support multiple payment methods including cash on delivery and online payments. You can choose your preferred payment method during checkout. All online transactions are secure and encrypted."
    
    elif any(word in message_lower for word in ['return', 'refund', 'exchange', 'problem']):
        if 'return' in message_lower:
            return "Most products have a 7-14 day return policy. For returns, go to your order history, select the item, and click 'Return'. You can also contact the shop directly or our customer support for assistance."
        elif 'refund' in message_lower:
            return "Refunds are processed within 3-5 business days after we receive your return. The money will be credited back to your original payment method. Need help with a specific return?"
        else:
            return "For returns, refunds, or exchanges, please contact the shop directly or reach out to our customer support. Most shops have a 7-14 day return policy depending on the product."
    
    elif any(word in message_lower for word in ['shop', 'store', 'seller', 'vendor']):
        if 'trusted' in message_lower or 'verified' in message_lower:
            return "All our shops are thoroughly verified! We check business licenses, customer reviews, and product quality. Each shop has ratings and reviews from customers. You can also see shop verification badges."
        else:
            return "We have many trusted shops and sellers on our platform. Each shop is verified and rated by customers. You can browse products by shop or search for specific shops in your area."
    
    elif any(word in message_lower for word in ['account', 'profile', 'settings', 'personal']):
        return "You can manage your account settings, update your profile, and view your order history from your dashboard. Need help with something specific? I can guide you through account management."
    
    elif any(word in message_lower for word in ['help', 'support', 'assist', 'guide']):
        return "I'm here to help! I can assist with shopping, orders, payments, returns, and general questions about our platform. What would you like to know more about? You can also use the quick tip buttons above for common questions."
    
    elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! Welcome to Gram Connect. I'm your AI shopping assistant. I can help you find products, track orders, understand our services, and much more. How can I assist you today?"
    
    elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're welcome! I'm happy to help. Is there anything else you'd like to know about our platform or services?"
    
    elif any(word in message_lower for word in ['food', 'groceries', 'vegetables', 'fruits']):
        if 'fresh' in message_lower:
            return "We partner with local farmers and markets to bring you the freshest produce! Many food items are available for same-day delivery. You can also schedule delivery for specific times."
        else:
            return "We have a great selection of fresh food, groceries, vegetables, and fruits from local shops and markets. Many items are available for same-day delivery. What specific food items are you looking for?"
    
    elif any(word in message_lower for word in ['electronics', 'gadgets', 'phones', 'laptops']):
        if 'warranty' in message_lower:
            return "All our electronics come with manufacturer warranty and our platform guarantee. We only work with authorized dealers. Most electronics have 1-2 year warranty coverage."
        else:
            return "Our electronics section includes phones, laptops, accessories, and other gadgets from authorized dealers. All electronics come with warranty and return policies. What type of electronic device interests you?"
    
    elif any(word in message_lower for word in ['clothing', 'fashion', 'shoes', 'accessories']):
        if 'size' in message_lower:
            return "Most clothing shops provide detailed size guides and measurements. You can also check customer reviews for sizing advice. Many shops offer free returns if the size doesn't fit."
        else:
            return "We offer a wide range of clothing, fashion items, shoes, and accessories for all ages and styles. Many shops provide size guides and styling tips. What fashion category are you exploring?"
    
    elif any(word in message_lower for word in ['home', 'kitchen', 'furniture', 'decor']):
        return "Our home and kitchen section includes furniture, decor, kitchen appliances, and household items. Perfect for home improvement and daily needs. What home category are you interested in?"
    
    elif any(word in message_lower for word in ['discount', 'deal', 'offer', 'sale']):
        return "We regularly have sales and discounts! Check our 'Deals' section for current offers, seasonal sales, and shop-specific promotions. Many shops also offer first-time customer discounts."
    
    elif any(word in message_lower for word in ['customer service', 'support', 'contact']):
        return "Our customer support team is available 24/7! You can reach us through live chat, email, or phone. We also have a comprehensive FAQ section and self-service options."
    
    elif any(word in message_lower for word in ['app', 'mobile', 'website']):
        return "Our platform works great on both mobile and desktop! We have a responsive website that adapts to any device. You can also access all features through your mobile browser."
    
    else:
        # Generic helpful response for other queries
        return f"I understand you're asking about '{user_message}'. While I'm primarily designed to help with e-commerce questions, I can try to assist you. Could you rephrase your question or ask about shopping, orders, products, or our services? You can also use the quick tip buttons above for common questions."

@csrf_exempt
def api_shopkeeper_login(request):
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
	try:
		data = json.loads(request.body.decode('utf-8'))
		email = (data.get('email') or '').strip()
		password = data.get('password') or ''
		if not email or not password:
			return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)
		shopkeeper = Shopkeeper.objects.get(email=email)
		if not shopkeeper.check_password(password):
			return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
		request.session['shopkeeper_id'] = shopkeeper.id
		request.session['user_type'] = 'shopkeeper'
		return JsonResponse({'success': True, 'shopkeeper': {'id': shopkeeper.id, 'name': shopkeeper.name, 'email': shopkeeper.email}})
	except Shopkeeper.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Account not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_shopkeeper_register(request):
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
	try:
		data = json.loads(request.body.decode('utf-8'))
		name = (data.get('name') or '').strip()
		email = (data.get('email') or '').strip()
		address = (data.get('address') or '').strip()
		password = data.get('password') or ''
		if not all([name, email, address, password]):
			return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
		if Shopkeeper.objects.filter(email=email).exists():
			return JsonResponse({'success': False, 'error': 'Email already in use'}, status=409)
		shopkeeper = Shopkeeper.objects.create_user(email=email, name=name, address=address, password=password)
		request.session['shopkeeper_id'] = shopkeeper.id
		request.session['user_type'] = 'shopkeeper'
		return JsonResponse({'success': True, 'shopkeeper': {'id': shopkeeper.id, 'name': shopkeeper.name, 'email': shopkeeper.email}})
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_delivery_login(request):
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
	try:
		data = json.loads(request.body.decode('utf-8'))
		email = (data.get('email') or '').strip()
		password = data.get('password') or ''
		if not email or not password:
			return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)
		dp = DeliveryPartner.objects.get(email=email)
		if not check_password(password, dp.password):
			return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
		request.session['delivery_id'] = dp.id
		request.session['user_type'] = 'delivery'
		return JsonResponse({'success': True, 'delivery': {'id': dp.id, 'name': dp.name, 'email': dp.email}})
	except DeliveryPartner.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Account not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_delivery_register(request):
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
	try:
		data = json.loads(request.body.decode('utf-8'))
		name = (data.get('name') or '').strip()
		email = (data.get('email') or '').strip()
		vehicle = (data.get('vehicle') or '').strip()
		password = data.get('password') or ''
		if not all([name, email, vehicle, password]):
			return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
		if DeliveryPartner.objects.filter(email=email).exists():
			return JsonResponse({'success': False, 'error': 'Email already in use'}, status=409)
		dp = DeliveryPartner.objects.create(name=name, email=email, vehicle=vehicle, password=make_password(password))
		request.session['delivery_id'] = dp.id
		request.session['user_type'] = 'delivery'
		return JsonResponse({'success': True, 'delivery': {'id': dp.id, 'name': dp.name, 'email': dp.email}})
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)
