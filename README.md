# Django Техническое задание

## Требования

- Python 3.11 и выше
- git

## Установка и запуск

1. Скачать проект на [GitHub](https://github.com/meumeu21/tz-django)
2. Создать виртуальное окружение (venv):

```bash
python3 -m venv venv
source venv/bin/activate (или .\venv\Scripts\Activate.ps1 в Windows)
```

3. Перейти в желаемый проект:

```bash
cd (название папки проекта)
```

4. Установить зависимости через:

```bash
pip install -r requirements.txt
```

5. Создать файл настроек .env:

```bash
cp .env.example .env
```

6. Сгенерировать секретный ключ и вставить его в .env вместо значения SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

7. Создать базу данных:

```bash
python manage.py migrate
```

8. Запустить сервер

```bash
python manage.py runserver
```