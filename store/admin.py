from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category,
    SubCategory,
    Size,
    Product,
    ProductImage,
    ProductVariant,
    Cart,
    CartItem,
    Wishlist,
    Review,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'image_preview')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="55" height="55" style="object-fit:cover;border-radius:50%;" />',
                obj.image.url
            )
        return "-"

    image_preview.short_description = "Image"


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'is_active')
    list_filter = ('category', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'category__name')


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_preview',
        'name',
        'category',
        'subcategory',
        'gender',
        'price',
        'discount_price',
        'total_stock',
        'is_new_arrival',
        'is_featured',
        'is_best_seller',
        'is_active',
    )

    list_filter = (
        'category',
        'subcategory',
        'gender',
        'is_new_arrival',
        'is_featured',
        'is_best_seller',
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'brand',
        'color',
        'fabric',
        'fit',
        'pattern',
        'occasion',
        'tags',
    )

    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    list_editable = (
        'price',
        'discount_price',
        'is_new_arrival',
        'is_featured',
        'is_best_seller',
        'is_active',
    )
    date_hierarchy = 'created_at'

    def image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" width="55" height="70" style="object-fit:cover;border-radius:10px;" />',
                obj.main_image.url
            )
        return "-"

    image_preview.short_description = "Image"

    def total_stock(self, obj):
        return sum(variant.stock for variant in obj.variants.all())

    total_stock.short_description = "Stock"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview')
    search_fields = ('product__name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="55" height="70" style="object-fit:cover;border-radius:10px;" />',
                obj.image.url
            )
        return "-"

    image_preview.short_description = "Image"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock', 'stock_status')
    list_filter = ('size', 'color')
    search_fields = ('product__name', 'color')
    list_editable = ('stock',)

    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color:red;font-weight:bold;">Out of Stock</span>')
        if obj.stock <= 5:
            return format_html('<span style="color:#b8860b;font-weight:bold;">Low Stock</span>')
        return format_html('<span style="color:green;font-weight:bold;">In Stock</span>')

    stock_status.short_description = "Status"


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'added_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'cart_total_items', 'cart_total_price', 'created_at')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]

    def cart_total_items(self, obj):
        return obj.total_items

    cart_total_items.short_description = "Items"

    def cart_total_price(self, obj):
        return f"₹{obj.total_price}"

    cart_total_price.short_description = "Total"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'variant', 'quantity', 'total_price', 'added_at')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('added_at',)

    def total_price(self, obj):
        return f"₹{obj.total_price}"

    total_price.short_description = "Total"


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating_stars', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    list_editable = ('is_approved',)

    def rating_stars(self, obj):
        return "★" * obj.rating + "☆" * (5 - obj.rating)

    rating_stars.short_description = "Rating"