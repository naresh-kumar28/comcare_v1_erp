from django.contrib import admin
from .models import Service, ServiceRequest


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'icon',
        'is_active',
        'ordering',
        'created_at',
    )
    list_editable = ('is_active', 'ordering')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'phone',
        'service_category',
        'preferred_time',
        'status',
        'created_at',
    )
    list_filter = ('status', 'service_category', 'created_at')
    list_editable = ('status',)
    search_fields = ('full_name', 'phone', 'service_category', 'issue_description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Customer Details', {
            'fields': (
                'full_name',
                'phone',
                'service_category',
                'preferred_time',
            )
        }),
        ('Issue Details & Attachment', {
            'fields': (
                'issue_description',
                'device_photo',
            )
        }),
        ('Status & Internal Notes', {
            'fields': (
                'status',
                'notes',
                'created_at',
                'updated_at',
            )
        }),
    )
