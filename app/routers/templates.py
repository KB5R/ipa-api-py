from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/api/v1/templates/templates-excel")
def output_excel_templates() -> FileResponse:
    """
    Скачать шаблон excel для массового создания пользователя
    """
    return FileResponse(
        path="templates/freeipa_users_template.xlsx",
        filename="freeipa_users_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)