from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # User management (Admin only)
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),

    # Vendor management
    path('vendor/profile/', views.VendorProfileView.as_view(), name='vendor_profile'),
    path('vendors/', views.VendorListView.as_view(), name='vendor_list'),

    # Membership management (Admin only)
    path('memberships/', views.MembershipListCreateView.as_view(), name='membership_list_create'),
    path('memberships/<int:pk>/', views.MembershipDetailView.as_view(), name='membership_detail'),
    path('my-memberships/', views.user_memberships, name='user_memberships'),

    # Utility endpoints
    path('categories/', views.categories_list, name='categories_list'),
]
