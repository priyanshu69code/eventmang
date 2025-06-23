from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404

from .models import Product, ProductImage, ProductReview, CartItem, Wishlist, Category
from .serializers import (
    ProductSerializer, ProductListSerializer, ProductImageSerializer,
    ProductReviewSerializer, CartItemSerializer, WishlistSerializer,
    CategorySerializer, VendorProductStatsSerializer
)
from authentication.permissions import IsVendorUser, IsAdminUser, IsOwnerOrAdmin


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.filter(status='active')

        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)

        # Filter by vendor
        vendor_id = self.request.query_params.get('vendor_id', None)
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )

        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter featured products
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)

        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering in ['price', '-price', 'name', '-name', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductSerializer
        return ProductListSerializer

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]


class VendorProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsVendorUser]

    def get_queryset(self):
        queryset = Product.objects.filter(vendor=self.request.user)

        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')


class VendorProductStatsView(APIView):
    permission_classes = [IsVendorUser]

    def get(self, request):
        vendor = request.user
        products = Product.objects.filter(vendor=vendor)

        stats = {
            'total_products': products.count(),
            'active_products': products.filter(status='active').count(),
            'pending_products': products.filter(status='pending_approval').count(),
            'out_of_stock_products': products.filter(status='out_of_stock').count(),
            'total_reviews': ProductReview.objects.filter(product__vendor=vendor).count(),
            'average_rating': ProductReview.objects.filter(product__vendor=vendor).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0.0
        }

        serializer = VendorProductStatsSerializer(stats)
        return Response(serializer.data)


class ProductReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return ProductReview.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(user=self.request.user, product=product)


class ProductImageListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return ProductImage.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product)


class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cart_summary(request):
    """Get cart summary with total items and total price"""
    cart_items = CartItem.objects.filter(user=request.user)
    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.total_price for item in cart_items)

    return Response({
        'total_items': total_items,
        'total_price': total_price,
        'items_count': cart_items.count()
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    """Clear all items from user's cart"""
    deleted_count = CartItem.objects.filter(user=request.user).delete()[0]
    return Response({
        'message': f'Cleared {deleted_count} items from cart'
    })


class WishlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class WishlistDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_products(request):
    """Get featured products"""
    products = Product.objects.filter(status='active', is_featured=True)[:10]
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def vendor_products(request, vendor_id):
    """Get products by specific vendor"""
    products = Product.objects.filter(vendor_id=vendor_id, status='active')

    category = request.query_params.get('category', None)
    if category:
        products = products.filter(category=category)

    serializer = ProductListSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
