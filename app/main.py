from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from app.api.routes import auth, dashboard, integrations, orgs, policies, projects, services
from app.core.config import settings
from app.core.errors import app_exception_handler, http_exception_handler, validation_exception_handler, AppException
from app.core.middleware import RequestIdMiddleware


tags_metadata = [
    {"name": "Auth", "description": "Authentication and token lifecycle."},
    {"name": "Orgs", "description": "Organization and member management."},
    {"name": "Projects", "description": "Project management within organizations."},
    {"name": "Services", "description": "Service registration under projects."},
    {"name": "Policies", "description": "Policy configuration (SLA, Severity, PR Gate)."},
    {"name": "Integrations", "description": "Integrations (Git/Jira/Slack) configuration."},
    {"name": "Dashboard", "description": "Summary counts and setup progress."},
]

app = FastAPI(
    title="Polaris Lab Console API",
    description=(
        "Polaris Lab 웹 콘솔 운영을 위한 초기 API (취약점 스캔/분석은 제외)\n\n"
        "Standard response envelope:\n"
        "- success: { ok: true, data, meta: { request_id, paging? } }\n"
        "- error: { ok: false, error: { code, message, detail? }, meta: { request_id } }\n\n"
        "Error codes: AUTH_REQUIRED, AUTH_INVALID, FORBIDDEN, NOT_FOUND, CONFLICT, VALIDATION_ERROR, BAD_REQUEST\n"
    ),
    version="0.1.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(auth.router)
app.include_router(orgs.router)
app.include_router(projects.router)
app.include_router(services.router)
app.include_router(policies.router)
app.include_router(integrations.router)
app.include_router(dashboard.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("servers", [{"url": "http://0.0.0.0:6000", "description": "Local dev"}])
    schema.setdefault("components", {}).setdefault(
        "securitySchemes",
        {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        },
    )
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
