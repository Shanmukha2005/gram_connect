        let users = {
            shopkeepers: [
                { email: "shop1@example.com", password: "shop123", name: "SuperMart", address: "123 Main St" }
            ],
            customers: [
                { email: "customer1@example.com", password: "customer123", name: "John Doe", phone: "9876543210" }
            ],
            delivery: [
                { email: "delivery1@example.com", password: "delivery123", name: "Mike Johnson", vehicle: "bike" }
            ]
        };
        
        let products = [
            { id: 1, shop: "SuperMart", name: "Milk", image: "https://4.imimg.com/data4/JF/JX/MY-9419122/milk-3.jpg", price: 50, quantity: "500ml", description: "Fresh cow milk" },
            { id: 2, shop: "SuperMart", name: "Bread", image: "https://5.imimg.com/data5/TF/EA/MH/SELLER-8764849/fresh-bread-500x500.png", price: 35, quantity: "1 loaf", description: "Whole wheat bread" },
            { id: 3, shop: "SuperMart", name: "Eggs", image: "https://4.imimg.com/data4/IU/DJ/IMOB-16689578/image.jpeg", price: 60, quantity: "12 pieces", description: "Farm fresh eggs" }
        ];
        
        let orders = [];
        let cart = [];
        let currentUser = null;
        let currentRole = null;
        
        // Function to open login modal
        function openModal(role) {
            document.getElementById(`${role}-modal`).style.display = 'flex';
        }
        
        // Function to open register modal
        function openRegisterModal(role) {
            closeModal(`${role}-modal`);
            document.getElementById(`${role}-register-modal`).style.display = 'flex';
        }
        
        // Function to close modal
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // Close modal when clicking outside of it
        window.onclick = function(event) {
            if (event.target.className === 'login-modal' || event.target.className === 'register-modal') {
                event.target.style.display = 'none';
            }
        }
        
        // Register form handlers
        document.getElementById('shopkeeper-register-form').onsubmit = function(e) {
            e.preventDefault();
            const newShopkeeper = {
                email: document.getElementById('shopkeeper-reg-email').value,
                password: document.getElementById('shopkeeper-reg-password').value,
                name: document.getElementById('shopkeeper-reg-name').value,
                address: document.getElementById('shopkeeper-reg-address').value
            };
            users.shopkeepers.push(newShopkeeper);
            alert('Shop registered successfully! Please login.');
            closeModal('shopkeeper-register-modal');
            document.getElementById('shopkeeper-register-form').reset();
        };
        
        document.getElementById('customer-register-form').onsubmit = function(e) {
            e.preventDefault();
            const newCustomer = {
                email: document.getElementById('customer-reg-email').value,
                password: document.getElementById('customer-reg-password').value,
                name: document.getElementById('customer-reg-name').value,
                phone: document.getElementById('customer-reg-phone').value
            };
            users.customers.push(newCustomer);
            alert('Account created successfully! Please login.');
            closeModal('customer-register-modal');
            document.getElementById('customer-register-form').reset();
        };
        
        document.getElementById('delivery-register-form').onsubmit = function(e) {
            e.preventDefault();
            const newDelivery = {
                email: document.getElementById('delivery-reg-email').value,
                password: document.getElementById('delivery-reg-password').value,
                name: document.getElementById('delivery-reg-name').value,
                vehicle: document.getElementById('delivery-reg-vehicle').value
            };
            users.delivery.push(newDelivery);
            alert('Application submitted successfully! Please login.');
            closeModal('delivery-register-modal');
            document.getElementById('delivery-register-form').reset();
        };
        
        // Login form handlers
        document.getElementById('shopkeeper-form').onsubmit = function(e) {
            e.preventDefault();
            const email = document.getElementById('shopkeeper-email').value;
            const password = document.getElementById('shopkeeper-password').value;
            
            const user = users.shopkeepers.find(u => u.email === email && u.password === password);
            if (user) {
                currentUser = user;
                currentRole = 'shopkeeper';
                showDashboard();
                closeModal('shopkeeper-modal');
                renderShopkeeperDashboard();
            } else {
                alert('Invalid email or password');
            }
        };
        
        document.getElementById('customer-form').onsubmit = function(e) {
            e.preventDefault();
            const email = document.getElementById('customer-email').value;
            const password = document.getElementById('customer-password').value;
            
            const user = users.customers.find(u => u.email === email && u.password === password);
            if (user) {
                currentUser = user;
                currentRole = 'customer';
                showDashboard();
                closeModal('customer-modal');
                renderCustomerDashboard();
            } else {
                alert('Invalid email or password');
            }
        };
        
        document.getElementById('delivery-form').onsubmit = function(e) {
            e.preventDefault();
            const email = document.getElementById('delivery-email').value;
            const password = document.getElementById('delivery-password').value;
            
            const user = users.delivery.find(u => u.email === email && u.password === password);
            if (user) {
                currentUser = user;
                currentRole = 'delivery';
                showDashboard();
                closeModal('delivery-modal');
                renderDeliveryDashboard();
            } else {
                alert('Invalid email or password');
            }
        };
        function toggleOrders() {
            const ordersSection = document.getElementById('customer-orders-section');
            if (ordersSection.style.display === 'block') {
                ordersSection.style.display = 'none';
            } else {
                ordersSection.style.display = 'block';
                renderCustomerOrders(); // Always refresh orders when shown
            }
        }
        // Show the appropriate dashboard
        function showDashboard() {
            document.getElementById('main-page').style.display = 'none';
            document.getElementById(`${currentRole}-dashboard`).style.display = 'block';
        }
        
        // Logout function
        function logout() {
            currentUser = null;
            currentRole = null;
            document.getElementById('main-page').style.display = 'block';
            document.getElementById('shopkeeper-dashboard').style.display = 'none';
            document.getElementById('customer-dashboard').style.display = 'none';
            document.getElementById('delivery-dashboard').style.display = 'none';
        }
        
        // Shopkeeper Dashboard Functions
        function renderShopkeeperDashboard() {
            // Render products
            const productList = document.getElementById('shopkeeper-product-list');
            productList.innerHTML = '';
            
            const shopProducts = products.filter(p => p.shop === currentUser.name);
            if (shopProducts.length === 0) {
                productList.innerHTML = '<p>No products added yet</p>';
            } else {
                shopProducts.forEach(product => {
                    const productCard = document.createElement('div');
                    productCard.className = 'product-card';
                    productCard.innerHTML = `
                        <img src="${product.image}" alt="${product.name}">
                        <h3>${product.name}</h3>
                        <p>₹${product.price}</p>
                        <p>Quantity: ${product.quantity}</p>
                        <p>${product.description}</p>
                    `;
                    productList.appendChild(productCard);
                });
            }
            
            // Render orders
            const orderList = document.getElementById('shopkeeper-order-list');
            orderList.innerHTML = '';

            const shopOrders = orders.filter(o => o.shop === currentUser.name);

            // Active orders (pending or ready)
            const activeOrders = shopOrders.filter(o => o.status === 'pending' || o.status === 'ready');
            if (activeOrders.length === 0) {
                orderList.innerHTML = '<p>No active orders</p>';
            } else {
                activeOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Customer: ${order.customer}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-${order.status}">${order.status}</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                        ${order.status === 'pending' ? `<button class="btn btn-shopkeeper" onclick="updateOrderStatus(${order.id}, 'ready')">Mark as Ready</button>` : ''}
                    `;
                    orderList.appendChild(orderCard);
                });
            }

            // Delivered orders (history)
            const deliveredOrders = shopOrders.filter(o => o.status === 'delivered');
            if (deliveredOrders.length > 0) {
                orderList.innerHTML += '<h3>Delivered Orders</h3>';
                deliveredOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Customer: ${order.customer}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-delivered">delivered</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                    `;
                    orderList.appendChild(orderCard);
                });
            }
        }
                
        // Add product form handler
        document.getElementById('add-product-form').onsubmit = function(e) {
            e.preventDefault();
            const newProduct = {
                id: products.length + 1,
                shop: currentUser.name,
                name: document.getElementById('product-name').value,
                image: document.getElementById('product-image').value,
                price: parseInt(document.getElementById('product-price').value),
                quantity: parseInt(document.getElementById('product-quantity').value),
                description: document.getElementById('product-description').value
            };
            products.push(newProduct);
            document.getElementById('add-product-form').reset();
            renderShopkeeperDashboard();
            alert('Product added successfully!');
        };

        
        function renderCustomerOrders() {
            const orderList = document.getElementById('customer-order-list');
            orderList.innerHTML = '';

            const customerOrders = orders.filter(o => o.customer === currentUser.name);

            // Active orders (pending or ready)
            const activeOrders = customerOrders.filter(o => o.status === 'pending' || o.status === 'ready');
            if (activeOrders.length === 0) {
                orderList.innerHTML = '<p>No active orders</p>';
            } else {
                activeOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Shop: ${order.shop}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-${order.status}">${order.status}</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                    `;
                    orderList.appendChild(orderCard);
                });
            }

            // Delivered orders (history)
            const deliveredOrders = customerOrders.filter(o => o.status === 'delivered');
            if (deliveredOrders.length > 0) {
                orderList.innerHTML += '<h3>Delivered Orders</h3>';
                deliveredOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Shop: ${order.shop}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-delivered">delivered</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                    `;
                    orderList.appendChild(orderCard);
                });
            }
        }

        // Customer Dashboard Functions
        function renderCustomerDashboard() {
            // Render products
            const productList = document.getElementById('customer-product-list');
            productList.innerHTML = '';
            
            if (products.length === 0) {
                productList.innerHTML = '<p>No products available</p>';
            } else {
                products.forEach(product => {
                    const productCard = document.createElement('div');
                    productCard.className = 'product-card';
                    productCard.innerHTML = `
                        <img src="${product.image}" alt="${product.name}">
                        <h3>${product.name}</h3>
                        <p>₹${product.price}</p>
                        <p>Available: ${product.quantity}</p>
                        <p>${product.description}</p>
                        <button class="btn btn-customer" onclick="addToCart(${product.id})">Add to Cart</button>
                    `;
                    productList.appendChild(productCard);
                });
            }
            
            // Set minimum delivery time (1 hour from now)
            setMinimumDeliveryTime();
            
            // Render cart
            renderCart();
            updateCartCount();
            renderCustomerOrders();
        }
        
        // Add to cart function
        function addToCart(productId) {
            const product = products.find(p => p.id === productId);
            if (!product) {
                alert('Product not found!');
                return;
            }

            const existingItem = cart.find(item => item.id === productId);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    quantity: 1,  // Starting quantity is 1
                    shop: product.shop,
                    unit: product.quantity, // This is the product's available quantity/unit
                    image: product.image    // Add image for cart display
                });
            }

            updateCartCount();
            renderCart();
            alert(`${product.name} added to cart!`);
        }
        
        // Update cart count in header
        function updateCartCount() {
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
                cartCount.textContent = totalItems;
            }
        }
        
        // Toggle cart visibility
        function toggleCart() {
            const cartModal = document.getElementById('cart-modal');
            cartModal.style.display = cartModal.style.display === 'block' ? 'none' : 'block';
        }
        
        // Set minimum delivery time (1 hour from now)
        function setMinimumDeliveryTime() {
            const deliveryTimeInput = document.getElementById('delivery-time');
            if (deliveryTimeInput) {
                const now = new Date();
                const oneHourLater = new Date(now.getTime() + (60 * 60 * 1000)); // Add 1 hour
                
                // Format the datetime for the input field
                const year = oneHourLater.getFullYear();
                const month = String(oneHourLater.getMonth() + 1).padStart(2, '0');
                const day = String(oneHourLater.getDate()).padStart(2, '0');
                const hours = String(oneHourLater.getHours()).padStart(2, '0');
                const minutes = String(oneHourLater.getMinutes()).padStart(2, '0');
                
                const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
                deliveryTimeInput.min = minDateTime;
                deliveryTimeInput.value = minDateTime;
            }
        }
        
        // Remove from cart function
        function removeFromCart(productId) {
            const itemIndex = cart.findIndex(item => item.id === productId);
            if (itemIndex !== -1) {
                cart.splice(itemIndex, 1);
                updateCartCount();
                renderCart();
            }
        }
        
        // Place order form handler (keep only ONE!)
        document.getElementById('place-order-form').onsubmit = function(e) {
            e.preventDefault();
            if (cart.length === 0) {
                alert('Your cart is empty!');
                return;
            }
            
            const newOrder = {
                id: orders.length + 1,
                customer: currentUser.name,
                shop: cart[0].shop, // Assuming all items are from same shop for simplicity
                items: [...cart],
                deliveryAddress: document.getElementById('delivery-address').value,
                deliveryPhone: document.getElementById('delivery-phone').value,
                deliveryTime: document.getElementById('delivery-time').value,
                status: 'pending',
                date: new Date().toISOString()
            };
            
            orders.push(newOrder);
            cart = [];
            document.getElementById('place-order-form').reset();
            updateCartCount();
            renderCart();
            alert('Order placed successfully!');
            renderCustomerOrders();           // <-- Show in customer dashboard
            renderShopkeeperDashboard();
            if (currentRole === 'delivery') renderDeliveryDashboard();
        };

        // Update order status
        function updateOrderStatus(orderId, status) {
            const orderIndex = orders.findIndex(o => o.id === orderId);
            if (orderIndex !== -1) {
                orders[orderIndex].status = status;
                renderShopkeeperDashboard();
                renderDeliveryDashboard();
                
            }
        }

        // Render cart
        function renderCart() {
            const cartItems = document.getElementById('cart-items');
            const emptyCartMessage = document.getElementById('empty-cart-message');
            const cartTotal = document.getElementById('cart-total');

            // Remove all cart-item elements
            cartItems.querySelectorAll('.cart-item').forEach(el => el.remove());

            if (cart.length === 0) {
                emptyCartMessage.style.display = 'block';
                cartTotal.textContent = '';
            } else {
                emptyCartMessage.style.display = 'none';

                cart.forEach(item => {
                    const cartItem = document.createElement('div');
                    cartItem.className = 'cart-item';
                    cartItem.innerHTML = `
                        <img src="${item.image}" alt="${item.name}">
                        <div class="cart-item-info">
                            <h4>${item.name}</h4>
                            <p>${item.unit}</p>
                            <p>₹${item.price} × ${item.quantity} = ₹${item.price * item.quantity}</p>
                            <button class="remove-item" onclick="removeFromCart(${item.id})">Remove</button>
                        </div>
                    `;
                    cartItems.appendChild(cartItem);
                });

                const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
                cartTotal.textContent = `Total: ₹${total}`;
            }
        }
        

        
        // Place order form handler
        document.getElementById('place-order-form').onsubmit = function(e) {
            e.preventDefault();
            if (cart.length === 0) {
                alert('Your cart is empty!');
                return;
            }
            
            const newOrder = {
                id: orders.length + 1,
                customer: currentUser.name,
                shop: cart[0].shop, // Assuming all items are from same shop for simplicity
                items: [...cart],
                deliveryAddress: document.getElementById('delivery-address').value,
                deliveryPhone: document.getElementById('delivery-phone').value,
                deliveryTime: document.getElementById('delivery-time').value,
                status: 'pending',
                date: new Date().toISOString()
            };
            
            orders.push(newOrder);
            cart = [];
            document.getElementById('place-order-form').reset();
            updateCartCount();
            renderCart();
            alert('Order placed successfully!');
            renderCustomerOrders();           // Customer dashboard
            renderShopkeeperDashboard();      // Shopkeeper dashboard
            renderDeliveryDashboard();        // Delivery dashboard
        };


        // Delivery Dashboard Functions
        function renderDeliveryDashboard() {
            const orderList = document.getElementById('delivery-order-list');
            orderList.innerHTML = '';

            // Show orders that are pending or ready
            const deliveryOrders = orders.filter(o => o.status === 'pending' || o.status === 'ready');
            if (deliveryOrders.length === 0) {
                orderList.innerHTML = '<p>No orders to deliver</p>';
            } else {
                deliveryOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Shop: ${order.shop}</p>
                        <p>Customer: ${order.customer}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-${order.status}">${order.status}</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                        ${order.status === 'ready' ? `<button class="btn btn-delivery" onclick="updateOrderStatus(${order.id}, 'delivered')">Mark as Delivered</button>` : ''}
                    `;
                    orderList.appendChild(orderCard);
                });
            }

            // Show delivered orders (history)
            const deliveredOrders = orders.filter(o => o.status === 'delivered');
            if (deliveredOrders.length > 0) {
                orderList.innerHTML += '<h3>Delivered Orders</h3>';
                deliveredOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Shop: ${order.shop}</p>
                        <p>Customer: ${order.customer}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-${order.status}">${order.status}</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                    `;
                    orderList.appendChild(orderCard);
                });
            }
        }
        
        // Product search functionality
        document.getElementById('product-search').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const filteredProducts = products.filter(product => 
                product.name.toLowerCase().includes(searchTerm) || 
                product.description.toLowerCase().includes(searchTerm)
            );
            
            const productList = document.getElementById('customer-product-list');
            productList.innerHTML = '';
            
            if (filteredProducts.length === 0) {
                productList.innerHTML = '<p>No products found</p>';
            } else {
                filteredProducts.forEach(product => {
                    const productCard = document.createElement('div');
                    productCard.className = 'product-card';
                    productCard.innerHTML = `
                        <img src="${product.image}" alt="${product.name}">
                        <h3>${product.name}</h3>
                        <p>₹${product.price}</p>
                        <p>Available: ${product.quantity}</p>
                        <p>${product.description}</p>
                        <button class="btn btn-customer" onclick="addToCart(${product.id})">Add to Cart</button>
                    `;
                    productList.appendChild(productCard);
                });
            }
        });