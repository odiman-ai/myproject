# spms_db/backend/core/openapi.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi(app: FastAPI):
    """
    Customize OpenAPI schema to include JWT Bearer and API Key security schemes.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="SPMS API",
        version="1.0.0",
        description="Sports Management System API with JWT and API Key Authentication",
        routes=app.routes,
    )

    # Add JWT Bearer auth
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT access token for user authentication"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header",
            "description": "API key for integrations and automated services"
        }
    }

    # Apply JWT security globally (optional)
    for path in openapi_schema["paths"].values():
        for method in path.values():
            # Skip public endpoints
            if method.get("summary", "").lower() in ("login", "refresh token"):
                continue

            security = method.get("security", [])
            # Apply both JWT and API key auth
            security.append({"BearerAuth": []})
            security.append({"ApiKeyAuth": []})
            method["security"] = security

    app.openapi_schema = openapi_schema
    return app
