from fastapi import HTTPException, status


class ItemNotFound(HTTPException):
    def __init__(self, detail: dict, headers: dict[str, str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )


class UnauthorizedRequest(HTTPException):
    def __init__(self):
        super().__init__(
            detail={"message": "Invalid authentication credentials"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class BadLoginRequest(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Incorrect username or password"},
        )


class PinError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Wrong pin. Contact to admin!"},
        )
