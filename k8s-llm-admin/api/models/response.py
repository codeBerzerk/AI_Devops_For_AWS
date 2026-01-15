from pydantic import BaseModel


class DiagnoseResponse(BaseModel):
    """Відповідь з діагнозом"""

    diagnosis: str
    model: str
    generation_time: float
    tokens_generated: int
    cached: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis": "## 1. Швидке резюме\nПод крашиться через...",
                "model": "llama3.2:3b-instruct",
                "generation_time": 12.5,
                "tokens_generated": 450,
                "cached": False,
            },
        }

