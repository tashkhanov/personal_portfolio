class SubdomainRouterMiddleware:
    """
    Middleware для маршрутизации субдомена hub.asatkhanov.uz.
    Если запрос приходит на хост, начинающийся с 'hub.' (например hub.asatkhanov.uz или hub.localhost),
    Django динамически переключает urlconf на saas_hub.subdomain_urls.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        if host.startswith('hub.') or host == 'hub.asatkhanov.uz':
            request.urlconf = 'saas_hub.subdomain_urls'
        return self.get_response(request)
