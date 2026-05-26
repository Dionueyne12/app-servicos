class AppError(Exception):
    status_code = 400

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class BadRequestError(AppError):
    status_code = 400


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class ConflictError(AppError):
    status_code = 409
