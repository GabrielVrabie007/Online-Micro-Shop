import secrets
import uuid
from typing import Annotated, Any
from time import time

from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_auth_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """
    Demonstrate basic HTTP authentication with username and password.

    Args:
        credentials (HTTPBasicCredentials): The basic auth credentials provided in the request.
            Contains username and password fields.

    Returns:
        dict: A dictionary containing the welcome message and provided credentials.
            Format: {
                "message": str,
                "username": str,
                "password": str
            }

    Example:
        Request: GET /demo-auth/basic-auth/ with Basic Auth header
        Response: {
            "message": "Hi!",
            "username": "john",
            "password": "password123"
        }
    """
    return {
        "message": "Hi!",
        "username": credentials.username,
        "password": credentials.password,
    }


usernames_to_passwords = {
    "admin": "admin",
    "john": "password",
}


static_auth_token_to_username = {
    "a0787852e766b02e87f6dd15e4c3d1f1": "admin",
    "a14f178e75dee69fa66ff3fad9db0daa": "john",
}


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    """
    Authenticate user using basic auth credentials and return username.

    Args:
        credentials (HTTPBasicCredentials): The basic auth credentials containing
            username and password.

    Returns:
        str: The authenticated username if credentials are valid.

    Raises:
        HTTPException: 401 status code if credentials are invalid.

    Notes:
        - Uses secrets.compare_digest for timing-attack safe password comparison
        - Credentials are checked against usernames_to_passwords dictionary
    """
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    correct_password = usernames_to_passwords.get(credentials.username)
    if correct_password is None:
        raise unauthed_exc

    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        correct_password.encode("utf-8"),
    ):
        raise unauthed_exc

    return credentials.username


def get_username_by_static_auth_token(
    static_token: str = Header(alias="x-auth-token"),
) -> str:
    """
    Authenticate user using a static auth token from request header.

    Args:
        static_token (str): The authentication token provided in x-auth-token header.

    Returns:
        str: The username associated with the valid token.

    Raises:
        HTTPException: 401 status code if token is invalid or not found.

    Notes:
        - Tokens are checked against static_auth_token_to_username dictionary
        - This is a simple implementation and should be replaced with JWT in production
    """
    if username := static_auth_token_to_username.get(static_token):
        return username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid",
    )


@router.get("/basic-auth-username/")
def demo_basic_auth_username(
    auth_username: str = Depends(get_auth_user_username),
):
    """
    Endpoint demonstrating successful basic auth with username verification.

    Args:
        auth_username (str): Username obtained from basic auth credentials.
            Automatically verified by get_auth_user_username dependency.

    Returns:
        dict: A dictionary containing welcome message and authenticated username.
            Format: {
                "message": str,
                "username": str
            }

    Example:
        Request: GET /demo-auth/basic-auth-username/ with Basic Auth header
        Response: {
            "message": "Hi, john!",
            "username": "john"
        }
    """
    return {
        "message": f"Hi, {auth_username}!",
        "username": auth_username,
    }


@router.get("/some-http-header-auth/")
def demo_auth_some_http_header(
    username: str = Depends(get_username_by_static_auth_token),
):
    """
    Endpoint demonstrating token-based authentication using HTTP header.

    Args:
        username (str): Username obtained from token authentication.
            Automatically verified by get_username_by_static_auth_token dependency.

    Returns:
        dict: A dictionary containing welcome message and authenticated username.
            Format: {
                "message": str,
                "username": str
            }

    Example:
        Request: GET /demo-auth/some-http-header-auth/ with x-auth-token header
        Response: {
            "message": "Hi, john!",
            "username": "john"
        }
    """
    return {
        "message": f"Hi, {username}!",
        "username": username,
    }


COOKIES: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_ID_KEY = "web-app-session-id"


def generate_session_id() -> str:
    """
    Generate a secure random session ID.

    Returns:
        str: A new UUID4 hex string to use as session identifier.

    Notes:
        - Uses uuid4 for cryptographically secure random session IDs
        - Returns 32-character hexadecimal string
    """
    return uuid.uuid4().hex


def get_session_data(
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
) -> dict:
    """
    Retrieve session data for a given session ID.

    Args:
        session_id (str): The session ID from the cookie.

    Returns:
        dict: The session data associated with the session ID.

    Raises:
        HTTPException: 401 status code if session ID is invalid or not found.

    Notes:
        - Sessions are stored in memory in the COOKIES dictionary
        - In production, use a proper session backend like Redis
    """
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )

    return COOKIES[session_id]


@router.post("/login-cookie/")
def demo_auth_login_set_cookie(
    response: Response,
    username: str = Depends(get_username_by_static_auth_token),
):
    """
    Create a new session and set session cookie after successful authentication.

    Args:
        response (Response): FastAPI response object to set cookie.
        username (str): Authenticated username from token authentication.

    Returns:
        dict: Simple success message.
            Format: {"result": "ok"}

    Notes:
        - Creates new session with username and login timestamp
        - Sets session cookie in response
        - In production, add proper session expiration and security flags
    """
    session_id = generate_session_id()
    COOKIES[session_id] = {
        "username": username,
        "login_at": int(time()),
    }
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
    return {"result": "ok"}


@router.get("/check-cookie/")
def demo_auth_check_cookie(
    user_session_data: dict = Depends(get_session_data),
):
    """
    Verify session cookie and return session information.

    Args:
        user_session_data (dict): Session data obtained from cookie.
            Automatically verified by get_session_data dependency.

    Returns:
        dict: Session information including welcome message and session data.
            Format: {
                "message": str,
                "username": str,
                "login_at": int
            }

    Example:
        Request: GET /demo-auth/check-cookie/ with valid session cookie
        Response: {
            "message": "Hello, john!",
            "username": "john",
            "login_at": 1643456789
        }
    """
    username = user_session_data["username"]
    return {
        "message": f"Hello, {username}!",
        **user_session_data,
    }


@router.get("/logout-cookie/")
def demo_auth_logout_cookie(
    response: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
    user_session_data: dict = Depends(get_session_data),
):
    """
    End user session and remove session cookie.

    Args:
        response (Response): FastAPI response object to remove cookie.
        session_id (str): Current session ID from cookie.
        user_session_data (dict): Session data for farewell message.

    Returns:
        dict: Farewell message with username.
            Format: {"message": str}

    Notes:
        - Removes session from COOKIES dictionary
        - Deletes session cookie from client
        - In production, implement proper session cleanup
    """
    COOKIES.pop(session_id)
    response.delete_cookie(COOKIE_SESSION_ID_KEY)
    username = user_session_data["username"]
    return {
        "message": f"Bye, {username}!",
    }


"""
Below is the improved implementation of authentication,more secure,time expire for sessions,using jwt tokens after authentication
"""
# from datetime import datetime, timedelta
# from typing import Annotated, Any
# import secrets
# import uuid
# from time import time

# from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie
# from fastapi.security import (
#     HTTPBasic,
#     HTTPBasicCredentials,
#     HTTPBearer,
#     OAuth2PasswordBearer,
# )
# from passlib.context import CryptContext
# from pydantic import BaseModel, EmailStr
# from jose import JWTError, jwt

# router = APIRouter(prefix="/auth", tags=["Authentication"])

# # Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # JWT Configuration
# SECRET_KEY = "your-secret-key-stored-in-env"  # Store in environment variables
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30


# class User(BaseModel):
#     username: str
#     email: EmailStr
#     disabled: bool = False


# class UserInDB(User):
#     hashed_password: str


# # Store users in a database instead of dict
# users_db = {
#     "john": {
#         "username": "john",
#         "email": "john@example.com",
#         "hashed_password": pwd_context.hash("password"),
#         "disabled": False,
#     }
# }


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


# def get_user(username: str) -> UserInDB | None:
#     if username in users_db:
#         user_dict = users_db[username]
#         return UserInDB(**user_dict)
#     return None


# def authenticate_user(username: str, password: str) -> UserInDB | None:
#     user = get_user(username)
#     if not user or not verify_password(password, user.hashed_password):
#         return None
#     return user


# def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
#     to_encode = data.copy()
#     expire = datetime.now() + (expires_delta or timedelta(minutes=15))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# # Session management with Redis-like storage (use actual Redis in production)
# class SessionStore:
#     def __init__(self):
#         self._sessions: dict[str, dict[str, Any]] = {}
#         self._expire_times: dict[str, float] = {}

#     def create_session(self, user_data: dict, expire_minutes: int = 30) -> str:
#         session_id = secrets.token_urlsafe(32)
#         expire_time = time() + expire_minutes * 60
#         self._sessions[session_id] = user_data
#         self._expire_times[session_id] = expire_time
#         return session_id

#     def get_session(self, session_id: str) -> dict | None:
#         if session_id not in self._sessions:
#             return None
#         if time() > self._expire_times[session_id]:
#             self.delete_session(session_id)
#             return None
#         return self._sessions[session_id]

#     def delete_session(self, session_id: str) -> None:
#         self._sessions.pop(session_id, None)
#         self._expire_times.pop(session_id, None)


# session_store = SessionStore()


# @router.post("/login")
# async def login(
#     response: Response, credentials: HTTPBasicCredentials = Depends(HTTPBasic())
# ):
#     user = authenticate_user(credentials.username, credentials.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Basic"},
#         )

#     # Create session
#     session_id = session_store.create_session(
#         {
#             "username": user.username,
#             "email": user.email,
#             "login_time": datetime.now().isoformat(),
#         }
#     )

#     # Create JWT token
#     access_token = create_access_token(
#         data={"sub": user.username},
#         expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
#     )

#     # Set secure cookie
#     response.set_cookie(
#         key="session_id",
#         value=session_id,
#         httponly=True,
#         secure=True,
#         samesite="lax",
#         max_age=1800,  # 30 minutes
#     )

#     return {"access_token": access_token, "token_type": "bearer"}


# @router.get("/me")
# async def get_current_user(session_id: str = Cookie(None)):
#     if not session_id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
#         )

#     session_data = session_store.get_session(session_id)
#     if not session_data:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
#         )

#     return session_data


# @router.post("/logout")
# async def logout(response: Response, session_id: str = Cookie(None)):
#     if session_id:
#         session_store.delete_session(session_id)
#     response.delete_cookie(key="session_id")
#     return {"message": "Successfully logged out"}
