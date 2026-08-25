import logging
from django.utils.deprecation import MiddlewareMixin
from .models import PageVisit

try:
    from user_agents import parse
    HAS_USER_AGENTS = True
except ImportError:
    HAS_USER_AGENTS = False

logger = logging.getLogger(__name__)

class AnalyticsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 1. Игнорируем запросы от админа (чтобы не трекать тебя)
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return
            
        path = request.path
        
        # 2. Игнорируем бесполезные технические пути
        if path.startswith('/admin/') or path.startswith('/static/') or path.startswith('/media/') or path.startswith('/__reload__/'):
            return
            
        if path in ['/favicon.ico', '/robots.txt', '/apple-touch-icon.png']:
            return
            
        try:
            # 3. Извлекаем реальный IP от Cloudflare
            cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
            if cf_connecting_ip:
                ip = cf_connecting_ip
            else:
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0].strip()
                else:
                    ip = request.META.get('REMOTE_ADDR')
                
            ua_string = request.META.get('HTTP_USER_AGENT', '')
            referer = request.META.get('HTTP_REFERER', '')
            
            # 4. Проверяем на бота и ИГНОРИРУЕМ их
            if HAS_USER_AGENTS and ua_string:
                user_agent = parse(ua_string)
                if user_agent.is_bot:
                    return  # Полностью игнорируем ботов
            
            if not request.session.session_key:
                request.session.save()
            session_key = request.session.session_key or ''
            
            visit = PageVisit(
                ip_address=ip,
                path=path,
                user_agent=ua_string,
                referer=referer,
                session_key=session_key
            )
            
            if HAS_USER_AGENTS and ua_string:
                visit.is_mobile = user_agent.is_mobile
                visit.is_tablet = user_agent.is_tablet
                visit.is_pc = user_agent.is_pc
                visit.is_bot = user_agent.is_bot
                
                visit.browser_family = f"{user_agent.browser.family} {user_agent.browser.version_string}".strip()
                visit.os_family = f"{user_agent.os.family} {user_agent.os.version_string}".strip()
                visit.device_family = user_agent.device.family
            
            visit.save()

            import random
            if random.randint(1, 50) == 1:
                from django.utils import timezone
                from datetime import timedelta
                cutoff = timezone.now() - timedelta(days=30)
                PageVisit.objects.filter(timestamp__lt=cutoff).delete()
            
        except Exception as e:
            logger.error(f"Analytics tracking failed: {e}")
            pass
