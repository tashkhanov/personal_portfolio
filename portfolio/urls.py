from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [



    path('.well-known/acp.json', views.acp_json, name='acp_json'),

    path('.well-known/http-message-signatures-directory', views.http_message_signatures_directory, name='http_message_signatures_directory'),

    path('.well-known/mcp/server-card.json', views.mcp_server_card, name='mcp_server_card'),

    path('.well-known/agent-skills/index.json', views.agent_skills_index, name='agent_skills_index'),
    path('.well-known/agent-skills/contact-skill.md', views.agent_skills_skill, name='agent_skills_skill'),

    path('.well-known/agent-card.json', views.agent_card_json, name='agent_card_json'),
    path('.well-known/oauth-protected-resource', views.oauth_protected_resource, name='oauth_protected_resource'),
    path('.well-known/jwks.json', views.jwks_json, name='jwks_json'),
    path('.well-known/oauth-authorization-server', views.oauth_discovery, name='oauth_discovery'),
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
