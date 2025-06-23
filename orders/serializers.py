from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory, TransactionLog, VendorOrderNotification
from products.models import Product, CartItem
from products.serializers import ProductListSerializer
from authentication.models import User


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    vendor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'total_price', 'vendor')

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            if not product.is_available:
                raise serializers.ValidationError("Product is not available")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = '__all__'
        read_only_fields = ('created_at',)


class TransactionLogSerializer(serializers.ModelSerializer):
    processed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TransactionLog
        fields = '__all__'
        read_only_fields = ('created_at',)


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    transactions = TransactionLogSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('order_number', 'created_at', 'updated_at', 'confirmed_at',
                           'shipped_at', 'delivered_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text="List of items with product_id and quantity"
    )
    use_cart = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_city', 'shipping_state', 'shipping_postal_code',
                 'shipping_country', 'billing_address', 'billing_city', 'billing_state',
                 'billing_postal_code', 'billing_country', 'contact_phone', 'contact_email',
                 'payment_method', 'notes', 'items', 'use_cart']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item")

        for item in value:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError("Each item must have product_id and quantity")

            try:
                product = Product.objects.get(id=item['product_id'])
                if not product.is_available:
                    raise serializers.ValidationError(f"Product {product.name} is not available")
                if item['quantity'] > product.stock_quantity:
                    raise serializers.ValidationError(f"Insufficient stock for {product.name}")
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with id {item['product_id']} does not exist")

        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        use_cart = validated_data.pop('use_cart', False)
        user = self.context['request'].user

        # If use_cart is True, get items from user's cart
        if use_cart:
            cart_items = CartItem.objects.filter(user=user)
            if not cart_items.exists():
                raise serializers.ValidationError("Cart is empty")
            items_data = [{'product_id': item.product.id, 'quantity': item.quantity} for item in cart_items]

        # Calculate total amount
        total_amount = 0
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            total_amount += product.price * item_data['quantity']

        validated_data['total_amount'] = total_amount
        validated_data['user'] = user

        # Create order
        order = Order.objects.create(**validated_data)

        # Create order items
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                vendor=product.vendor,
                quantity=item_data['quantity'],
                unit_price=product.price,
                total_price=product.price * item_data['quantity']
            )

            # Reduce stock quantity
            product.stock_quantity -= item_data['quantity']
            if product.stock_quantity <= 0:
                product.status = 'out_of_stock'
            product.save()

        # Clear cart if use_cart was True
        if use_cart:
            CartItem.objects.filter(user=user).delete()

        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Order created',
            changed_by=user
        )

        return order


class OrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'status', 'total_amount', 'payment_method',
                 'payment_status', 'total_items', 'created_at', 'estimated_delivery_date']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = ['status', 'notes']

    def update(self, instance, validated_data):
        notes = validated_data.pop('notes', '')
        old_status = instance.status
        new_status = validated_data.get('status', instance.status)

        # Update order
        order = super().update(instance, validated_data)

        # Create status history if status changed
        if old_status != new_status:
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=notes,
                changed_by=self.context['request'].user
            )

            # Update timestamps based on status
            from django.utils import timezone
            if new_status == 'confirmed':
                order.confirmed_at = timezone.now()
            elif new_status == 'shipped':
                order.shipped_at = timezone.now()
            elif new_status == 'delivered':
                order.delivered_at = timezone.now()
            order.save()

        return order


class VendorOrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    vendor_items = serializers.SerializerMethodField()
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user', 'status', 'total_amount', 'payment_method',
                 'payment_status', 'shipping_address', 'contact_phone', 'contact_email',
                 'vendor_items', 'total_items', 'created_at', 'notes']

    def get_vendor_items(self, obj):
        vendor = self.context['request'].user
        vendor_items = obj.items.filter(vendor=vendor)
        return OrderItemSerializer(vendor_items, many=True).data


class VendorOrderNotificationSerializer(serializers.ModelSerializer):
    order = OrderListSerializer(read_only=True)
    vendor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = VendorOrderNotification
        fields = '__all__'
        read_only_fields = ('created_at',)
