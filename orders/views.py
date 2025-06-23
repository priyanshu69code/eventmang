from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Order, OrderItem, OrderStatusHistory, TransactionLog, VendorOrderNotification
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderListSerializer,
    OrderStatusUpdateSerializer, VendorOrderSerializer,
    VendorOrderNotificationSerializer, OrderItemSerializer
)
from authentication.permissions import IsAdminUser, IsVendorUser, IsOwnerOrAdmin


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            queryset = Order.objects.all()
        else:
            queryset = Order.objects.filter(user=user)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Order.objects.all()
        return Order.objects.filter(user=user)


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        user = request.user

        # Get order based on user role
        if user.is_admin:
            order = get_object_or_404(Order, pk=pk)
        elif user.is_vendor:
            # Vendors can only update orders that contain their products
            order = get_object_or_404(Order, pk=pk, items__vendor=user)
        else:
            # Regular users cannot update order status
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderStatusUpdateSerializer(
            order,
            data=request.data,
            context={'request': request},
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Order status updated successfully',
                'order': OrderSerializer(order).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorOrdersView(generics.ListAPIView):
    serializer_class = VendorOrderSerializer
    permission_classes = [IsVendorUser]

    def get_queryset(self):
        vendor = self.request.user
        queryset = Order.objects.filter(items__vendor=vendor).distinct()

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')


class VendorOrderDetailView(generics.RetrieveAPIView):
    serializer_class = VendorOrderSerializer
    permission_classes = [IsVendorUser]

    def get_queryset(self):
        vendor = self.request.user
        return Order.objects.filter(items__vendor=vendor).distinct()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_stats(request):
    """Get order statistics for the current user"""
    user = request.user

    if user.is_admin:
        orders = Order.objects.all()
    elif user.is_vendor:
        orders = Order.objects.filter(items__vendor=user).distinct()
    else:
        orders = Order.objects.filter(user=user)

    stats = {
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'confirmed_orders': orders.filter(status='confirmed').count(),
        'shipped_orders': orders.filter(status='shipped').count(),
        'delivered_orders': orders.filter(status='delivered').count(),
        'cancelled_orders': orders.filter(status='cancelled').count(),
    }

    if user.is_admin or user.is_vendor:
        stats['total_revenue'] = orders.filter(
            payment_status='paid'
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

    return Response(stats)


@api_view(['POST'])
@permission_classes([IsVendorUser])
def update_order_item_status(request, order_id, item_id):
    """Update status of specific order item (vendor only)"""
    vendor = request.user

    try:
        order_item = OrderItem.objects.get(
            id=item_id,
            order_id=order_id,
            vendor=vendor
        )
    except OrderItem.DoesNotExist:
        return Response({'error': 'Order item not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in dict(OrderItem._meta.get_field('status').choices):
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    order_item.status = new_status
    order_item.save()

    # Create notification for customer
    VendorOrderNotification.objects.create(
        vendor=vendor,
        order=order_item.order,
        message=f"Item '{order_item.product.name}' status updated to {new_status}"
    )

    return Response({
        'message': 'Order item status updated successfully',
        'item': OrderItemSerializer(order_item).data
    })


@api_view(['GET'])
@permission_classes([IsVendorUser])
def vendor_notifications(request):
    """Get notifications for vendor"""
    vendor = request.user
    notifications = VendorOrderNotification.objects.filter(vendor=vendor)

    # Mark as read if requested
    if request.query_params.get('mark_read') == 'true':
        notifications.update(is_read=True)

    serializer = VendorOrderNotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, pk):
    """Cancel an order"""
    user = request.user

    try:
        if user.is_admin:
            order = Order.objects.get(pk=pk)
        else:
            order = Order.objects.get(pk=pk, user=user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if order can be cancelled
    if order.status in ['delivered', 'cancelled', 'refunded']:
        return Response(
            {'error': f'Cannot cancel order with status: {order.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update order status
    order.status = 'cancelled'
    order.save()

    # Restore product stock
    for item in order.items.all():
        product = item.product
        product.stock_quantity += item.quantity
        if product.status == 'out_of_stock' and product.stock_quantity > 0:
            product.status = 'active'
        product.save()

    # Create status history
    OrderStatusHistory.objects.create(
        order=order,
        status='cancelled',
        notes=request.data.get('reason', 'Cancelled by user'),
        changed_by=user
    )

    return Response({
        'message': 'Order cancelled successfully',
        'order': OrderSerializer(order).data
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_order_analytics(request):
    """Get comprehensive order analytics for admin"""
    from datetime import datetime, timedelta

    # Date range filtering
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)

    orders = Order.objects.filter(created_at__gte=start_date)

    analytics = {
        'total_orders': orders.count(),
        'total_revenue': orders.filter(payment_status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'average_order_value': orders.filter(payment_status='paid').aggregate(
            avg=Sum('total_amount')
        )['avg'] or 0,
        'orders_by_status': {},
        'orders_by_payment_method': {},
        'daily_orders': [],
        'top_products': [],
    }

    # Calculate average order value
    paid_orders_count = orders.filter(payment_status='paid').count()
    if paid_orders_count > 0:
        analytics['average_order_value'] = analytics['total_revenue'] / paid_orders_count

    # Orders by status
    status_counts = orders.values('status').annotate(count=Count('id'))
    for item in status_counts:
        analytics['orders_by_status'][item['status']] = item['count']

    # Orders by payment method
    payment_counts = orders.values('payment_method').annotate(count=Count('id'))
    for item in payment_counts:
        analytics['orders_by_payment_method'][item['payment_method']] = item['count']

    # Daily orders for the last 7 days
    for i in range(7):
        date = (timezone.now() - timedelta(days=i)).date()
        daily_count = orders.filter(created_at__date=date).count()
        analytics['daily_orders'].append({
            'date': date.strftime('%Y-%m-%d'),
            'count': daily_count
        })

    # Top products
    from django.db.models import F
    top_products = OrderItem.objects.filter(
        order__created_at__gte=start_date
    ).values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('unit_price'))
    ).order_by('-total_quantity')[:10]

    analytics['top_products'] = list(top_products)

    return Response(analytics)
