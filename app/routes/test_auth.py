from fastapi import APIRouter, Depends


from schemas.user import UserSchema, Token
from app.services.jwt import hash_password, encode_jwt


router = APIRouter(prefix="/jwt", tags="JWT")


Vitalik = UserSchema(
    username="Vitalik",
    password=hash_password("qwerty"),
    email="easyforpapizi@example.com",
)


Dimon = UserSchema(
    username="Dimon",
    password=hash_password("topsecret"),
    email="Dimon312@example.com",
)


users_db: dict[str, UserSchema] = {
    Vitalik.username: Vitalik,
    Dimon.username: Dimon,
}


def validate_auth_user():
    pass


@router.post("/login/", response_model=Token)
def auth_user_with_jwt(
    user: UserSchema = Depends(validate_auth_user),
):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
    }
    token = encode_jwt(jwt_payload)
    return Token(access_token=token, token_type="Bearer")
