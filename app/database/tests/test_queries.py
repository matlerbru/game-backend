from di import container
from database.queries import get_user_full, _UserFull
import schemas
import pytest


@pytest.mark.asyncio
async def test_get_user_full():

    user = await get_user_full("user1")
    user.hashed_password.startswith("$2b$12$")

    assert user == _UserFull.model_validate(
        {
            "id": 1,
            "username": "user1",
            "hashed_password": user.hashed_password,
            "level": 0,
            "priviledge": schemas.Priviledge.NIL,
        }
    )

    with pytest.raises(IndexError):
        await get_user_full("user0")
