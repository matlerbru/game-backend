from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
import di
from typing import Annotated
from fastapi import Depends


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def authenticate(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    auth = di.container.auth_service()
    try:
        return await auth.authenticate(token=token)
    except auth.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
