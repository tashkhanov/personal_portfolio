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
    def process_response(self, request, response):
        if getattr(response, "status_code", 200) >= 400:
            return response

        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return response
            
        path = request.path

        
        if path.startswith('/admin/') or path.startswith('/static/') or path.startswith('/media/') or path.startswith('/__reload__/'):
            return response
            
        if path in ['/favicon.ico', '/robots.txt', '/apple-touch-icon.png']:
            return response
            
        try:
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
            
            if HAS_USER_AGENTS and ua_string:
                user_agent = parse(ua_string)
                if user_agent.is_bot:
                    return response
            
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

        return response

from django.http import HttpResponse
from .models import Project, Service

class MarkdownNegotiationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'text/markdown' in request.META.get('HTTP_ACCEPT', ''):
            md = [
                "# Asatkhanov Ibrohim - Fullstack Developer Portfolio",
                "Hello AI Agent! This is a machine-readable version of my portfolio.",
                "## About Me",
                "I am a highly skilled Fullstack Developer (Python, Django, Laravel, PHP, JS, Vue). I specialize in eliminating code headaches and delivering robust web systems.",
                "## My Projects"
            ]
            
            for p in Project.objects.all():
                md.append(f"### {p.title}\n- Technologies: {p.tags}\n- Description: {p.description_ru}\n")
                
            md.append("## My Services")
            for s in Service.objects.all():
                md.append(f"### {s.title_ru}\n- Description: {s.description_ru}\n")
                
            md.append("## Contact\nEmail: contact@asatkhanov.uz\nTelegram: @khan710")
                
            return HttpResponse("\n".join(md), content_type="text/markdown")

        return self.get_response(request)
