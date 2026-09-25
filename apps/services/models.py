from django.db import models
from django.utils.text import slugify
from django.conf import settings


class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='laptop', help_text="Lucide icon name (e.g. laptop, printer, video, Wrench)")
    icon_bg_color = models.CharField(max_length=100, default='bg-blue-50 text-[var(--color-primary)]', help_text="Tailwind background & text color classes")
    short_description = models.TextField()
    bullet_points = models.JSONField(default=list, blank=True, help_text="JSON array of bullet points e.g. ['Point 1', 'Point 2']")
    is_active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordering', 'id']
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ServiceRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending / New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    TIME_CHOICES = (
        ('Morning (9:00 AM – 12:00 PM)', 'Morning (9:00 AM – 12:00 PM)'),
        ('Afternoon (12:00 PM – 3:00 PM)', 'Afternoon (12:00 PM – 3:00 PM)'),
        ('Evening (3:00 PM – 6:00 PM)', 'Evening (3:00 PM – 6:00 PM)'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='service_requests'
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    service_category = models.CharField(max_length=100)
    preferred_time = models.CharField(max_length=100, choices=TIME_CHOICES, default='Morning (9:00 AM – 12:00 PM)')
    issue_description = models.TextField()
    device_photo = models.ImageField(upload_to='service_requests/%Y-%m-%d', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, help_text="Internal notes for technicians")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Service Requests / Booking Leads'

    def __str__(self):
        return f"{self.full_name} - {self.service_category} ({self.phone})"
