from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review


def update_product_rating(product):
    agg = product.reviews.aggregate(avg_rating=Avg('rating'))
    product.rating = round(agg['avg_rating'], 1) if agg['avg_rating'] else 0
    product.reviews_count = product.reviews.count()
    product.save(update_fields=['rating', 'reviews_count'])


@receiver(post_save, sender=Review)
def review_saved(sender, instance, **kwargs):
    update_product_rating(instance.product)


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    update_product_rating(instance.product)
