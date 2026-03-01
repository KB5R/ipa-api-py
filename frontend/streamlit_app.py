import streamlit as st
import requests
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()
YOPASS_URL = os.getenv("YOPASS_URL")
API_URL = os.getenv("API_URL")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'session_cookie' not in st.session_state:
    st.session_state.session_cookie = None
if 'username' not in st.session_state:
    st.session_state.username = None


# Func work api FastAPI

def login(username: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{API_URL}/api/v1/session/login",
            data={"username": username, "password": password}
        )

        if response.ok:
            # Сохраняем cookie из ответа
            st.session_state.session_cookie = response.cookies.get('ipa_session')
            st.session_state.logged_in = True
            st.session_state.username = username
            return True
        else:
            st.error(f"Ошибка входа: {response.json().get('detail', 'Неизвестная ошибка')}")
            return False
    except Exception as e:
        st.error(f"Ошибка подключения: {e}")
        return False


def logout():
    """Выход из системы"""
    try:
        if st.session_state.session_cookie:
            requests.post(
                f"{API_URL}/api/v1/session/logout",
                cookies={'ipa_session': st.session_state.session_cookie}
            )
    finally:
        st.session_state.logged_in = False
        st.session_state.session_cookie = None
        st.session_state.username = None


def get_cookies() -> dict:
    """Возвращает cookies для запросов"""
    return {'ipa_session': st.session_state.session_cookie}


def reset_password(identifier: str) -> Optional[dict]:
    """Сброс пароля пользователя"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/users/{identifier}/reset-password",
            cookies=get_cookies()
        )

        if response.ok:
            return response.json()
        else:
            st.error(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
            return None
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return None


def create_user(first_name: str, last_name: str, email: str,
                phone: str = "", title: str = "", groups: str = "") -> Optional[dict]:
    """Создание пользователя"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/users/create-form",
            data={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "title": title,
                "groups": groups
            },
            cookies=get_cookies()
        )

        if response.ok:
            return response.json()
        else:
            st.error(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
            return None
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return None


def bulk_create_from_excel(file) -> Optional[dict]:
    """Массовое создание из Excel"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/users/bulk-create-from-excel",
            files={"file": file},
            cookies=get_cookies()
        )

        if response.ok:
            return response.json()
        else:
            st.error(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
            return None
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return None


# Настройка страницы
st.set_page_config(
    page_title="FreeIPA Portal",
    page_icon="",
    layout="wide"
)

# Заголовок
st.title("FreeIPA Portal")

# === ФОРМА ВХОДА ===
if not st.session_state.logged_in:
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("Вход в систему")

        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            submitted = st.form_submit_button("Войти", use_container_width=True)

            if submitted:
                if login(username, password):
                    st.success("Вы авторизованы")
                    st.rerun()

# === ГЛАВНАЯ СТРАНИЦА (после входа) ===
else:
    # Шапка с информацией о пользователе
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Вы:** {st.session_state.username}")
    with col2:
        if st.button("🚪 Выйти", width="stretch"):
            logout()
            st.rerun()

    st.markdown("---")

    # Вкладки для разных операций
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Сброс пароля", "Массовый сброс паролей", "Создать пользователя", "Массовое создание", "Аналитика"])

    # === ВКЛАДКА 1: СБРОС ПАРОЛЯ ===
    with tab1:
        st.header("Сброс пароля")
        st.markdown("Введите username или email пользователя")

        with st.form("reset_password_form"):
            identifier = st.text_input("Username или Email", placeholder="ivan.ivanov или ivan@test.com")

            submitted = st.form_submit_button("Сбросить пароль", use_container_width=True)

            if submitted and identifier:
                result = reset_password(identifier)

                if result:
                    st.success(f"Пароль успешно сброшен для пользователя **{result['username']}**")

                    st.markdown("### Yopass ссылка:")
                    st.text_input(
                        "Скопируйте ссылку ниже (выделите и Ctrl+C):",
                        value=result['yopass_link'],
                        disabled=True,
                        label_visibility="collapsed"
                    )

                    st.info("Выделите ссылку выше и скопируйте её (Ctrl+C). Отправьте пользователю (действует 7 дней, одноразовая)")

    # === ВКЛАДКА 2: МАССОВЫЙ СБРОС ПАРОЛЕЙ ===
    with tab2:
        st.header(" Массовый сброс паролей")
        st.markdown("Загрузите Excel файл со списком пользователей для сброса паролей")

        # Галочка для отправки на SMTP
        send_to_smtp = st.checkbox(
            "Отправить пароли на email (SMTP)",
            value=False,
            help="Если включено, пароли будут отправлены пользователям на email автоматически"
        )

        if send_to_smtp:
            st.info("Пароли будут отправлены на email пользователей через SMTP")
        else:
            st.info("Yopass ссылки будут показаны здесь для ручной отправки")

        # Загрузка файла
        uploaded_file = st.file_uploader(
            "Выберите Excel файл с пользователями",
            type=['xlsx'],
            key="bulk_reset_file"
        )

        if uploaded_file is not None:
            st.markdown("### Формат файла:")
            st.markdown("""
            | Username или Email |
            |--------------------|
            | ivan.ivanov        |
            | petr@company.com   |
            | maria.sidorova     |
            """)

            if st.button("🔄 Сбросить пароли", use_container_width=True, key="bulk_reset_btn"):
                with st.spinner("Сбрасываем пароли..."):
                    # TODO: Реализовать вызов API
                    # Пока заглушка
                    st.warning(" Функция в разработке")

                    # Заглушка результата
                    st.success("Обработано: 3 пользователя")

                    if send_to_smtp:
                        st.success("Email отправлены: 2")
                        st.error("Email не отправлены: 1")

                    with st.expander("Результаты (кликните для раскрытия)"):
                        st.markdown("**ivan.ivanov**")
                        if send_to_smtp:
                            st.success("Пароль сброшен, email отправлен на ivan@company.com")
                        else:
                            st.success("Пароль сброшен")
                            st.text_input(
                                "Yopass ссылка:",
                                value="https://pass.soc.rt.ru/s/example123",
                                disabled=True,
                                label_visibility="collapsed",
                                key="bulk_reset_demo_1"
                            )
                        st.markdown("---")

                        st.markdown("**petr@company.com**")
                        if send_to_smtp:
                            st.success("Пароль сброшен, email отправлен")
                        else:
                            st.success("Пароль сброшен")
                            st.text_input(
                                "Yopass ссылка:",
                                value="https://pass.soc.rt.ru/s/example456",
                                disabled=True,
                                label_visibility="collapsed",
                                key="bulk_reset_demo_2"
                            )
                        st.markdown("---")

                        st.markdown("**maria.sidorova**")
                        st.error("❌ Пользователь не найден")

    # === ВКЛАДКА 3: СОЗДАТЬ ПОЛЬЗОВАТЕЛЯ ===
    with tab3:
        st.header("Создание пользователя")

        with st.form("create_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input("Имя *", placeholder="Иван")
                email = st.text_input("Email *", placeholder="ivan@company.com")
                title = st.text_input("Должность", placeholder="Менеджер")

            with col2:
                last_name = st.text_input("Фамилия *", placeholder="Иванов")
                phone = st.text_input("Телефон", placeholder="+7 999 123 45 67")
                groups = st.text_input("Группы (через запятую)", placeholder="admins, developers")

            submitted = st.form_submit_button("Создать пользователя", use_container_width=True)

            if submitted:
                if not first_name or not last_name or not email:
                    st.error("Заполните обязательные поля: Имя, Фамилия, Email")
                else:
                    result = create_user(first_name, last_name, email, phone, title, groups)

                    if result:
                        st.success(f"Пользователь **{result['username']}** успешно создан!")

                        if result.get('yopass_link'):
                            st.markdown("### Yopass ссылка:")
                            st.text_input(
                                "Скопируйте ссылку ниже (выделите и Ctrl+C):",
                                value=result['yopass_link'],
                                disabled=True,
                                label_visibility="collapsed",
                                key="create_yopass_link"
                            )

                        if result.get('groups'):
                            if result['groups'].get('added'):
                                st.success(f"Добавлен в группы: {', '.join(result['groups']['added'])}")
                            if result['groups'].get('failed'):
                                st.warning(f"Не удалось добавить в группы: {result['groups']['failed']}")

    # === ВКЛАДКА 4: МАССОВОЕ СОЗДАНИЕ ===
    with tab4:
        st.header("Массовое создание из Excel")

        st.markdown("### Шаг 1: Скачайте шаблон Excel")
        st.markdown(f"[Скачать шаблон]({API_URL}/api/v1/templates/templates-excel)")

        st.markdown("### Шаг 2: Загрузите заполненный файл")

        uploaded_file = st.file_uploader("Выберите Excel файл", type=['xlsx'])

        if uploaded_file is not None:
            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("Создать пользователей", use_container_width=True):
                    with st.spinner("Создаём пользователей..."):
                        result = bulk_create_from_excel(uploaded_file)

                    if result:
                        st.success(f"Создано: **{len(result['success'])}**")

                        if result['failed']:
                            st.error(f"Ошибок: **{len(result['failed'])}**")

                        # Показываем созданных пользователей
                        if result['success']:
                            with st.expander("📋 Созданные пользователи (кликните для раскрытия)"):
                                for idx, user in enumerate(result['success']):
                                    st.markdown(f"**{user['username']}** - {user['email']}")
                                    st.text_input(
                                        "Yopass ссылка:",
                                        value=user['yopass_link'],
                                        disabled=True,
                                        label_visibility="collapsed",
                                        key=f"bulk_yopass_{idx}"
                                    )
                                    st.markdown("---")

                        # Показываем ошибки
                        if result['failed']:
                            with st.expander("Ошибки (кликните для раскрытия)"):
                                for fail in result['failed']:
                                    st.error(f"Строка {fail['row']}: {fail['error']}")


    with tab5:
        st.header("Аналитика и отчёты")
        
        st.markdown("### 1. Экспорт данных о пользователях и группах в CSV")
        
        if st.button("Получить CSV отчёт", width="stretch"):
            with st.spinner("Генерируем отчёт..."):
                try:
                    response = requests.get(
                        f"{API_URL}/api/v1/report/full-usersgroups-info",
                        cookies=get_cookies(),
                        timeout=30
                    )
                    
                    if response.ok:
                        # Сохраняем CSV в session_state
                        st.session_state.csv_data = response.content
                        st.success("Отчёт готов к скачиванию!")
                    else:
                        st.error(f"Ошибка: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Ошибка: {e}")
        
        # Показываем кнопку скачивания если данные есть
        if 'csv_data' in st.session_state:
            st.download_button(
                label="Скачать CSV файл",
                data=st.session_state.csv_data,
                file_name="users_groups_report.csv",
                mime="text/csv",
                width="stretch"
            )
            st.caption("Файл содержит: username, email, список групп")
        
        st.markdown("---")
        
        st.info("Дополнительная аналитика и статистика будут добавлены позже")
st.markdown("---")
st.markdown("*FreeIPA Portal - Управление пользователями*")
