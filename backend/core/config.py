from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
from pathlib import Path
import os


def _find_env_file() -> str:
    """Find .env file - check backend dir first, then project root."""
    here = Path(__file__).resolve().parent.parent
    candidates = [here / ".env", here.parent / ".env"]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(here.parent / ".env")


def _parse_comma_list(v):
    """Parse a comma-separated string or list into a list of strings."""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        return [item.strip() for item in v.split(",") if item.strip()]
    return v


class Settings(BaseSettings):
    LLM_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    
    DATABASE_URL: str = "sqlite:///./redswarm.db"
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    SECRET_KEY: str = "your_secret_key_here_change_in_production"
    ALLOWED_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:5173"]
    
    ALLOWED_TARGET_RANGES: Union[str, List[str]] = [
        "192.168.0.0/16",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "127.0.0.1/32"
    ]
    
    MAX_AGENTS: int = 10
    AGENT_TIMEOUT: int = 300
    AGENT_MEMORY_SIZE: int = 1000
    
    MAX_ATTACK_DEPTH: int = 10
    SIMULATION_TIMEOUT: int = 3600
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/redswarm.log"
    
    CTF_MODE: bool = False
    CTF_LEADERBOARD_ENABLED: bool = True
    
    GOD_MODE_ENABLED: bool = True
    GOD_MODE_INJECTION_DELAY: int = 5
    
    ENABLE_INSIDER_AGENT: bool = True
    ENABLE_APT_PERSONAS: bool = True
    ENABLE_REAL_TIME_GRAPH: bool = True
    ENABLE_EXPORT_REPORTS: bool = True
    
    @field_validator("ALLOWED_ORIGINS", "ALLOWED_TARGET_RANGES", mode="before")
    @classmethod
    def parse_comma_separated(cls, v):
        return _parse_comma_list(v)
    
    class Config:
        env_file = _find_env_file()
        case_sensitive = True
        extra = "ignore"


_settings = Settings()


def _is_real_key(key: str) -> bool:
    """Check if an API key is a real key, not a placeholder."""
    if not key:
        return False
    placeholders = ("your_", "sk-xxx", "change_me", "placeholder", "example")
    return not any(key.lower().startswith(p) for p in placeholders)


if _settings.LLM_PROVIDER == "openai" and not _is_real_key(_settings.OPENAI_API_KEY) and _is_real_key(_settings.ANTHROPIC_API_KEY):
    _settings.LLM_PROVIDER = "anthropic"
    _settings.LLM_MODEL = "claude-sonnet-4-20250514"

settings = _settings
