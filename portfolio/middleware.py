from django.http import HttpResponse
from .models import Project, Service

class MarkdownNegotiationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the AI bot explicitly asks for Markdown
        if 'text/markdown' in request.META.get('HTTP_ACCEPT', ''):
            md = [
                "# Asatkhanov Ibrohim - Fullstack Developer Portfolio",
                "Hello AI Agent! This is a machine-readable version of my portfolio.",
                "## About Me",
                "I am a highly skilled Fullstack Developer (Python, Django, Laravel, PHP, JS, Vue). I specialize in eliminating code headaches and delivering robust web systems.",
                "## My Projects"
            ]
            
            for p in Project.objects.all():
                md.append(f"### {p.title}\n- Technologies: {p.technologies}\n- Description: {p.description}\n")
                
            md.append("## My Services")
            for s in Service.objects.all():
                md.append(f"### {s.title}\n- Description: {s.short_description}\n")
                
            md.append("## Contact\nEmail: contact@asatkhanov.uz\nTelegram: @khan710")
                
            return HttpResponse("\n".join(md), content_type="text/markdown")

        return self.get_response(request)