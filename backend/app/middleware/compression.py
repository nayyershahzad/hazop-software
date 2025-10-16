from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import gzip
import time
import logging

logger = logging.getLogger(__name__)

class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to compress responses using gzip and add caching headers for better performance.
    """

    def __init__(self, app: ASGIApp, min_size: int = 500, compress_level: int = 6):
        """
        Initialize compression middleware.

        Args:
            app: The ASGI application
            min_size: Minimum size in bytes before compressing (default 500)
            compress_level: Gzip compression level 1-9 (default 6, higher = better compression but slower)
        """
        super().__init__(app)
        self.min_size = min_size
        self.compress_level = compress_level
        logger.info(f"Compression middleware initialized with min_size={min_size}, level={compress_level}")

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

        # Skip compression for streaming responses or those already compressed
        if (
            "Content-Encoding" in response.headers or
            "Transfer-Encoding" in response.headers or
            response.status_code < 200 or
            response.status_code >= 300
        ):
            return response

        # Check if client accepts gzip encoding
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response

        # Skip small responses to avoid compression overhead
        if (
            "Content-Length" in response.headers and
            int(response.headers["Content-Length"]) < self.min_size
        ):
            return response

        # Get response body
        body = b""

        # Response may be StreamingResponse, Response, or other
        if hasattr(response, "body"):
            body = response.body
        elif hasattr(response, "body_iterator"):
            # For streaming responses, collect the whole body first
            async for chunk in response.body_iterator:
                body += chunk

        # Only compress if body is not empty
        if not body:
            return response

        # Compress the body
        compressed_body = gzip.compress(body, compresslevel=self.compress_level)

        # Skip if compression didn't reduce the size (rare but possible)
        if len(compressed_body) >= len(body):
            return response

        # Create new response with compressed body
        resp = Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

        # Add content encoding header
        resp.headers["Content-Encoding"] = "gzip"
        resp.headers["Content-Length"] = str(len(compressed_body))
        resp.headers["Vary"] = "Accept-Encoding"

        # Add compression ratio for debugging (optional)
        original_size = len(body)
        compressed_size = len(compressed_body)
        compression_ratio = round((1 - compressed_size / original_size) * 100, 2)
        resp.headers["X-Compression-Ratio"] = f"{compression_ratio}%"

        return resp