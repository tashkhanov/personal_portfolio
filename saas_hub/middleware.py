def get_effective_host(request) -> str:
    candidates = [
        request.META.get('HTTP_X_FORWARDED_HOST', ''),
        request.META.get('HTTP_X_ORIGINAL_HOST', ''),
        request.META.get('HTTP_HOST', ''),
    ]
    try:
        candidates.append(request.get_host())
    except Exception:
        pass

    for raw in candidates:
        if not raw:
            continue
        for part in raw.split(','):
            h = part.split(':')[0].strip().lower()
            if h.startswith('hub.') or h == 'hub.asatkhanov.uz':
                return h
    return ''


class SubdomainRouterMiddleware:
    """
    Middleware для маршрутизации субдомена hub.asatkhanov.uz.
    Если запрос приходит на хост, начинающийся с 'hub.' (например hub.asatkhanov.uz или hub.localhost),
    Django динамически переключает urlconf на saas_hub.subdomain_urls.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if get_effective_host(request):
            request.urlconf = 'saas_hub.subdomain_urls'
        return self.get_response(request)

