from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Category,
    SubCategory,
    Product,
    ProductImage,
    ProductVariant,
    Review,
    Cart,
    CartItem,
    Wishlist,
)


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'image_url',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        return None


class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = SubCategory
        fields = [
            'id',
            'name',
            'slug',
            'category',
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = [
            'id',
            'image_url',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'size',
            'color',
            'stock',
        ]

    def get_size(self, obj):
        return obj.size.name if obj.size else None


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'rating',
            'comment',
            'created_at',
        ]

    def get_user(self, obj):
        return obj.user.username


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    main_image_url = serializers.SerializerMethodField()
    selling_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'brand',
            'category',
            'subcategory',
            'gender',
            'price',
            'discount_price',
            'selling_price',
            'main_image_url',
            'color',
            'fabric',
            'fit',
            'pattern',
            'occasion',
            'is_new_arrival',
            'is_featured',
            'is_best_seller',
        ]

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_subcategory(self, obj):
        return obj.subcategory.name if obj.subcategory else None

    def get_selling_price(self, obj):
        return obj.selling_price

    def get_main_image_url(self, obj):
        request = self.context.get('request')

        if obj.main_image and request:
            return request.build_absolute_uri(obj.main_image.url)

        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
    main_image_url = serializers.SerializerMethodField()
    extra_images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    selling_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'brand',
            'category',
            'subcategory',
            'gender',
            'short_description',
            'description',
            'price',
            'discount_price',
            'selling_price',
            'main_image_url',
            'extra_images',
            'variants',
            'color',
            'fabric',
            'fit',
            'pattern',
            'occasion',
            'tags',
            'is_new_arrival',
            'is_featured',
            'is_best_seller',
            'reviews',
        ]

    def get_main_image_url(self, obj):
        request = self.context.get('request')

        if obj.main_image and request:
            return request.build_absolute_uri(obj.main_image.url)

        return None

    def get_selling_price(self, obj):
        return obj.selling_price

    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        return ReviewSerializer(reviews, many=True).data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'date_joined',
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_slug = serializers.SerializerMethodField()
    product_image_url = serializers.SerializerMethodField()
    variant_size = serializers.SerializerMethodField()
    variant_color = serializers.SerializerMethodField()
    selling_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_slug',
            'product_image_url',
            'variant',
            'variant_size',
            'variant_color',
            'quantity',
            'selling_price',
            'total_price',
            'added_at',
        ]

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_slug(self, obj):
        return obj.product.slug

    def get_product_image_url(self, obj):
        request = self.context.get('request')

        if obj.product.main_image and request:
            return request.build_absolute_uri(obj.product.main_image.url)

        return None

    def get_variant_size(self, obj):
        if obj.variant and obj.variant.size:
            return obj.variant.size.name

        return None

    def get_variant_color(self, obj):
        if obj.variant:
            return obj.variant.color

        return None

    def get_selling_price(self, obj):
        return obj.product.selling_price

    def get_total_price(self, obj):
        return obj.total_price


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'total_items',
            'total_price',
            'items',
            'created_at',
        ]

    def get_items(self, obj):
        items = obj.items.select_related(
            'product',
            'variant',
            'variant__size'
        ).all()

        return CartItemSerializer(
            items,
            many=True,
            context=self.context
        ).data

    def get_total_items(self, obj):
        return obj.total_items

    def get_total_price(self, obj):
        return obj.total_price


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'id',
            'product',
            'created_at',
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'rating',
            'comment',
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')

        return value
    

class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


class AdminSubCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = [
            'id',
            'name',
            'slug',
            'is_active',
        ]


class AdminCategoryDetailSerializer(serializers.ModelSerializer):
    subcategories = AdminSubCategorySimpleSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'image_url',
            'is_active',
            'subcategories',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        return None


class AdminProductManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'subcategory',
            'name',
            'slug',
            'brand',
            'gender',
            'short_description',
            'description',
            'price',
            'discount_price',
            'main_image',
            'color',
            'fabric',
            'fit',
            'pattern',
            'occasion',
            'tags',
            'is_new_arrival',
            'is_featured',
            'is_best_seller',
            'is_active',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'slug',
            'created_at',
        ]


class AdminProductVariantManageSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    size_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'product',
            'product_name',
            'size',
            'size_name',
            'color',
            'stock',
        ]

    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

    def get_size_name(self, obj):
        return obj.size.name if obj.size else None


class AdminCartItemSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    variant_size = serializers.SerializerMethodField()
    variant_color = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'username',
            'product_name',
            'variant_size',
            'variant_color',
            'quantity',
            'total_price',
            'added_at',
        ]

    def get_username(self, obj):
        return obj.cart.user.username

    def get_product_name(self, obj):
        return obj.product.name

    def get_variant_size(self, obj):
        if obj.variant and obj.variant.size:
            return obj.variant.size.name

        return None

    def get_variant_color(self, obj):
        if obj.variant:
            return obj.variant.color

        return None

    def get_total_price(self, obj):
        return obj.total_price


class AdminReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id',
            'username',
            'product_name',
            'rating',
            'comment',
            'is_approved',
            'created_at',
        ]

    def get_username(self, obj):
        return obj.user.username

    def get_product_name(self, obj):
        return obj.product.name