# Conductor

Conductor - система сброса паролей для FreeIPA с веб-интерфейсом для helpdesk и администраторов.

## Что умеет

- Сбрасывать пароль одному пользователю по `username` или `email`
- Выполнять массовый сброс паролей списком или через Excel
- Выдавать пароль напрямую или через одноразовую ссылку Yopass
- Отправлять Yopass ссылку пользователю по email через SMTP
- Искать пользователей, блокировать и разблокировать доступ
- Создавать пользователей вручную или из Excel
- Экспортировать отчёты по пользователям и группам

## Стек

- `FastAPI` - backend API
- `Streamlit` - операторский интерфейс
- `python-freeipa` - интеграция с FreeIPA
- `Yopass` - безопасная передача временных паролей
- `openpyxl` - обработка Excel

## Структура проекта

```text
.
├── app/                    # FastAPI приложение
│   ├── routers/            # API endpoints
│   ├── services/           # FreeIPA и Yopass
│   ├── models/             # Pydantic модели
│   └── utils/              # Excel, валидация, транслитерация
├── frontend/               # Streamlit интерфейс
├── templates/              # Excel шаблоны
├── bin/yopass              # Yopass CLI
└── main.py                 # Точка входа
```

## Быстрый старт

```bash
uv sync
uv run main.py
```

Backend API будет доступен на `http://0.0.0.0:8080`, Swagger - на `http://localhost:8080/docs`.

Отдельно запустите операторский интерфейс:

```bash
uv run streamlit run frontend/app.py
```

По умолчанию Streamlit будет доступен на `http://localhost:8501`.

## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения:

```env
IPA_HOST=ipa.example.com
YOPASS=/path/to/yopass/binary
YOPASS_URL=https://your-yopass-instance.com
API_URL=http://localhost:8080
APP_NAME=Conductor
APP_TAGLINE=Система сброса паролей для FreeIPA
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=helpdesk@example.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=helpdesk@example.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_SUBJECT=Conductor: сброс пароля FreeIPA
HELPDESK_EMAIL=helpdesk@example.com
PASSWORD_RESET_EMAIL_TEMPLATE=/app/templates/password_reset_email.txt
```

Для локальной работы обычно достаточно:

- `API_URL=http://localhost:8080`
- `APP_NAME=Conductor`
- `APP_TAGLINE=Система сброса паролей для FreeIPA`

## Основной сценарий

1. Оператор входит в Conductor через FreeIPA.
2. Находит пользователя по `username`, имени или `email`.
3. Сбрасывает пароль.
4. Передаёт пользователю новый пароль напрямую, через Yopass или автоматически отправляет Yopass ссылку на email.

## Отправка на почту

Conductor умеет отправлять письмо после сброса пароля, если:

- у пользователя есть email в FreeIPA;
- настроен SMTP в `.env`;
- при сбросе включена опция отправки письма.

В письмо отправляется `Yopass` ссылка, а не открытый пароль.

Шаблон письма по умолчанию лежит в [templates/password_reset_email.txt](/home/mk/project/conductor/templates/password_reset_email.txt).
Можно переопределить его через `PASSWORD_RESET_EMAIL_TEMPLATE`.

Доступные переменные шаблона:

- `{app_name}`
- `{username}`
- `{yopass_link}`
- `{expiration}`
- `{expiration_block}`
- `{helpdesk_email}`

## Доступ

После логина backend проверяет членство в одной из групп:

- `helpdesk`
- `admins`

При необходимости список можно изменить в [app/routers/auth.py](/home/mk/project/conductor/app/routers/auth.py).
