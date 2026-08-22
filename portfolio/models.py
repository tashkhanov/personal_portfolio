from django.db import models

LUCIDE_ICONS = [
    ('globe', 'Веб-сайт / Глобальный (Globe)'),
    ('bot', 'Бот (Bot)'),
    ('database', 'База данных (Database)'),
    ('zap', 'Молния / Быстро (Zap)'),
    ('credit-card', 'Оплата (Credit Card)'),
    ('shopping-cart', 'Магазин (Shopping Cart)'),
    ('smartphone', 'Мобильный (Smartphone)'),
    ('server', 'Сервер (Server)'),
    ('code', 'Код (Code)'),
    ('layout-dashboard', 'Дашборд (Dashboard)'),
    ('settings', 'Настройки (Settings)'),
    ('shield', 'Безопасность (Shield)'),
    ('palette', 'Дизайн (Palette)'),
    ('pen-tool', 'Перо / Вектор (Pen Tool)'),
    ('cpu', 'Процессор (CPU)'),
    ('cloud', 'Облако (Cloud)'),
    ('briefcase', 'Портфель (Briefcase)'),
    ('check-circle', 'Галочка (Check Circle)'),
    ('message-square', 'Сообщение (Message)'),
    ('star', 'Звезда (Star)'),
    ('activity', 'Активность (Activity)'),
]

GRADIENT_CHOICES = [
    ('linear-gradient(135deg, #111111, #434343)', 'Тёмный (Dark Graphite)'),
    ('linear-gradient(135deg, #1a2980, #26d0ce)', 'Океан (Ocean Blue)'),
    ('linear-gradient(135deg, #0f2027, #203a43, #2c5364)', 'Космос (Deep Space)'),
    ('linear-gradient(135deg, #2c3e50, #3498db)', 'Небо (Sky Blue)'),
    ('linear-gradient(135deg, #ff4b1f, #ff9068)', 'Закат (Sunset Orange)'),
    ('linear-gradient(135deg, #4b6cb7, #182848)', 'Ночь (Cosmic Night)'),
    ('linear-gradient(135deg, #8E2DE2, #4A00E0)', 'Неон (Neon Purple)'),
    ('linear-gradient(135deg, #1D976C, #93F9B9)', 'Мята (Mint Green)'),
    ('linear-gradient(135deg, #F09819, #EDDE5D)', 'Золото (Golden Hour)'),
    ('linear-gradient(135deg, #3a1c71, #d76d77, #ffaf7b)', 'Сумерки (Twilight)'),
]



class SiteSettings(models.Model):
    name = models.CharField('Имя', max_length=100, default='Khan')
    title = models.CharField('Заголовок', max_length=200, default='Fullstack разработчик')
    subtitle = models.CharField('Подзаголовок', max_length=300, default='Laravel | Frontend | Python')
    is_available = models.BooleanField('Доступен для заказов', default=True)
    hero_text = models.TextField('Текст на главной', default='Fullstack-разработчик. Избавляю от головной боли с кодом.')
    about_text = models.TextField('Обо мне', default='Профессионально избавляю вас от головной боли с кодом и недоделанными проектами.')
    kwork_username = models.CharField('Kwork логин', max_length=100, default='DevKhan')
    kwork_url = models.URLField('Kwork ссылка', default='https://kwork.ru/user/devkhan')
    telegram_username = models.CharField('Telegram', max_length=100, default='@asatkhanov')
    telegram_url = models.URLField('Telegram ссылка', default='https://t.me/asatkhanov')
    telegram_bot_token = models.CharField('Telegram Bot Token', max_length=200, blank=True, help_text='Для отправки сообщений из формы')
    telegram_chat_id = models.CharField('Telegram Chat ID', max_length=50, blank=True, help_text='Куда отправлять сообщения')
    email = models.EmailField('Email', default='hello@khan.dev')
    github_url = models.URLField('GitHub', default='https://github.com/', blank=True)
    og_image = models.ImageField('Превью для соцсетей (OG Image)', upload_to='settings/', blank=True, null=True, help_text='Картинка 1200x630 (Telegram, VK)')
    resume = models.FileField('Резюме', upload_to='resume/', blank=True, null=True, help_text='PDF файл резюме для скачивания с главной страницы')
    portrait = models.ImageField('Портрет', upload_to='about/', blank=True, null=True, help_text='Фото для страницы "Обо мне"')
    about_full_text = models.TextField('Развернутый текст обо мне', default='Тут будет подробная история моего пути...', help_text='Поддерживает HTML-теги для форматирования')

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'






    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            return
        super().save(*args, **kwargs)


class Stat(models.Model):
    value = models.CharField('Значение', max_length=20)
    label_ru = models.CharField('Подпись (RU)', max_length=100)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'
        ordering = ['order']

    def __str__(self):
        return f'{self.value} — {self.label_ru}'



class Skill(models.Model):
    name = models.CharField('Название', max_length=100)
    order = models.IntegerField('Порядок', default=0)


    class Meta:
        verbose_name = 'Технология'
        verbose_name_plural = 'Технологии'
        ordering = ['order']

    def __str__(self):
        return self.name


class Category(models.Model):
    name_ru = models.CharField('Название (RU)', max_length=100)
    slug = models.SlugField('Slug', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name_ru


class Certificate(models.Model):
    title = models.CharField('Название', max_length=200)
    institution = models.CharField('Организация', max_length=200, blank=True)
    image = models.ImageField('Фото/Скан', upload_to='certificates/')
    issued_date = models.CharField('Дата выдачи', max_length=50, blank=True)
    credential_id = models.CharField('ID документа', max_length=50, blank=True)
    duration = models.CharField('Длительность', max_length=100, blank=True)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'
        ordering = ['order']

    def __str__(self):
        return self.title


class Experience(models.Model):
    company = models.CharField('Компания / Проект', max_length=200)
    position = models.CharField('Должность', max_length=200)
    period = models.CharField('Период', max_length=100)
    description = models.TextField('Описание (HTML)')
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Опыт работы'
        verbose_name_plural = 'Опыт работы'
        ordering = ['order']

    def __str__(self):
        return f'{self.position} в {self.company}'


class Project(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Slug', unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория')
    description_ru = models.TextField('Описание (RU)')
    full_description_ru = models.TextField('Полное описание (RU)', blank=True)
    icon = models.CharField('Иконка (Lucide)', max_length=50, choices=LUCIDE_ICONS, default='globe')
    gradient = models.CharField('Градиент фона', max_length=100, choices=GRADIENT_CHOICES, default='linear-gradient(135deg, #111111, #434343)')
    image = models.ImageField('Главное изображение', upload_to='projects/', blank=True)
    tags = models.CharField('Теги (через запятую)', max_length=500, default='Laravel, PHP, MySQL')
    year = models.CharField('Год', max_length=10, default='2025')
    status = models.CharField('Статус', max_length=50, default='Завершён')
    client_name = models.CharField('Клиент', max_length=100, default='Конфиденциально')
    demo_url = models.URLField('Демо ссылка', blank=True)
    github_url = models.URLField('GitHub ссылка', blank=True)
    is_featured = models.BooleanField('На главной', default=True)
    is_active = models.BooleanField('Активен', default=True)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-is_featured', 'order', '-created_at']

    def __str__(self):
        return self.title



    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_category_slug(self):
        return self.category.slug if self.category else ''


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images', verbose_name='Проект')
    image = models.ImageField('Изображение', upload_to='projects/gallery/', blank=True, null=True)
    video = models.FileField('Видео (MP4)', upload_to='projects/gallery/videos/', blank=True, null=True, help_text='Загрузите короткое видео. Если загружено, показывается вместо картинки.')
    caption = models.CharField('Подпись', max_length=200, blank=True)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Скриншот'
        verbose_name_plural = 'Скриншоты'
        ordering = ['order']

    def __str__(self):
        return f'{self.project.title} - {self.order}'


class Service(models.Model):
    icon = models.CharField('Иконка (Lucide)', max_length=50, choices=LUCIDE_ICONS, default='globe')
    title_ru = models.CharField('Заголовок (RU)', max_length=200)
    slug = models.SlugField('Slug', unique=True, default='')
    description_ru = models.TextField('Описание (RU)')
    full_description_ru = models.TextField('Полное описание (RU)', blank=True)
    gradient = models.CharField('Градиент', max_length=100, choices=GRADIENT_CHOICES, default='linear-gradient(135deg, #111111, #434343)')
    image = models.ImageField('Изображение', upload_to='services/', blank=True, help_text='Загрузите вместо emoji или как дополнение')
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order']

    def __str__(self):
        return self.title_ru

class ServiceFeature(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features', verbose_name='Услуга')
    text_ru = models.CharField('Что входит (RU)', max_length=300)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Что входит'
        verbose_name_plural = 'Что входит'
        ordering = ['order']

    def __str__(self):
        return f'{self.service.title_ru} — {self.text_ru}'



class Review(models.Model):
    author = models.CharField('Автор', max_length=100)
    avatar_text = models.CharField('Текст аватара', max_length=5, default='U')
    text_ru = models.TextField('Отзыв (RU)')
    role_ru = models.CharField('Роль (RU)', max_length=100)
    role_en = models.CharField('Роль (EN)', max_length=100, blank=True)
    stars = models.IntegerField('Звёзды', default=5)
    is_active = models.BooleanField('Активен', default=True)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['order']

    def __str__(self):
        return f'{self.author} — {self.role_ru}'



class ContactMessage(models.Model):
    name = models.CharField('Имя', max_length=200)
    email = models.EmailField('Email')
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.created_at.strftime("%d.%m.%Y")}'

class PageVisit(models.Model):
    timestamp = models.DateTimeField('Время', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP Адрес', null=True, blank=True)
    path = models.CharField('Страница', max_length=500)
    user_agent = models.TextField('User Agent', blank=True)
    referer = models.TextField('Откуда перешел (Referer)', blank=True)
    
    is_mobile = models.BooleanField('Мобильный?', default=False)
    is_tablet = models.BooleanField('Планшет?', default=False)
    is_pc = models.BooleanField('ПК?', default=False)
    is_bot = models.BooleanField('Бот?', default=False)
    browser_family = models.CharField('Браузер', max_length=100, blank=True)
    os_family = models.CharField('ОС', max_length=100, blank=True)
    device_family = models.CharField('Устройство', max_length=100, blank=True)
    
    session_key = models.CharField('Ключ сессии', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Посещение'
        verbose_name_plural = 'Аналитика посещений'
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%d.%m.%Y %H:%M')}] {self.ip_address} -> {self.path}"

