from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import io
from django.http import HttpResponse

from authentication.models import User, VendorProfile
from products.models import Product, ProductReview, CartItem
from orders.models import Order, OrderItem, TransactionLog
from authentication.permissions import IsAdminUser
from .models import UserActivityLog, Report


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sales_report(request):
    """Generate sales report"""
    # Date filtering
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if not start_date or not end_date:
        # Default to last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Base queryset
    orders = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    )

    # Category filtering
    category = request.query_params.get('category')
    if category:
        orders = orders.filter(items__product__category=category)

    # Vendor filtering
    vendor_id = request.query_params.get('vendor_id')
    if vendor_id:
        orders = orders.filter(items__vendor_id=vendor_id)

    # Calculate metrics
    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = orders.count()
    average_order_value = total_sales / total_orders if total_orders > 0 else 0

    # Sales by category
    sales_by_category = OrderItem.objects.filter(
        order__in=orders
    ).values('product__category').annotate(
        total_sales=Sum('total_price'),
        total_quantity=Sum('quantity')
    ).order_by('-total_sales')

    # Sales by vendor
    sales_by_vendor = OrderItem.objects.filter(
        order__in=orders
    ).values('vendor__username', 'vendor__vendor_profile__shop_name').annotate(
        total_sales=Sum('total_price'),
        total_orders=Count('order', distinct=True)
    ).order_by('-total_sales')

    # Daily sales trend
    daily_sales = []
    current_date = start_date
    while current_date <= end_date:
        daily_total = orders.filter(
            created_at__date=current_date
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        daily_sales.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'sales': float(daily_total)
        })
        current_date += timedelta(days=1)

    report_data = {
        'period': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        },
        'summary': {
            'total_sales': float(total_sales),
            'total_orders': total_orders,
            'average_order_value': float(average_order_value)
        },
        'sales_by_category': list(sales_by_category),
        'sales_by_vendor': list(sales_by_vendor),
        'daily_sales': daily_sales
    }

    return Response(report_data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def inventory_report(request):
    """Generate inventory report"""
    products = Product.objects.all()

    # Filter by category
    category = request.query_params.get('category')
    if category:
        products = products.filter(category=category)

    # Filter by vendor
    vendor_id = request.query_params.get('vendor_id')
    if vendor_id:
        products = products.filter(vendor_id=vendor_id)

    # Filter by status
    status_filter = request.query_params.get('status')
    if status_filter:
        products = products.filter(status=status_filter)

    # Calculate metrics
    total_products = products.count()
    total_stock_value = sum(product.price * product.stock_quantity for product in products)
    low_stock_products = products.filter(stock_quantity__lte=10).count()
    out_of_stock_products = products.filter(stock_quantity=0).count()

    # Products by category
    products_by_category = products.values('category').annotate(
        count=Count('id'),
        total_stock=Sum('stock_quantity'),
        total_value=Sum('price')
    )

    # Top products by stock value
    top_products_by_value = products.order_by('-price')[:10].values(
        'name', 'vendor__username', 'price', 'stock_quantity', 'category'
    )

    # Low stock alert
    low_stock_alert = products.filter(stock_quantity__lte=10).values(
        'name', 'vendor__username', 'stock_quantity', 'category'
    )

    report_data = {
        'summary': {
            'total_products': total_products,
            'total_stock_value': float(total_stock_value),
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products
        },
        'products_by_category': list(products_by_category),
        'top_products_by_value': list(top_products_by_value),
        'low_stock_alert': list(low_stock_alert)
    }

    return Response(report_data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_activity_report(request):
    """Generate user activity report"""
    # Date filtering
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__date__range=[start_date, end_date]).count()
    new_users = User.objects.filter(date_joined__date__range=[start_date, end_date]).count()

    # Users by role
    users_by_role = User.objects.values('role').annotate(count=Count('id'))

    # Active vendors
    active_vendors = VendorProfile.objects.filter(
        user__last_login__date__range=[start_date, end_date]
    ).count()

    # User registrations trend
    registration_trend = []
    current_date = start_date
    while current_date <= end_date:
        daily_registrations = User.objects.filter(
            date_joined__date=current_date
        ).count()

        registration_trend.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'registrations': daily_registrations
        })
        current_date += timedelta(days=1)

    # Top active users (by orders)
    top_active_users = User.objects.annotate(
        order_count=Count('orders')
    ).filter(order_count__gt=0).order_by('-order_count')[:10].values(
        'username', 'email', 'role', 'order_count', 'date_joined'
    )

    report_data = {
        'period': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        },
        'summary': {
            'total_users': total_users,
            'active_users': active_users,
            'new_users': new_users,
            'active_vendors': active_vendors
        },
        'users_by_role': list(users_by_role),
        'registration_trend': registration_trend,
        'top_active_users': list(top_active_users)
    }

    return Response(report_data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def vendor_performance_report(request):
    """Generate vendor performance report"""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Get vendor performance data
    vendors = User.objects.filter(role='vendor')

    vendor_performance = []
    for vendor in vendors:
        # Sales data
        vendor_orders = Order.objects.filter(
            items__vendor=vendor,
            created_at__date__range=[start_date, end_date],
            payment_status='paid'
        ).distinct()

        total_sales = vendor_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = vendor_orders.count()

        # Product data
        total_products = Product.objects.filter(vendor=vendor).count()
        active_products = Product.objects.filter(vendor=vendor, status='active').count()

        # Reviews data
        reviews = ProductReview.objects.filter(product__vendor=vendor)
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        total_reviews = reviews.count()

        vendor_data = {
            'vendor_id': vendor.id,
            'vendor_name': vendor.username,
            'shop_name': getattr(vendor.vendor_profile, 'shop_name', '') if hasattr(vendor, 'vendor_profile') else '',
            'category': getattr(vendor.vendor_profile, 'category', '') if hasattr(vendor, 'vendor_profile') else '',
            'total_sales': float(total_sales),
            'total_orders': total_orders,
            'total_products': total_products,
            'active_products': active_products,
            'average_rating': float(avg_rating),
            'total_reviews': total_reviews
        }
        vendor_performance.append(vendor_data)

    # Sort by total sales
    vendor_performance.sort(key=lambda x: x['total_sales'], reverse=True)

    # Top vendors by different metrics
    top_by_sales = sorted(vendor_performance, key=lambda x: x['total_sales'], reverse=True)[:10]
    top_by_orders = sorted(vendor_performance, key=lambda x: x['total_orders'], reverse=True)[:10]
    top_by_rating = sorted(vendor_performance, key=lambda x: x['average_rating'], reverse=True)[:10]

    report_data = {
        'period': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        },
        'all_vendors': vendor_performance,
        'top_by_sales': top_by_sales,
        'top_by_orders': top_by_orders,
        'top_by_rating': top_by_rating
    }

    return Response(report_data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def transaction_report(request):
    """Generate transaction report"""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    transactions = TransactionLog.objects.filter(
        created_at__date__range=[start_date, end_date]
    )

    # Summary metrics
    total_transactions = transactions.count()
    successful_transactions = transactions.filter(status='success').count()
    failed_transactions = transactions.filter(status='failed').count()
    total_amount = transactions.filter(status='success').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Transactions by type
    transactions_by_type = transactions.values('transaction_type').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    )

    # Transactions by payment method
    transactions_by_method = transactions.values('payment_method').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    )

    # Daily transaction trend
    daily_transactions = []
    current_date = start_date
    while current_date <= end_date:
        daily_count = transactions.filter(created_at__date=current_date).count()
        daily_amount = transactions.filter(
            created_at__date=current_date,
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0

        daily_transactions.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'count': daily_count,
            'amount': float(daily_amount)
        })
        current_date += timedelta(days=1)

    report_data = {
        'period': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        },
        'summary': {
            'total_transactions': total_transactions,
            'successful_transactions': successful_transactions,
            'failed_transactions': failed_transactions,
            'success_rate': (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0,
            'total_amount': float(total_amount)
        },
        'transactions_by_type': list(transactions_by_type),
        'transactions_by_method': list(transactions_by_method),
        'daily_transactions': daily_transactions
    }

    return Response(report_data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_report_csv(request):
    """Export report data as CSV"""
    report_type = request.query_params.get('type', 'sales')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'

    writer = csv.writer(response)

    if report_type == 'sales':
        # Export sales data
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        orders = Order.objects.filter(
            created_at__date__range=[start_date, end_date],
            payment_status='paid'
        )

        writer.writerow(['Order Number', 'Customer', 'Total Amount', 'Payment Method', 'Status', 'Date'])
        for order in orders:
            writer.writerow([
                order.order_number,
                order.user.username,
                order.total_amount,
                order.payment_method,
                order.status,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

    elif report_type == 'inventory':
        # Export inventory data
        products = Product.objects.all()

        writer.writerow(['Product Name', 'Vendor', 'Category', 'Price', 'Stock Quantity', 'Status'])
        for product in products:
            writer.writerow([
                product.name,
                product.vendor.username,
                product.category,
                product.price,
                product.stock_quantity,
                product.status
            ])

    return response
