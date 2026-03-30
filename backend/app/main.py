from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import database_manager
from app.exceptions.exception_handlers import register_exception_handlers
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware

settings = get_settings()
logger = logging.getLogger("online_bookstore.docs")
SWAGGER_STATIC_PREFIX = "/static/swagger"
SWAGGER_JS_URL = f"{SWAGGER_STATIC_PREFIX}/swagger-ui-bundle.js"
SWAGGER_CSS_URL = f"{SWAGGER_STATIC_PREFIX}/swagger-ui.css"
SWAGGER_FAVICON_URL = f"{SWAGGER_STATIC_PREFIX}/favicon-32x32.png"
APP_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = APP_DIR.parent
PROJECT_ROOT = BACKEND_ROOT.parent if BACKEND_ROOT.name == "backend" else BACKEND_ROOT
FRONTEND_DIR = PROJECT_ROOT / "frontend"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = APP_DIR / "frontend"
FRONTEND_ASSETS_DIR = FRONTEND_DIR / "assets"
FRONTEND_ASSETS_PREFIX = "/assets"

try:
    from swagger_ui_bundle import swagger_ui_path
except ImportError:
    swagger_ui_path = None


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not settings.testing:
        await database_manager.connect()
    yield
    if not settings.testing:
        await database_manager.disconnect()


configure_logging()
app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan, docs_url=None)
app.openapi_version = "3.0.3"

if swagger_ui_path is not None:
    app.mount(SWAGGER_STATIC_PREFIX, StaticFiles(directory=swagger_ui_path), name="swagger-static")
else:
    logger.warning(
        "Local Swagger UI assets are unavailable. Install requirements again to enable /docs without a CDN."
    )

if FRONTEND_ASSETS_DIR.exists():
    app.mount(FRONTEND_ASSETS_PREFIX, StaticFiles(directory=FRONTEND_ASSETS_DIR), name="frontend-assets")
else:
    logger.warning("Frontend assets directory is unavailable. The root UI will not load correctly.")

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    RateLimiterMiddleware,
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", include_in_schema=False)
async def storefront() -> Response:
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse(
            """
            <!DOCTYPE html>
            <html>
            <head><title>Frontend Unavailable</title></head>
            <body style="font-family: Arial, sans-serif; max-width: 720px; margin: 3rem auto; line-height: 1.5;">
                <h1>Frontend files are not installed yet.</h1>
                <p>Restore the <code>frontend/</code> directory and reload this page.</p>
            </body>
            </html>
            """,
            status_code=503,
        )
    return FileResponse(index_path)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req: Request) -> HTMLResponse:
    if swagger_ui_path is None:
        return HTMLResponse(
            """
            <!DOCTYPE html>
            <html>
            <head><title>Swagger UI Unavailable</title></head>
            <body style="font-family: Arial, sans-serif; max-width: 720px; margin: 3rem auto; line-height: 1.5;">
                <h1>Swagger UI assets are not installed yet.</h1>
                <p>Run <code>pip install -r requirements.txt</code>, restart the server, and reload this page.</p>
            </body>
            </html>
            """,
            status_code=503,
        )

    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
    if oauth2_redirect_url:
        oauth2_redirect_url = root_path + oauth2_redirect_url

    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url=root_path + SWAGGER_JS_URL,
        swagger_css_url=root_path + SWAGGER_CSS_URL,
        swagger_favicon_url=root_path + SWAGGER_FAVICON_URL,
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
        swagger_ui_parameters=app.swagger_ui_parameters,
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect() -> HTMLResponse:
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
