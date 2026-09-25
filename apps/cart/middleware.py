class GuestSessionMiddleware:
    """
    Middleware that preserves the guest session key in request.session['guest_session_key']
    so that when session key cycles upon login, guest cart and wishlist can be merged smoothly.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and not request.user.is_authenticated:
            if hasattr(request, 'session') and request.session.session_key:
                request.session['guest_session_key'] = request.session.session_key
                request._pre_login_session_key = request.session.session_key
        return self.get_response(request)
