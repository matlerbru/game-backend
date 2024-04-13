import schemas
from datetime import datetime, timedelta, timezone
from jose import jwt
import schemas
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import JWTError, jwt
from auth.interface import AuthorizationServiceInterface
from fastapi import HTTPException, status, Depends, Form
import schemas
from auth.interface import AuthorizationServiceInterface
import di
from fastapi.security import OAuth2PasswordBearer


class AuthorizationService(AuthorizationServiceInterface):
    def __init__(
        self,
        signing: str,
        hash_key: str,
        token_expiration_time: int,
    ) -> None:
        self.signing = signing
        self.key = hash_key
        self.token_time = token_expiration_time

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")

    def create_token(self, username: str) -> str:
        _data = {"sub": username}
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.token_time)
        _data["exp"] = expire
        return jwt.encode(
            _data,
            self.key,
            algorithm=self.signing,
        )

    async def authenticate(self, token: OAuth2PasswordBearer) -> schemas.UserAuth:
        try:
            payload = jwt.decode(
                token,
                self.key,
                algorithms=[self.signing],
            )
            username: str = payload.get("sub")
            if username is None:
                raise AuthorizationService.InvalidTokenError
            token_data = schemas.TokenData(username=username)
        except JWTError:
            raise AuthorizationService.InvalidTokenError
        try:
            user = await self._get_user_auth_from_database(token_data.username)
        except AuthorizationService.InvalidCredentialsError:
            raise AuthorizationService.InvalidTokenError
        return user

    async def authenticate_user(self, user: str | int, password: str) -> None:
        user = await self._get_user_credentials_from_database(user)
        if not self._verify_password(password, user.hashed_password):
            raise AuthorizationService.InvalidCredentialsError

    async def _get_user_auth_from_database(self, user: str | int) -> schemas.UserAuth:
        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            values = await cursor.execute(
                f"""
                SELECT users.id, users.priviledge FROM users
                WHERE users.{"username" if isinstance(user, str) else "id"} = %s 
                """,
                [user],
            )
            try:
                return schemas.UserAuth.model_validate(values[0])
            except IndexError:
                raise AuthorizationService.InvalidCredentialsError
        finally:
            await cursor.close()
            await conn.close()

    async def _get_user_credentials_from_database(
        self,
        user: str | int,
    ) -> schemas.UserCredentials:
        try:
            conn = await di.container.db_connection()
            cursor = await conn.cursor()
            values = await cursor.execute(
                f"""
                SELECT users.id, users.username, users.hashed_password FROM users
                WHERE users.{"username" if isinstance(user, str) else "id"} = %s;   
                """,
                [user],
            )
            try:
                return schemas.UserCredentials.model_validate(values[0])
            except IndexError:
                raise AuthorizationService.InvalidCredentialsError
        finally:
            await cursor.close()
            await conn.close()
