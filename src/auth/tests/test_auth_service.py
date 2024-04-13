from di import container
import pytest
import schemas
import asyncio


@pytest.mark.dependency()
@pytest.mark.asyncio
async def test_hash_password():
    auth = container.auth_service()
    hashed_password: str = auth.hash_password("123456")
    assert len(hashed_password) == 60
    assert hashed_password.startswith("$2b$12$")

    # Verify that different hashes is created
    hashed_password_set = set([auth.hash_password("123456") for _ in range(10)])
    assert len(hashed_password_set) == 10


@pytest.mark.dependency(depends=["test_hash_password"])
@pytest.mark.asyncio
async def test_verify_password():
    password = "123456"
    auth = container.auth_service()
    hashed_password: str = auth.hash_password(password)
    assert auth._verify_password(password, hashed_password)
    assert not auth._verify_password("", hashed_password)
    assert not auth._verify_password(password[1:], hashed_password)
    assert not auth._verify_password(password[:-1], hashed_password)


@pytest.mark.dependency()
@pytest.mark.asyncio
async def test_create_token():
    auth = container.auth_service()
    assert len(auth.create_token("user1")) == 124
    assert len(auth.create_token("user2")) == 124


@pytest.mark.dependency(depends=["test_create_token"])
@pytest.mark.asyncio
async def test_authenticate():
    auth = container.auth_service()
    access_token = auth.create_token("user1")
    user_auth = await auth.authenticate(access_token)
    assert user_auth == schemas.UserAuth.model_validate(
        {"id": 1, "priviledge": schemas.Priviledge.NIL}
    )

    access_token = auth.create_token("user0")
    with pytest.raises(auth.InvalidTokenError):
        await auth.authenticate(access_token)


@pytest.mark.asyncio
async def test_authenticate_user():
    auth = container.auth_service()
    assert await auth.authenticate_user("user1", "password1") is None
    assert await auth.authenticate_user(2, "password2") is None

    with pytest.raises(auth.InvalidCredentialsError):
        await auth.authenticate_user("user0", "password0")

    with pytest.raises(auth.InvalidCredentialsError):
        await auth.authenticate_user("user1", "password0")

    with pytest.raises(auth.InvalidCredentialsError):
        await auth.authenticate_user(1, "password0")


@pytest.mark.asyncio
async def test_get_user_auth_from_database():
    auth = container.auth_service()
    user_auth = await auth._get_user_auth_from_database("user1")
    assert user_auth == schemas.UserAuth.model_validate(
        {"id": 1, "priviledge": schemas.Priviledge.NIL}
    )

    user_auth = await auth._get_user_auth_from_database(2)
    assert user_auth == schemas.UserAuth.model_validate(
        {"id": 2, "priviledge": schemas.Priviledge.NIL}
    )

    with pytest.raises(auth.InvalidCredentialsError):
        user_auth = await auth._get_user_auth_from_database("user0")


@pytest.mark.asyncio
async def test_get_user_credentials_from_database():
    auth = container.auth_service()

    user_credentials = await auth._get_user_credentials_from_database("user1")
    assert user_credentials == schemas.UserCredentials.model_validate(
        {
            "id": 1,
            "username": "user1",
            "hashed_password": "$2b$12$ztHWdHhD.R0NrcwOmHxsnOK2FMS4NRlI9fX5WtIAfqw1Msrj7E.pa",
        }
    )

    user_credentials = await auth._get_user_credentials_from_database(2)
    assert user_credentials == schemas.UserCredentials.model_validate(
        {
            "id": 2,
            "username": "user2",
            "hashed_password": "$2b$12$KK1bVU72T1yMus2bJxUD.uaZ6M4ltAYYW/iBPLmRIYsHfle6Gr92C",
        }
    )

    with pytest.raises(auth.InvalidCredentialsError):
        await auth._get_user_credentials_from_database("user0")
