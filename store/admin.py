from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Address, Payment, Discount, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'stock', 'available', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'slug', 'description')
    list_filter = ('available', 'category')
    prepopulated_fields = {'slug': ('name',)}
    actions = ['make_available', 'make_unavailable']

    def make_available(self, request, queryset):
        rows_updated = queryset.update(available=True)
        self.message_user(request, f"{rows_updated} produit(s) marqué(s) comme disponible(s).")
    make_available.short_description = "Marquer comme disponible"

    def make_unavailable(self, request, queryset):
        rows_updated = queryset.update(available=False)
        self.message_user(request, f"{rows_updated} produit(s) marqué(s) comme non disponible(s).")
    make_unavailable.short_description = "Marquer comme non disponible"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('cart', 'product')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_price', 'created_at', 'updated_at')
    search_fields = ('user__username', 'status')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity')
    search_fields = ('order__id', 'product__name')
    list_filter = ('order', 'product')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line1', 'city', 'state', 'postal_code', 'country')
    search_fields = ('user__username', 'address_line1', 'city')
    list_filter = ('country', 'state')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_date', 'amount', 'payment_method', 'payment_status')
    search_fields = ('order__id', 'payment_method', 'payment_status')
    list_filter = ('payment_method', 'payment_status', 'payment_date')

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'active', 'start_date', 'end_date')
    search_fields = ('code', 'description')
    list_filter = ('active', 'start_date', 'end_date')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'rating')
    list_filter = ('rating', 'created_at')
