from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


async def handle_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as error:
        logger.warning(f"{error}")
        undefined_error = HTTPException(500)

        return JSONResponse(
            content={
                "code": 500,
                "detail": str(error),
            },
            status_code=undefined_error.status_code,
        )