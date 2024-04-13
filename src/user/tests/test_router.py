from httpx import AsyncClient, ASGITransport
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status
from di import container
from user.router import validate_new_password, validate_new_username
from auth.router import _get_access_token as get_access_token
from database.queries import get_user_full
import schemas
import pydantic
import pytest
import api


class UserFull(pydantic.BaseModel):
    id: int
    username: str
    hashed_password: str
    level: int
    priviledge: int


@pytest.mark.asyncio
async def test_create_user():

    async def create_user(data: OAuth2PasswordRequestForm):

        async with AsyncClient(
            transport=ASGITransport(app=api.api), base_url="http://localhost:15000"
        ) as ac:
            response = await ac.post(
                "/user",
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                content=f"username={data.username}&password={data.password}",
            )
            return response

    response = await create_user(
        OAuth2PasswordRequestForm(username="Request1", password="password")
    )

    assert response.status_code == 200
    assert response.json() == None
    await get_user_full("Request1")


@pytest.mark.asyncio
async def test_read_users_me():

    async def get_user_me(token: str):

        async with AsyncClient(
            transport=ASGITransport(app=api.api), base_url="http://localhost:15000"
        ) as ac:
            response = await ac.get(
                "/user/me",
                headers={
                    "accept": "application/json",
                    "Authorization": "Bearer " + token,
                },
            )
            return response

    user_service = container.user_service()
    await user_service.create_user("getUserMe", "password")
    token = (await get_access_token("getUserMe", "password")).access_token
    response = await get_user_me(token)
    assert response.status_code == 200
    await get_user_full("getUserMe")

    response = await get_user_me("")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user():

    async def get_user(username: str):

        async with AsyncClient(
            transport=ASGITransport(app=api.api), base_url="http://localhost:15000"
        ) as ac:
            response = await ac.get(
                f"/user?username={username}",
                headers={
                    "accept": "application/json",
                },
            )
            return response

    user_service = container.user_service()
    await user_service.create_user("getUser", "password")

    response = await get_user("getUser")

    assert response.status_code == 200
    user = schemas.User.model_validate(response.json())
    assert user == schemas.User.model_validate(
        (await get_user_full("getUser")).model_dump()
    )

    response = await get_user("getUser0")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_post_variable():

    async def post_variable(key: str, value: str | None, token: str):

        async with AsyncClient(
            transport=ASGITransport(app=api.api), base_url="http://localhost:15000"
        ) as ac:
            response = await ac.post(
                f"/user/variable?key={key}&value={value}",
                headers={
                    "accept": "application/json",
                    "Authorization": "Bearer " + token,
                },
            )
        return response

    user_service = container.user_service()
    await user_service.create_user("postVariable", "password")
    token = (await get_access_token("postVariable", "password")).access_token

    response = await post_variable("key", "value", token)
    assert response.status_code == 200
    assert response.json() == None

    assert (await user_service.get_variable("postVariable", "key")) == "value"

    response = await post_variable("key", "value", "")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_variable():

    async def get_variable(key: str, token: str):

        async with AsyncClient(
            transport=ASGITransport(app=api.api), base_url="http://localhost:15000"
        ) as ac:
            response = await ac.get(
                f"/user/variable?key={key}",
                headers={
                    "accept": "application/json",
                    "Authorization": "Bearer " + token,
                },
            )
        return response

    user_service = container.user_service()
    await user_service.create_user("getVariable", "password")
    token = (await get_access_token("getVariable", "password")).access_token

    await user_service.set_variable("getVariable", "key", "value")

    response = await get_variable("key", token)
    assert response.status_code == 200
    assert response.json() == "value"

    response = await get_variable("key", "")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user():

    async def delete_user(token: str):

        async with AsyncClient(
            transport=ASGITransport(app=api.api), base_url="http://localhost:15000"
        ) as ac:
            response = await ac.delete(
                f"/user",
                headers={
                    "accept": "application/json",
                    "Authorization": "Bearer " + token,
                },
            )
        return response

    user_service = container.user_service()
    await user_service.create_user("DeleteUser", "password")
    token = (await get_access_token("DeleteUser", "password")).access_token

    response = await delete_user(token)

    assert response.status_code == 200
    assert response.json() == None

    with pytest.raises(IndexError):
        await get_user_full("DeleteUser")

    response = await delete_user("")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password():

    async def change_password(password: str, token: str):

        async with AsyncClient(
            transport=ASGITransport(app=api.api), base_url="http://localhost:15000"
        ) as ac:
            response = await ac.post(
                f"/user/password",
                headers={
                    "accept": "application/json",
                    "Authorization": "Bearer " + token,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                content=f"password={password}",
            )
        return response

    user_service = container.user_service()
    await user_service.create_user("changePassword", "password")
    token = (await get_access_token("changePassword", "password")).access_token

    password = (await get_user_full("changePassword")).hashed_password

    response = await change_password("newPassword", token)

    assert response.status_code == 200
    assert response.json() == None

    newPassword = (await get_user_full("changePassword")).hashed_password

    assert password != newPassword

    token = (await get_access_token("changePassword", "newPassword")).access_token
    response = await change_password("p", token)
    assert response.status_code == 400

    response = await change_password("newPassword", "")
    assert response.status_code == 401


def test_validate_new_username():

    validate_new_username("username")
    validate_new_username("Username")
    validate_new_username("username1")
    validate_new_username("u1sername")
    validate_new_username("u" * 2)
    validate_new_username("u" * 14)

    with pytest.raises(HTTPException):
        validate_new_username("u#sername")

    with pytest.raises(HTTPException):
        validate_new_username("1username")

    with pytest.raises(HTTPException):
        validate_new_username("u")

    with pytest.raises(HTTPException):
        validate_new_username("u" * 15)


def test_validate_new_password():

    validate_new_password("password")
    validate_new_password("1p#assword2")
    validate_new_password("password")
    validate_new_password("p" * 6)
    validate_new_password("p" * 63)

    with pytest.raises(HTTPException):
        validate_new_password("p" * 5)

    with pytest.raises(HTTPException):
        validate_new_password("p" * 64)

    with pytest.raises(HTTPException):
        validate_new_password("pass word")
