from django import forms
from .models import Shopkeeper, Customer, DeliveryPartner, Product, Order

class ShopkeeperForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Shopkeeper
        fields = ['name', 'email', 'address', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'password']

class DeliveryPartnerForm(forms.ModelForm):
    class Meta:
        model = DeliveryPartner
        fields = ['name', 'email', 'vehicle', 'password']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['shopkeeper', 'name', 'image', 'price', 'quantity', 'description']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'shopkeeper', 'delivery_partner', 'delivery_address', 'delivery_phone', 'delivery_time', 'status']
