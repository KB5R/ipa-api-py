from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from app.config import logger, SESSION_EXPIRATION_MINUTES
from app.dependencies import authenticate_user, user_sessions, ipa_clients, cleanup_session
import uuid


router = APIRouter()

@router.post("/api/v1/session/login")
def login(request: Request,
                username: str = Form(...),
                password: str = Form(...)
                ) -> JSONResponse:
    """Аутентификация пользователя в FreeIPA"""
    try:
        logger.info(f"Login attempt: {username}")
        # Аутентифицируем пользователя в FreeIPA
        client = authenticate_user(username, password)

        # Проверяем группу пользователя
        user_info = client._request("user_show", args=[username], params={})
        groups = user_info['result'].get('memberof_group', [])
        allowed_groups = ['admins', 'helpdesk'] # Настроить в соответствии
        if not any(g in groups for g in allowed_groups):
            raise HTTPException(
                status_code=403,
                detail="Доступ запрещён: требуется группа helpdesk или admins"
            )

        # Создаём сессию
        session_id = str(uuid.uuid4())
        expires = datetime.now() + timedelta(minutes=SESSION_EXPIRATION_MINUTES)

        # Сохраняем данные сессии
        user_sessions[session_id] = {
            "username": username,
            "created": datetime.now(),
            "expires": expires
        }

        # Сохраняем клиент FreeIPA
        ipa_clients[session_id] = client

        # Создаём ответ с кукой
        response = JSONResponse(
            content={
                "status": "ok",
                "user": username,
                "session_id": session_id
            }
        )

        response.set_cookie(
            key="ipa_session",
            value=session_id,
            httponly=False,  # Разрешаем доступ из JavaScript
            max_age=SESSION_EXPIRATION_MINUTES * 60,
            path="/",
            samesite="lax"  # Работает для same-site запросов
        )

        logger.info(f"Login successful: {username}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Login failed: {username} - {str(e)}")
        raise HTTPException(status_code=401, detail=f"Ошибка авторизации: {str(e)}")



@router.post("/api/v1/session/logout")
def logout(request: Request) -> JSONResponse:
    """Выход из системы"""
    session_id = request.cookies.get("ipa_session")

    if session_id:
        cleanup_session(session_id)

    response = JSONResponse(content={"status": "logged out"})
    response.delete_cookie("ipa_session", path="/")
    return response
