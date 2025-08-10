#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from fastapi import FastAPI

from app.api.router import v1 as v1_router
from common.container.container import Container
from common.exception.exception_handler import register_exception
from common.response.response_schema import ResponseModel
from utils.serializers import MsgSpecJSONResponse


def register_app():
    # 初始化依赖注入容器
    Container()
    # FastAPI
    app = FastAPI(
        title="chat-a2a",
        version="0.0.1",
        description="chat-a2a",
        docs_url="/v1/docs",
        redoc_url="/v1/redocs",
        openapi_url="/v1/openapi",
        default_response_class=MsgSpecJSONResponse,
    )

    # 日志
    register_logger()

    # 中间件
    register_middleware(app)

    # 路由
    register_router(app)

    # 全局异常处理
    register_exception(app)

    return app


def register_logger() -> None:
    """
    系统日志

    :return:
    """


def register_middleware(app: FastAPI):
    """
    中间件，执行顺序从下往上

    :param app:
    :return:
    """


def register_router(app: FastAPI):
    """
    路由

    :param app: FastAPI
    :return:
    """

    @app.get("/health")
    def health() -> ResponseModel:
        return ResponseModel(data={"status": "ok"})

    # API
    app.include_router(v1_router)


