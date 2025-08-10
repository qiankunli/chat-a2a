#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic.errors import PydanticUserError
from starlette.exceptions import HTTPException
from uvicorn.protocols.http.h11_impl import STATUS_PHRASES

from common.exception.errors import BaseExceptionMixin
from common.response.response_code import (
    CustomResponseCode,
    StandardResponseCode,
)
from common.response.response_schema import response_base
from common.schema import (
    CUSTOM_USAGE_ERROR_MESSAGES,
    CUSTOM_VALIDATION_ERROR_MESSAGES,
)
from libs.conf import settings
from utils.serializers import MsgSpecJSONResponse


def _get_exception_code(status_code: int):
    try:
        STATUS_PHRASES[status_code]
    except Exception:
        code = StandardResponseCode.HTTP_400
    else:
        code = status_code
    return code


async def _validation_exception_handler(request: Request, e: RequestValidationError | ValidationError):
    errors = []
    for error in e.errors():
        custom_message = CUSTOM_VALIDATION_ERROR_MESSAGES.get(error['type'])
        if custom_message:
            ctx = error.get('ctx')
            if not ctx:
                error['msg'] = custom_message
            else:
                error['msg'] = custom_message.format(**ctx)
                ctx_error = ctx.get('error')
                if ctx_error:
                    error['ctx']['error'] = (
                        ctx_error.__str__().replace("'", '"') if isinstance(ctx_error, Exception) else None
                    )
        errors.append(error)
    error = errors[0]
    if error.get('type') == 'json_invalid':
        message = 'json解析失败'
    else:
        error_input = error.get('input')
        location = error.get('loc')
        if isinstance(location, tuple):
            field = str(location[-1])
        else:
            field = ''
        error_msg = error.get('msg') or ''
        message = f'{field} {error_msg}，输入：{error_input}' if settings.ENVIRONMENT == 'dev' else error_msg
    msg = f'请求参数非法: {message}'
    data = {'errors': errors} if settings.ENVIRONMENT == 'dev' else None
    content = {
        'code': StandardResponseCode.HTTP_422,
        'msg': msg,
        'data': data,
    }
    request.state.__request_validation_exception__ = content  # 用于在中间件中获取异常信息
    return MsgSpecJSONResponse(status_code=422, content=content)


def register_exception(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        全局HTTP异常处理

        :param request:
        :param exc:
        :return:
        """
        if settings.ENVIRONMENT == 'dev':
            content = {
                'code': exc.status_code,
                'msg': exc.detail,
                'data': None,
            }
        else:
            res = response_base.fail(res=CustomResponseCode.HTTP_400)
            content = res.model_dump()
        request.state.__request_http_exception__ = content
        return MsgSpecJSONResponse(
            status_code=_get_exception_code(exc.status_code),
            content=content,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        fastapi 数据验证异常处理

        :param request:
        :param exc:
        :return:
        """
        return await _validation_exception_handler(request, exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """
        pydantic 数据验证异常处理

        :param request:
        :param exc:
        :return:
        """
        return await _validation_exception_handler(request, exc)

    @app.exception_handler(PydanticUserError)
    async def pydantic_user_error_handler(request: Request, exc: PydanticUserError):
        """
        Pydantic 用户异常处理

        :param request:
        :param exc:
        :return:
        """
        content = {
            'code': StandardResponseCode.HTTP_500,
            'msg': CUSTOM_USAGE_ERROR_MESSAGES.get(str(exc.code)),
            'data': None,
        }
        request.state.__request_pydantic_user_error__ = content
        return MsgSpecJSONResponse(
            status_code=StandardResponseCode.HTTP_500,
            content=content,
        )

    @app.exception_handler(AssertionError)
    async def assertion_error_handler(request: Request, exc: AssertionError):
        """
        断言错误处理

        :param request:
        :param exc:
        :return:
        """
        if settings.ENVIRONMENT == 'dev':
            content = {
                'code': StandardResponseCode.HTTP_500,
                'msg': str(''.join(exc.args) if exc.args else exc.__doc__),
                'data': None,
            }
        else:
            res = response_base.fail(res=CustomResponseCode.HTTP_500)
            content = res.model_dump()
        request.state.__request_assertion_error__ = content
        return MsgSpecJSONResponse(
            status_code=StandardResponseCode.HTTP_500,
            content=content,
        )

    @app.exception_handler(BaseExceptionMixin)
    async def custom_exception_handler(request: Request, exc: BaseExceptionMixin):
        """
        全局自定义异常处理

        :param request:
        :param exc:
        :return:
        """
        content = {
            'code': exc.code,
            'msg': str(exc.msg),
            'data': exc.data if exc.data else None,
        }
        request.state.__request_custom_exception__ = content
        return MsgSpecJSONResponse(
            status_code=_get_exception_code(exc.code),
            content=content,
            background=exc.background,
        )

    @app.exception_handler(Exception)
    async def all_unknown_exception_handler(request: Request, exc: Exception):
        """
        全局未知异常处理

        :param request:
        :param exc:
        :return:
        """
        if settings.ENVIRONMENT == 'dev':
            content = {
                'code': StandardResponseCode.HTTP_500,
                'msg': str(exc),
                'data': None,
            }
        else:
            res = response_base.fail(res=CustomResponseCode.HTTP_500)
            content = res.model_dump()
        request.state.__request_all_unknown_exception__ = content
        return MsgSpecJSONResponse(
            status_code=StandardResponseCode.HTTP_500,
            content=content,
        )
