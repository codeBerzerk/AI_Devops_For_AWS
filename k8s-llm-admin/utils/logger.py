
import sys
from loguru import logger
from config.settings import settings

# Видалити default handler
logger.remove()

# Console handler (з кольорами)
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)

# File handler (всі логи)
if settings.LOG_DIR:
    logger.add(
        settings.LOG_DIR / "app.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Error logs окремо
    logger.add(
        settings.LOG_DIR / "errors.log",
        level="ERROR",
        rotation="5 MB",
        retention="14 days",
        compression="zip"
    )

# Export
__all__ = ["logger"]
