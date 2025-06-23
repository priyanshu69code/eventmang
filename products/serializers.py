from rest_framework import serializers
from .models import Product, ProductImage, ProductReview, CartItem, Wishlist, Category
from authentication.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
        read_only_fields = ('created_at',)


class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = ProductReview
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'is_verified_purchase')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    vendor = serializers.StringRelatedField(read_only=True)
    vendor_id = serializers.IntegerField(write_only=True, required=False)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 2)
        return 0.0

    def get_total_reviews(self, obj):
        return obj.reviews.count()

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_vendor:
            validated_data['vendor'] = request.user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    vendor = serializers.StringRelatedField(read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    is_available = serializers.ReadOnlyField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'vendor', 'image', 'primary_image',
                 'stock_quantity', 'status', 'is_featured', 'average_rating',
                 'total_reviews', 'is_available', 'created_at']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 2)
        return 0.0

    def get_total_reviews(self, obj):
        return obj.reviews.count()

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None


class CartItemSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('added_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            if not product.is_available:
                raise serializers.ValidationError("Product is not available")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = '__all__'
        read_only_fields = ('added_at',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")


class VendorProductStatsSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    pending_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
