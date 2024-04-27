from mysql.connector.errors import IntegrityError
from user.interface import UserServiceInterface
from auth.interface import AuthorizationServiceInterface
import schemas
import di


class UserService(UserServiceInterface):
    def __init__(self, auth: AuthorizationServiceInterface) -> None:
        self.auth = auth

    async def create_user(self, username: str, password: str) -> None:
        await self._insert_user(username, self.auth.hash_password(password))

    async def _insert_user(self, user: str, hashed_password: str) -> None:

        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            await cursor.execute(
                """
                INSERT INTO users (username, hashed_password)
                VALUES (%s, %s);   
                """,
                [user, hashed_password],
            )
        except IntegrityError:
            raise UserService.DuplicateUserError

        finally:
            await cursor.close()
            await conn.commit()
            await conn.close()

    async def remove_user(self, username: str) -> None:
        await self._delete_user(username)

    async def get_user(self, user: str | int) -> schemas.User:

        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            values = await cursor.execute(
                f"""
                SELECT users.id, users.username, users.level FROM users
                WHERE {"username" if isinstance(user, str) else "id"} = %s;
                """,
                [user],
            )
            try:
                return schemas.User.model_validate(values[0])
            except IndexError:
                raise UserService.UserNotExistingError
        finally:
            await cursor.close()
            await conn.close()

    async def set_variable(self, user: str | int, key: str, value: str | None) -> None:

        if key == "":
            raise UserService.KeyNotExistingError

        user_id = (
            user
            if isinstance(user, int)
            else schemas.User.model_validate(await self.get_user(user)).id
        )

        if value is None or value == "":
            return await self._delete_variable(user_id, key)

        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            await cursor.execute(
                """
                INSERT INTO variables (user_id, name, val)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                val = %s
                """,
                [user_id, key, str(value), str(value)],
            )

        finally:
            await cursor.close()
            await conn.commit()
            await conn.close()

    async def _delete_variable(self, user: str | int, key: str):

        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            await cursor.execute(
                f"""
                DELETE FROM variables 
                WHERE {"username" if isinstance(user, str) else "id"} = %s
                AND variables.name = %s;
                """,
                [user, key],
            )
        finally:
            await cursor.close()
            await conn.commit()
            await conn.close()

    async def get_variable(
        self,
        user: str | int,
        key: str,
    ) -> str:

        user_id = (
            user
            if isinstance(user, int)
            else schemas.User.model_validate(await self.get_user(user)).id
        )

        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            response = await cursor.execute(
                f"""
                SELECT val FROM variables
                WHERE user_id = %s AND name = %s;
                """,
                [user_id, key],
            )
        finally:
            await cursor.close()
            await conn.close()

        try:
            variable = response[0]["val"]
        except IndexError:
            raise UserService.KeyNotExistingError
        return variable

    async def change_password(self, user: str | int, password: str) -> None:

        await self.get_user(user)
        hashed_password = self.auth.hash_password(password)

        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            await cursor.execute(
                f"""
                UPDATE users SET
                hashed_password = %s
                WHERE {"username" if isinstance(user, str) else "id"} = %s;
                """,
                [hashed_password, user],
            )
        finally:
            await cursor.close()
            await conn.commit()
            await conn.close()

    async def _delete_user(
        self,
        user: str | int,
    ) -> None:

        user_id = (
            user
            if isinstance(user, int)
            else schemas.User.model_validate(await self.get_user(user)).id
        )
        await self.get_user(user_id)

        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            await cursor.execute(
                f"""
                DELETE FROM users 
                WHERE id = %s;
                """,
                [user_id],
            )
        finally:
            await cursor.close()
            await conn.commit()
            await conn.close()

        try:
            await self.get_user(user_id)
            raise UserService.UserNotDeletedError
        except UserService.UserNotExistingError:
            pass

        await self._delete_all_user_variables(user_id)

    async def _delete_all_user_variables(self, user: str | int) -> None:

        user_id = (
            user
            if isinstance(user, int)
            else schemas.User.model_validate(await self.get_user(user)).id
        )

        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            await cursor.execute(
                f"""
                DELETE FROM variables
                WHERE user_id = %s;
                """,
                [user_id],
            )
        finally:

            await cursor.close()
            await conn.commit()
            await conn.close()
