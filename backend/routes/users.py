from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User as UserModel
from schemas import User, UserUpdate
from auth import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/profile", response_model=User)
def get_profile(current_user: UserModel = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user


@router.put("/profile", response_model=User)
def update_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    logger.info(f"Profile update attempt for user: {current_user.username}")
    
    # Check if new email/username already exists
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(UserModel).filter(UserModel.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(UserModel).filter(UserModel.username == user_update.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.password:
        from auth import get_password_hash
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"Profile updated successfully for user: {current_user.username}")
    return current_user


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user account."""
    logger.info(f"Account deletion for user: {current_user.username}")
    
    db.delete(current_user)
    db.commit()
    
    logger.info(f"Account deleted successfully: {current_user.username}")
    return None
