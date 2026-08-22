# Personal Portfolio - Fullstack Developer

Современное портфолио fullstack-разработчика, созданное на **Django 5** и **Vanilla JavaScript**, с интеграцией крутых микроанимаций и плавных переходов.

## Особенности проекта

*   🚀 **Стек**: Django 5, Python 3, Vanilla JS, CSS3, HTML5
*   ✨ **Анимации**: GSAP, Vanilla Tilt, Swiper.js
*   🔥 **Производительность**: Swup.js для мгновенных AJAX-переходов между страницами
*   🛡️ **Защита контента**: Блокировка DevTools (F12), отключение ПКМ и копирования, защита видео от скачивания.
*   📊 **Аналитика**: Встроенная легковесная аналитика (сбор ОС, браузеров, устройств) через кастомный middleware
*   📱 **Адаптивность**: Mobile-first подход, 100% отзывчивый дизайн
*   💬 **Связь**: Интеграция с Telegram API для получения заявок с формы обратной связи

## Как запустить локально

1.  Клонируйте репозиторий:
    \\ash
    git clone https://github.com/your-username/personal-portfolio.git
    cd personal-portfolio
    \2.  Создайте и активируйте виртуальное окружение:
    \\ash
    python -m venv venv
    venv\\Scripts\\activate  # Для Windows
    # source venv/bin/activate # Для Mac/Linux
    \3.  Установите зависимости:
    \\ash
    pip install -r requirements.txt
    \4.  Сделайте миграции базы данных:
    \\ash
    python manage.py migrate
    \5.  Запустите сервер:
    \\ash
    python manage.py runserver
    \
Откройте \http://localhost:8000\ в вашем браузере.
