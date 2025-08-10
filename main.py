#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sys

from pathlib import Path

import uvicorn

from app.registrar import register_app
from libs.conf import settings

# todo 根据settings.ENVIRONMENT 来配置log level
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
)
app = register_app()

if __name__ == '__main__':
    # 如果你喜欢在 IDE 中进行 DEBUG，main 启动方法会很有帮助
    # 如果你喜欢通过 print 方式进行调试，建议使用 fastapi cli 方式启动服务
    try:
        config = uvicorn.Config(
            app=f'{Path(__file__).stem}:app', reload=True, host=settings.UVICORN_HOST, port=settings.UVICORN_PORT
        )
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        raise e
