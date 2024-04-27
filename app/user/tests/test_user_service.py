from di import container
import pydantic
import pytest
import schemas
from database.queries import get_user_full


@pytest.mark.dependency()
@pytest.mark.asyncio
async def test_insert_user():
    user_service = container.user_service()
    await user_service._insert_user("TestInsertUser", "password")
    user = await get_user_full("TestInsertUser")
    assert user.hashed_password == "password"
    assert user.level == 0
    assert user.priviledge == schemas.Priviledge.NIL


@pytest.mark.dependency()
@pytest.mark.dependency(depends=["test_insert_user"])
@pytest.mark.asyncio
async def test_create_user():
    user_service = container.user_service()
    await user_service.create_user("TestCreateUser", "password")
    user = await get_user_full("TestCreateUser")
    assert user.hashed_password.startswith("$2b$12$")

    with pytest.raises(user_service.DuplicateUserError):
        await user_service.create_user("TestCreateUser", "password")


@pytest.mark.dependency(depends=["test_create_user"])
@pytest.mark.asyncio
async def test_delete_user():

    user_service = container.user_service()
    await user_service.create_user("TestDeleteUser", "password")
    await user_service._delete_user("TestDeleteUser")

    with pytest.raises(IndexError):
        await get_user_full("TestDeleteUser")

    await user_service.create_user("TestDeleteUser", "password")
    user_full = await get_user_full("TestDeleteUser")
    await user_service._delete_user(user_full.id)

    with pytest.raises(IndexError):
        await get_user_full("TestDeleteUser")


@pytest.mark.dependency(depends=["test_create_user", "test_delete_user"])
@pytest.mark.asyncio
async def test_remove_user():

    user_service = container.user_service()
    auth_service = container.auth_service()
    await user_service.create_user("TestRemoveUser", "password")
    await user_service.remove_user("TestRemoveUser")

    with pytest.raises(IndexError):
        await get_user_full("TestRemoveUser")

    await user_service.create_user("TestRemoveUser", "password")


@pytest.mark.asyncio
async def test_get_user():
    user_service = container.user_service()
    user = await user_service.get_user("user1")
    assert user == schemas.User.model_validate(
        {"id": 1, "username": "user1", "level": 0}
    )

    user = await user_service.get_user(2)
    assert user == schemas.User.model_validate(
        {"id": 2, "username": "user2", "level": 0}
    )

    with pytest.raises(user_service.UserNotExistingError):
        await user_service.get_user("user0")


@pytest.mark.asyncio
async def test_set_variable():
    user_service = container.user_service()

    await user_service.set_variable("user1", "key1", "value1")
    assert await user_service.get_variable("user1", "key1") == "value1"

    await user_service.set_variable("user1", "key1", None)
    with pytest.raises(user_service.KeyNotExistingError):
        await user_service.get_variable("user1", "key1")

    await user_service.set_variable("user1", "key1", "")
    with pytest.raises(user_service.KeyNotExistingError):
        await user_service.get_variable("user1", "key1")

    await user_service.set_variable(1, "key2", "value2")
    assert await user_service.get_variable("user1", "key2") == "value2"

    with pytest.raises(user_service.KeyNotExistingError):
        await user_service.set_variable("user1", "", "value1")


@pytest.mark.asyncio
async def test_get_variable():
    user_service = container.user_service()

    await user_service.set_variable("user1", "key1", "value1")
    assert await user_service.get_variable("user1", "key1") == "value1"
    assert await user_service.get_variable(1, "key1") == "value1"

    with pytest.raises(user_service.KeyNotExistingError):
        await user_service.get_variable("user1", "key0")

    with pytest.raises(user_service.UserNotExistingError):
        await user_service.get_variable("user0", "key0")


@pytest.mark.asyncio
async def test_change_password():
    user_service = container.user_service()

    user = await get_user_full("user1")
    await user_service.change_password("user1", "password11")
    user_new_password = await get_user_full("user1")
    assert user.hashed_password != user_new_password.hashed_password

    user = await get_user_full("user1")
    await user_service.change_password(1, "password11")
    user_new_password = await get_user_full("user1")
    assert user.hashed_password != user_new_password.hashed_password

    with pytest.raises(user_service.UserNotExistingError):
        await user_service.change_password("user0", "password1")


@pytest.mark.asyncio
async def test_delete_all_user_variables():
    semaphore = container.db_semaphore()._semaphore
    user_service = container.user_service()

    await user_service.create_user("deleteAllUserVariables", "password")

    await user_service.set_variable("deleteAllUserVariables", "key1", "value1")

    await user_service.set_variable("deleteAllUserVariables", "key2", "value2")

    await user_service._delete_all_user_variables("deleteAllUserVariables")

    with pytest.raises(user_service.KeyNotExistingError):
        await user_service.get_variable("deleteAllUserVariables", "key1")

    with pytest.raises(user_service.KeyNotExistingError):
        await user_service.get_variable("deleteAllUserVariables", "key2")

    await user_service.set_variable("deleteAllUserVariables", "key1", "value1")

    user = await user_service.get_user("deleteAllUserVariables")

    await user_service._delete_all_user_variables(user.id)

    with pytest.raises(user_service.KeyNotExistingError):
        await user_service.get_variable("deleteAllUserVariables", "key1")
