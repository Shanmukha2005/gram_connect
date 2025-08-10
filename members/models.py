from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class ShopkeeperManager(BaseUserManager):
    def create_user(self, email, name, address, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, address=address)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, address, password):
        user = self.create_user(email, name, address, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Shopkeeper(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='shopkeeper_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='shopkeeper_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = ShopkeeperManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'address']

    def __str__(self):
        return self.email

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=128)

class DeliveryPartner(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    vehicle = models.CharField(max_length=50)
    password = models.CharField(max_length=128)

class Product(models.Model):
    shopkeeper = models.ForeignKey(Shopkeeper, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.CharField(max_length=50)
    description = models.TextField()

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shopkeeper = models.ForeignKey(Shopkeeper, on_delete=models.CASCADE)
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_name = models.CharField(max_length=100, default='Unknown Customer')
    delivery_address = models.CharField(max_length=255)
    delivery_phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash_on_delivery', 'Cash on Delivery'),
        ('online_payment', 'Online Payment')
    ], default='cash_on_delivery')
    special_instructions = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ready', 'Ready'),
        ('assigned', 'Assigned'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} from {self.shopkeeper.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity} in Order #{self.order.id}"
