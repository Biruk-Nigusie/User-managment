import re

def validate_password_strength(v: str) -> str:
    """
    Reusable password validator.
    Raises ValueError if criteria are not met.
    """
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters long')
    if not re.search(r"\d", v):
        raise ValueError('Password must contain at least one number')
    if not re.search(r"[A-Z]", v):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
        raise ValueError('Password must contain at least one special character')
    return v