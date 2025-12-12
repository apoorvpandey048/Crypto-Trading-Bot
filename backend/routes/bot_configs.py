from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User as UserModel, BotConfig as BotConfigModel
from schemas import BotConfig, BotConfigCreate, BotConfigUpdate
from auth import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bot-configs", tags=["Bot Configurations"])


@router.get("/", response_model=List[BotConfig])
def get_bot_configs(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all bot configurations for the current user."""
    configs = db.query(BotConfigModel).filter(
        BotConfigModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return configs


@router.post("/", response_model=BotConfig, status_code=status.HTTP_201_CREATED)
def create_bot_config(
    config: BotConfigCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new bot configuration."""
    logger.info(f"Creating bot config for user {current_user.username}: {config.name}")
    
    # Check if name already exists for this user
    existing = db.query(BotConfigModel).filter(
        BotConfigModel.user_id == current_user.id,
        BotConfigModel.name == config.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A bot configuration with this name already exists"
        )
    
    db_config = BotConfigModel(
        user_id=current_user.id,
        name=config.name,
        api_key=config.api_key,
        api_secret=config.api_secret,
        is_testnet=config.is_testnet,
        is_active=config.is_active
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    logger.info(f"Bot config created: {db_config.id}")
    return db_config


@router.get("/{config_id}", response_model=BotConfig)
def get_bot_config(
    config_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific bot configuration."""
    config = db.query(BotConfigModel).filter(
        BotConfigModel.id == config_id,
        BotConfigModel.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot configuration not found"
        )
    
    return config


@router.put("/{config_id}", response_model=BotConfig)
def update_bot_config(
    config_id: int,
    config_update: BotConfigUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a bot configuration."""
    logger.info(f"Updating bot config {config_id} for user {current_user.username}")
    
    config = db.query(BotConfigModel).filter(
        BotConfigModel.id == config_id,
        BotConfigModel.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot configuration not found"
        )
    
    # Check if new name conflicts
    if config_update.name and config_update.name != config.name:
        existing = db.query(BotConfigModel).filter(
            BotConfigModel.user_id == current_user.id,
            BotConfigModel.name == config_update.name,
            BotConfigModel.id != config_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A bot configuration with this name already exists"
            )
        config.name = config_update.name
    
    if config_update.api_key is not None:
        config.api_key = config_update.api_key
    
    if config_update.api_secret is not None:
        config.api_secret = config_update.api_secret
    
    if config_update.is_testnet is not None:
        config.is_testnet = config_update.is_testnet
    
    if config_update.is_active is not None:
        config.is_active = config_update.is_active
    
    db.commit()
    db.refresh(config)
    
    logger.info(f"Bot config {config_id} updated successfully")
    return config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bot_config(
    config_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a bot configuration."""
    logger.info(f"Deleting bot config {config_id} for user {current_user.username}")
    
    config = db.query(BotConfigModel).filter(
        BotConfigModel.id == config_id,
        BotConfigModel.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot configuration not found"
        )
    
    db.delete(config)
    db.commit()
    
    logger.info(f"Bot config {config_id} deleted successfully")
    return None
