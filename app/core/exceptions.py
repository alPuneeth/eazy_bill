import logging

from starlette import status

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    # FULL visibility for YOU
    logger.error("Validation error on %s %s - Errors: %s - Body: %s",
                request.method,
                request.url.path,
                exc.errors(),
                exc.body
                )

    messages = [error.get("msg", "Invalid request") for error in exc.errors()]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": messages}
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    logger.warning(
                    "HTTP %s on %s %s: %s", 
                    exc.status_code,
                    request.method,
                    request.url.path,
                    exc.detail
                    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
