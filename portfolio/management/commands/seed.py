from django.core.management.base import BaseCommand
from portfolio.models import SiteSettings, Stat, Skill, Category, Project, Service, ServiceFeature, Review


class Command(BaseCommand):
    help = 'Заполнить базу данных начальными данными'

    def handle(self, *args, **options):
        self.stdout.write('Заполнение базы данных...')

        SiteSettings.objects.get_or_create(pk=1, defaults={
            'name': 'Khan', 'title': 'Fullstack разработчик', 'subtitle': 'Laravel | Frontend | Python',
            'hero_text': 'Fullstack-разработчик. Избавляю от головной боли с кодом. Laravel | Frontend | Python — от скрипта до полноценной системы.',
            'about_text': 'Профессионально избавляю вас от головной боли с кодом и недоделанными проектами. Разрабатываю веб-проекты и ботов разной сложности: от простых скриптов и парсеров на Python до полноценных систем на Laravel и Django. Опишите задачу своими словами — разберусь и предложу рабочее решение. Пишите! Поработаем.',
            'kwork_username': 'DevKhan', 'kwork_url': 'https://kwork.ru/user/devkhan',
            'telegram_username': '@asatkhanov', 'telegram_url': 'https://t.me/asatkhanov', 'email': 'hello@khan.dev',
        })

        for value, label_ru, label_en, order in [('5.0', 'Рейтинг', 'Rating', 1), ('10', 'Заказов', 'Orders', 2), ('7', 'Отзывов', 'Reviews', 3), ('100%', 'Вовремя', 'On-time', 4)]:
            Stat.objects.get_or_create(label_ru=label_ru, defaults={'value': value, 'label_en': label_en, 'order': order})

        for i, name in enumerate(['Laravel', 'PHP', 'Python', 'Django', 'JavaScript', 'jQuery', 'AJAX', 'HTML', 'CSS', 'Bootstrap 5', 'MySQL', 'PostgreSQL', 'SQLite', 'WordPress', 'Git', 'python-telegram-bot']):
            Skill.objects.get_or_create(name=name, defaults={'order': i})

        for name_ru, name_en, slug in [('CRM', 'CRM', 'crm'), ('Боты', 'Bots', 'bot'), ('Интернет-магазин', 'E-commerce', 'ecommerce'), ('Парсеры', 'Parsers', 'parser'), ('WordPress', 'WordPress', 'wordpress'), ('Интеграции', 'Integrations', 'integration')]:
            Category.objects.get_or_create(slug=slug, defaults={'name_ru': name_ru, 'name_en': name_en})

        services_data = [
            ('🌐', 'Веб-сайты и CRM', 'Websites & CRM', 'websites-crm', 'Сайты, веб-сервисы и CRM-системы на Laravel, Django и PHP. Полный цикл от идеи до запуска.', 'Websites and CRM on Laravel, Django and PHP. Full cycle.',
             'Разрабатываю полноценные веб-приложения с нуля: от лендингов до сложных CRM-систем. Использую современный стек Laravel/PHP и Django/Python. Гарантирую чистый код, безопасность и масштабируемость.',
             'linear-gradient(135deg,#1a1a2e,#16213e)', 1,
             ['Адаптивный дизайн', 'REST API', 'Админ-панель', 'База данных', 'Деплой на сервер', 'SSL сертификат']),
            ('🤖', 'Telegram-боты', 'Telegram Bots', 'telegram-bots', 'Боты любой сложности, в том числе с ИИ и автоматизацией. Интеграции с платёжными системами.', 'Bots of any complexity, including AI. Payment integrations.',
             'Создаю Telegram-ботов для автоматизации бизнеса: приём заказов, уведомления, оплата, интеграция с CRM. Также делаю ботов с ИИ на базе OpenAI и других моделей.',
             'linear-gradient(135deg,#2d132c,#801336)', 2,
             ['python-telegram-bot', 'ИИ-интеграция', 'Платёжные системы', 'Webhook', 'База данных', 'Деплой на сервер']),
            ('📊', 'Парсинг данных', 'Data Parsing', 'data-parsing', 'Парсинг с обходом Cloudflare и других защит. Автоматизация сбора информации.', 'Parsing with Cloudflare bypass.',
             'Парсинг данных с любых сайтов, включая защищённые Cloudflare. Сбор информации, мониторинг цен, конкурентный анализ. Сохранение в базу данных, CSV или Excel.',
             'linear-gradient(135deg,#162447,#1f4068)', 3,
             ['Обход Cloudflare', 'Ротация прокси', 'Многопоточность', 'CSV/Excel экспорт', 'Расписание', 'Уведомления']),
            ('⚡', 'Доработки и исправления', 'Fixes & Improvements', 'fixes', 'Исправлю баги, доработаю существующий проект, добавлю новый функционал.', 'Fix bugs, improve projects.',
             'Разберусь в чужом коде, исправлю баги, добавлю новый функционал, оптимизирую производительность. Работаю с любыми CMS и фреймворками.',
             'linear-gradient(135deg,#2d1a2e,#4a1942)', 4,
             ['Анализ кода', 'Исправление багов', 'Оптимизация', 'Новый функционал', 'Миграции', 'Тестирование']),
            ('💳', 'Интеграции платежей', 'Payment Integration', 'payment-integration', 'Тинькофф, Сбер, ЮMoney, Точка Банк. Интеграция с налоговой.', 'Tinkoff, Sber, YooMoney.',
             'Подключаю платёжные системы к вашему сайту или приложению. Работаю с Тинькофф, Сбер, ЮMoney, Точка Банк. Автоматическая отправка чеков в ФНС.',
             'linear-gradient(135deg,#1f1c2c,#928dab)', 5,
             ['Тинькофф', 'Сбер', 'ЮMoney', 'Точка Банк', 'ФНС (54-ФЗ)', 'Webhook']),
            ('📱', 'WordPress', 'WordPress', 'wordpress-solutions', 'Лендинги, блоги, интернет-магазины. Плагины и доработки.', 'Landing pages, blogs, stores.',
             'Быстрые и бюджетные решения на WordPress: лендинги, блоги, интернет-магазины, корпоративные сайты. Разработка и доработка плагинов, интеграции.',
             'linear-gradient(135deg,#1a1a2e,#0f3460)', 6,
             ['Лендинги', 'Блоги', 'WooCommerce', 'Плагины', 'Интеграции', 'Оптимизация']),
        ]
        for icon, title_ru, title_en, slug, desc_ru, desc_en, full_desc, grad, order, features in services_data:
            svc, created = Service.objects.get_or_create(slug=slug, defaults={
                'icon': icon, 'title_ru': title_ru, 'title_en': title_en,
                'description_ru': desc_ru, 'description_en': desc_en,
                'full_description_ru': full_desc, 'gradient': grad, 'order': order,
            })
            if created:
                for i, f in enumerate(features):
                    ServiceFeature.objects.create(service=svc, text_ru=f, text_en=f, order=i)

        cat_crm = Category.objects.get(slug='crm')
        cat_bot = Category.objects.get(slug='bot')
        cat_ecom = Category.objects.get(slug='ecommerce')
        cat_parser = Category.objects.get(slug='parser')
        cat_wp = Category.objects.get(slug='wordpress')
        cat_int = Category.objects.get(slug='integration')

        projects_data = [
            ('CRM система', 'crm-sistema', cat_crm, 'Полноценная CRM с автоматизацией, Telegram и платёжными.', 'Full CRM with automation, Telegram and payments.', 'Клиенту требовалась система для управления заказами, клиентами и финансами. Разработана полноценная CRM с интуитивным интерфейсом и мощным бэкендом на Laravel.', '🌐', 'linear-gradient(135deg,#1a1a2e,#16213e)', 'Laravel, PHP, MySQL, Telegram API, Stripe', '2025', True, 1),
            ('Telegram-бот с ИИ', 'telegram-bot-ai', cat_bot, 'Бот для автоматизации бизнес-процессов и поддержки.', 'Bot for business automation and support.', 'Бот с интеграцией OpenAI API для обработки естественного языка и автоматического ответа на вопросы клиентов. Интегрирован с CRM.', '🤖', 'linear-gradient(135deg,#2d132c,#801336)', 'Python, python-telegram-bot, OpenAI, PostgreSQL', '2025', True, 2),
            ('Интернет-магазин', 'internet-magazin', cat_ecom, 'Интернет-магазин с платёжными системами и админкой.', 'Online store with payments and admin panel.', 'Полноценный интернет-магазин с каталогом товаров, корзиной, онлайн-оплатой и админ-панелью для управления.', '🛒', 'linear-gradient(135deg,#0f3460,#16213e)', 'Laravel, MySQL, Stripe, Bootstrap', '2025', True, 3),
            ('Парсер Cloudflare', 'parser-cloudflare', cat_parser, 'Сбор данных с защищённых сайтов с обходом защиты.', 'Data collection from protected sites.', 'Система автоматического сбора данных с сайтов, защищённых Cloudflare. Включает ротацию прокси и обход капчи.', '📊', 'linear-gradient(135deg,#162447,#1f4068)', 'Python, Selenium, Cloudflare, SQLite', '2025', True, 4),
            ('Интеграция Тильда + Банк', 'integration-tilda-bank', cat_int, 'Подключение платёжной системы банка к сайту на Тильде.', 'Connecting bank payment system to Tilda.', 'Интеграция платёжного шлюза банка с сайтом на Тильда. Автоматическая отправка данных о платежах в ФНС.', '💳', 'linear-gradient(135deg,#1f1c2c,#928dab)', 'PHP, Tilda API, Bank API, Telegram', '2025', True, 5),
            ('Блог с админкой', 'blog-s-admin', cat_wp, 'Раздел блога с виджетами и админ-панелью.', 'Blog section with widgets and admin panel.', 'Доработка сайта на WordPress: добавлен раздел блога с виджетами, поиском, тегами и удобной админ-панелью.', '📝', 'linear-gradient(135deg,#1a1a2e,#0f3460)', 'WordPress, PHP, jQuery, CSS', '2025', True, 6),
            ('Email-рассылка', 'email-rassilka', cat_crm, 'Система email-рассылок с шаблонами и аналитикой.', 'Email system with templates and analytics.', 'Система для массовых email-рассылок с drag-and-drop редактором шаблонов, сегментацией и аналитикой.', '📧', 'linear-gradient(135deg,#2d1a2e,#4a1942)', 'Laravel, Redis, Queue, MySQL', '2024', False, 7),
            ('Telegram-бот магазин', 'telegram-bot-shop', cat_bot, 'Бот для заказа товаров с корзиной и оплатой.', 'Bot for ordering with cart and payments.', 'Telegram-магазин с каталогом товаров, корзиной, онлайн-оплатой и уведомлениями о статусе заказа.', '🤖', 'linear-gradient(135deg,#1a2e1a,#1a4a2e)', 'Python, PostgreSQL, Stripe, python-telegram-bot', '2024', False, 8),
        ]
        for title, slug, cat, desc_ru, desc_en, full_desc, icon, grad, tags, year, featured, order in projects_data:
            Project.objects.get_or_create(slug=slug, defaults={
                'title': title, 'category': cat, 'description_ru': desc_ru, 'description_en': desc_en,
                'full_description_ru': full_desc, 'icon': icon, 'gradient': grad, 'tags': tags,
                'year': year, 'is_featured': featured, 'order': order,
            })

        for author, avatar, text_ru, text_en, role_ru, role_en, stars, order in [
            ('v1lfa', 'V1', 'Выполнение поставленных задач на высоте.', '', 'Интернет-магазин', 'E-commerce', 5, 1),
            ('Mike_7895', 'M7', 'Все супер. Сделано быстро и качественно. Советую работать.', '', 'Парсинг', 'Parsing', 5, 2),
            ('bel31shil', 'B1', 'Профессиональная консультация, быстро сделал работу, всё работает.', '', 'Интеграция', 'Integration', 5, 3),
            ('makcim-benko', 'MB', 'Исполнитель выполнил работу на отлично. Все согласно ТЗ.', '', 'WordPress', 'WordPress', 5, 4),
            ('Anatoly_1969', 'A', 'Очень доволен работой! Обязательно снова обращусь!', '', 'WordPress', 'WordPress', 5, 5),
        ]:
            Review.objects.get_or_create(author=author, role_ru=role_ru, defaults={
                'avatar_text': avatar, 'text_ru': text_ru, 'text_en': text_en,
                'role_en': role_en, 'stars': stars, 'order': order,
            })

        self.stdout.write(self.style.SUCCESS('База данных заполнена!'))
