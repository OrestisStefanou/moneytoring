from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_password_strenth():
    pass


def email_is_valid(email: str) -> bool:
    if len(email) < 4:
        return False
    
    if '@' not in email:
        return False
    
    if email[0] == '@':
        return False


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)