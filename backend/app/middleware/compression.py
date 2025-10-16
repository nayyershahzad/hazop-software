from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging

logger = logging.getLogger(__name__)

class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add performance headers and caching for better performance.
    Note: This version doesn't do compression but just adds caching headers.
    FastAPI's built-in GZipMiddleware can be used if needed.
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize performance middleware.

        Args:
            app: The ASGI application
        """
        super().__init__(app)
        logger.info(f"Performance middleware initialized")

    async def dispatch(self, request: Request, call_next):
        # Track request processing time
        start_time = time.time()

        # Process the request and get the response
        response = await call_next(request)

        # Track request processing time
        process_time = time.time() - start_time

        # Add processing time header for debugging/monitoring
        response.headers["X-Process-Time"] = str(process_time)

        # Add cache control headers for static assets and common responses
        path = request.url.path
        method = request.method

        if method == "GET":
            # Cache control for static assets (images, CSS, JS)
            if path.endswith(('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', '.woff', '.woff2')):
                # Cache for 7 days (604800 seconds)
                response.headers["Cache-Control"] = "public, max-age=604800, stale-while-revalidate=86400"
            else:
                # Add some cache control for API responses that don't change frequently
                if (
                    # Study details and dashboard don't change frequently
                    ("/api/studies/" in path and (path.endswith("/dashboard") or not any(x in path for x in ["/nodes", "/deviations"]))) or
                    # Reference data rarely changes
                    path.startswith(("/api/reference"))
                ):
                    # Cache for 5 minutes with 1 minute stale-while-revalidate
                    response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=60"
                else:
                    # Default for other GET requests - short cache with revalidation
                    response.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"

        return response