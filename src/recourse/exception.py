from __future__ import annotations


class ServerException(Exception):

  def __init__(self, message: str | None = None, ex: Exception | None = None,
      status_code=None):
    super().__init__(message)
    self.status_code = status_code
    self.exception = ex
    self.message = message


class RateLimitException(ServerException):
  def __init__(self, ex: Exception | None = None, message: str | None = None):
    super().__init__(ex=ex, message=message, status_code=429)


class UnauthorizedException(ServerException):
  def __init__(self, ex: Exception | None = None, message: str | None = None):
    super().__init__(ex=ex, message=message, status_code=401)


class NotFoundException(ServerException):
  def __init__(self, ex: Exception | None = None, message: str | None = None):
    super().__init__(ex=ex, message=message, status_code=404)


class EntityNotFoundException(NotFoundException):
  def __init__(self, ex: Exception | None = None, message: str | None = None):
    super().__init__(ex=ex, message=message)

class SessionNotFoundException(EntityNotFoundException):
  def __init__(self, ex: Exception | None = None, message: str | None = None):
    super().__init__(ex=ex, message=message)

class FileNotFoundException(NotFoundException):
  def __init__(self, ex: Exception | None = None, message: str | None = None):
    super().__init__(ex=ex, message=message)

class IllegalArgumentException(ServerException):
  def __init__(self, ex: Exception | None = None, message: str | None = None):
    super().__init__(ex=ex, message=message, status_code=400)

class StillProcessingException(ServerException):
  def __init__(self, ex: Exception | None = None, message: str | None = None):
    super().__init__(ex=ex, message=message, status_code=425)

class OptimisticLockError(Exception):
  """Raised when optimistic locking fails."""
  def __init__(self, message: str):
    self.message = message
    super().__init__(self.message)