from datetime import datetime, timedelta
import jwt, bcrypt
from core.config import settings


def encode_jwt_token(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expiration_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    """
    Create and sign a JWT token with the given payload.

    Args:
        payload: Dictionary containing claims to encode in the token
        private_key: Key used to sign the token
        algorithm: Signing algorithm to use
        expire_minutes: Minutes until token expiration
        expire_timedelta: Custom expiration time delta

    Returns:
        Encoded JWT token as string
    """
    to_encode = payload.copy()
    now = datetime.now()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire, iat=now)

    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded


def decode_jwt_token(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to decode
        public_key: Key used to verify the token signature
        algorithm: Algorithm used for verification

    Returns:
        Dictionary containing the decoded token claims

    Raises:
        jwt.InvalidTokenError: If token is invalid or expired
    """
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> bytes:
    """
    Hash a password using bcrypt with a random salt.

    Args:
        password: Plain text password

    Returns:
        Hashed password as bytes
    """
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def verify_password(password: str, hashed_password: bytes) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password to verify
        hashed_password: Previously hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)
