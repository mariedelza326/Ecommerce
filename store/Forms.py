from django import forms
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Address, Payment, Discount, Review

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if Category.objects.filter(slug=slug).exists():
            raise forms.ValidationError('Ce slug est déjà utilisé.')
        return slug

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'stock', 'available', 'image', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError('Le prix doit être supérieur à zéro.')
        return price

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['user']

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['cart', 'product', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError('La quantité doit être supérieure à zéro.')
        return quantity

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'status', 'total_price']
        widgets = {
            'total_price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def clean_total_price(self):
        total_price = self.cleaned_data.get('total_price')
        if total_price < 0:
            raise forms.ValidationError('Le prix total ne peut pas être négatif.')
        return total_price

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'price', 'quantity']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError('Le prix doit être supérieur à zéro.')
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError('La quantité doit être supérieure à zéro.')
        return quantity

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['user', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']
        widgets = {
            'address_line2': forms.TextInput(attrs={'placeholder': 'Optionnel'}),
        }

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if not postal_code.isdigit():
            raise forms.ValidationError('Le code postal doit être numérique.')
        return postal_code

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['order', 'payment_date', 'amount', 'payment_method', 'payment_status']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Le montant doit être supérieur à zéro.')
        return amount

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['code', 'description', 'discount_amount', 'active', 'start_date', 'end_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'discount_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_discount_amount(self):
        discount_amount = self.cleaned_data.get('discount_amount')
        if discount_amount < 0:
            raise forms.ValidationError('Le montant de la remise ne peut pas être négatif.')
        return discount_amount

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError('La date de fin ne peut pas être antérieure à la date de début.')
        return end_date

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['product', 'user', 'rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('La note doit être comprise entre 1 et 5.')
        return rating
