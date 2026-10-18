from django.urls import path
from . import views

urlpatterns = [
    path('', views.hub_dashboard, name='subdomain_dashboard'),
    path('login/', views.hub_login, name='subdomain_login'),
    path('logout/', views.hub_logout, name='subdomain_logout'),
    path('tenant/<slug:slug>/', views.tenant_detail, name='subdomain_tenant_detail'),
    path('tenant/<slug:slug>/invoice/<int:payment_id>/', views.invoice_detail, name='subdomain_invoice_detail'),
    path('tenant/<slug:slug>/api/toggle-shift/', views.api_toggle_shift, name='subdomain_api_toggle_shift'),
    path('tenant/<slug:slug>/api/booking-status/', views.api_update_booking_status, name='subdomain_api_booking_status'),
    path('tenant/<slug:slug>/api/create-booking/', views.api_create_booking, name='subdomain_api_create_booking'),
    path('tenant/<slug:slug>/api/settings/', views.api_update_tenant_settings, name='subdomain_api_tenant_settings'),
    path('tenant/<slug:slug>/api/set-tier/', views.api_set_tenant_tier, name='subdomain_api_set_tenant_tier'),
    path('api/killswitch/', views.api_killswitch, name='subdomain_api_killswitch'),
    path('api/extend/', views.api_extend, name='subdomain_api_extend'),
    path('api/tenants/add/', views.api_add_tenant, name='subdomain_api_add_tenant'),
]
