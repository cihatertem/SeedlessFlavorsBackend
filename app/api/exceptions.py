from fastapi import HTTPException, status


class ItemNotFound(HTTPException):
    def __init__(self, detail: dict, headers: dict[str, str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )
