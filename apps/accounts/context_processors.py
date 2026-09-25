def account_layout(request):
    """
    Context processor to dynamically supply 'base_template' for account & auth views.
    - For HTMX tab switching targeting '#account-main-content': returns partial base template.
    - For authenticated users full page render: returns 'account_base.html'.
    - For unauthenticated users full page render: returns 'base.html'.
    """
    hx_target = request.headers.get('HX-Target', '')
    if request.headers.get('HX-Request') and (not hx_target or hx_target in ['account-main-content', '#account-main-content']):
        return {'base_template': 'partials/account_partial_base.html'}
    
    if request.user.is_authenticated:
        return {'base_template': 'account_base.html'}
        
    return {'base_template': 'base.html'}
