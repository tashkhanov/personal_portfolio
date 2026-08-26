from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('auth.md', views.auth_md, name='auth_md'),
    path('.well-known/api-catalog', views.api_catalog, name='api_catalog'),
    path('api/openapi.yaml', views.openapi_yaml, name='openapi_yaml'),

    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('llms.txt', views.ai_markdown, name='ai_markdown'),

    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects, name='projects'),
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    path('process/', views.process, name='process'),
    path('api/contact/', views.contact_submit, name='contact_submit'),
    path('api/chat/', views.ai_chat, name='ai_chat'),
]
