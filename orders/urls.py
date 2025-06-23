from django.urls import path
from . import views

urlpatterns = [
    # Order endpoints
    path('', views.OrderListCreateView.as_view(), name='order_list_create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('<int:pk>/cancel/', views.cancel_order, name='cancel_order'),

    # Vendor order endpoints
    path('vendor/orders/', views.VendorOrdersView.as_view(), name='vendor_orders'),
    path('vendor/orders/<int:pk>/', views.VendorOrderDetailView.as_view(), name='vendor_order_detail'),
    path('vendor/<int:order_id>/items/<int:item_id>/status/', views.update_order_item_status, name='update_order_item_status'),
    path('vendor/notifications/', views.vendor_notifications, name='vendor_notifications'),

    # Statistics and analytics
    path('stats/', views.order_stats, name='order_stats'),
    path('admin/analytics/', views.admin_order_analytics, name='admin_order_analytics'),
]
