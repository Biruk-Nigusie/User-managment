from pydantic import BaseModel, EmailStr, field_validator
import re
from email_validator import validate_email, EmailNotValidError
from utils.validators import validate_password_strength


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        return validate_password_strength(v)
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        try:
            # check_deliverability=True verifies the domain has MX records
            email_info = validate_email(v, check_deliverability=True)
            return email_info.normalized
        except EmailNotValidError as e:
            # Returns a clean message like "The domain name gmail.co does not exist"
            raise ValueError(str(e))
from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str
class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str
    @field_validator('new_password')
    @classmethod
    def new_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)
