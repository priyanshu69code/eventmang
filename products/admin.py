from django.contrib import admin
from .models import Product, ProductImage, ProductReview, CartItem, Wishlist, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'category', 'price', 'stock_quantity', 'status', 'is_featured', 'created_at')
    list_filter = ('category', 'status', 'is_featured', 'created_at')
    search_fields = ('name', 'description', 'sku', 'vendor__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor', 'name', 'description', 'category')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity', 'sku')
        }),
        ('Product Details', {
            'fields': ('image', 'weight', 'dimensions', 'tags')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'added_at')
    list_filter = ('added_at', 'updated_at')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('added_at', 'updated_at', 'total_price')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('added_at',)
