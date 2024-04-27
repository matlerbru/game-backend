from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, HTTPException, status
import schemas
import auth
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends, HTTPException, status
import user.requestForms as rf
import schemas
from fastapi import Depends
import schemas
import di


router = APIRouter()


def validate_new_username(username: str) -> None:
    if not username.isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be alpha numeric.",
        )
    if username[0].isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must start with a letter.",
        )
    if len(username) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must have a lenght of at least 2 digits.",
        )
    if len(username) > 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must have a lenght of maximum 14 digits.",
        )


def validate_new_password(password: str) -> None:
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must have a lenght of at least 6 digits.",
        )
    if len(password) > 63:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must have a lenght of maximum 63 digits.",
        )
    if " " in password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must not contain empty space.",
        )


@router.post("")
async def create_user(data: Annotated[rf.NewUser, Depends()]) -> None:
    validate_new_username(data.username)
    validate_new_password(data.password)

    user_service = di.container.user_service()
    try:
        await user_service.create_user(data.username, data.password)
    except user_service.DuplicateUserError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User already exists.",
        )


@router.get("/me", response_model=schemas.User)
async def read_users_me(
    userAuth: Annotated[schemas.UserAuth, Depends(auth.authenticate)],
) -> schemas.User:
    user_service = di.container.user_service()
    return await user_service.get_user(userAuth.id)


@router.get("")
async def get_user(
    username: str,
) -> schemas.User:
    user_service = di.container.user_service()
    try:
        return await user_service.get_user(username)
    except user_service.UserNotExistingError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not is not existing",
        )


@router.post("/variable")
async def post_variable(
    key: str,
    value: str | None,
    userAuth: Annotated[schemas.UserAuth, Depends(auth.authenticate)],
) -> None:
    user_service = di.container.user_service()
    await user_service.set_variable(userAuth.id, key, value)


@router.get("/variable")
async def get_variable(
    key: str,
    userAuth: Annotated[schemas.UserAuth, Depends(auth.authenticate)],
) -> str:
    user_service = di.container.user_service()
    return await user_service.get_variable(userAuth.id, key)


@router.delete("")
async def delete_user(
    userAuth: Annotated[schemas.UserAuth, Depends(auth.authenticate)],
) -> None:
    user_service = di.container.user_service()
    await user_service.remove_user(userAuth.id)


@router.post("/password")
async def change_password(
    userAuth: Annotated[schemas.UserAuth, Depends(auth.authenticate)],
    data: Annotated[rf.PasswordChange, Depends()],
) -> None:
    validate_new_password(data.password)
    user_service = di.container.user_service()
    await user_service.change_password(userAuth.id, data.password)
