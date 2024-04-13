from di import container
from database.mysql import MySqlConnection
from database.queries import get_user_full
import tempfile
import schemas
import pytest
import asyncio


@pytest.mark.asyncio
async def test_close():
    db_semaphore = container.db_semaphore()._semaphore
    semaphore_count = db_semaphore._value
    conn = await container.db_connection()
    try:
        assert semaphore_count - 1 == db_semaphore._value
    finally:
        await conn.close()
    assert semaphore_count == db_semaphore._value


@pytest.mark.asyncio
async def test_commit():

    if container.db_semaphore()._semaphore._value < 2:
        pytest.skip("Semaphore too small to perform test.")

    conn = await container.db_connection()
    try:
        cursor = await conn.cursor()

        await cursor.execute(
            """
        INSERT INTO users (username, hashed_password)
        VALUES ("testMySqlCommit", "password");   
        """
        )
        await cursor.close()

        with pytest.raises(IndexError):
            await get_user_full("testMySqlCommit")

    finally:
        await conn.commit()
        await conn.close()

    await get_user_full("testMySqlCommit")


@pytest.mark.asyncio
async def test_rollback():

    if container.db_semaphore()._semaphore._value < 2:
        pytest.skip("Semaphore too small to perform test.")

    # skib if semaphore is less than 2
    conn = await container.db_connection()
    try:
        cursor = await conn.cursor()

        await cursor.execute(
            """
        INSERT INTO users (username, hashed_password)
        VALUES ("testMySqlRollback", "password");   
        """
        )

        with pytest.raises(IndexError):
            await get_user_full("testMySqlRollback")

        await conn.rollback()
        await conn.commit()

        with pytest.raises(IndexError):
            await get_user_full("testMySqlRollback")
    finally:
        await cursor.close()
        await conn.close()


@pytest.mark.asyncio
async def test_is_connectable():
    db_config = dict(schemas.Settings.model_validate(container.config()).database)
    del db_config["connection_limit"]

    assert await MySqlConnection.is_connectable(**db_config)
    db_config["password"] = "wrongPassword"
    assert not await MySqlConnection.is_connectable(**db_config)


@pytest.mark.asyncio
async def test_cursor():
    conn = await container.db_connection()
    try:
        cursor = await conn.cursor()
        assert isinstance(cursor, conn._Cursor)
    finally:
        await cursor.close()
        await conn.close()


@pytest.mark.asyncio
async def test_cursor_execute():
    conn = await container.db_connection()
    try:
        cursor = await conn.cursor()

        with pytest.raises(KeyError):
            await cursor.execute(
                """
                INSERT INTO users (username, hashed_password)
                VALUES (%s, "password");   
                """,
                ["testCursorExecute", "password"],
            )

        assert (
            len(
                await cursor.execute(
                    """
            INSERT INTO users (username, hashed_password)
            VALUES (%s, "password"), (%s, "password");   
            """,
                    ["testCursorExecute1", "testCursorExecute2"],
                )
            )
            == 0
        )

        assert (
            len(
                await cursor.execute(
                    """
            SELECT * FROM users
            WHERE username LIKE 'testCursorExecute%';
            """
                )
            )
            == 2
        )

    finally:
        await cursor.close()
        await conn.close()


@pytest.mark.asyncio
async def test_cursor_execute_multiple():
    conn = await container.db_connection()
    try:
        cursor = await conn.cursor()

        with pytest.raises(KeyError):
            await cursor.execute_multiple(
                """
                INSERT INTO users (username, hashed_password)
                VALUES (%s, "password");   
                """,
                ["testCursorExecute", "password"],
            )

        len(
            await cursor.execute_multiple(
                """
            INSERT INTO users (username, hashed_password)
            VALUES (%s, "password"), (%s, "password");   
            
            SELECT * FROM users
            WHERE username LIKE 'testCursorExecuteMultiple_NOT_FOUND';
            """,
                ["testCursorExecuteMultiple1", "testCursorExecuteMultiple2"],
            )
        ) == 0

        await conn.rollback()

        assert (
            len(
                await cursor.execute_multiple(
                    """
            INSERT INTO users (username, hashed_password)
            VALUES (%s, "password"), (%s, "password");   
            
            SELECT * FROM users
            WHERE username LIKE 'testCursorExecuteMultiple%';
            """,
                    ["testCursorExecuteMultiple1", "testCursorExecuteMultiple2"],
                )
            )
            == 2
        )

    finally:
        await cursor.close()
        await conn.close()


@pytest.mark.asyncio
async def test_cursor_execute_file():
    queries = b"""
    INSERT INTO users (username, hashed_password)
    VALUES ("testCursorExecuteMultiple1", "password"), ("testCursorExecuteMultiple2", "password");   
    
    SELECT * FROM users
    WHERE username LIKE 'testCursorExecuteMultiple%';
    """

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    with temp_file as file:
        file.write(queries)

    conn = await container.db_connection()
    try:
        cursor = await conn.cursor()
        assert len(await cursor.execute_file(file.name)) == 2

    finally:
        await cursor.close()
        await conn.close()


@pytest.mark.asyncio
async def test_cursor_close(): 
    conn = await container.db_connection()
    cursor = await conn.cursor()
    try:
        await cursor.close()
        with pytest.raises(cursor.CursorNotConnectedError):
            await cursor.execute("SELECT * FROM users;")
            
        await cursor.close()
        
    finally:
        await conn.close()
        
        