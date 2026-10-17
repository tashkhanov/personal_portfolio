import json
import secrets
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Tenant, SubscriptionPayment, TenantSyncLog
from .services import TenantApiClient, BillingService
from .middleware import get_effective_host


def superuser_required(view_func):
    """
    Декоратор проверки прав: разрешает доступ только суперпользователю Django.
    Автоматически определяет URL страницы входа в зависимости от субдомена.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            host = get_effective_host(request) or request.get_host().split(':')[0].lower()
            login_url = '/login/' if host.startswith('hub.') or host == 'hub.asatkhanov.uz' else '/saas-hub/login/'
            return redirect(f"{login_url}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper


def hub_login(request):
    """
    Страница входа в командный центр SaaS Hub в luxury dark стиле.
    """
    if request.user.is_authenticated and request.user.is_superuser:
        host = get_effective_host(request) or request.get_host().split(':')[0].lower()
        redirect_url = '/' if host.startswith('hub.') or host == 'hub.asatkhanov.uz' else '/saas-hub/'
        return redirect(redirect_url)

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next')
                if not next_url:
                    host = get_effective_host(request) or request.get_host().split(':')[0].lower()
                    next_url = '/' if host.startswith('hub.') or host == 'hub.asatkhanov.uz' else '/saas-hub/'
                return redirect(next_url)
            else:
                error = "Доступ запрещен. Требуются права Создателя / Супер-администратора."
        else:
            error = "Неверный логин или пароль администратора."

    return render(request, 'saas_hub/login.html', {'error': error})


def hub_logout(request):
    """
    Выход из командного центра.
    """
    logout(request)
    host = get_effective_host(request) or request.get_host().split(':')[0].lower()
    login_url = '/login/' if host.startswith('hub.') or host == 'hub.asatkhanov.uz' else '/saas-hub/login/'
    return redirect(login_url)


@superuser_required
def hub_dashboard(request):
    """
    Главный командный центр: сводные KPI, карточки заведений, живой пинг и Kill Switch.
    """
    metrics = BillingService.get_network_metrics()
    tenants = Tenant.objects.all()

    # Опрашиваем каждый салон в реальном времени для получения живой телеметрии
    telemetry = {}
    for t in tenants:
        telemetry[t.id] = TenantApiClient.get_remote_status(t, timeout_sec=1.5)

    context = {
        'metrics': metrics,
        'tenants': tenants,
        'telemetry': telemetry,
        'now': timezone.now(),
        'method_choices': SubscriptionPayment.METHOD_CHOICES,
    }
    return render(request, 'saas_hub/dashboard.html', context)


@superuser_required
def tenant_detail(request, slug):
    """
    Детальная страница заведения в SaaS Hub:
    быстрые ссылки на родные меню (клиентское, админка, мастер), статус подписки, история оплат и настройки.
    """
    tenant = get_object_or_404(Tenant, slug=slug)
    remote_status = TenantApiClient.get_remote_status(tenant, timeout_sec=1.0)
    payments = tenant.payments.all()
    sync_logs = tenant.sync_logs.all()[:20]

    context = {
        'tenant': tenant,
        'remote_status': remote_status,
        'payments': payments,
        'sync_logs': sync_logs,
        'method_choices': SubscriptionPayment.METHOD_CHOICES,
    }
    return render(request, 'saas_hub/tenant_detail.html', context)


@require_POST
@superuser_required
def api_toggle_shift(request, slug):
    """AJAX переключение смены мастера"""
    try:
        tenant = get_object_or_404(Tenant, slug=slug)
        data = json.loads(request.body)
        barber_id = int(data.get('barber_id'))
        res = TenantApiClient.toggle_barber_shift(tenant, barber_id)
        return JsonResponse(res)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
@superuser_required
def api_update_booking_status(request, slug):
    """AJAX обновление статуса бронирования"""
    try:
        tenant = get_object_or_404(Tenant, slug=slug)
        data = json.loads(request.body)
        booking_id = int(data.get('booking_id'))
        status = data.get('status')
        res = TenantApiClient.update_booking_status(tenant, booking_id, status)
        return JsonResponse(res)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
@superuser_required
def api_create_booking(request, slug):
    """AJAX ручное бронирование от лица администратора / клиента"""
    try:
        tenant = get_object_or_404(Tenant, slug=slug)
        data = json.loads(request.body)
        res = TenantApiClient.create_booking(tenant, data)
        return JsonResponse(res)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
@superuser_required
def api_update_tenant_settings(request, slug):
    """AJAX сохранение настроек заведения"""
    try:
        tenant = get_object_or_404(Tenant, slug=slug)
        data = json.loads(request.body)
        tenant.name = data.get('name', tenant.name).strip()
        tenant.phone = data.get('phone', tenant.phone).strip()
        tenant.owner_name = data.get('owner_name', tenant.owner_name).strip()
        tenant.bot_username = data.get('bot_username', tenant.bot_username).strip()
        tenant.monthly_fee = Decimal(str(data.get('monthly_fee', tenant.monthly_fee)))
        tenant.api_base_url = data.get('api_base_url', tenant.api_base_url).strip()
        tenant.api_secret_token = data.get('api_secret_token', tenant.api_secret_token).strip()
        
        expires_str = data.get('subscription_expires_at')
        if expires_str:
            import datetime
            tenant.subscription_expires_at = datetime.datetime.strptime(expires_str, '%Y-%m-%d').date()

        tenant.notes = data.get('notes', tenant.notes).strip()
        tenant.save()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
@superuser_required
def api_killswitch(request):
    """
    AJAX-рубильник Kill Switch: моментально блокирует или разблокирует доступ к боту и WebApp.
    """
    try:
        data = json.loads(request.body)
        tenant_id = data.get('tenant_id')
        activate = bool(data.get('activate', False))

        tenant = get_object_or_404(Tenant, id=tenant_id)
        result = BillingService.toggle_tenant_killswitch(tenant, activate=activate)
        return JsonResponse({'status': 'ok', 'result': result})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
@superuser_required
def api_extend(request):
    """
    AJAX-продление подписки: добавляет дни, записывает платеж в журнал и синхронизирует с ботом.
    """
    try:
        data = json.loads(request.body)
        tenant_id = data.get('tenant_id')
        days = int(data.get('days', 30))
        amount = Decimal(str(data.get('amount', 500000)))
        method = data.get('method', 'click')
        comment = data.get('comment', 'Продление через SaaS Hub')

        tenant = get_object_or_404(Tenant, id=tenant_id)
        payment = BillingService.record_payment_and_extend(
            tenant=tenant,
            amount=amount,
            days=days,
            method=method,
            comment=comment
        )

        return JsonResponse({
            'status': 'ok',
            'payment_id': payment.id,
            'new_expiry': tenant.subscription_expires_at.strftime('%d.%m.%Y'),
            'days_left': tenant.days_left,
            'status_display': tenant.status_display,
            'status_badge_class': tenant.status_badge_class,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
@superuser_required
def api_add_tenant(request):
    """
    Онбординг нового заведения: регистрирует клиента в центральной базе.
    """
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

        name = data.get('name', '').strip()
        slug = data.get('slug', '').strip().lower()
        bot_username = data.get('bot_username', '').strip()
        owner_name = data.get('owner_name', '').strip()
        phone = data.get('phone', '').strip()
        monthly_fee = Decimal(str(data.get('monthly_fee', 500000)))
        api_base_url = data.get('api_base_url', 'http://127.0.0.1:8080').strip()
        api_secret_token = data.get('api_secret_token', '').strip() or secrets.token_urlsafe(16)

        if not name or not slug:
            return JsonResponse({'status': 'error', 'message': 'Название и Slug обязательны!'}, status=400)

        # Начальный срок подписки: 30 дней вперед
        expiry = timezone.localdate() + timezone.timedelta(days=30)

        tenant = Tenant.objects.create(
            name=name,
            slug=slug,
            bot_username=bot_username,
            owner_name=owner_name,
            phone=phone,
            monthly_fee=monthly_fee,
            api_base_url=api_base_url,
            api_secret_token=api_secret_token,
            subscription_expires_at=expiry,
            is_active=True
        )

        return JsonResponse({'status': 'ok', 'tenant_id': tenant.id, 'slug': tenant.slug})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@superuser_required
def invoice_detail(request, slug, payment_id):
    """
    Стильный печатный инвойс для владельца заведения.
    """
    tenant = get_object_or_404(Tenant, slug=slug)
    payment = get_object_or_404(SubscriptionPayment, id=payment_id, tenant=tenant)

    context = {
        'tenant': tenant,
        'payment': payment,
        'creator_name': 'Ibrokhim Asatkhanov',
        'creator_brand': 'Asatkhanov Technologies / SaaS Network',
        'contact_telegram': '@asatkhanov',
        'contact_website': 'asatkhanov.uz',
    }
    return render(request, 'saas_hub/invoice.html', context)
