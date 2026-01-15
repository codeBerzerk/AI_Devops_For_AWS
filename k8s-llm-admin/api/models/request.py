from typing import Optional

from pydantic import BaseModel, Field


class DiagnoseRequest(BaseModel):
    """Запит на діагностику"""

    message: str = Field(..., description="Опис проблеми українською")
    resource_type: Optional[str] = Field(
        None,
        description="Тип ресурсу (pod, service, node)",
    )
    namespace: str = Field(
        default="default",
        description="Kubernetes namespace",
    )
    kubectl_output: Optional[str] = Field(
        None,
        description="Вивід kubectl команд",
    )
    language: str = Field(
        default="uk",
        description="Мова відповіді (uk або en)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Мій под в CrashLoopBackOff, що робити?",
                "resource_type": "pod",
                "namespace": "production",
            },
        }

