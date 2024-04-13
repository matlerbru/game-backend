from httpx import AsyncClient, ASGITransport
import pytest
import schemas
import api


@pytest.mark.asyncio
async def test_get_access_token():

    async def get_access_token(username: str, password: str):

        async with AsyncClient(
            transport=ASGITransport(app=api.api), base_url="http://localhost:15000"
        ) as ac:
            response = await ac.post(
                "/auth/token",
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                content=f"username={username}&password={password}",
            )
            return response

    token_response = await get_access_token("user1", "password1")
    assert token_response.status_code == 200
    assert schemas.Token.model_validate(token_response.json())

    token_response = await get_access_token("user0", "password1")
    assert token_response.status_code == 401

    token_response = await get_access_token("user1", "password0")
    assert token_response.status_code == 401
