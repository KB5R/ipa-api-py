import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

YOPASS_URL = os.getenv("YOPASS_URL")
YOPASS = os.getenv("YOPASS")
IPA_HOST = os.getenv("IPA_HOST")
APP_NAME = os.getenv("APP_NAME", "Conductor")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT", "15"))
SMTP_SUBJECT = os.getenv("SMTP_SUBJECT", f"{APP_NAME}: сброс пароля FreeIPA")
HELPDESK_EMAIL = os.getenv("HELPDESK_EMAIL", SMTP_FROM or "")
PASSWORD_RESET_EMAIL_TEMPLATE = os.getenv(
    "PASSWORD_RESET_EMAIL_TEMPLATE",
    str(BASE_DIR / "templates" / "password_reset_email.txt"),
)
SESSION_EXPIRATION_MINUTES = 60

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
