# spms_db/backend/core/audit_log.py
import logging
import json
from datetime import datetime
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("spms_audit_log")
logger.setLevel(logging.INFO)

# You can configure logging to a file, e.g.,
# handler = logging.FileHandler("audit.log")
# formatter = logging.Formatter("%(asctime)s - %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses for auditing purposes.
    Logs: timestamp, method, path, client IP, user ID/API key, status code, and optionally body.
    """
    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next):
        start_time = datetime.utcnow()

        # Identify client (user_id from JWT, API key, or anonymous IP)
        client_id = await self.get_client_identifier(request)
        method = request.method
        path = request.url.path
        client_ip = request.client.host

        # Capture request body if enabled
        request_body = None
        if self.log_request_body and method in ("POST", "PUT", "PATCH"):
            try:
                request_body = await request.body()
                request_body = request_body.decode("utf-8")
            except Exception:
                request_body = "<failed to read body>"

        # Process request
        response: Response = await call_next(request)
        status_code = response.status_code

        # Capture response body if enabled
        response_body = None
        if self.log_response_body:
            try:
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                response.body_iterator = iterate_in_chunks(response_body)
                response_body = response_body.decode("utf-8")
            except Exception:
                response_body = "<failed to read response>"

        # Build log entry
        log_entry = {
            "timestamp": start_time.isoformat(),
            "method": method,
            "path": path,
            "client_ip": client_ip,
            "client_id": client_id,
            "status_code": status_code,
        }
        if request_body:
            log_entry["request_body"] = request_body
        if response_body:
            log_entry["response_body"] = response_body

        logger.info(json.dumps(log_entry))
        return response

    async def get_client_identifier(self, request: Request) -> str:
        """
        Identify the client making the request:
        - JWT user ID
        - API key
        - IP for anonymous
        """
        # API Key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey:{api_key}"

        # JWT
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                from backend.auth.utils import decode_access_token
                payload = decode_access_token(token)
                user_id = payload.get("user_id")
                if user_id:
                    return f"user:{user_id}"
            except Exception:
                return "unknown_user"

        # Anonymous
        return f"anon:{request.client.host}"


# Helper to restore response.body_iterator after reading
async def iterate_in_chunks(data: bytes, chunk_size: int = 4096):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]
