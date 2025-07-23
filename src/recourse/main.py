from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from os import getenv

from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi
from sentry_sdk import capture_exception


load_dotenv(".env")

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from taxiway.config import settings
from taxiway.exceptions import ServerException

# Set up logging configuration
logger = logging.getLogger(__name__)

# Initialize Sentry
sentry_sdk.init(
  dsn=settings.SENTRY_DSN,
  traces_sample_rate=1.0,
  profiles_sample_rate=1.0,
  send_default_pii=True,
  environment=settings.ENVIRONMENT,
  _experiments={
    # Set continuous_profiling_auto_start to True
    # to automatically start the profiler on when
    # possible.
    "continuous_profiling_auto_start": True,
  }
)
# Maximum number of retries for connection attempts
MAX_RETRIES = 10
# Initial delay in seconds
INITIAL_DELAY = 1
# Maximum delay in seconds
MAX_DELAY = 30


async def retry_with_backoff(func, *args, **kwargs):
  """
  Retry a function with exponential backoff.

  Args:
      func: The async function to retry
      *args, **kwargs: Arguments to pass to the function

  Returns:
      The result of the function call

  Raises:
      Exception: If all retries fail
  """
  delay = INITIAL_DELAY
  last_exception = None

  for attempt in range(MAX_RETRIES):
    try:
      return await func(*args, **kwargs)
    except Exception as e:
      last_exception = e
      if attempt < MAX_RETRIES - 1:
        logger.warning(
          f"Connection attempt {attempt + 1}/{MAX_RETRIES} failed: {str(e)}. Retrying in {delay} seconds...")
        await asyncio.sleep(delay)
        # Exponential backoff with jitter
        delay = min(delay * 2, MAX_DELAY) * (0.8 + 0.4 * (time.time() % 1))
      else:
        logger.error(f"All connection attempts failed: {str(e)}")

  # If we've exhausted all retries, raise the last exception
  raise last_exception


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Handle startup and shutdown events for the DP service."""
  try:
   yield

  except Exception as e:
    logger.error(f"Error in lifespan startup: {e}")
    raise

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Get CORS configuration from environment variables
cors_origins = getenv('CORS_ORIGINS', '').split(',')
cors_allow_credentials = getenv('CORS_ALLOW_CREDENTIALS',
                                'true').lower() == 'true'
cors_allow_methods = getenv('CORS_ALLOW_METHODS', '*').split(',')
cors_allow_headers = getenv('CORS_ALLOW_HEADERS', '*').split(',')

# Add CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=cors_origins,
  allow_credentials=cors_allow_credentials,
  allow_methods=cors_allow_methods,
  allow_headers=cors_allow_headers,
  expose_headers=['Location'],  # Allow access to Location header for redirects
  max_age=600  # Cache preflight requests for 10 minutes
)


# Add exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
  """Handle general exceptions."""
  logger.error(f"Unhandled exception: {exc}")
  capture_exception(exc)
  return JSONResponse(
    status_code=500,
    content={"detail": "Internal server error"}
  )


@app.exception_handler(ServerException)
async def server_exception_handler(request: Request, exc: ServerException):
  """Handle server exceptions."""
  logger.error(exc.message, exc_info=exc.exception)
  capture_exception(exc)
  return JSONResponse(
    status_code=exc.status_code,
    content=exc.message
  )


# Include routers
app.include_router(sessions_router)
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(bot_or_not_router)
app.include_router(dp_router)
app.include_router(event_router)


def generate_openapi_schema():
  """
  Generate the OpenAPI schema for the FastAPI application.
  """
  return get_openapi(
    title="SuperMarketer CMP v1 API",
    version="1.0.0",
    description="SuperMarketer v1 CMP API",
    routes=app.routes,
  )


@app.get("/openapi.json")
def get_openapi_endpoint():
  """
  Retrieve the generated OpenAPI schema.
  """
  return JSONResponse(content=generate_openapi_schema())


if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=5000
  )