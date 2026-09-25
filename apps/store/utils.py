import ipaddress
import threading
import requests
from django.db import close_old_connections


def get_client_ip(request):
    """
    Extract client IP address from Django request, handling proxy/load balancer
    headers (HTTP_X_FORWARDED_FOR) as well as REMOTE_ADDR.
    """
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_private_or_local_ip(ip):
    """
    Check if an IP address is local, loopback, or private range.
    """
    if not ip or ip.lower() in ('localhost', '127.0.0.1', '::1'):
        return True
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_multicast or ip_obj.is_link_local
    except ValueError:
        return False


def _perform_ip_lookup_and_log(query, ip_address, user_id):
    """
    Worker function executed in background thread. Performs IP geolocation
    lookup via ip-api.com and saves FailedSearchLog entry.
    """
    from .models import FailedSearchLog

    city = None
    region = None
    country = None

    try:
        if is_private_or_local_ip(ip_address):
            city = 'Local'
            region = 'Local'
            country = 'Local'
        else:
            try:
                url = f"http://ip-api.com/json/{ip_address}"
                resp = requests.get(url, timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get('status') == 'success':
                        city = data.get('city')
                        region = data.get('regionName') or data.get('region')
                        country = data.get('country')
            except Exception:
                # Catch any timeout/network/API error silently so search logging succeeds
                pass

        user = None
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.filter(pk=user_id).first()
            except Exception:
                pass

        # Clean IP address for GenericIPAddressField validation
        valid_ip = ip_address
        if ip_address:
            try:
                ipaddress.ip_address(ip_address)
            except ValueError:
                valid_ip = None

        FailedSearchLog.objects.create(
            search_query=query,
            city=city,
            region=region,
            country=country,
            ip_address=valid_ip,
            user=user
        )
    except Exception:
        pass
    finally:
        close_old_connections()


def log_failed_search_async(request, search_query):
    """
    Spawns non-blocking thread to log zero-result search query asynchronously.
    """
    query = (search_query or '').strip()
    if not query:
        return

    ip_address = get_client_ip(request)
    user_id = request.user.id if request.user and request.user.is_authenticated else None

    thread = threading.Thread(
        target=_perform_ip_lookup_and_log,
        args=(query, ip_address, user_id),
        daemon=True
    )
    thread.start()
