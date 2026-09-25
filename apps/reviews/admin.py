from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'display_rating',
        'title',
        'is_verified_purchase',
        'created_at',
    )
    # list_filter = (
    #     'rating',
    #     'is_verified_purchase',
    #     'created_at',
    # )
    search_fields = (
        'title',
        'comment',
        'user__first_name',
        'user__last_name',
        'user__phone_number',
        'user__email',
        'product__title',
    )
    raw_id_fields = ('product', 'user')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('Verification & Status', {
            'fields': ('is_verified_purchase',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description="Rating")
    def display_rating(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return f"{obj.rating}/5 ({stars})"
