import pydantic
from enum import IntEnum
import logging


class DatabaseSettings(pydantic.BaseModel):
    host: str = pydantic.Field()
    name: str = pydantic.Field()
    user: str = "root"
    password: str
    port: int
    connection_limit: int | None = None


class Authorization(pydantic.BaseModel):
    secret_key: str
    algorithm: str
    token_expire_time: int


class Settings(pydantic.BaseModel):
    root_path: str = "/"
    database: DatabaseSettings
    authorization: Authorization


class Priviledge(IntEnum):
    NIL = 0
    SUSPENDED = 5
    INACTIVE = 10
    ACTIVE = 15
    GM = 20
    SUPERUSER = 25
    ADMINISTRATOR = 30


class UserAuth(pydantic.BaseModel):
    id: int
    priviledge: Priviledge


class User(pydantic.BaseModel):
    id: int
    username: str
    level: int


class UserCredentials(pydantic.BaseModel):
    id: int
    username: str
    hashed_password: str


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    username: str | None = None
