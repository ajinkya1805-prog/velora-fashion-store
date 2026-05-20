from django.urls import path
from . import api_views

urlpatterns = [
    # Public user APIs
    path('user/categories/', api_views.UserCategoryListAPI.as_view(), name='api_user_categories'),
    path('user/products/', api_views.UserProductListAPI.as_view(), name='api_user_products'),
    path('user/products/<slug:product_slug>/', api_views.UserProductDetailAPI.as_view(), name='api_user_product_detail'),
    path('user/search/', api_views.UserSearchAPI.as_view(), name='api_user_search'),

    # Cart APIs
    path('user/cart/', api_views.UserCartAPI.as_view(), name='api_user_cart'),
    path('user/cart/add/', api_views.UserCartAddAPI.as_view(), name='api_user_cart_add'),
    path('user/cart/update/<int:item_id>/', api_views.UserCartUpdateAPI.as_view(), name='api_user_cart_update'),
    path('user/cart/remove/<int:item_id>/', api_views.UserCartRemoveAPI.as_view(), name='api_user_cart_remove'),

    # Wishlist APIs
    path('user/wishlist/', api_views.UserWishlistAPI.as_view(), name='api_user_wishlist'),
    path('user/wishlist/toggle/', api_views.UserWishlistToggleAPI.as_view(), name='api_user_wishlist_toggle'),

    # Profile APIs
    path('user/profile/', api_views.UserProfileAPI.as_view(), name='api_user_profile'),
    path('user/profile/update/', api_views.UserProfileUpdateAPI.as_view(), name='api_user_profile_update'),

    # Reviews APIs
    path('user/products/<int:product_id>/reviews/', api_views.UserProductReviewsAPI.as_view(), name='api_user_product_reviews'),
    path('user/products/<int:product_id>/reviews/add/', api_views.UserReviewAddAPI.as_view(), name='api_user_review_add'),

    # Admin APIs
    path('admin/dashboard/stats/', api_views.AdminDashboardStatsAPI.as_view(), name='api_admin_dashboard_stats'),
    path('admin/users/', api_views.AdminUsersAPI.as_view(), name='api_admin_users'),

    path('admin/products/', api_views.AdminProductsAPI.as_view(), name='api_admin_products'),
    path('admin/products/create/', api_views.AdminProductCreateAPI.as_view(), name='api_admin_product_create'),
    path('admin/products/<int:product_id>/update/', api_views.AdminProductUpdateAPI.as_view(), name='api_admin_product_update'),
    path('admin/products/<int:product_id>/delete/', api_views.AdminProductDeleteAPI.as_view(), name='api_admin_product_delete'),
    path('admin/products/<int:product_id>/images/add/', api_views.AdminProductImageAddAPI.as_view(), name='api_admin_product_image_add'),
    path('admin/products/<int:product_id>/variants/add/', api_views.AdminProductVariantAddAPI.as_view(), name='api_admin_product_variant_add'),

    path('admin/variants/<int:variant_id>/update/', api_views.AdminProductVariantUpdateAPI.as_view(), name='api_admin_variant_update'),
    path('admin/variants/<int:variant_id>/delete/', api_views.AdminProductVariantDeleteAPI.as_view(), name='api_admin_variant_delete'),

    path('admin/categories/', api_views.AdminCategoriesAPI.as_view(), name='api_admin_categories'),
    path('admin/stock/', api_views.AdminStockAPI.as_view(), name='api_admin_stock'),
    path('admin/carts/', api_views.AdminCartsAPI.as_view(), name='api_admin_carts'),
    path('admin/cart-items/', api_views.AdminCartItemsAPI.as_view(), name='api_admin_cart_items'),
    path('admin/wishlist/', api_views.AdminWishlistAPI.as_view(), name='api_admin_wishlist'),
    path('admin/reviews/', api_views.AdminReviewsAPI.as_view(), name='api_admin_reviews'),
    path('admin/reviews/<int:review_id>/approve/', api_views.AdminReviewApproveAPI.as_view(), name='api_admin_review_approve'),
    path('admin/reviews/<int:review_id>/reject/', api_views.AdminReviewRejectAPI.as_view(), name='api_admin_review_reject'),
]