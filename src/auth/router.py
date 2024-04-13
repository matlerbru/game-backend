from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends, HTTPException, status
import schemas
import di
import auth.requestForms as rf


router = APIRouter()


async def _get_access_token(username: str, password: str) -> schemas.Token:
    auth = di.container.auth_service()

    try:
        await auth.authenticate_user(username, password)
    except auth.InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_token(username)
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.post("/token")
async def get_access_token(
    data: Annotated[rf.Login, Depends()],
) -> schemas.Token:
    return await _get_access_token(data.username, data.password)
