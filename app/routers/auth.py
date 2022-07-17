import logging
from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi import HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends

from app.controllers import auth as auth_controller
from app.entities.app_user import User
from app.entities.auth_token import Token
from app.dependencies import get_session, extract_user_id_from_token
from app.errors import auth as auth_errors

router  = APIRouter()

@router.post("/token", response_model=Token, tags=["Authentication"], status_code=200)
async def login_for_acess_token(
    session: AsyncSession = Depends(get_session), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        token = await auth_controller.create_token(
            session=session,
            email=form_data.username,
            password=form_data.password    
        )
    except auth_errors.AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong email or password",
        )
    except Exception as err:
        logging.exception("Unexpected error during signup:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )
    
    return token


@router.post("/signup", tags=["Authentication"], status_code=201)
async def signup(user: User, session: AsyncSession = Depends(get_session)):
    try:
        await auth_controller.create_user(session=session, **user.dict())
    except auth_errors.EmailUnavailable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    except auth_errors.InvalidEmail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email",
        )
    except Exception as err:
        logging.exception("Unexpected error during signup:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )


# # This is for testing purposes
@router.get("/users/me/", tags=["Authentication"])
async def auth_test_endpoint(user_id = Depends(extract_user_id_from_token)):
    return {"user_id": user_id}