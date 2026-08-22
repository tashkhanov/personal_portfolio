from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects, name='projects'),
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    path('process/', views.process, name='process'),
    path('api/contact/', views.contact_submit, name='contact_submit'),
    path('api/chat/', views.ai_chat, name='ai_chat'),
]
