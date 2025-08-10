#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录
BasePath = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{BasePath}/.env", env_file_encoding="utf-8", extra="ignore"
    )

    ENVIRONMENT: Literal['dev', 'test', 'prod'] = 'dev'
    # Env MySQL
    DB_USERNAME: str = ""
    DB_PASSWORD: str = ""
    DB_ENGINE: str = "mysql+aiomysql"
    DB_HOST: str = ""
    DB_PORT: int = 3306
    DB_DATABASE: str = "test"
    DB_ECHO: bool = False
    DB_CHARSET: str = "utf8mb4"

    SQLALCHEMY_DATABASE_URL: str = ""

    @field_validator("SQLALCHEMY_DATABASE_URL", mode="before")
    def assemble_mysql_connection(  # pylint: disable=no-self-argument
            cls, v: str, info: ValidationInfo
    ):
        if len(v) == 0:
            # 部分客户用户名和密码可能带@字符
            username = quote_plus(info.data["DB_USERNAME"])
            password = quote_plus(info.data["DB_PASSWORD"])
            return (
                f"{info.data['DB_ENGINE']}://{username}:{password}@"
                f"{info.data['DB_HOST']}:{info.data['DB_PORT']}/{info.data['DB_DATABASE']}?charset={info.data['DB_CHARSET']}"
            )
        return v

    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_API_BASE: str = ""
    LLM_API_KEY: str = ""

    A2A_RUNTIME_ENDPOINT: str = "http://localhost:9999"

    # unicorn
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 9998

    API_V1_STR: str = "/v1"


settings = Settings()
