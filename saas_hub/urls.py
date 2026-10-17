from django.urls import path
from . import views

app_name = 'saas_hub'

urlpatterns = [
    path('', views.hub_dashboard, name='dashboard'),
    path('login/', views.hub_login, name='login'),
    path('logout/', views.hub_logout, name='logout'),
    path('tenant/<slug:slug>/', views.tenant_detail, name='tenant_detail'),
    path('tenant/<slug:slug>/invoice/<int:payment_id>/', views.invoice_detail, name='invoice_detail'),
    path('tenant/<slug:slug>/api/toggle-shift/', views.api_toggle_shift, name='api_toggle_shift'),
    path('tenant/<slug:slug>/api/booking-status/', views.api_update_booking_status, name='api_booking_status'),
    path('tenant/<slug:slug>/api/create-booking/', views.api_create_booking, name='api_create_booking'),
    path('tenant/<slug:slug>/api/settings/', views.api_update_tenant_settings, name='api_tenant_settings'),
    path('api/killswitch/', views.api_killswitch, name='api_killswitch'),
    path('api/extend/', views.api_extend, name='api_extend'),
    path('api/tenants/add/', views.api_add_tenant, name='api_add_tenant'),
]
