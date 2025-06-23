from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, VendorProfile, Membership


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'address', 'date_of_birth', 'is_verified')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'address', 'date_of_birth', 'is_verified')
        }),
    )


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'user', 'category', 'rating', 'is_verified', 'created_at')
    list_filter = ('category', 'is_verified', 'created_at')
    search_fields = ('shop_name', 'user__username', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'shop_name', 'category', 'business_license')
        }),
        ('Details', {
            'fields': ('description', 'website', 'logo')
        }),
        ('Statistics', {
            'fields': ('rating', 'total_reviews', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'duration', 'start_date', 'end_date', 'is_active', 'amount_paid')
    list_filter = ('duration', 'is_active', 'start_date', 'end_date')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Membership Details', {
            'fields': ('user', 'duration', 'start_date', 'end_date', 'is_active')
        }),
        ('Payment', {
            'fields': ('amount_paid',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
