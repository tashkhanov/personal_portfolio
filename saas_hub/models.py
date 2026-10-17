import datetime
from django.db import models
from django.utils import timezone


class Tenant(models.Model):
    """
    Модель заведения/салона в B2B SaaS сети (Brohouse и другие клиенты).
    """
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_WARNING = 'WARNING'
    STATUS_GRACE = 'GRACE_PERIOD'
    STATUS_LOCKED = 'LOCKED'

    name = models.CharField(max_length=150, verbose_name="Название заведения")
    slug = models.SlugField(max_length=80, unique=True, verbose_name="Уникальный Slug")
    bot_username = models.CharField(max_length=100, blank=True, default="", verbose_name="Юзернейм бота")
    owner_name = models.CharField(max_length=150, blank=True, default="", verbose_name="Владелец / Управляющий")
    phone = models.CharField(max_length=50, blank=True, default="", verbose_name="Телефон для связи")
    monthly_fee = models.DecimalField(max_digits=12, decimal_places=0, default=500000, verbose_name="Абонплата в месяц (сум)")
    api_base_url = models.URLField(default="http://127.0.0.1:8080", verbose_name="Базовый API URL бота")
    api_secret_token = models.CharField(max_length=255, default="admin123", verbose_name="Мастер-токен супер-админа")
    is_active = models.BooleanField(default=True, verbose_name="Статус рубильника (Kill Switch)")
    subscription_expires_at = models.DateField(verbose_name="Дата окончания подписки")
    grace_period_days = models.PositiveIntegerField(default=2, verbose_name="Льготный период (дней)")
    notes = models.TextField(blank=True, default="", verbose_name="Заметки / История клиента")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Заведение SaaS"
        verbose_name_plural = "Заведения SaaS"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.slug})"

    @property
    def days_left(self) -> int:
        today = timezone.localdate()
        return (self.subscription_expires_at - today).days

    @property
    def subscription_status(self) -> str:
        if not self.is_active:
            return self.STATUS_LOCKED
        d = self.days_left
        if d > 3:
            return self.STATUS_ACTIVE
        elif 0 <= d <= 3:
            return self.STATUS_WARNING
        elif -self.grace_period_days <= d < 0:
            return self.STATUS_GRACE
        else:
            return self.STATUS_LOCKED

    @property
    def status_display(self) -> str:
        status_map = {
            self.STATUS_ACTIVE: "Активна",
            self.STATUS_WARNING: "Истекает (≤ 3 дн)",
            self.STATUS_GRACE: "Льготный период",
            self.STATUS_LOCKED: "Заблокирован",
        }
        return status_map.get(self.subscription_status, "Неизвестно")

    @property
    def status_badge_class(self) -> str:
        badge_map = {
            self.STATUS_ACTIVE: "badge-active",
            self.STATUS_WARNING: "badge-warning",
            self.STATUS_GRACE: "badge-grace",
            self.STATUS_LOCKED: "badge-locked",
        }
        return badge_map.get(self.subscription_status, "badge-secondary")

    @property
    def formatted_monthly_fee(self) -> str:
        return f"{int(self.monthly_fee):,} сум".replace(",", " ")

    @property
    def progress_percent(self) -> int:
        if self.days_left <= 0:
            return 100
        if self.days_left >= 30:
            return 100
        return max(5, min(100, int(self.days_left * 100 / 30)))

    @property
    def health_color(self) -> str:
        if self.days_left <= 0:
            return "var(--red)"
        if self.days_left <= 3:
            return "var(--amber)"
        return "var(--t1)"


class SubscriptionPayment(models.Model):
    """
    Журнал оплат и транзакций по абонентской плате.
    """
    METHOD_CHOICES = [
        ('click', 'Click'),
        ('payme', 'Payme'),
        ('uzum', 'Uzum Bank'),
        ('cash', 'Наличные'),
        ('bank_transfer', 'Банковский перевод (Р/С)'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments', verbose_name="Заведение")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Сумма платежа (сум)")
    paid_at = models.DateTimeField(default=timezone.now, verbose_name="Дата и время оплаты")
    days_added = models.PositiveIntegerField(default=30, verbose_name="Добавлено дней")
    payment_method = models.CharField(max_length=50, choices=METHOD_CHOICES, default='click', verbose_name="Способ оплаты")
    receipt_number = models.CharField(max_length=100, blank=True, default="", verbose_name="Номер чека / Инвойса")
    comment = models.CharField(max_length=255, blank=True, default="", verbose_name="Комментарий к платежу")

    class Meta:
        verbose_name = "Платеж по подписке"
        verbose_name_plural = "Платежи по подпискам"
        ordering = ['-paid_at']

    def __str__(self):
        return f"{self.tenant.name} — {int(self.amount):,} сум ({self.paid_at.strftime('%d.%m.%Y')})"

    @property
    def formatted_amount(self) -> str:
        return f"{int(self.amount):,} сум".replace(",", " ")


class TenantSyncLog(models.Model):
    """
    Логирование сетевого пинга и проверки здоровья удаленного бота.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sync_logs', verbose_name="Заведение")
    status_code = models.IntegerField(default=200, verbose_name="HTTP статус")
    response_time_ms = models.IntegerField(default=0, verbose_name="Время ответа (мс)")
    is_healthy = models.BooleanField(default=True, verbose_name="Бот доступен")
    error_message = models.TextField(blank=True, default="", verbose_name="Ошибка если есть")
    synced_at = models.DateTimeField(auto_now_add=True, verbose_name="Время проверки")

    class Meta:
        verbose_name = "Лог синхронизации"
        verbose_name_plural = "Логи синхронизации"
        ordering = ['-synced_at']
