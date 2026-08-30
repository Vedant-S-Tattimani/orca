from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.services.auth_service import verify_password, get_password_hash, create_access_token
from app.services.user_service import UserService
from app.api.deps import get_current_active_user
from app.utils.rate_limiter import RateLimiter

router = APIRouter()

# Rate limiters
login_limiter = RateLimiter(max_requests=5, window_seconds=900)      # 5 per 15 min
register_limiter = RateLimiter(max_requests=3, window_seconds=3600)  # 3 per hour

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    role: str = "fisherman"

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str

@router.post("/register", response_model=UserResponse)
async def register(request: Request, user_in: UserCreate):
    client_ip = request.client.host if request.client else "unknown"
    if not register_limiter.allow(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many registration attempts. Try again later."
        )

    user_svc = UserService()
    existing_user = await user_svc.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )
        
    user_data = user_in.dict()
    user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    
    new_user = await user_svc.create_user(user_data)
    
    return UserResponse(
        id=str(new_user["_id"]),
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"]
    )

@router.post("/login", response_model=Token)
async def login_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    client_ip = request.client.host if request.client else "unknown"
    if not login_limiter.allow(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Try again in 15 minutes."
        )

    user_svc = UserService()
    user = await user_svc.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_active_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"]
    )

