import di
import pydantic
import schemas

"""These query functions should be used ony test and validation.
"""


class _UserFull(pydantic.BaseModel):
    id: int
    username: str
    hashed_password: str
    level: int
    priviledge: int


async def get_user_full(username: str) -> _UserFull:

    conn = await di.container.db_connection()
    try:
        cursor = await conn.cursor()
        values = await cursor.execute(
            f"""
            SELECT * FROM users
            WHERE users.username = %s;
            """,
            [username],
        )
        return _UserFull.model_validate(values[0])
    finally:
        await cursor.close()
        await conn.close()
