Django Gallery Project
Проект: Галерея на Django
Разрабатывался командой из двух человек на macOS.

Установка проекта:
1. Клонирование репозитория:

git clone <ссылка_на_репозиторий>
cd <название_папки_проекта>

2. Создание виртуального окружения:

python3 -m venv venv
source venv/bin/activate

(На Windows команда для активации виртуального окружения будет venv\Scripts\activate.)

3. Установка зависимостей
Убедитесь, что у вас установлен pip. Затем:

pip install -r requirements.txt

Настройка базы данных:

Проект использует PostgreSQL.
Создайте базу данных вручную через PgAdmin или командой:

createdb my_database_name

Важно! Настройки подключения берутся из файла .env.
Создайте .env в корне проекта со следующим содержимым:

env
# --- Настройки Django --- 
DEBUG=True

SECRET_KEY=*****
(
Сгенерировать можно командой:
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' 
)

# --- Настройки базы данных (PostgreSQL) ---
DB_ENGINE=django.db.backends.postgresql
DB_NAME=******
DB_USER=******
DB_PASSWORD=*******
DB_HOST==*******
DB_PORT==*******
Важно:

Замените значения DB_USER, DB_PASSWORD, DB_NAME, если у вас свои.

Применение миграций
Выполните стандартные команды Django:

python manage.py makemigrations
python manage.py migrate

Запуск сервера:

python manage.py runserver

После запуска проект будет доступен по адресу:
http://127.0.0.1:8000/

Возможные проблемы
Если появятся ошибки подключения к базе данных:

Убедитесь, что PostgreSQL сервер запущен (brew services start postgresql на macOS).

Проверьте правильность данных в .env.

Проверьте, что создана база данных.


Примечание
Мы работали командой из двух человек на macOS, поэтому в случае незначительных различий в окружении (например, Windows/Linux) возможны мелкие отличия в командах или настройках.