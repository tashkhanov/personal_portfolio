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
    
    return render(request, 'portfolio/index.html', ctx)


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
