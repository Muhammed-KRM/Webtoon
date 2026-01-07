"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from app.core.config import settings
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.schemas.base_response import BaseResponse
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=BaseResponse[UserResponse])
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return BaseResponse.success_response(
            UserResponse.model_validate(new_user),
            "User registered successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        from loguru import logger
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )


@router.post("/login", response_model=BaseResponse[Token])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    # Find user
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # JWT subject must be a string
        expires_delta=access_token_expires
    )
    
    return BaseResponse.success_response(
        Token(access_token=access_token, token_type="bearer"),
        "Login successful"
    )


@router.get("/me", response_model=BaseResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return BaseResponse.success_response(
        UserResponse.model_validate(current_user),
        "User information retrieved"
    )

