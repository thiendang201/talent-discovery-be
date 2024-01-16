from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from exception import UnicornException
from routers.user.schemes import LoginPayload
from schemas import PageParams, PagedResponseSchema
from supabase_client.main import supabase_client

from tags import AUTH_TAG

userRouter = APIRouter(prefix="/user")


@userRouter.post(
    "/login",
    tags=[AUTH_TAG],
)
async def login(payload: LoginPayload):
    try:
        return supabase_client.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except:
        raise UnicornException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Wrong email or password",
            type="user.forbidden",
        )
