from src.database.mysql import MySqlConnection
import asyncio
import mysql.connector


async def async_main():

    database = MySqlConnection("localhost", 15000, "root", "root", "legende_spil")
    await database.connect()

    cursor = await database.cursor()
    res = await cursor.execute(
        """
        SELECT id, username, level FROM users
        WHERE username = 'user1';
    """
    )
    print(res)

    async with cursor as cs:
        res = await cs.execute(
            """
            SELECT id, username, level FROM users;
        """
        )
        print(res)

    exit()

    database = MySqlConnection("localhost", 15000, "root", "root", "legende_spil")
    await database._connect()

    cursor = await database._connection.cursor()

    try:
        await cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT,
        username VARCHAR(30) UNIQUE,
        hashed_password VARCHAR(255),
        level INT DEFAULT 0,
        priviledge INT DEFAULT 0,
        PRIMARY KEY (id)
        );
        """
        )
    except mysql.connector.Error as e:
        print("Failed creating database: {}".format(e))

    try:
        await cursor.execute(
            """
        INSERT INTO users (username, hashed_password)
        VALUES ("user1", "password1");                
        """
        )
    except mysql.connector.Error as e:
        print("Failed creating user: {}".format(e))

    try:
        await cursor.execute(
            """
        SELECT id, username, level FROM users
        WHERE username = 'user1';
        """
        )

        print(await cursor.fetchone())
        print(await cursor.fetchall())

    except (mysql.connector.Error, TypeError) as e:
        print("Failed getting user: {}".format(e))

    await cursor.close()
    await database._connection.close()


if __name__ == "__main__":

    asyncio.run(async_main())
