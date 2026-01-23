from passlib.hash import pbkdf2_sha256
from password_validator import PasswordValidator
# Instantiate a validator object:
schema = PasswordValidator()
schema.min(8)\
      .max(64)\
      .has().uppercase()\
      .has().lowercase()\
      .has().digits()\
      .has().symbols()\
      .has().no().spaces()

def hash_password(password):
    return pbkdf2_sha256.hash(password)
def verify_password(password, hashed_password):
    return pbkdf2_sha256.verify(password, hashed_password)

