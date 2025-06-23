from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, TransactionLog, VendorOrderNotification


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at',)


class TransactionLogInline(admin.TabularInline):
    model = TransactionLog
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'payment_status',
                   'payment_method', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email', 'contact_email')
    readonly_fields = ('order_number', 'total_items', 'created_at', 'updated_at',
                      'confirmed_at', 'shipped_at', 'delivered_at')
    inlines = [OrderItemInline, OrderStatusHistoryInline, TransactionLogInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total_amount', 'total_items')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('Shipping Address', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state',
                      'shipping_postal_code', 'shipping_country')
        }),
        ('Billing Address', {
            'fields': ('billing_address', 'billing_city', 'billing_state',
                      'billing_postal_code', 'billing_country'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Additional Information', {
            'fields': ('notes', 'estimated_delivery_date', 'tracking_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'vendor', 'quantity', 'unit_price', 'total_price', 'status')
    list_filter = ('status', 'created_at', 'vendor')
    search_fields = ('order__order_number', 'product__name', 'vendor__username')
    readonly_fields = ('total_price', 'created_at', 'updated_at')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'changed_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'changed_by__username')
    readonly_fields = ('created_at',)


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'transaction_type', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('transaction_type', 'status', 'payment_method', 'created_at')
    search_fields = ('order__order_number', 'transaction_id')
    readonly_fields = ('created_at',)


@admin.register(VendorOrderNotification)
class VendorOrderNotificationAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'order', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('vendor__username', 'order__order_number', 'message')
    readonly_fields = ('created_at',)
