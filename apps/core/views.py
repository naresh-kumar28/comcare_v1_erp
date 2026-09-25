from django.http import JsonResponse
from django.shortcuts import render
from apps.categories.models import Category
from apps.store.models import Product

# --- Health check (no sensitive information exposed) ---

def health(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        db_status = 'ok'
    except Exception:
        db_status = 'error'
    status = 200 if db_status == 'ok' else 503
    return JsonResponse({'status': 'ok' if status == 200 else 'degraded', 'database': db_status}, status=status)

# --- User-Facing Frontend Views ---

def home(request):
    from django.utils import timezone
    from datetime import timedelta

    categories = Category.objects.filter(is_active=True)[:7]
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    new_arrivals = Product.objects.filter(is_new_arrival=True, is_active=True)[:8]
    best_sellers = Product.objects.filter(is_best_seller=True, is_active=True)[:8]

    # --- Recently Viewed Products ---
    cutoff = timezone.now() - timedelta(days=30)
    recently_viewed = Product.objects.none()

    if request.user.is_authenticated:
        # Logged-in: fetch from database
        from apps.store.models import RecentlyViewedProduct
        rv_entries = (
            RecentlyViewedProduct.objects
            .filter(user=request.user, viewed_at__gte=cutoff)
            .select_related('product')
            .order_by('-viewed_at')[:8]
        )
        # Preserve order by extracting products
        recently_viewed = [entry.product for entry in rv_entries if entry.product.is_active][:8]
    else:
        # Guest: fetch from session
        import time
        viewed_list = request.session.get('recently_viewed', [])
        cutoff_ts = int(time.time()) - (30 * 24 * 3600)  # 30 days in seconds

        # Filter by 30-day cutoff and get product IDs (already ordered newest-first)
        product_ids = [v['id'] for v in viewed_list if v.get('ts', 0) >= cutoff_ts][:8]

        if product_ids:
            # Fetch products and reorder to match session order
            products_map = {p.id: p for p in Product.objects.filter(id__in=product_ids, is_active=True)}
            recently_viewed = [products_map[pid] for pid in product_ids if pid in products_map][:8]

    from apps.reviews.models import Review

    client_reviews = (
        Review.objects
        .select_related('user', 'product')
        .order_by('-created_at')[:6]
    )

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'recently_viewed': recently_viewed,
        'client_reviews': client_reviews,
    }
    return render(request, 'home.html', context)



def search(request):
    from django.db.models import Q
    q = request.GET.get('q', '').strip()
    products = []
    if q:
        products = Product.objects.filter(
            Q(title__icontains=q) |
            Q(brand__icontains=q) |
            Q(sku__icontains=q),
            is_active=True
        )[:5]
        if not products:
            from apps.store.utils import log_failed_search_async
            log_failed_search_async(request, q)
    return render(request, 'partials/search_preview_fragment.html', {'products': products, 'query': q})






    

def categories(request):
    from django.db.models import Count, Q
    from apps.categories.models import Category
    categories_list = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    )
    return render(request, 'categories.html', {'categories': categories_list})

def about(request):
    return render(request, 'about.html')
    
def contact(request):
    return render(request, 'contact.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms(request):
    return render(request, 'terms.html')

def refund_policy(request):
    return render(request, 'refund_policy.html')

def page_not_found_view(request, exception=None):
    return render(request, '404.html', status=404)

def server_error_view(request):
    return render(request, '500.html', status=500)



