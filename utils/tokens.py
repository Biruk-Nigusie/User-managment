from datetime import datetime, timedelta
import jwt
from core.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRE_MINUTES = 60

def create_email_token(user_id:int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)
    payload = {'sub': str(user_id), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
def verify_email_token(token:str) ->int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('sub') # is user_id is not found token is not valid.
        if user_id is None:
            raise ValueError("Invalid token")
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.PyJWTError:
        raise ValueError("Invalid token")

