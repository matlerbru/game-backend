from di import container
from schemas import Settings
from database.mysql import MySqlConnection
import pytest
import asyncio
import schemas
import yaml
import os

# python3.11 -m pytest src


def pytest_sessionstart(session):

    with open("config.yml", "r") as file:
        settings = Settings.model_validate(yaml.safe_load(file))
        container.config.authorization.from_dict(dict(settings.authorization))

    ## could this be made as a daemon?
    os.system("docker compose -f docker-compose-db-test.yml up -d >/dev/null 2>&1")

    async def setup_database():

        db_settings = schemas.DatabaseSettings.model_validate(
            container.config.database()
        )

        while True:
            if await MySqlConnection.is_connectable(
                db_settings.host,
                db_settings.port,
                db_settings.user,
                db_settings.password,
                db_settings.name,
            ):
                break
            await asyncio.sleep(0.1)

        try:
            conn = await container.db_connection()
            cursor = await conn.cursor()

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
