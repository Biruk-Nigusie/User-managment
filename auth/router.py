from datetime import datetime, timezone
import jwt
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_mail import MessageSchema, FastMail
from sqlmodel import select
from core.jwt import create_access_token
from core.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas.user import UserCreate, UserLogin, ResetPasswordSchema
from db.session import get_session
from models.user import User
from core.security import hash_password, verify_password
from auth.dependencies import get_current_user
from utils.tokens import verify_email_token, create_email_token
from core.email import send_verification_email
from fastapi import BackgroundTasks
from core.email import conf
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    dbsession: AsyncSession = Depends(get_session),
):
    result = await dbsession.exec(select(User).where(User.email == user.email))
    if result.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
    )

    dbsession.add(new_user)
    await dbsession.commit()
    await dbsession.refresh(new_user)

    token = create_email_token(new_user.id)

    await send_verification_email(
        email_to=new_user.email,
        token=token,
        background_tasks=background_tasks,
    )

    return {
        "id": new_user.id,
        "email": new_user.email,
        "message": "User created. Verification email sent."
    }
@router.get("/verify-email")
async def verify_email(token: str, dbsession: AsyncSession = Depends(get_session)):
    user_id = verify_email_token(token)

    result = await dbsession.exec(select(User).where(User.id == user_id))
    user = result.first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    dbsession.add(user)
    await dbsession.commit()

    return {"message": "Email successfully verified"}

@router.post("/login")
async def login(user: UserLogin, dbsession: AsyncSession = Depends(get_session)):
    # find user by email
    result = await dbsession.exec(select(User).where(User.email == user.email))
    existing_user = result.first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # verify password
    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not existing_user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
    # create JWT token
    access_token = create_access_token({"sub": str(existing_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
@router.get("/me")
async def read_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}
@router.get("/verify-email")
async def verify_email(token:str, dbsession: AsyncSession = Depends(get_session)):
    try:
        user_id = verify_email_token(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,  detail=str(e))
    result = await dbsession.exec(select(User).where(User.id == user_id))
    user = result.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_verified = True
    dbsession.add(user)
    await dbsession.commit()
    await dbsession.refresh(user)
    return {"message": "Email verified successfully", "email":user.email}
@router.post("/forgot-password")
async def forgot_password(email: str,background_tasks: BackgroundTasks,  dbsession: AsyncSession = Depends(get_session) ,):
    result = await dbsession.exec(select(User).where(User.email == email))
    user = result.first()
    if not user:
        # Do not reveal email existence
        return {"msg": "If the email exists, a reset link has been sent."}

    # Generate a JWT token with short expiry
    reset_token = create_access_token(
    {
        "sub": str(user.id), # subject, user id
        "iat":datetime.now(timezone.utc).timestamp(),# issued-at time,
        # standard JWT field,current time in seconds used to check if the
        # token is issued before the password was last changed
        # reject any token that was issued before the last password change->invalidate old tokens.
    },

    )
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        body=f"Click here to reset your password: {reset_link}",
        subtype="plain"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

    return {"msg": "If the email exists, a reset link has been sent."}
@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordSchema,
    dbsession: AsyncSession = Depends(get_session),
):
    try:
        payload = jwt.decode(
            data.token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
        )
        user_id = int(payload.get("sub"))
        token_iat = payload.get("iat") # retrieve the time the token was issued
        if token_iat is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    result = await dbsession.exec(
        select(User).where(User.id == user_id)
    )
    user = result.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.password_changed_at and token_iat < user.password_changed_at.replace(tzinfo=timezone.utc).timestamp():
        # if token is issued before the last password change, it's rejected
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is no longer valid")
    user.hashed_password = hash_password(data.new_password)
    user.password_changed_at = datetime.now(timezone.utc) # update password_changed_at to the current utc time
    dbsession.add(user)
    await dbsession.commit()
    await dbsession.refresh(user)

    return {"msg": "Password reset successful"}

