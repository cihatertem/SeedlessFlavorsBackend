import pytest
from fastapi import status


@pytest.mark.anyio
class MainTests:
    async def test_health_check(self, async_client):
        response = await async_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    async def test_sqlalchemy_integrity_exception_handling(self, async_client):
        response = await async_client.get("/test_integrity")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "IntegrityError" in response.json()["message"]
