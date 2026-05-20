from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product, Size, Cart, CartItem, ProductVariant, Wishlist, Review
from django.db.models import Q, Avg
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum

# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import user_passes_test

def home(request):
    categories = Category.objects.filter(is_active=True)[:5]

    new_arrivals = Product.objects.filter(
        is_active=True,
        is_new_arrival=True
    ).order_by('-created_at')[:4]

    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).order_by('-created_at')[:4]

    context = {
        'categories': categories,
        'new_arrivals': new_arrivals,
        'featured_products': featured_products,
    }

    return render(request, 'store/home.html', context)

def category_products(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)

    products = Product.objects.filter(
        category=category,
        is_active=True
    ).order_by('-created_at')

    subcategories = category.subcategories.filter(is_active=True)

    selected_subcategory = request.GET.get('subcategory')
    selected_size = request.GET.get('size')
    selected_color = request.GET.get('color')
    selected_fabric = request.GET.get('fabric')
    selected_fit = request.GET.get('fit')
    selected_pattern = request.GET.get('pattern')
    selected_occasion = request.GET.get('occasion')
    sort = request.GET.get('sort')

    if selected_subcategory:
        products = products.filter(subcategory__slug=selected_subcategory)

    if selected_size:
        products = products.filter(variants__size__name=selected_size).distinct()

    # Detailed filters only for Men and Women
    if category.slug in ['men', 'women']:
        if selected_color:
            products = products.filter(color__iexact=selected_color)

        if selected_fabric:
            products = products.filter(fabric__iexact=selected_fabric)

        if selected_fit:
            products = products.filter(fit__iexact=selected_fit)

        if selected_pattern:
            products = products.filter(pattern__iexact=selected_pattern)

        if selected_occasion:
            products = products.filter(occasion__iexact=selected_occasion)

    if sort == 'low_to_high':
        products = products.order_by('price')
    elif sort == 'high_to_low':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    sizes = Size.objects.filter(
        productvariant__product__category=category
    ).distinct()

    colors = Product.objects.filter(
        category=category,
        is_active=True
    ).exclude(color='').values_list('color', flat=True).distinct()

    fabrics = Product.objects.filter(
        category=category,
        is_active=True
    ).exclude(fabric='').values_list('fabric', flat=True).distinct()

    fits = Product.objects.filter(
        category=category,
        is_active=True
    ).exclude(fit='').values_list('fit', flat=True).distinct()

    patterns = Product.objects.filter(
        category=category,
        is_active=True
    ).exclude(pattern='').values_list('pattern', flat=True).distinct()

    occasions = Product.objects.filter(
        category=category,
        is_active=True
    ).exclude(occasion='').values_list('occasion', flat=True).distinct()

    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
        'sizes': sizes,
        'colors': colors,
        'fabrics': fabrics,
        'fits': fits,
        'patterns': patterns,
        'occasions': occasions,

        'selected_subcategory': selected_subcategory,
        'selected_size': selected_size,
        'selected_color': selected_color,
        'selected_fabric': selected_fabric,
        'selected_fit': selected_fit,
        'selected_pattern': selected_pattern,
        'selected_occasion': selected_occasion,
        'sort': sort,
    }

    return render(request, 'store/category_products.html', context)

def product_detail(request, product_slug):
    product = get_object_or_404(
        Product,
        slug=product_slug,
        is_active=True
    )

    extra_images = product.extra_images.all()
    variants = product.variants.all()

    reviews = product.reviews.filter(is_approved=True).select_related('user')

    average_rating = reviews.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating']

    if average_rating:
        average_rating = round(average_rating, 1)

    user_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(
            user=request.user,
            product=product
        ).first()

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).order_by('-created_at')[:4]

    context = {
        'product': product,
        'extra_images': extra_images,
        'variants': variants,
        'related_products': related_products,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': reviews.count(),
        'user_review': user_review,
    }

    return render(request, 'store/product_detail.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            Cart.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Welcome to VELORA. Your account has been created.')
            return redirect('home')

    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            Cart.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'You are logged in successfully.')
            return redirect('home')

    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    variant_id = request.POST.get('variant')
    quantity = int(request.POST.get('quantity', 1))

    variant = None

    if product.variants.exists():
        if not variant_id:
            messages.error(request, 'Please select a size before adding to cart.')
            return redirect('product_detail', product_slug=product.slug)

        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

        if variant.stock <= 0:
            messages.error(request, 'Selected size is out of stock.')
            return redirect('product_detail', product_slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart')


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'variant').all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }

    return render(request, 'store/cart.html', context)


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    action = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()

    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('cart')


@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    cart_item.delete()
    messages.success(request, 'Product removed from cart.')
    return redirect('cart')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product').order_by('-created_at')

    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, f'{product.name} removed from wishlist.')
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, f'{product.name} added to wishlist.')

    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


@login_required
def remove_wishlist_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    messages.success(request, f'{product.name} removed from wishlist.')
    return redirect('wishlist')

def search_products(request):
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
        ).distinct().order_by('-created_at')

    context = {
        'query': query,
        'products': products,
    }

    return render(request, 'store/search_results.html', context)

def new_arrivals_view(request):
    products = Product.objects.filter(
        is_active=True,
        is_new_arrival=True
    ).order_by('-created_at')

    return render(request, 'store/new_arrivals.html', {
        'products': products
    })


def sale_products_view(request):
    products = Product.objects.filter(
        is_active=True,
        discount_price__isnull=False
    ).order_by('-created_at')

    return render(request, 'store/sale.html', {
        'products': products
    })

@login_required
def profile_view(request):
    user = request.user

    cart, created = Cart.objects.get_or_create(user=user)
    wishlist_count = Wishlist.objects.filter(user=user).count()

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    context = {
        'profile_user': user,
        'cart': cart,
        'wishlist_count': wishlist_count,
    }

    return render(request, 'store/profile.html', context)

@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not rating or not comment:
            messages.error(request, 'Please add both rating and review comment.')
            return redirect('product_detail', product_slug=product.slug)

        Review.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={
                'rating': rating,
                'comment': comment,
                'is_approved': True,
            }
        )

        messages.success(request, 'Your review has been saved.')
        return redirect('product_detail', product_slug=product.slug)

    return redirect('product_detail', product_slug=product.slug)

def support_page(request, page_slug):
    pages = {
        'contact': {
            'title': 'Contact Us',
            'eyebrow': 'VELORA Support',
            'description': 'Need help with products, sizing, orders, or general questions? Reach out to us.',
            'icon': 'fa-headset',
        },
        'returns': {
            'title': 'Returns & Exchanges',
            'eyebrow': 'Easy Returns',
            'description': 'Understand our return and exchange process before shopping.',
            'icon': 'fa-rotate-left',
        },
        'shipping': {
            'title': 'Shipping Policy',
            'eyebrow': 'Delivery Details',
            'description': 'Everything you need to know about delivery timelines and shipping charges.',
            'icon': 'fa-truck-fast',
        },
        'faqs': {
            'title': 'FAQs',
            'eyebrow': 'Quick Answers',
            'description': 'Find answers to common questions about VELORA shopping.',
            'icon': 'fa-circle-question',
        },
        'store-locator': {
            'title': 'Store Locator',
            'eyebrow': 'Visit VELORA',
            'description': 'Find VELORA store information and offline shopping support.',
            'icon': 'fa-location-dot',
        },
        'help': {
            'title': 'Help Center',
            'eyebrow': 'Customer Care',
            'description': 'Get help with your account, cart, wishlist, returns, and shopping experience.',
            'icon': 'fa-life-ring',
        },
    }

    page = pages.get(page_slug)

    if not page:
        return redirect('home')

    if request.method == 'POST' and page_slug == 'contact':
        messages.success(request, 'Your message has been received. We will contact you soon.')
        return redirect('support_page', page_slug='contact')

    context = {
        'page': page,
        'support_type': page_slug,
    }

    return render(request, 'store/support_page.html', context)

def staff_required(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(staff_required, login_url='login')
def admin_dashboard(request):
    total_users = User.objects.count()
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_carts = Cart.objects.count()
    total_cart_items = CartItem.objects.count()
    total_wishlist_items = Wishlist.objects.count()
    total_reviews = Review.objects.count()

    low_stock_variants = ProductVariant.objects.filter(stock__gt=0, stock__lte=5).select_related(
        'product',
        'size'
    )

    out_of_stock_variants = ProductVariant.objects.filter(stock=0).select_related(
        'product',
        'size'
    )

    recent_products = Product.objects.select_related(
        'category',
        'subcategory'
    ).order_by('-created_at')[:6]

    recent_carts = Cart.objects.select_related(
        'user'
    ).order_by('-created_at')[:6]

    recent_reviews = Review.objects.select_related(
        'user',
        'product'
    ).order_by('-created_at')[:6]

    total_stock = ProductVariant.objects.aggregate(
        total=Sum('stock')
    )['total'] or 0

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'active_products': active_products,
        'total_categories': total_categories,
        'total_carts': total_carts,
        'total_cart_items': total_cart_items,
        'total_wishlist_items': total_wishlist_items,
        'total_reviews': total_reviews,
        'low_stock_variants': low_stock_variants,
        'out_of_stock_variants': out_of_stock_variants,
        'recent_products': recent_products,
        'recent_carts': recent_carts,
        'recent_reviews': recent_reviews,
        'total_stock': total_stock,
    }

    return render(request, 'store/admin_dashboard.html', context)

@user_passes_test(staff_required, login_url='login')
def admin_dashboard_data(request, section):
    section_map = {
        'users': {
            'title': 'Registered Users',
            'eyebrow': 'Customer Accounts',
            'description': 'All users registered on VELORA.',
            'icon': 'fa-users',
        },
        'products': {
            'title': 'All Products',
            'eyebrow': 'Product Catalogue',
            'description': 'All products added from Django admin.',
            'icon': 'fa-shirt',
        },
        'categories': {
            'title': 'Categories',
            'eyebrow': 'Store Structure',
            'description': 'Main product categories available on the website.',
            'icon': 'fa-layer-group',
        },
        'stock': {
            'title': 'Stock Details',
            'eyebrow': 'Inventory',
            'description': 'Product size/color variants and stock quantity.',
            'icon': 'fa-boxes-stacked',
        },
        'carts': {
            'title': 'Customer Carts',
            'eyebrow': 'Cart Activity',
            'description': 'Users who have cart records.',
            'icon': 'fa-bag-shopping',
        },
        'cart-items': {
            'title': 'Cart Items',
            'eyebrow': 'Cart Products',
            'description': 'Products currently added to user carts.',
            'icon': 'fa-cart-flatbed',
        },
        'wishlist': {
            'title': 'Wishlist Items',
            'eyebrow': 'Saved Products',
            'description': 'Products saved by users in wishlist.',
            'icon': 'fa-heart',
        },
        'reviews': {
            'title': 'Reviews',
            'eyebrow': 'Customer Voice',
            'description': 'Product ratings and reviews submitted by users.',
            'icon': 'fa-star',
        },
    }

    page = section_map.get(section)

    if not page:
        return redirect('admin_dashboard')

    objects = []

    if section == 'users':
        objects = User.objects.order_by('-date_joined')

    elif section == 'products':
        objects = Product.objects.select_related(
            'category',
            'subcategory'
        ).order_by('-created_at')

    elif section == 'categories':
        objects = Category.objects.order_by('name')

    elif section == 'stock':
        objects = ProductVariant.objects.select_related(
            'product',
            'size'
        ).order_by('product__name')

    elif section == 'carts':
        objects = Cart.objects.select_related(
            'user'
        ).order_by('-created_at')

    elif section == 'cart-items':
        objects = CartItem.objects.select_related(
            'cart',
            'cart__user',
            'product',
            'variant',
            'variant__size'
        ).order_by('-added_at')

    elif section == 'wishlist':
        objects = Wishlist.objects.select_related(
            'user',
            'product'
        ).order_by('-created_at')

    elif section == 'reviews':
        objects = Review.objects.select_related(
            'user',
            'product'
        ).order_by('-created_at')

    context = {
        'section': section,
        'page': page,
        'objects': objects,
    }

    return render(request, 'store/admin_dashboard_data.html', context)