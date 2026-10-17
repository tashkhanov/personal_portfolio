import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Tenant, SubscriptionPayment, TenantSyncLog
from .middleware import SubdomainRouterMiddleware


class SaasHubModelTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()
        self.tenant = Tenant.objects.create(
            name="Brohouse Barbershop",
            slug="brohouse",
            bot_username="@brohouse_bot",
            owner_name="Шеф",
            phone="+998 97 012-55-55",
            monthly_fee=Decimal(500000),
            api_base_url="http://127.0.0.1:8080",
            api_secret_token="admin123",
            subscription_expires_at=self.today + timezone.timedelta(days=20),
            is_active=True
        )

    def test_tenant_days_left_and_status(self):
        self.assertEqual(self.tenant.days_left, 20)
        self.assertEqual(self.tenant.subscription_status, Tenant.STATUS_ACTIVE)

        # Warning status (<= 3 days)
        self.tenant.subscription_expires_at = self.today + timezone.timedelta(days=2)
        self.tenant.save()
        self.assertEqual(self.tenant.subscription_status, Tenant.STATUS_WARNING)

        # Grace period status (-1 day)
        self.tenant.subscription_expires_at = self.today - timezone.timedelta(days=1)
        self.tenant.save()
        self.assertEqual(self.tenant.subscription_status, Tenant.STATUS_GRACE)

        # Locked status (past grace period)
        self.tenant.subscription_expires_at = self.today - timezone.timedelta(days=5)
        self.tenant.save()
        self.assertEqual(self.tenant.subscription_status, Tenant.STATUS_LOCKED)

        # Manual Kill Switch overrides
        self.tenant.subscription_expires_at = self.today + timezone.timedelta(days=20)
        self.tenant.is_active = False
        self.tenant.save()
        self.assertEqual(self.tenant.subscription_status, Tenant.STATUS_LOCKED)

    def test_payment_recording(self):
        payment = SubscriptionPayment.objects.create(
            tenant=self.tenant,
            amount=Decimal(500000),
            days_added=30,
            payment_method='click',
            receipt_number='INV-TEST-001'
        )
        self.assertIn("500 000 сум", payment.formatted_amount)
        self.assertEqual(self.tenant.payments.count(), 1)


class SaasHubViewAndMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.today = timezone.localdate()
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='secretpassword123',
            email='admin@asatkhanov.uz'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            password='secretpassword123'
        )
        self.tenant = Tenant.objects.create(
            name="Brohouse Test",
            slug="brohouse-test",
            monthly_fee=Decimal(500000),
            subscription_expires_at=self.today + timezone.timedelta(days=15),
            is_active=True
        )

    def test_subdomain_middleware_routing(self):
        from django.test import RequestFactory
        mw = SubdomainRouterMiddleware(lambda r: None)
        rf = RequestFactory()

        def make(host, forwarded=None):
            extra = {'HTTP_HOST': host}
            if forwarded:
                extra['HTTP_X_FORWARDED_HOST'] = forwarded
            req = rf.get('/', **extra)
            req.urlconf = None
            return req

        with self.settings(ALLOWED_HOSTS=['*']):
            req1 = make('hub.asatkhanov.uz')
            mw(req1)
            self.assertEqual(req1.urlconf, 'saas_hub.subdomain_urls')

            req2 = make('hub.localhost:8000')
            mw(req2)
            self.assertEqual(req2.urlconf, 'saas_hub.subdomain_urls')

            req3 = make('asatkhanov.uz')
            mw(req3)
            self.assertIsNone(req3.urlconf)

            # Через Cloudflare Worker: Host = pythonanywhere, оригинальный хост в X-Forwarded-Host
            req4 = make('khan710.pythonanywhere.com', forwarded='hub.asatkhanov.uz')
            mw(req4)
            self.assertEqual(req4.urlconf, 'saas_hub.subdomain_urls')

    def test_dashboard_access_control(self):
        # Anonymous user gets redirected
        resp = self.client.get('/saas-hub/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)

        # Superuser gets 200 OK
        self.client.login(username='admin', password='secretpassword123')
        resp = self.client.get('/saas-hub/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Brohouse Test")

    def test_api_killswitch_view(self):
        self.client.login(username='admin', password='secretpassword123')
        resp = self.client.post(
            '/saas-hub/api/killswitch/',
            data=json.dumps({'tenant_id': self.tenant.id, 'activate': False}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'ok')
        self.tenant.refresh_from_db()
        self.assertFalse(self.tenant.is_active)

    def test_api_extend_view(self):
        self.client.login(username='admin', password='secretpassword123')
        initial_expiry = self.tenant.subscription_expires_at
        resp = self.client.post(
            '/saas-hub/api/extend/',
            data=json.dumps({
                'tenant_id': self.tenant.id,
                'days': 30,
                'amount': 500000,
                'method': 'click',
                'comment': 'Тест продления'
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.subscription_expires_at, initial_expiry + timezone.timedelta(days=30))
        self.assertEqual(self.tenant.payments.count(), 1)
