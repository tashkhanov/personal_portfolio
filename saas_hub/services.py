import time
import requests
from decimal import Decimal
from django.utils import timezone
from .models import Tenant, SubscriptionPayment, TenantSyncLog


class TenantApiClient:
    """
    HTTP-клиент для взаимодействия с удаленными ботами и aiohttp-серверами заведений сети.
    """

    @staticmethod
    def get_remote_status(tenant: Tenant, timeout_sec: float = 2.5) -> dict:
        """
        Пингует удаленный сервер бота, замеряет задержку и запрашивает актуальную статистику.
        """
        url = f"{tenant.api_base_url.rstrip('/')}/api/super/tenants"
        headers = {
            "X-Super-Admin-Token": tenant.api_secret_token,
            "User-Agent": "AsatkhanovHub/1.0",
        }
        start_time = time.time()
        try:
            resp = requests.get(url, headers=headers, timeout=timeout_sec)
            elapsed_ms = int((time.time() - start_time) * 1000)

            is_healthy = resp.status_code == 200
            data = resp.json() if is_healthy else {}

            # Сохраняем аудит-лог пинга
            TenantSyncLog.objects.create(
                tenant=tenant,
                status_code=resp.status_code,
                response_time_ms=elapsed_ms,
                is_healthy=is_healthy,
                error_message="" if is_healthy else f"HTTP {resp.status_code}: {resp.text[:200]}"
            )

            # Находим данные именно этого тенанта
            tenant_info = {}
            if isinstance(data, list):
                for t in data:
                    if t.get("tenant_slug") == tenant.slug:
                        tenant_info = t
                        break
                if not tenant_info and data:
                    tenant_info = data[0]
            elif isinstance(data, dict):
                tenants_list = data.get("tenants", [])
                for t in tenants_list:
                    if t.get("tenant_slug") == tenant.slug:
                        tenant_info = t
                        break
                if not tenant_info and tenants_list:
                    tenant_info = tenants_list[0]

            return {
                "online": is_healthy,
                "latency_ms": elapsed_ms,
                "remote_data": tenant_info,
                "error": None if is_healthy else f"HTTP {resp.status_code}"
            }
        except requests.exceptions.RequestException as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            TenantSyncLog.objects.create(
                tenant=tenant,
                status_code=0,
                response_time_ms=elapsed_ms,
                is_healthy=False,
                error_message=str(e)[:255]
            )
            return {
                "online": False,
                "latency_ms": elapsed_ms,
                "remote_data": {},
                "error": "Сервер бота недоступен (Offline)"
            }

    @staticmethod
    def remote_killswitch(tenant: Tenant, action: str) -> dict:
        """
        Отправляет команду на удаленный бот для переключения рубильника Kill Switch.
        """
        # Эндпоинт в B2B-SaaS: /api/super/tenants/{id_or_slug}/toggle-active
        url = f"{tenant.api_base_url.rstrip('/')}/api/super/tenants/{tenant.slug}/toggle-active"
        headers = {
            "X-Super-Admin-Token": tenant.api_secret_token,
            "Content-Type": "application/json",
            "User-Agent": "AsatkhanovHub/1.0",
        }
        try:
            resp = requests.post(url, headers=headers, json={"action": action}, timeout=3.0)
            return {"success": resp.status_code == 200, "data": resp.json() if resp.status_code == 200 else resp.text}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def remote_extend(tenant: Tenant, days: int = 30) -> dict:
        """
        Синхронизирует продление дней подписки на удаленном сервере бота.
        """
        # Эндпоинт в B2B-SaaS: /api/super/tenants/{id_or_slug}/extend-30
        url = f"{tenant.api_base_url.rstrip('/')}/api/super/tenants/{tenant.slug}/extend-30"
        headers = {
            "X-Super-Admin-Token": tenant.api_secret_token,
            "Content-Type": "application/json",
            "User-Agent": "AsatkhanovHub/1.0",
        }
        try:
            resp = requests.post(url, headers=headers, json={"days": days}, timeout=3.0)
            return {"success": resp.status_code == 200, "data": resp.json() if resp.status_code == 200 else resp.text}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def sync_tenant_subscription(tenant: Tenant) -> dict:
        """
        Полная двухсторонняя синхронизация биллинга: пушит параметры из SaaS Hub (тариф, дату окончания, статус)
        прямо в базу данных удаленного бота.
        """
        url = f"{tenant.api_base_url.rstrip('/')}/api/super/tenants/{tenant.slug}/sync-subscription"
        headers = {
            "X-Super-Admin-Token": tenant.api_secret_token,
            "Content-Type": "application/json",
            "User-Agent": "AsatkhanovHub/1.0",
        }
        expires_str = tenant.subscription_expires_at.strftime("%Y-%m-%d 23:59:59")
        payload = {
            "tier": tenant.tier,
            "monthly_fee": int(tenant.monthly_fee),
            "expires_at": expires_str,
            "is_active": 1 if tenant.is_active else 0,
            "name": tenant.name,
            "contact_phone": tenant.phone,
            "contact_name": tenant.owner_name,
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=3.0)
            return {"success": resp.status_code == 200, "data": resp.json() if resp.status_code == 200 else resp.text}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def sync_remote_tier(tenant: Tenant, tier: str) -> dict:
        """
        Отправляет новый тариф в удаленный бот для немедленного обновления квот и возможностей.
        """
        url = f"{tenant.api_base_url.rstrip('/')}/api/super/tenants/{tenant.slug}/sync-subscription"
        headers = {
            "X-Super-Admin-Token": tenant.api_secret_token,
            "Content-Type": "application/json",
            "User-Agent": "AsatkhanovHub/1.0",
        }
        expires_str = tenant.subscription_expires_at.strftime("%Y-%m-%d 23:59:59")
        payload = {
            "tier": tier,
            "monthly_fee": int(tenant.monthly_fee),
            "expires_at": expires_str,
            "is_active": 1 if tenant.is_active else 0,
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=3.0)
            return {"success": resp.status_code == 200, "data": resp.json() if resp.status_code == 200 else resp.text}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # ОПЕРАЦИОННОЕ УПРАВЛЕНИЕ САЛОНОМ (ЗАПИСИ, БАРБЕРЫ, СМЕНЫ, УСЛУГИ, ФИЛИАЛЫ)
    # =========================================================================

    @staticmethod
    def get_bookings(tenant: Tenant) -> list:
        """Получение всех записей клиентов заведения"""
        url = f"{tenant.api_base_url.rstrip('/')}/api/bookings"
        headers = {"X-Super-Admin-Token": tenant.api_secret_token, "User-Agent": "AsatkhanovHub/1.0"}
        try:
            resp = requests.get(url, headers=headers, timeout=3.0)
            return resp.json() if resp.status_code == 200 else []
        except Exception:
            return []

    @staticmethod
    def update_booking_status(tenant: Tenant, booking_id: int, status: str) -> dict:
        """Смена статуса записи (confirmed, completed, cancelled)"""
        url = f"{tenant.api_base_url.rstrip('/')}/api/bookings/{booking_id}/status"
        headers = {"X-Super-Admin-Token": tenant.api_secret_token, "Content-Type": "application/json", "User-Agent": "AsatkhanovHub/1.0"}
        try:
            resp = requests.post(url, headers=headers, json={"status": status}, timeout=3.0)
            return {"success": resp.status_code == 200, "data": resp.json() if resp.status_code == 200 else resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def create_booking(tenant: Tenant, booking_data: dict) -> dict:
        """Ручное создание записи клиента через Super-Admin панель"""
        url = f"{tenant.api_base_url.rstrip('/')}/api/bookings"
        headers = {"X-Super-Admin-Token": tenant.api_secret_token, "Content-Type": "application/json", "User-Agent": "AsatkhanovHub/1.0"}
        try:
            resp = requests.post(url, headers=headers, json=booking_data, timeout=3.0)
            return {"success": resp.status_code == 200, "data": resp.json() if resp.status_code == 200 else resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_barbers(tenant: Tenant) -> list:
        """Получение всех барберов салона со статусами смен"""
        url = f"{tenant.api_base_url.rstrip('/')}/api/barbers"
        headers = {"X-Super-Admin-Token": tenant.api_secret_token, "User-Agent": "AsatkhanovHub/1.0"}
        try:
            resp = requests.get(url, headers=headers, timeout=3.0)
            return resp.json() if resp.status_code == 200 else []
        except Exception:
            return []

    @staticmethod
    def toggle_barber_shift(tenant: Tenant, barber_id: int) -> dict:
        """Переключение смены барбера ('В смене' / 'Выходной')"""
        url = f"{tenant.api_base_url.rstrip('/')}/api/barbers/{barber_id}/toggle-shift"
        headers = {"X-Super-Admin-Token": tenant.api_secret_token, "User-Agent": "AsatkhanovHub/1.0"}
        try:
            resp = requests.post(url, headers=headers, timeout=3.0)
            return {"success": resp.status_code == 200, "data": resp.json() if resp.status_code == 200 else resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_services(tenant: Tenant) -> list:
        """Получение полного прайс-листа услуг заведения"""
        url = f"{tenant.api_base_url.rstrip('/')}/api/services"
        headers = {"X-Super-Admin-Token": tenant.api_secret_token, "User-Agent": "AsatkhanovHub/1.0"}
        try:
            resp = requests.get(url, headers=headers, timeout=3.0)
            return resp.json() if resp.status_code == 200 else []
        except Exception:
            return []

    @staticmethod
    def get_branches(tenant: Tenant) -> list:
        """Получение списка филиалов заведения"""
        url = f"{tenant.api_base_url.rstrip('/')}/api/branches"
        headers = {"X-Super-Admin-Token": tenant.api_secret_token, "User-Agent": "AsatkhanovHub/1.0"}
        try:
            resp = requests.get(url, headers=headers, timeout=3.0)
            return resp.json() if resp.status_code == 200 else []
        except Exception:
            return []


class BillingService:
    """
    Сервис бизнес-логики биллинга, расчета MRR и фиксации оплат.
    """

    @staticmethod
    def get_network_metrics() -> dict:
        tenants = Tenant.objects.all()
        total_count = tenants.count()
        active_count = 0
        warning_count = 0
        grace_count = 0
        locked_count = 0
        total_mrr = Decimal(0)

        for t in tenants:
            total_mrr += t.monthly_fee
            st = t.subscription_status
            if st == Tenant.STATUS_ACTIVE:
                active_count += 1
            elif st == Tenant.STATUS_WARNING:
                warning_count += 1
            elif st == Tenant.STATUS_GRACE:
                grace_count += 1
            elif st == Tenant.STATUS_LOCKED:
                locked_count += 1

        # Расчет оплат за текущий месяц
        now = timezone.now()
        month_payments = SubscriptionPayment.objects.filter(
            paid_at__year=now.year,
            paid_at__month=now.month
        )
        total_collected_month = sum(p.amount for p in month_payments) if month_payments.exists() else Decimal(0)

        return {
            "total_tenants": total_count,
            "active_count": active_count,
            "warning_count": warning_count,
            "grace_count": grace_count,
            "locked_count": locked_count,
            "total_mrr": total_mrr,
            "formatted_mrr": f"{int(total_mrr):,} сум".replace(",", " "),
            "total_collected_month": total_collected_month,
            "formatted_collected_month": f"{int(total_collected_month):,} сум".replace(",", " "),
            "recent_payments": SubscriptionPayment.objects.select_related('tenant')[:10],
        }

    @staticmethod
    def record_payment_and_extend(tenant: Tenant, amount: Decimal, days: int, method: str, comment: str = "") -> SubscriptionPayment:
        """
        Записывает факт оплаты, сдвигает дату окончания подписки и синхронизирует с удаленным ботом.
        """
        today = timezone.localdate()
        current_expiry = tenant.subscription_expires_at

        # Если подписка уже просрочена, отсчет идет от сегодняшнего дня
        base_date = max(today, current_expiry)
        new_expiry = base_date + timezone.timedelta(days=days)

        tenant.subscription_expires_at = new_expiry
        tenant.is_active = True
        tenant.save()

        # Генерируем номер чека
        receipt_no = f"INV-{tenant.slug.upper()[:4]}-{int(time.time())}"

        payment = SubscriptionPayment.objects.create(
            tenant=tenant,
            amount=amount,
            days_added=days,
            payment_method=method,
            receipt_number=receipt_no,
            comment=comment
        )

        # Полная синхронизация с ботом (пушим точную новую дату и тариф)
        remote_res = TenantApiClient.sync_tenant_subscription(tenant)

        return payment

    @staticmethod
    def toggle_tenant_killswitch(tenant: Tenant, activate: bool) -> dict:
        """
        Переключает флаг активности в Django и отправляет команду на удаленный бот.
        """
        tenant.is_active = activate
        tenant.save()
        remote_res = TenantApiClient.sync_tenant_subscription(tenant)
        return {
            "tenant_id": tenant.id,
            "slug": tenant.slug,
            "is_active": tenant.is_active,
            "status_display": tenant.status_display,
            "status_badge_class": tenant.status_badge_class,
            "remote_sync": remote_res
        }
