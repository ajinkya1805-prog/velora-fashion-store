from django.contrib.auth.models import User
from django.db.models import Q, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    Category,
    Product,
    ProductImage,
    Cart,
    CartItem,
    ProductVariant,
    Wishlist,
    Review,
)

from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    CartSerializer,
    WishlistSerializer,
    UserProfileSerializer,
    ReviewSerializer,
    ReviewCreateSerializer,
)


class UserCategoryListAPI(APIView):
    def get(self, request):
        categories = Category.objects.filter(is_active=True).order_by('name')

        serializer = CategorySerializer(
            categories,
            many=True,
            context={'request': request}
        )

        return Response({
            'success': True,
            'count': categories.count(),
            'categories': serializer.data,
        })


class UserProductListAPI(APIView):
    def get(self, request):
        products = Product.objects.filter(is_active=True).select_related(
            'category',
            'subcategory'
        ).order_by('-created_at')

        category = request.GET.get('category')
        subcategory = request.GET.get('subcategory')
        size = request.GET.get('size')
        color = request.GET.get('color')
        fabric = request.GET.get('fabric')
        fit = request.GET.get('fit')
        pattern = request.GET.get('pattern')
        occasion = request.GET.get('occasion')
        is_new_arrival = request.GET.get('is_new_arrival')
        sale = request.GET.get('sale')
        sort = request.GET.get('sort')

        if category:
            products = products.filter(category__slug=category)

        if subcategory:
            products = products.filter(subcategory__slug=subcategory)

        if size:
            products = products.filter(variants__size__name=size).distinct()

        if color:
            products = products.filter(color__iexact=color)

        if fabric:
            products = products.filter(fabric__iexact=fabric)

        if fit:
            products = products.filter(fit__iexact=fit)

        if pattern:
            products = products.filter(pattern__iexact=pattern)

        if occasion:
            products = products.filter(occasion__iexact=occasion)

        if is_new_arrival == 'true':
            products = products.filter(is_new_arrival=True)

        if sale == 'true':
            products = products.filter(discount_price__isnull=False)

        if sort == 'low_to_high':
            products = products.order_by('price')
        elif sort == 'high_to_low':
            products = products.order_by('-price')
        elif sort == 'newest':
            products = products.order_by('-created_at')

        serializer = ProductListSerializer(
            products,
            many=True,
            context={'request': request}
        )

        return Response({
            'success': True,
            'count': products.count(),
            'products': serializer.data,
        })


class UserProductDetailAPI(APIView):
    def get(self, request, product_slug):
        try:
            product = Product.objects.select_related(
                'category',
                'subcategory'
            ).prefetch_related(
                'extra_images',
                'variants',
                'variants__size',
                'reviews'
            ).get(slug=product_slug, is_active=True)

        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(
            product,
            context={'request': request}
        )

        return Response({
            'success': True,
            'product': serializer.data,
        })


class UserSearchAPI(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()

        products = Product.objects.none()

        if query:
            products = Product.objects.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(color__icontains=query) |
                Q(fabric__icontains=query) |
                Q(fit__icontains=query) |
                Q(pattern__icontains=query) |
                Q(occasion__icontains=query) |
                Q(tags__icontains=query) |
                Q(category__name__icontains=query) |
                Q(subcategory__name__icontains=query),
                is_active=True
            ).select_related(
                'category',
                'subcategory'
            ).distinct().order_by('-created_at')

        serializer = ProductListSerializer(
            products,
            many=True,
            context={'request': request}
        )

        return Response({
            'success': True,
            'query': query,
            'count': products.count(),
            'products': serializer.data,
        })


class UserCartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)

        serializer = CartSerializer(
            cart,
            context={'request': request}
        )

        return Response({
            'success': True,
            'cart': serializer.data,
        })


class UserCartAddAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = request.data.get('quantity', 1)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({
                'success': False,
                'message': 'Quantity must be a number.',
            }, status=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return Response({
                'success': False,
                'message': 'Quantity must be at least 1.',
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        variant = None

        if product.variants.exists():
            if not variant_id:
                return Response({
                    'success': False,
                    'message': 'Please select a size/variant.',
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product
                )
            except ProductVariant.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Selected variant not found.',
                }, status=status.HTTP_404_NOT_FOUND)

            if variant.stock <= 0:
                return Response({
                    'success': False,
                    'message': 'Selected variant is out of stock.',
                }, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({
            'success': True,
            'message': f'{product.name} added to cart.',
            'cart_count': cart.total_items,
        })


class UserCartUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        action = request.data.get('action')

        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Cart item not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()

        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

        else:
            return Response({
                'success': False,
                'message': 'Invalid action. Use increase or decrease.',
            }, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(user=request.user)

        return Response({
            'success': True,
            'message': 'Cart updated.',
            'cart_count': cart.total_items,
        })


class UserCartRemoveAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Cart item not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        cart = cart_item.cart
        cart_item.delete()

        return Response({
            'success': True,
            'message': 'Product removed from cart.',
            'cart_count': cart.total_items,
        })


class UserWishlistAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist_items = Wishlist.objects.filter(
            user=request.user
        ).select_related(
            'product',
            'product__category',
            'product__subcategory'
        ).order_by('-created_at')

        serializer = WishlistSerializer(
            wishlist_items,
            many=True,
            context={'request': request}
        )

        return Response({
            'success': True,
            'count': wishlist_items.count(),
            'wishlist': serializer.data,
        })


class UserWishlistToggleAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).first()

        if wishlist_item:
            wishlist_item.delete()
            added = False
            message = f'{product.name} removed from wishlist.'
        else:
            Wishlist.objects.create(
                user=request.user,
                product=product
            )
            added = True
            message = f'{product.name} added to wishlist.'

        wishlist_count = Wishlist.objects.filter(user=request.user).count()

        return Response({
            'success': True,
            'added': added,
            'message': message,
            'wishlist_count': wishlist_count,
        })


class UserProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)

        return Response({
            'success': True,
            'profile': serializer.data,
        })


class UserProfileUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        user.first_name = request.data.get('first_name', user.first_name).strip()
        user.last_name = request.data.get('last_name', user.last_name).strip()
        user.email = request.data.get('email', user.email).strip()
        user.save()

        serializer = UserProfileSerializer(user)

        return Response({
            'success': True,
            'message': 'Profile updated successfully.',
            'profile': serializer.data,
        })


class UserProductReviewsAPI(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        reviews = product.reviews.filter(
            is_approved=True
        ).select_related('user').order_by('-created_at')

        serializer = ReviewSerializer(
            reviews,
            many=True
        )

        return Response({
            'success': True,
            'product': product.name,
            'count': reviews.count(),
            'reviews': serializer.data,
        })


class UserReviewAddAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        Review.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={
                'rating': serializer.validated_data['rating'],
                'comment': serializer.validated_data['comment'],
                'is_approved': True,
            }
        )

        return Response({
            'success': True,
            'message': 'Review saved successfully.',
        })
    

def api_bool(value, default=False):
    if value is None:
        return default

    return str(value).lower() in ["true", "1", "yes", "on"]


class AdminDashboardStatsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_stock = ProductVariant.objects.aggregate(total=Sum('stock'))['total'] or 0

        return Response({
            'success': True,
            'stats': {
                'total_users': User.objects.count(),
                'total_products': Product.objects.count(),
                'active_products': Product.objects.filter(is_active=True).count(),
                'total_categories': Category.objects.count(),
                'total_carts': Cart.objects.count(),
                'total_cart_items': CartItem.objects.count(),
                'total_wishlist_items': Wishlist.objects.count(),
                'total_reviews': Review.objects.count(),
                'total_stock': total_stock,
                'low_stock_count': ProductVariant.objects.filter(stock__gt=0, stock__lte=5).count(),
                'out_of_stock_count': ProductVariant.objects.filter(stock=0).count(),
            }
        })


class AdminUsersAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.order_by('-date_joined')

        data = []

        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
            })

        return Response({
            'success': True,
            'count': users.count(),
            'users': data,
        })


class AdminProductsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        products = Product.objects.select_related(
            'category',
            'subcategory'
        ).order_by('-created_at')

        data = []

        for product in products:
            data.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'category': product.category.name if product.category else None,
                'subcategory': product.subcategory.name if product.subcategory else None,
                'brand': product.brand,
                'gender': product.gender,
                'price': product.price,
                'discount_price': product.discount_price,
                'selling_price': product.selling_price,
                'color': product.color,
                'fabric': product.fabric,
                'fit': product.fit,
                'pattern': product.pattern,
                'occasion': product.occasion,
                'tags': product.tags,
                'is_new_arrival': product.is_new_arrival,
                'is_featured': product.is_featured,
                'is_best_seller': product.is_best_seller,
                'is_active': product.is_active,
                'created_at': product.created_at,
            })

        return Response({
            'success': True,
            'count': products.count(),
            'products': data,
        })


class AdminProductCreateAPI(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        category_id = request.data.get('category')
        name = request.data.get('name')
        price = request.data.get('price')

        if not category_id:
            return Response({
                'success': False,
                'message': 'Category is required.',
            }, status=status.HTTP_400_BAD_REQUEST)

        if not name:
            return Response({
                'success': False,
                'message': 'Product name is required.',
            }, status=status.HTTP_400_BAD_REQUEST)

        if not price:
            return Response({
                'success': False,
                'message': 'Price is required.',
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Category not found.',
            }, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.create(
            category=category,
            subcategory_id=request.data.get('subcategory') or None,
            name=name,
            brand=request.data.get('brand', ''),
            gender=request.data.get('gender', ''),
            short_description=request.data.get('short_description', ''),
            description=request.data.get('description', ''),
            price=price,
            discount_price=request.data.get('discount_price') or None,
            main_image=request.FILES.get('main_image'),
            color=request.data.get('color', ''),
            fabric=request.data.get('fabric', ''),
            fit=request.data.get('fit', ''),
            pattern=request.data.get('pattern', ''),
            occasion=request.data.get('occasion', ''),
            tags=request.data.get('tags', ''),
            is_new_arrival=api_bool(request.data.get('is_new_arrival')),
            is_featured=api_bool(request.data.get('is_featured')),
            is_best_seller=api_bool(request.data.get('is_best_seller')),
            is_active=api_bool(request.data.get('is_active'), default=True),
        )

        return Response({
            'success': True,
            'message': 'Product created successfully.',
            'product_id': product.id,
            'product_slug': product.slug,
        }, status=status.HTTP_201_CREATED)


class AdminProductUpdateAPI(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def put(self, request, product_id):
        return self.update_product(request, product_id)

    def patch(self, request, product_id):
        return self.update_product(request, product_id)

    def update_product(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        normal_fields = [
            'name',
            'brand',
            'gender',
            'short_description',
            'description',
            'price',
            'discount_price',
            'color',
            'fabric',
            'fit',
            'pattern',
            'occasion',
            'tags',
        ]

        for field in normal_fields:
            if field in request.data:
                value = request.data.get(field)

                if field == 'discount_price' and value == '':
                    value = None

                setattr(product, field, value)

        boolean_fields = [
            'is_new_arrival',
            'is_featured',
            'is_best_seller',
            'is_active',
        ]

        for field in boolean_fields:
            if field in request.data:
                setattr(product, field, api_bool(request.data.get(field)))

        if request.data.get('category'):
            product.category_id = request.data.get('category')

        if request.data.get('subcategory'):
            product.subcategory_id = request.data.get('subcategory')

        if request.FILES.get('main_image'):
            product.main_image = request.FILES.get('main_image')

        product.save()

        return Response({
            'success': True,
            'message': 'Product updated successfully.',
            'product_id': product.id,
            'product_slug': product.slug,
        })


class AdminProductDeleteAPI(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        product.delete()

        return Response({
            'success': True,
            'message': 'Product deleted successfully.',
        })


class AdminCategoriesAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        categories = Category.objects.order_by('name')

        data = []

        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'is_active': category.is_active,
            })

        return Response({
            'success': True,
            'count': categories.count(),
            'categories': data,
        })


class AdminStockAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        variants = ProductVariant.objects.select_related(
            'product',
            'size'
        ).order_by('product__name')

        data = []

        for variant in variants:
            if variant.stock == 0:
                stock_status = 'Out of Stock'
            elif variant.stock <= 5:
                stock_status = 'Low Stock'
            else:
                stock_status = 'In Stock'

            data.append({
                'id': variant.id,
                'product_id': variant.product.id,
                'product_name': variant.product.name,
                'size': variant.size.name if variant.size else None,
                'color': variant.color,
                'stock': variant.stock,
                'status': stock_status,
            })

        return Response({
            'success': True,
            'count': variants.count(),
            'stock': data,
        })


class AdminCartsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        carts = Cart.objects.select_related('user').order_by('-created_at')

        data = []

        for cart in carts:
            data.append({
                'id': cart.id,
                'username': cart.user.username,
                'email': cart.user.email,
                'total_items': cart.total_items,
                'total_price': cart.total_price,
                'created_at': cart.created_at,
            })

        return Response({
            'success': True,
            'count': carts.count(),
            'carts': data,
        })


class AdminCartItemsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        cart_items = CartItem.objects.select_related(
            'cart',
            'cart__user',
            'product',
            'variant',
            'variant__size'
        ).order_by('-added_at')

        data = []

        for item in cart_items:
            data.append({
                'id': item.id,
                'username': item.cart.user.username,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'variant_size': item.variant.size.name if item.variant and item.variant.size else None,
                'variant_color': item.variant.color if item.variant else None,
                'quantity': item.quantity,
                'total_price': item.total_price,
                'added_at': item.added_at,
            })

        return Response({
            'success': True,
            'count': cart_items.count(),
            'cart_items': data,
        })


class AdminWishlistAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        wishlist_items = Wishlist.objects.select_related(
            'user',
            'product'
        ).order_by('-created_at')

        data = []

        for item in wishlist_items:
            data.append({
                'id': item.id,
                'username': item.user.username,
                'email': item.user.email,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_slug': item.product.slug,
                'created_at': item.created_at,
            })

        return Response({
            'success': True,
            'count': wishlist_items.count(),
            'wishlist': data,
        })


class AdminReviewsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        reviews = Review.objects.select_related(
            'user',
            'product'
        ).order_by('-created_at')

        data = []

        for review in reviews:
            data.append({
                'id': review.id,
                'username': review.user.username,
                'product_id': review.product.id,
                'product_name': review.product.name,
                'rating': review.rating,
                'comment': review.comment,
                'is_approved': review.is_approved,
                'created_at': review.created_at,
            })

        return Response({
            'success': True,
            'count': reviews.count(),
            'reviews': data,
        })


class AdminReviewApproveAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Review not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        review.is_approved = True
        review.save()

        return Response({
            'success': True,
            'message': 'Review approved successfully.',
        })


class AdminReviewRejectAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Review not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        review.is_approved = False
        review.save()

        return Response({
            'success': True,
            'message': 'Review rejected successfully.',
        })


class AdminProductImageAddAPI(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        image = request.FILES.get('image')

        if not image:
            return Response({
                'success': False,
                'message': 'Please upload an image.',
            }, status=status.HTTP_400_BAD_REQUEST)

        product_image = ProductImage.objects.create(
            product=product,
            image=image
        )

        return Response({
            'success': True,
            'message': 'Product image added successfully.',
            'image_id': product_image.id,
        }, status=status.HTTP_201_CREATED)


class AdminProductVariantAddAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        variant = ProductVariant.objects.create(
            product=product,
            size_id=request.data.get('size') or None,
            color=request.data.get('color', ''),
            stock=request.data.get('stock', 0),
        )

        return Response({
            'success': True,
            'message': 'Product variant added successfully.',
            'variant_id': variant.id,
        }, status=status.HTTP_201_CREATED)


class AdminProductVariantUpdateAPI(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, variant_id):
        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Variant not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        if 'size' in request.data:
            variant.size_id = request.data.get('size') or None

        if 'color' in request.data:
            variant.color = request.data.get('color', '')

        if 'stock' in request.data:
            variant.stock = request.data.get('stock', 0)

        variant.save()

        return Response({
            'success': True,
            'message': 'Variant updated successfully.',
            'variant_id': variant.id,
        })


class AdminProductVariantDeleteAPI(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, variant_id):
        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Variant not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        variant.delete()

        return Response({
            'success': True,
            'message': 'Variant deleted successfully.',
        })