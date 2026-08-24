"""Registration and login."""

from fastapi import APIRouter, status
from sqlalchemy import select

from app.deps import CurrentUser, DbDep, SettingsDep
from app.errors import AuthenticationError, ConflictError, ValidationError
from app.models import Player, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.security import create_access_token, hash_password, verify_password
from app.services.clock import is_valid_timezone

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_for(user: User, settings: SettingsDep) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(str(user.id), settings),
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an account and its player profile",
)
def register(payload: RegisterRequest, db: DbDep, settings: SettingsDep) -> TokenResponse:
    """Register a new hunter. The account and player profile are created together."""
    email = payload.email.lower().strip()

    if db.scalar(select(User).where(User.email == email)) is not None:
        raise ConflictError("An account with that email already exists.")

    if not is_valid_timezone(payload.timezone):
        raise ValidationError(
            f"{payload.timezone!r} is not a known IANA timezone "
            "(for example: 'Asia/Seoul')."
        )

    user = User(email=email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.flush()

    player = Player(user_id=user.id, name=payload.name, timezone=payload.timezone)
    db.add(player)

    db.commit()
    db.refresh(user)

    return _token_for(user, settings)


@router.post("/login", response_model=TokenResponse, summary="Exchange credentials for a token")
def login(payload: LoginRequest, db: DbDep, settings: SettingsDep) -> TokenResponse:
    """Log in. The same error is returned for unknown email and wrong password."""
    user = db.scalar(select(User).where(User.email == payload.email.lower().strip()))

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationError("Incorrect email or password.")

    return _token_for(user, settings)


@router.get("/me", response_model=UserResponse, summary="The authenticated account")
def me(user: CurrentUser) -> User:
    return user
