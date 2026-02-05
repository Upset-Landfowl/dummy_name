
from passlib.context import CryptContext

ctx = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    deprecated="auto"
)

def hash_password(password) -> str:
    return ctx.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return ctx.verify(plain_password, hashed_password)
