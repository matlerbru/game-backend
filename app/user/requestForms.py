from typing import Annotated
from fastapi import HTTPException, status, Depends, Form


class NewUser:

    def __init__(
        self,
        *,
        username: Annotated[
            str,
            Form(),
        ],
        password: Annotated[
            str,
            Form(),
        ],
    ):
        self.username = username
        self.password = password


class PasswordChange:

    def __init__(
        self,
        *,
        password: Annotated[
            str,
            Form(),
        ],
    ):
        self.password = password
