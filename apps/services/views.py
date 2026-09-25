from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Service, ServiceRequest


def services_list(request):
    services = Service.objects.filter(is_active=True)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        service_category = request.POST.get('service_category', 'Laptop Repair').strip()
        preferred_time = request.POST.get('preferred_time', 'Morning (9:00 AM – 12:00 PM)').strip()
        issue_description = request.POST.get('issue_description', '').strip()
        device_photo = request.FILES.get('device_photo')

        if full_name and phone and issue_description:
            req_obj = ServiceRequest.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                phone=phone,
                service_category=service_category,
                preferred_time=preferred_time,
                issue_description=issue_description,
                device_photo=device_photo
            )

            photo_url = req_obj.device_photo.url if req_obj.device_photo else None

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('HX-Request'):
                return JsonResponse({
                    'status': 'success',
                    'message': 'Service request submitted successfully! Our technical team in Purnea will call you shortly.',
                    'photo_url': photo_url
                })

            context = {
                'services': services,
                'form_submitted': True,
                'submitted_name': full_name,
            }
            return render(request, 'services.html', context)

    context = {
        'services': services,
        'form_submitted': False,
    }
    return render(request, 'services.html', context)