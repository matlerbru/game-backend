from di import container
from schemas import Settings
from database.mysql_connector import MySqlConnection
import pytest
import asyncio
import di
import os

# python3.11 -m pytest src


def pytest_sessionstart(session):

    ## could this be made as a daemon?
    os.system("docker compose -f docker-compose-db-test.yml up -d >/dev/null 2>&1")

    async def setup_database():

        try:
            conn = await container.db_connection()
            cursor = await conn.cursor()
            
            await cursor.execute("drop table users;")
            await cursor.execute("drop table variables;")

            await cursor.execute_file("mysql-setup-tables.sql")
            await cursor.execute_file("mysql-setup-test.sql")
        finally:
            await cursor.close()
            await conn.commit()
            await conn.close()

    asyncio.get_event_loop().run_until_complete(setup_database())


def pytest_sessionfinish(session, exitstatus):
    os.system("docker compose -f docker-compose-db-test.yml down >/dev/null 2>&1")


@pytest.fixture(scope="function", autouse=True)
def db_semaphore_release(request):
    semaphore = container.db_semaphore()._semaphore
    val = semaphore._value
    yield
    assert val == semaphore._value
