from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import User as UserModel, Note as NoteModel
from schemas import Note, NoteCreate, NoteUpdate
from auth import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/notes", tags=["Notes"])


@router.get("/", response_model=List[Note])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search in title and content"),
    pinned_only: bool = False,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all notes for the current user with optional filtering."""
    query = db.query(NoteModel).filter(NoteModel.user_id == current_user.id)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (NoteModel.title.ilike(search_pattern)) |
            (NoteModel.content.ilike(search_pattern)) |
            (NoteModel.tags.ilike(search_pattern))
        )
    
    if pinned_only:
        query = query.filter(NoteModel.is_pinned == True)
    
    notes = query.order_by(
        NoteModel.is_pinned.desc(),
        NoteModel.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return notes


@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new note."""
    logger.info(f"Creating note for user {current_user.username}: {note.title}")
    
    db_note = NoteModel(
        user_id=current_user.id,
        title=note.title,
        content=note.content,
        tags=note.tags,
        is_pinned=note.is_pinned
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    logger.info(f"Note created: {db_note.id}")
    return db_note


@router.get("/{note_id}", response_model=Note)
def get_note(
    note_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific note."""
    note = db.query(NoteModel).filter(
        NoteModel.id == note_id,
        NoteModel.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return note


@router.put("/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a note."""
    logger.info(f"Updating note {note_id} for user {current_user.username}")
    
    note = db.query(NoteModel).filter(
        NoteModel.id == note_id,
        NoteModel.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    if note_update.title is not None:
        note.title = note_update.title
    
    if note_update.content is not None:
        note.content = note_update.content
    
    if note_update.tags is not None:
        note.tags = note_update.tags
    
    if note_update.is_pinned is not None:
        note.is_pinned = note_update.is_pinned
    
    db.commit()
    db.refresh(note)
    
    logger.info(f"Note {note_id} updated successfully")
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a note."""
    logger.info(f"Deleting note {note_id} for user {current_user.username}")
    
    note = db.query(NoteModel).filter(
        NoteModel.id == note_id,
        NoteModel.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    db.delete(note)
    db.commit()
    
    logger.info(f"Note {note_id} deleted successfully")
    return None
