from django.shortcuts import render
from django.db.models import Q, Count
from django.core.paginator import Paginator
from apps.categories.models import Category
from .models import Product

def shop(request):
    # Fetch all active products
    queryset = Product.objects.filter(is_active=True)

    # 1. Search filter
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(brand__icontains=q) |
            Q(sku__icontains=q)
        )

    # 2. Category filter (can handle multiple selected categories)
    selected_cats = request.GET.getlist('cat')
    # If a single cat is passed via query string from home page (e.g. ?cat=laptop-accessories)
    single_cat = request.GET.get('cat')
    if single_cat and single_cat not in selected_cats:
        selected_cats.append(single_cat)
        
    if selected_cats:
        queryset = queryset.filter(category__slug__in=selected_cats)

    # 3. Brand filter (multiple)
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        queryset = queryset.filter(brand__in=selected_brands)

    # 4. Price range filter
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        try:
            queryset = queryset.filter(selling_price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            queryset = queryset.filter(selling_price__lte=float(max_price))
        except ValueError:
            pass

    # 5. Availability/Stock filter
    selected_stock = request.GET.getlist('stock')
    if selected_stock:
        stock_queries = Q()
        if 'in_stock' in selected_stock:
            stock_queries |= Q(stock_qty__gt=3)
        if 'low_stock' in selected_stock:
            stock_queries |= Q(stock_qty__gt=0, stock_qty__lte=3)
        if 'out_of_stock' in selected_stock:
            stock_queries |= Q(stock_qty=0)
        queryset = queryset.filter(stock_queries)

    # 6. Sorting & Collection Filtering
    sort = request.GET.get('sort', '').strip()
    if sort == 'featured':
        queryset = queryset.filter(is_featured=True).order_by('-created_at')
    elif sort == 'new_arrivals':
        queryset = queryset.filter(is_new_arrival=True).order_by('-created_at')
    elif sort == 'best_sellers':
        queryset = queryset.filter(is_best_seller=True).order_by('-created_at')
    elif sort == 'recently_viewed':
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Case, When
        cutoff = timezone.now() - timedelta(days=30)
        if request.user.is_authenticated:
            from .models import RecentlyViewedProduct
            product_ids = list(
                RecentlyViewedProduct.objects
                .filter(user=request.user, viewed_at__gte=cutoff)
                .order_by('-viewed_at')
                .values_list('product_id', flat=True)[:20]
            )
        else:
            import time
            viewed_list = request.session.get('recently_viewed', [])
            cutoff_ts = int(time.time()) - (30 * 24 * 3600)
            product_ids = [v['id'] for v in viewed_list if v.get('ts', 0) >= cutoff_ts][:20]

        if product_ids:
            queryset = queryset.filter(id__in=product_ids)
            preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(product_ids)])
            queryset = queryset.order_by(preserved_order)
        else:
            queryset = queryset.none()
    elif sort == 'price_asc':
        queryset = queryset.order_by('selling_price')
    elif sort == 'price_desc':
        queryset = queryset.order_by('-selling_price')
    elif sort == 'newest':
        queryset = queryset.order_by('-created_at')
    elif sort == 'rating':
        queryset = queryset.order_by('-rating')
    else:
        # Default: featured first, then newest
        queryset = queryset.order_by('-is_featured', '-created_at')

    # Get dynamic categories with product count annotation
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('name')

    # Get dynamic brands from active products
    brands = Product.objects.filter(is_active=True).values_list('brand', flat=True).distinct().order_by('brand')

    # Pagination
    paginator = Paginator(queryset, 12)  # 12 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Build query string for pagination links (preserves other params)
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    url_params = query_params.urlencode()

    # Build current filters dictionary to pass to template
    current_filters = {
        'q': q,
        'selected_cats': selected_cats,
        'selected_brands': selected_brands,
        'min_price': min_price,
        'max_price': max_price,
        'selected_stock': selected_stock,
        'sort': sort,
    }

    total_products = queryset.count()
    if q and total_products == 0:
        from .utils import log_failed_search_async
        log_failed_search_async(request, q)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_filters': current_filters,
        'url_params': url_params,
        'total_products': total_products,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'partials/product_list_fragment.html', context)

    return render(request, 'shop.html', context)


def product_detail(request, slug):
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from .models import RecentlyViewedProduct

    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]

    # --- Track Recently Viewed ---
    if request.user.is_authenticated:
        # Logged-in: save to database (update_or_create handles duplicates)
        RecentlyViewedProduct.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={'viewed_at': timezone.now()},
        )
        # Trim: keep only the latest 20 entries per user
        old_ids = (
            RecentlyViewedProduct.objects
            .filter(user=request.user)
            .order_by('-viewed_at')
            .values_list('id', flat=True)[20:]
        )
        if old_ids:
            RecentlyViewedProduct.objects.filter(id__in=list(old_ids)).delete()
    else:
        # Guest: save to session
        import time
        viewed_list = request.session.get('recently_viewed', [])

        # Remove existing entry for this product (to move it to the top)
        viewed_list = [v for v in viewed_list if v['id'] != product.id]

        # Prepend new view
        viewed_list.insert(0, {'id': product.id, 'ts': int(time.time())})

        # Keep only latest 20
        viewed_list = viewed_list[:20]

        request.session['recently_viewed'] = viewed_list
        request.session.modified = True

    highlights = [
        {"label": "Processor", "value": product.processor_short, "icon": "cpu"},
        {"label": "RAM", "value": product.ram_short, "icon": "memory-stick"},
        {"label": "Storage", "value": product.storage_short, "icon": "hard-drive"},
        {"label": "Graphics", "value": product.graphics_short, "icon": "component"},
        {"label": "Display", "value": product.display_short, "icon": "monitor"},
        {"label": "Battery", "value": product.battery_short, "icon": "battery"},
        {"label": "Warranty", "value": product.warranty_short, "icon": "shield-check"},
    ]

    highlights = [item for item in highlights if item["value"]]
    
    from django.db.models import Count
    from django.core.paginator import Paginator
    from apps.reviews.models import Review

    rating_breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    total_reviews = product.reviews.count()
    if total_reviews > 0:
        counts = product.reviews.values('rating').annotate(count=Count('id'))
        counts_map = {c['rating']: c['count'] for c in counts}
        for star in range(1, 6):
            rating_breakdown[star] = round((counts_map.get(star, 0) / total_reviews) * 100)

    paginator = Paginator(product.reviews.all(), 10)
    reviews_page = paginator.get_page(1)

    from apps.reviews.views import check_verified_purchase

    user_review = None
    user_has_reviewed = False
    can_review = False
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()
        user_has_reviewed = user_review is not None
        can_review = check_verified_purchase(request.user, product)

    context = {
        'product': product,
        'related_products': related_products,
        'highlights': highlights,
        'reviews': reviews_page,
        'user_has_reviewed': user_has_reviewed,
        'user_review': user_review,
        'can_review': can_review,
        'rating_breakdown': rating_breakdown,
    }
    return render(request, 'product_detail.html', context)