from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('user', 'User'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_vendor(self):
        return self.role == 'vendor'

    @property
    def is_customer(self):
        return self.role == 'user'


class VendorProfile(models.Model):
    CATEGORY_CHOICES = [
        ('catering', 'Catering'),
        ('florist', 'Florist'),
        ('decoration', 'Decoration'),
        ('lighting', 'Lighting'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    shop_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    business_license = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shop_name} - {self.category}"

    class Meta:
        verbose_name = "Vendor Profile"
        verbose_name_plural = "Vendor Profiles"


class Membership(models.Model):
    DURATION_CHOICES = [
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='6_months')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            duration_mapping = {
                '6_months': timedelta(days=180),
                '1_year': timedelta(days=365),
                '2_years': timedelta(days=730),
            }
            self.end_date = self.start_date + duration_mapping[self.duration]
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.end_date < timezone.now().date()

    def __str__(self):
        return f"{self.user.username} - {self.duration} ({self.start_date} to {self.end_date})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"
