#!/usr/bin/python3
import uvicorn
import asyncio
from database.queries import create_user
import di
import schemas
import api


async def main():
    config = uvicorn.Config(api.api, port=4040, host="0.0.0.0", log_config="log.ini")
    server = uvicorn.Server(config)

    try:
        conn = await di.container.db_connection()
        cursor = await conn.cursor()
        await cursor.execute_file("mysql-setup-tables.sql")
    finally:
        await cursor.close()
        await conn.commit()
        await conn.close()

    await create_user("admin", "password", schemas.Priviledge.ADMINISTRATOR)
    await server.serve()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
