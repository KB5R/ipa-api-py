import smtplib
from email.message import EmailMessage
from pathlib import Path

from app.config import (
    APP_NAME,
    HELPDESK_EMAIL,
    PASSWORD_RESET_EMAIL_TEMPLATE,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SUBJECT,
    SMTP_TIMEOUT,
    SMTP_USERNAME,
    SMTP_USE_SSL,
    SMTP_USE_TLS,
)


DEFAULT_TEMPLATE = """Здравствуйте!

Для вашей учетной записи FreeIPA был выполнен сброс пароля.

Логин: {username}
Ссылка для получения временного пароля: {yopass_link}
{expiration_block}
Ссылка одноразовая. После входа рекомендуется сразу сменить пароль.

Если вы не ожидали это письмо, свяжитесь с helpdesk: {helpdesk_email}

{app_name}
"""


def is_smtp_configured() -> bool:
    return bool(SMTP_HOST and SMTP_PORT and SMTP_FROM)


def load_email_template() -> str:
    template_path = Path(PASSWORD_RESET_EMAIL_TEMPLATE)
    if template_path.is_file():
        return template_path.read_text(encoding="utf-8")
    return DEFAULT_TEMPLATE


def render_password_reset_email(
    username: str,
    yopass_link: str,
    expiration: str | None = None,
) -> str:
    template = load_email_template()
    expiration_block = f"Срок действия временного пароля: {expiration}\n" if expiration else ""
    helpdesk_email = HELPDESK_EMAIL or SMTP_FROM or "helpdesk"
    return template.format(
        app_name=APP_NAME,
        username=username,
        yopass_link=yopass_link,
        expiration=expiration or "",
        expiration_block=expiration_block,
        helpdesk_email=helpdesk_email,
    ).strip() + "\n"


def send_password_reset_email(
    recipient: str,
    username: str,
    yopass_link: str,
    expiration: str | None = None,
) -> None:
    if not is_smtp_configured():
        raise RuntimeError("SMTP не настроен")

    message = EmailMessage()
    message["Subject"] = SMTP_SUBJECT
    message["From"] = SMTP_FROM
    message["To"] = recipient
    message.set_content(
        render_password_reset_email(
            username=username,
            yopass_link=yopass_link,
            expiration=expiration,
        )
    )

    smtp_class = smtplib.SMTP_SSL if SMTP_USE_SSL else smtplib.SMTP
    with smtp_class(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
        if not SMTP_USE_SSL and SMTP_USE_TLS:
            server.starttls()
        if SMTP_USERNAME:
            server.login(SMTP_USERNAME, SMTP_PASSWORD or "")
        server.send_message(message)
