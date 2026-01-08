from functools import lru_cache
import os

from pydantic import BaseModel


class Settings(BaseModel):
    """应用配置：数据库、通用大模型(LLM) 等。"""

    APP_NAME: str = "Source Comparison Agent Backend"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 示例：mysql+asyncmy://user:password@localhost:3306/source_agent
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+asyncmy://dump:dump111@localhost:6006/source_agent",
    )

    # 通用大模型配置（默认按 OpenAI 兼容接口命名，可指向 DeepSeek 等）
    LLM_API_KEY: str = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    LLM_BASE_URL: str = os.getenv(
        "LLM_BASE_URL",
        os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )
    LLM_DEFAULT_MODEL: str = os.getenv(
        "LLM_DEFAULT_MODEL",
        os.getenv("OPENAI_MODEL", "qwen-turbo"),
    )
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_STREAM: bool = os.getenv("LLM_STREAM", "true").lower() == "true"

    # 外部搜索
    WEB_SEARCH_API_URL: str = os.getenv(
        "WEB_SEARCH_API_URL", "https://api.bocha.cn/v1/web-search"
    )
    WEB_SEARCH_API_KEY: str = os.getenv("WEB_SEARCH_API_KEY", "")

    # MOI数据库配置（内部数据源）
    MOI_BASE_URL: str = os.getenv(
        "MOI_BASE_URL",
        "https://freetier-01.cn-hangzhou.cluster.matrixonecloud.cn"
    )
    MOI_API_KEY: str = os.getenv(
        "MOI_API_KEY",
        "aAVwjAZB4RG_JcPaFR0ZVR4r5yitSjHeKimpdSFKsDaBEt4QzZGZk35D2dEIBmXXbJKG7XHTsTzq-GyC"
    )

    # CAS Configuration
    # CAS Server Base URL
    CAS_SERVER_URL: str = os.getenv("CAS_SERVER_URL", "http://10.222.3.121:8080/cas")
    # Backend URL (for callbacks)
    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://10.222.3.121:5173")
    # Frontend URL (to redirect after login)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://10.222.3.121:5173")
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-please")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    MODE: str = os.getenv("MODE", "test")

settings = Settings()
