from __future__ import annotations

from os import getenv

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env files
load_dotenv(".env")


class Settings(BaseSettings):
  ENVIRONMENT: str | None = getenv("ENVIRONMENT")
  DATABASE_URL: str | None = getenv("TAXIWAY_DATABASE_URL")
  SENTRY_DSN: str | None = getenv("SENTRY_DSN", "")

  BASE_API_SERVICE_HOST: str | None = getenv("BASE_URL")

  # Google Cloud and Gemini Configuration
  GOOGLE_CLOUD_PROJECT: str | None = getenv("GOOGLE_CLOUD_PROJECT")
  GOOGLE_CLOUD_LOCATION: str | None = getenv("GOOGLE_CLOUD_LOCATION")
  GENAI_MODEL_BASE: str | None = getenv("GENAI_MODEL_BASE")
  VERTEX_API_KEY: str | None = getenv("VERTEX_API_KEY")

settings = Settings()