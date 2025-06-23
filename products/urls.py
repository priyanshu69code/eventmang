from django.urls import path
from . import views

urlpatterns = [
    # Product endpoints
    path('', views.ProductListCreateView.as_view(), name='product_list_create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('featured/', views.featured_products, name='featured_products'),

    # Vendor specific endpoints
    path('vendor/products/', views.VendorProductsView.as_view(), name='vendor_products'),
    path('vendor/stats/', views.VendorProductStatsView.as_view(), name='vendor_stats'),
    path('vendor/<int:vendor_id>/products/', views.vendor_products, name='vendor_product_list'),

    # Product reviews
    path('<int:product_id>/reviews/', views.ProductReviewListCreateView.as_view(), name='product_reviews'),

    # Product images
    path('<int:product_id>/images/', views.ProductImageListCreateView.as_view(), name='product_images'),

    # Cart endpoints
    path('cart/', views.CartItemListCreateView.as_view(), name='cart_list_create'),
    path('cart/<int:pk>/', views.CartItemDetailView.as_view(), name='cart_item_detail'),
    path('cart/summary/', views.cart_summary, name='cart_summary'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Wishlist endpoints
    path('wishlist/', views.WishlistListCreateView.as_view(), name='wishlist_list_create'),
    path('wishlist/<int:pk>/', views.WishlistDetailView.as_view(), name='wishlist_detail'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
]
