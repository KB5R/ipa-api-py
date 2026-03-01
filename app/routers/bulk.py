from app.dependencies import get_user_client
from app.services.freeipa import resolve_username
from app.services.yopass import create_yopass_link
from app.utils.excel import parse_identifiers_column
from fastapi import APIRouter, Request, UploadFile, File
from typing import Dict, List, Any


router = APIRouter()

@router.post("/api/v1/users/bulk-delete")
def bulk_delete_users(identifiers: List[str], request: Request) -> Dict[str, List[Dict[str, Any]]]:
    """
    Массовое удаление пользователей
    
    Принимает username или email

    ["ivan.ivanov", "petr@test.com", "petya.petrov"]
    """
    results = {"success": [], "failed": []}
    client = get_user_client(request)

    for identifier in identifiers:
        try:
            # Находим username (по email или напрямую)
            username = resolve_username(client, identifier)
            
            # Удаляем пользователя
            client._request("user_del", args=[username], params={})
            
            # Добавляем в успешные
            results["success"].append({
                "identifier": identifier,
                "username": username
            })
            
        except ValueError as e:
            # Пользователь не найден
            results["failed"].append({
                "identifier": identifier,
                "error": str(e)
            })
        except Exception as e:
            # Любая другая ошибка (FreeIPA, сеть и т.д.)
            results["failed"].append({
                "identifier": identifier,
                "error": f"Ошибка удаления: {str(e)}"
            })

    return results


@router.post("/api/v1/users/bulk-disable")
def bulk_disable_users(identifiers: List[str], request: Request) -> Dict[str, List[Dict[str, Any]]]:
    """
    Массовое отключение пользователей
    
    Принимает username или email

    ["ivan.ivanov", "petr@test.com", "petya.petrov"]
    """
    results = {"success": [], "failed": []}
    client = get_user_client(request)

    for identifier in identifiers:
        try:
            # Находим username (по email или напрямую)
            username = resolve_username(client, identifier)
            
            # Удаляем пользователя
            client._request("user_disable", args=[username], params={})
            
            # Добавляем в успешные
            results["success"].append({
                "identifier": identifier,
                "username": username
            })
            
        except ValueError as e:
            # Пользователь не найден
            results["failed"].append({
                "identifier": identifier,
                "error": str(e)
            })
        except Exception as e:
            # Любая другая ошибка (FreeIPA, сеть и т.д.)
            results["failed"].append({
                "identifier": identifier,
                "error": f"Ошибка отключения: {str(e)}"
            })

    return results


@router.post("/api/v1/users/bulk-enable")
def bulk_enable_users(identifiers: List[str], request: Request) -> Dict[str, List[Dict[str, Any]]]:
    """
    Массовое включение пользователей
    
    Принимает username или email

    ["ivan.ivanov", "petr@test.com", "petya.petrov"]
    """
    results = {"success": [], "failed": []}
    client = get_user_client(request)

    for identifier in identifiers:
        try:
            # Находим username (по email или напрямую)
            username = resolve_username(client, identifier)
            
            # Удаляем пользователя
            client._request("user_enable", args=[username], params={})
            
            # Добавляем в успешные
            results["success"].append({
                "identifier": identifier,
                "username": username
            })
            
        except ValueError as e:
            # Пользователь не найден
            results["failed"].append({
                "identifier": identifier,
                "error": str(e)
            })
        except Exception as e:
            # Любая другая ошибка (FreeIPA, сеть и т.д.)
            results["failed"].append({
                "identifier": identifier,
                "error": f"Ошибка включения: {str(e)}"
            })

    return results


@router.post("/api/v1/users/bulk-reset-password")
def bulk_reset_password(identifiers: List[str], request: Request) -> Dict[str, List[Dict[str, Any]]]:
    """
    Массовый сброс паролей пользователей

    Можно передавать username или email - API сам определит:
    ["ivan.ivanov", "petr@test.com", "elena.sidorova"]
    """
    results = {
        "success": [],
        "failed": []
    }

    client = get_user_client(request)

    for identifier in identifiers:
        try:
            # Находим username (вся логика внутри функции)
            username = resolve_username(client, identifier)  # ← ВОТ И ВСЁ!

            # Сбрасываем пароль
            reset_result = client._request(
                "user_mod",
                args=[username],
                params={"random": True}
            )

            password = reset_result['result']['randompassword']

            results["success"].append({
                "identifier": identifier,
                "username": username,
                "password": password
            })

        except Exception as e:
            results["failed"].append({
                "identifier": identifier,
                "error": str(e)
            })

    return results


@router.post("/api/v1/users/bulk-reset-password-with-yopass")
def bulk_reset_password_with_yopass(identifiers: List[str], request: Request) -> Dict[str, List[Dict[str, Any]]]:
    """
    Массовый сброс паролей из JSON списка с Yopass ссылками

    Принимает username или email:
    ["ivan.ivanov", "petr@test.com"]
    """
    results = {"success": [], "failed": []}
    client = get_user_client(request)

    for identifier in identifiers:
        try:
            username = resolve_username(client, identifier)
            reset_result = client._request("user_mod", args=[username], params={"random": True})
            password = reset_result['result']['randompassword']
            yopass_link = create_yopass_link(username, password)
            email_list = reset_result['result'].get('mail', [])
            email = email_list[0] if email_list else ""
            results["success"].append({
                "identifier": identifier,
                "username": username,
                "email": email,
                "yopass_link": yopass_link
            })
        except Exception as e:
            results["failed"].append({"identifier": identifier, "error": str(e)})

    return results


@router.post("/api/v1/users/bulk-disable-preview-list")
def bulk_disable_preview_list(identifiers: List[str], request: Request) -> Dict[str, Any]:
    """
    Dry-run: резолвит пользователей из JSON списка, ничего не делает в FreeIPA

    Принимает username или email:
    ["ivan.ivanov", "petr@test.com"]
    """
    found = []
    not_found = []
    client = get_user_client(request)

    for identifier in identifiers:
        try:
            username = resolve_username(client, identifier)
            found.append({"identifier": identifier, "username": username})
        except ValueError as e:
            not_found.append({"identifier": identifier, "error": str(e)})
        except Exception as e:
            not_found.append({"identifier": identifier, "error": str(e)})

    return {
        "found": found,
        "not_found": not_found,
        "total": len(identifiers),
        "found_count": len(found),
        "not_found_count": len(not_found)
    }


@router.post("/api/v1/users/bulk-reset-password-from-excel")
async def bulk_reset_password_from_excel(request: Request, file: UploadFile = File(...)) -> Dict[str, List[Dict[str, Any]]]:
    """
    Массовый сброс паролей из Excel файла

    Колонка A: username или email (строка 1 — заголовок, пропускается)

    Возвращает Yopass ссылки для каждого пользователя
    """
    results = {"success": [], "failed": []}
    client = get_user_client(request)

    contents = await file.read()
    identifiers = parse_identifiers_column(contents)

    for identifier in identifiers:
        try:
            username = resolve_username(client, identifier)

            reset_result = client._request("user_mod", args=[username], params={"random": True})
            password = reset_result['result']['randompassword']

            yopass_link = create_yopass_link(username, password)
            email_list = reset_result['result'].get('mail', [])
            email = email_list[0] if email_list else ""

            results["success"].append({
                "identifier": identifier,
                "username": username,
                "email": email,
                "yopass_link": yopass_link
            })

        except Exception as e:
            results["failed"].append({
                "identifier": identifier,
                "error": str(e)
            })

    return results


@router.post("/api/v1/users/bulk-disable-preview")
async def bulk_disable_preview(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Dry-run: резолвит пользователей из Excel, ничего не делает в FreeIPA

    Колонка A: username или email (строка 1 — заголовок, пропускается)
    """
    found = []
    not_found = []
    client = get_user_client(request)

    contents = await file.read()
    identifiers = parse_identifiers_column(contents)

    for identifier in identifiers:
        try:
            username = resolve_username(client, identifier)
            found.append({"identifier": identifier, "username": username})
        except ValueError as e:
            not_found.append({"identifier": identifier, "error": str(e)})
        except Exception as e:
            not_found.append({"identifier": identifier, "error": str(e)})

    return {
        "found": found,
        "not_found": not_found,
        "total": len(identifiers),
        "found_count": len(found),
        "not_found_count": len(not_found)
    }


@router.post("/api/v1/users/bulk-disable-from-excel")
async def bulk_disable_from_excel(request: Request, file: UploadFile = File(...)) -> Dict[str, List[Dict[str, Any]]]:
    """
    Массовая блокировка пользователей из Excel файла

    Колонка A: username или email (строка 1 — заголовок, пропускается)
    """
    results = {"success": [], "failed": []}
    client = get_user_client(request)

    contents = await file.read()
    identifiers = parse_identifiers_column(contents)

    for identifier in identifiers:
        try:
            username = resolve_username(client, identifier)
            client._request("user_disable", args=[username], params={})
            results["success"].append({"identifier": identifier, "username": username})
        except ValueError as e:
            results["failed"].append({"identifier": identifier, "error": str(e)})
        except Exception as e:
            results["failed"].append({
                "identifier": identifier,
                "error": f"Ошибка блокировки: {str(e)}"
            })

    return results
