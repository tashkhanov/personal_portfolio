from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, Stat, Skill, Category, Project, ProjectImage, Service, ServiceFeature, Review, ContactMessage, PageVisit, Certificate, Experience

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'video', 'caption', 'order']

class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1
    fields = ['text_ru', 'order']

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основное', {'fields': ('name', 'title', 'subtitle', 'is_available', 'hero_text', 'about_text', 'resume', 'portrait', 'og_image', 'about_full_text')}),
        ('Контакты', {'fields': ('kwork_username', 'kwork_url', 'telegram_username', 'telegram_url', 'email', 'github_url')}),
        ('Telegram интеграция', {'fields': ('telegram_bot_token', 'telegram_chat_id'), 'description': 'Для получения сообщений с формы обратной связи'}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ['value', 'label_ru', 'order']
    list_editable = ['order']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['title', 'institution', 'issued_date', 'order']
    list_editable = ['order']
    search_fields = ['title', 'institution']

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'period', 'order']
    list_editable = ['order']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_ru', 'slug']
    prepopulated_fields = {'slug': ('name_ru',)}

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['colored_title', 'category', 'year', 'status', 'is_featured', 'is_active', 'order']
    list_display_links = ['colored_title']
    list_filter = ['category', 'is_featured', 'is_active', 'year']
    search_fields = ['title', 'tags']
    list_editable = ['category', 'year', 'status', 'is_featured', 'is_active', 'order']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]
    fieldsets = (
        ('Основное', {'fields': ('title', 'slug', 'category', 'icon', 'gradient', 'image')}),
        ('Описание', {'fields': ('description_ru', 'full_description_ru')}),
        ('Детали', {'fields': ('tags', 'year', 'status', 'client_name')}),
        ('Ссылки', {'fields': ('demo_url', 'github_url')}),
        ('Настройки', {'fields': ('is_featured', 'is_active', 'order')}),
    )

    def colored_title(self, obj):
        return format_html('<span style="color: #00d4ff; font-weight: bold;">{}</span>', obj.title)
    colored_title.short_description = 'Название'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'icon', 'order']
    list_display_links = ['title_ru']
    list_editable = ['icon', 'order']
    prepopulated_fields = {'slug': ('title_ru',)}
    inlines = [ServiceFeatureInline]
    fieldsets = (
        ('Основное', {'fields': ('icon', 'title_ru', 'slug', 'gradient')}),
        ('Описание', {'fields': ('description_ru', 'full_description_ru')}),
        ('Настройки', {'fields': ('order',)}),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author', 'role_ru', 'stars', 'is_active', 'order']
    list_display_links = ['author']
    list_filter = ['stars', 'is_active']
    list_editable = ['role_ru', 'stars', 'is_active', 'order']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'short_message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    list_editable = ['is_read']
    readonly_fields = ['name', 'email', 'message', 'created_at']

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Сообщение'

    def has_add_permission(self, request):
        return False

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'path', 'ip_address', 'device_info', 'browser_family', 'os_family')
    list_filter = ('is_bot', 'is_mobile', 'is_pc', 'timestamp', 'os_family', 'browser_family')
    search_fields = ('ip_address', 'path', 'user_agent', 'referer', 'session_key')
    readonly_fields = [f.name for f in PageVisit._meta.fields]
    
    def has_add_permission(self, request):
        return False
        
    def device_info(self, obj):
        from django.utils.safestring import mark_safe
        if obj.is_bot: return mark_safe('<span style="color: gray;">Бот</span>')
        if obj.is_mobile: return mark_safe('<span style="color: #2196F3;">📱</span>')
        if obj.is_tablet: return mark_safe('<span style="color: #9C27B0;">📱</span>')
        if obj.is_pc: return mark_safe('<span style="color: #4CAF50;">💻</span>')
        return "Неизвестно"
    device_info.short_description = "Тип"

admin.site.site_header = 'Khan Portfolio'
admin.site.site_title = 'Админка'
admin.site.index_title = 'Управление сайтом'
