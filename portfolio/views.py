import json
import re
import requests
import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SiteSettings, Stat, Skill, Category, Project, Service, Review, ContactMessage, Certificate, Experience


def get_context():
    settings = SiteSettings.objects.first()
    if not settings:
        settings = SiteSettings.objects.create()
    context = {
        'site': SiteSettings.objects.first(),
        'stats': Stat.objects.all(),
        'skills': Skill.objects.all(),
        'services': Service.objects.all()[:6],
        'projects': Project.objects.filter(is_featured=True)[:6],
        'reviews': Review.objects.all(),
        'categories': Category.objects.filter(project__is_active=True).distinct(),
    }
    return context


def send_telegram(settings, name, email, message):
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
    try:
        text = f"📬 *Новое сообщение с сайта*\n\n👤 *Имя:* {name}\n📧 *Email:* {email}\n\n💬 *Сообщение:*\n{message}"
        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        requests.post(url, json={
            'chat_id': settings.telegram_chat_id,
            'text': text,
            'parse_mode': 'Markdown',
        }, timeout=5)
    except Exception:
        pass


def index(request):
    ctx = get_context()
    ctx['projects'] = Project.objects.filter(is_active=True, is_featured=True)[:4]
    
    reviews_list = Review.objects.filter(is_active=True)
    from django.core.paginator import Paginator
    paginator = Paginator(reviews_list, 6)
    page_number = request.GET.get('page')
    ctx['reviews'] = paginator.get_page(page_number)
    
    response = render(request, 'portfolio/index.html', ctx)
    response['Link'] = '</.well-known/api-catalog>; rel="api-catalog", </api/openapi.yaml>; rel="service-desc", </llms.txt>; rel="describedby"'
    return response


def about(request):
    ctx = get_context()
    ctx['certificates'] = Certificate.objects.all()
    ctx['experiences'] = Experience.objects.all()
    return render(request, 'portfolio/about.html', ctx)


from django.core.paginator import Paginator

def projects(request):
    ctx = get_context()
    cat_slug = request.GET.get('cat', 'all')
    if cat_slug != 'all':
        project_list = Project.objects.filter(is_active=True, category__slug=cat_slug)
    else:
        project_list = Project.objects.filter(is_active=True)
        
    paginator = Paginator(project_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    ctx['all_projects'] = page_obj
    ctx['selected_category'] = cat_slug
    return render(request, 'portfolio/projects.html', ctx)


def service_detail(request, slug):
    ctx = get_context()
    service = get_object_or_404(Service, slug=slug)
    ctx['service'] = service
    ctx['features'] = service.features.all()
    ctx['related_projects'] = Project.objects.filter(is_active=True)[:3]
    return render(request, 'portfolio/service_detail.html', ctx)


def process(request):
    ctx = get_context()
    ctx['process_steps'] = [
        {'num': '01', 'title_ru': 'Знакомство', 'title_en': 'Discovery', 'desc_ru': 'Обсуждаем вашу задачу, сроки и бюджет. Выясняю все детали, чтобы предложить оптимальное решение.', 'desc_en': 'We discuss your task, timeline and budget.', 'icon': '💬', 'duration': '1 день'},
        {'num': '02', 'title_ru': 'Анализ и ТЗ', 'title_en': 'Analysis & Specs', 'desc_ru': 'Составляю техническое задание, разбиваю проект на этапы, утверждаю с вами.', 'desc_en': 'I prepare technical specifications.', 'icon': '📋', 'duration': '1-2 дня'},
        {'num': '03', 'title_ru': 'Разработка', 'title_en': 'Development', 'desc_ru': 'Пишу чистый и масштабируемый код. Регулярно показываю промежуточные результаты.', 'desc_en': 'Writing clean and scalable code.', 'icon': '⚙️', 'duration': 'от 3 дней'},
        {'num': '04', 'title_ru': 'Тестирование', 'title_en': 'Testing', 'desc_ru': 'Проверяю все сценарии, тестирую на разных устройствах, исправляю баги.', 'desc_en': 'Testing all scenarios and devices.', 'icon': '🧪', 'duration': '1-2 дня'},
        {'num': '05', 'title_ru': 'Запуск', 'title_en': 'Launch', 'desc_ru': 'Деплою на сервер, проверяю работоспособность в продакшене, передаю доступы.', 'desc_en': 'Deploying to production.', 'icon': '🚀', 'duration': '1 день'},
        {'num': '06', 'title_ru': 'Поддержка', 'title_en': 'Support', 'desc_ru': 'Помогаю с доработками, отвечаю на вопросы, обеспечиваю стабильную работу.', 'desc_en': 'Ongoing support and improvements.', 'icon': '🛠️', 'duration': '30 дней'},
    ]
    return render(request, 'portfolio/process.html', ctx)


def contact_submit(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()
        if name and email and message_text:
            ContactMessage.objects.create(name=name, email=email, message=message_text)
            settings = SiteSettings.objects.first()
            send_telegram(settings, name, email, message_text)
            return JsonResponse({'status': 'ok', 'message': 'Сообщение отправлено!'})
        return JsonResponse({'status': 'error', 'message': 'Заполните все поля'})
    return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'})


SYSTEM_PROMPT = """Ты AI-ассистент на сайте фрилансера Khan.
Он fullstack-разработчик. Отвечай кратко и по делу. Не используй звездочки (*) и markdown форматирование — пиши обычным текстом. Если клиент хочет обсудить новый проект — отправляй в Telegram @asatkhanov."""


def clean_response(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'^\s*[-•]\s*', '— ', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


@csrf_exempt
def ai_chat(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'})

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        history = data.get('history', [])
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'status': 'error', 'message': 'Неверный формат данных'})

    if not user_message:
        return JsonResponse({'status': 'error', 'message': 'Введите сообщение'})

    try:
        from .models import Project, Service, Skill
        
        projects = Project.objects.filter(is_active=True)
        projects_text = "Мои проекты:\n" + "\n".join([f"— {p.title}: {p.description_ru}. Стек: {p.tags}. Статус: {p.status}." for p in projects])
        
        services = Service.objects.all()
        services_text = "Мои услуги:\n" + "\n".join([f"— {s.title_ru}: {s.description_ru}." for s in services])
        
        skills = Skill.objects.all()
        skills_text = "Мой стек технологий: " + ", ".join([s.name for s in skills]) + "."
        
        context_prompt = f"{SYSTEM_PROMPT}\n\nИНФОРМАЦИЯ ИЗ БАЗЫ ДАННЫХ (используй её для ответов):\n{skills_text}\n\n{services_text}\n\n{projects_text}"

        contents = []
        for msg in history[-20:]:
            contents.append({"role": msg.get("role", "user"), "parts": [{"text": msg.get("text", "")}]})

        r = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key=AIzaSyA3_xDtbS_0aGZ87lao6KH4ioDn48k37io',
            json={
                "systemInstruction": {"parts": [{"text": context_prompt}]},
                "contents": contents, 
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}
            },
            timeout=30
        )
        if r.status_code == 200:
            resp = r.json()
            text = resp['candidates'][0]['content']['parts'][0]['text']
            return JsonResponse({'status': 'ok', 'response': clean_response(text)})
        print("GEMINI API ERROR:", r.text)
        return JsonResponse({'status': 'ok', 'response': 'Напишите Khan в Telegram: @asatkhanov'})
    except Exception as e:
        print("GEMINI EXCEPTION:", str(e))
        return JsonResponse({'status': 'ok', 'response': 'Напишите Khan в Telegram: @asatkhanov'})

from django.http import HttpResponse

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def sitemap_xml(request):
    from django.urls import reverse
    from .models import Service
    
    pages = ['portfolio:index', 'portfolio:about', 'portfolio:projects', 'portfolio:process']
    base_url = f"{request.scheme}://{request.get_host()}"
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for page in pages:
        xml.append(f"  <url><loc>{base_url}{reverse(page)}</loc></url>")
        
    for service in Service.objects.all():
        xml.append(f"  <url><loc>{base_url}{reverse('portfolio:service_detail', args=[service.slug])}</loc></url>")
        
    xml.append('</urlset>')
    
    return HttpResponse("\n".join(xml), content_type="application/xml")

def ai_markdown(request):
    from .models import Project, Service
    
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

from django.http import JsonResponse

def api_catalog(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    data = {
        "linkset": [
            {
                "anchor": f"{base_url}/api/",
                "service-desc": [
                    {"href": f"{base_url}/api/openapi.yaml", "type": "application/vnd.oai.openapi"}
                ],
                "service-doc": [
                    {"href": f"{base_url}/api/docs/", "type": "text/html"}
                ],
                "status": [
                    {"href": f"{base_url}/", "type": "text/html"}
                ]
            }
        ]
    }
    return JsonResponse(data, content_type='application/linkset+json')

def openapi_yaml(request):
    yaml_content = """openapi: 3.0.0
info:
  title: Asatkhanov Portfolio API
  version: 1.0.0
paths:
  /api/contact/:
    post:
      summary: Send a contact message
      responses:
        '200':
          description: OK
"""
    from django.http import HttpResponse
    return HttpResponse(yaml_content, content_type='application/yaml')

def auth_md(request):
    md = """# auth.md

This site is a public portfolio. There are no private APIs or resources that require authentication for AI agents.
All content is publicly available.

## Agent Audience
All AI agents, crawlers, and LLMs.

## Registration
No registration is required.

## Authentication Methods
None required.
"""
    from django.http import HttpResponse
    return HttpResponse(md, content_type='text/markdown')

def oauth_discovery(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    data = {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/auth.md",
        "token_endpoint": f"{base_url}/auth.md",
        "jwks_uri": f"{base_url}/.well-known/jwks.json",
        "grant_types_supported": ["client_credentials"],
        "response_types_supported": ["token"]
    }
    from django.http import JsonResponse
    return JsonResponse(data)

def jwks_json(request):
    from django.http import JsonResponse
    return JsonResponse({"keys": []})

def oauth_protected_resource(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    data = {
        "resource": base_url,
        "authorization_servers": [
            base_url
        ],
        "scopes_supported": ["read"],
        "bearer_methods_supported": ["header"]
    }
    from django.http import JsonResponse
    return JsonResponse(data)

def agent_card_json(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    data = {
        "name": "Asatkhanov Portfolio Agent",
        "version": "1.0.0",
        "description": "Information agent for Ibrohim Asatkhanov's portfolio, skills, and services.",
        "supportedInterfaces": [
            {
                "url": f"{base_url}/api/chat/",
                "transport": "http"
            }
        ],
        "capabilities": [
            {
                "id": "cap-info",
                "name": "Portfolio Information",
                "description": "Provides details about Ibrohim's projects and skills."
            }
        ],
        "skills": [
            {
                "id": "skill-contact",
                "name": "Contact Submission",
                "description": "Can send a message to Ibrohim."
            }
        ],
        "extensions": [
            {
                "uri": "https://github.com/google-agentic-commerce/AP2/tree/v0.1.0",
                "required": True,
                "params": {
                    "roles": ["merchant"]
                }
            }
        ]
    }
    from django.http import JsonResponse
    return JsonResponse(data)

def agent_skills_skill(request):
    md = """---
name: contact-form
description: Submits a contact request to the portfolio owner.
---
# Contact Form Skill
This skill allows agents to submit a message via the /api/contact/ endpoint.
POST /api/contact/
Content-Type: application/json
{
  "name": "Agent",
  "email": "agent@example.com",
  "message": "Hello"
}
"""
    from django.http import HttpResponse
    return HttpResponse(md, content_type='text/markdown')

def agent_skills_index(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    skill_url = f"{base_url}/.well-known/agent-skills/contact-skill.md"
    
    # Recreate the exact skill content to hash it
    skill_content = """---
name: contact-form
description: Submits a contact request to the portfolio owner.
---
# Contact Form Skill
This skill allows agents to submit a message via the /api/contact/ endpoint.
POST /api/contact/
Content-Type: application/json
{
  "name": "Agent",
  "email": "agent@example.com",
  "message": "Hello"
}
"""
    import hashlib
    digest = hashlib.sha256(skill_content.encode('utf-8')).hexdigest()
    
    data = {
        "$schema": "https://schemas.agentskills.io/discovery/0.2.0/schema.json",
        "skills": [
            {
                "name": "contact-form",
                "type": "skill-md",
                "description": "Submits a contact request to the portfolio owner.",
                "url": skill_url,
                "digest": f"sha256:{digest}"
            }
        ]
    }
    from django.http import JsonResponse
    return JsonResponse(data)

def mcp_server_card(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    data = {
        "serverInfo": {
            "name": "Asatkhanov MCP Server",
            "version": "1.0.0"
        },
        "endpoints": [
            {
                "url": f"{base_url}/mcp",
                "transport": "http"
            }
        ],
        "capabilities": {
            "tools": {
                "submit_contact": {
                    "description": "Submit a contact message to Ibrohim"
                }
            },
            "resources": {
                "portfolio_data": {
                    "description": "JSON representation of all projects and services"
                }
            },
            "prompts": {}
        }
    }
    from django.http import JsonResponse
    return JsonResponse(data)

def http_message_signatures_directory(request):
    data = {
        "keys": [
            {
                "kty": "RSA",
                "kid": "agent-key-2026",
                "use": "sig",
                "alg": "RS256",
                "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw",
                "e": "AQAB"
            }
        ]
    }
    from django.http import JsonResponse
    return JsonResponse(data)

def acp_json(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    data = {
        "protocol": {
            "name": "acp",
            "version": "1.0.0"
        },
        "api_base_url": f"{base_url}/api",
        "transports": ["http"],
        "capabilities": {
            "services": ["portfolio_booking"]
        }
    }
    from django.http import JsonResponse
    return JsonResponse(data)
