from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

# Modèle représentant une catégorie de produits
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Modèle représentant un produit
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def clean(self):
        if self.price < 0:
            raise ValidationError('Le prix ne peut pas être négatif.')

    def __str__(self):
        return self.name

    def update_stock(self, quantity):
        """Met à jour le stock du produit."""
        if quantity < 0 and abs(quantity) > self.stock:
            raise ValidationError('La quantité demandée dépasse le stock disponible.')
        self.stock += quantity
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
        ]

# Modèle représentant un panier d'achats
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total_price(self):
        """Calcule le prix total du panier."""
        return sum(item.product.price * item.quantity for item in self.items.all())

# Modèle représentant un article dans le panier
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError('La quantité doit être positive.')

# Modèle représentant une commande
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.total_price < 0:
            raise ValidationError('Le prix total ne peut pas être négatif.')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_total_price(self):
        """Calcule le prix total de la commande."""
        return sum(item.price * item.quantity for item in self.items.all())

    def update_status(self, new_status):
        """Met à jour le statut de la commande."""
        if new_status not in dict(self.STATUS_CHOICES).keys():
            raise ValidationError('Statut invalide.')
        self.status = new_status
        self.save()

# Modèle représentant un article dans une commande
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        if self.price < 0:
            raise ValidationError('Le prix ne peut pas être négatif.')
        if self.quantity <= 0:
            raise ValidationError('La quantité doit être positive.')

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]

# Modèle représentant une adresse pour les livraisons
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.address_line1}, {self.address_line2}, {self.city}, {self.state}, {self.postal_code}, {self.country}"

# Modèle pour les paiements
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        
    )
    PAYMENT_STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
       
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_status}"

# Modèle pour les réductions et promotions
class Discount(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError('La date de fin doit être après la date de début.')

    def __str__(self):
        return f"{self.code} - {self.discount_amount}"

# Modèle pour les avis produit
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # e.g., 1 to 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError('La note doit être entre 1 et 5.')

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

# Signal qui crée automatiquement un panier pour chaque nouvel utilisateur
@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
