from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    # 🔴 FULL visibility for YOU
    logger.error("Validation error")
    logger.error("Errors: %s", exc.errors())
    logger.error("Body: %s", exc.body)

    # Extract first meaningful error message
    message = exc.errors()[0].get("msg", "Invalid request")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": message}
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
        content={"message": exc.detail}
    )
