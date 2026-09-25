from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from apps.cart.models import OrderItem
from apps.store.models import Product
from .models import Review


def check_verified_purchase(user, product):
    return OrderItem.objects.filter(
        order__user=user,
        order__order_status='delivered',
        product=product
    ).exists()


def get_rating_breakdown(product):
    rating_breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    total_reviews = product.reviews.count()
    if total_reviews > 0:
        counts = product.reviews.values('rating').annotate(count=Count('id'))
        counts_map = {c['rating']: c['count'] for c in counts}
        for star in range(1, 6):
            rating_breakdown[star] = round((counts_map.get(star, 0) / total_reviews) * 100)
    return rating_breakdown


@login_required(login_url='login')
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not check_verified_purchase(request.user, product):
        is_htmx = getattr(request, 'htmx', False) or request.headers.get('HX-Request')
        if is_htmx:
            return render(request, 'partials/review_error.html', 
                          {'message': 'You can only review products you have purchased and received.'}, 
                          status=403)
        return HttpResponseForbidden("You can only review products you have purchased and received.")

    if request.method == "POST":
        rating = max(1, min(5, int(request.POST.get('rating', 5))))
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()

        review, created = Review.objects.get_or_create(
            product=product, user=request.user,
            defaults={
                'rating': rating, 
                'title': title, 
                'comment': comment
            }
        )
        if not created:
            # existing review update (edit case)
            review.rating = rating
            review.title = title
            review.comment = comment
        review.is_verified_purchase = check_verified_purchase(request.user, product)
        review.save()

        # Refresh product & construct OOB rating summary
        product.refresh_from_db()
        rating_breakdown = get_rating_breakdown(product)
        user_has_reviewed = True

        card_html = render_to_string('partials/review_card.html', {'review': review}, request=request)
        oob_html = render_to_string('partials/rating_summary_oob.html', {
            'product': product,
            'rating_breakdown': rating_breakdown,
            'user_has_reviewed': user_has_reviewed,
            'request': request,
        }, request=request)

        response = HttpResponse(card_html + oob_html)
        response['HX-Trigger'] = 'closeReviewModal'
        return response
    return HttpResponseBadRequest()


@login_required(login_url='login')
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == "POST":
        review.rating = max(1, min(5, int(request.POST.get('rating', review.rating))))
        review.title = request.POST.get('title', review.title).strip()
        review.comment = request.POST.get('comment', review.comment).strip()
        review.save()

        product = review.product
        product.refresh_from_db()
        rating_breakdown = get_rating_breakdown(product)

        card_html = render_to_string('partials/review_card.html', {'review': review}, request=request)
        oob_html = render_to_string('partials/rating_summary_oob.html', {
            'product': product,
            'rating_breakdown': rating_breakdown,
            'user_has_reviewed': True,
            'request': request,
        }, request=request)

        return HttpResponse(card_html + oob_html)
    return HttpResponseBadRequest()


@login_required(login_url='login')
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product = review.product
    review.delete()

    product.refresh_from_db()
    rating_breakdown = get_rating_breakdown(product)
    oob_html = render_to_string('partials/rating_summary_oob.html', {
        'product': product,
        'rating_breakdown': rating_breakdown,
        'user_has_reviewed': False,
        'request': request,
    }, request=request)

    return HttpResponse(oob_html)


def load_more_reviews(request, product_id):
    from django.core.paginator import Paginator
    product = get_object_or_404(Product, id=product_id)
    page_number = request.GET.get('page', 2)
    review_list = product.reviews.all()
    paginator = Paginator(review_list, 10)
    page_obj = paginator.get_page(page_number)
    return render(request, 'partials/review_list_fragment.html', {
        'reviews': page_obj,
        'product': product,
    })
