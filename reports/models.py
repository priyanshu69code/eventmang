from django.db import models
from authentication.models import User
from orders.models import Order


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('user_activity', 'User Activity Report'),
        ('vendor_performance', 'Vendor Performance Report'),
        ('transaction', 'Transaction Report'),
    ]

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    date_from = models.DateField()
    date_to = models.DateField()
    filters = models.JSONField(blank=True, null=True, help_text="Additional filters applied to the report")
    file_path = models.FileField(upload_to='reports/', blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.report_type}"

    class Meta:
        ordering = ['-created_at']


class UserActivityLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('product_view', 'Product View'),
        ('product_create', 'Product Create'),
        ('product_update', 'Product Update'),
        ('product_delete', 'Product Delete'),
        ('order_create', 'Order Create'),
        ('order_update', 'Order Update'),
        ('cart_add', 'Cart Add'),
        ('cart_remove', 'Cart Remove'),
        ('profile_update', 'Profile Update'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, blank=True, null=True)
    resource_id = models.CharField(max_length=50, blank=True, null=True)
    details = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
        ]
