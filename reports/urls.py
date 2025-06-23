from django.urls import path
from . import views

urlpatterns = [
    # Report endpoints (Admin only)
    path('sales/', views.sales_report, name='sales_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('user-activity/', views.user_activity_report, name='user_activity_report'),
    path('vendor-performance/', views.vendor_performance_report, name='vendor_performance_report'),
    path('transactions/', views.transaction_report, name='transaction_report'),

    # Export endpoints
    path('export/csv/', views.export_report_csv, name='export_report_csv'),
]
