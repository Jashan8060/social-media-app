from passlib.context import CryptContext

def hash(password: str):
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return password_context.hash(password)

def verify(plain_password, hashed_password):
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return password_context.verify(plain_password, hashed_password)