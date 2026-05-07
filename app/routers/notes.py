import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Note, User
from app.schemas import NoteCreate, NoteResponse, NoteUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notes", tags=["notes"])

# OWASP A10 demo in this stack (FastAPI + SQLAlchemy):
# BAD (do not use): leaks internal exception detail/stack context to the client.
# try:
#     risky_operation()
# except Exception as exc:
#     raise HTTPException(status_code=500, detail=str(exc))  # leaks internals
#
# GOOD (current pattern below): log server-side details and return safe message.
# except Exception as exc:
#     logger.error("Unexpected <operation> error: %s", exc)
#     raise HTTPException(status_code=500, detail="Internal server error.") from exc


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteResponse:
    try:
        note = Note(title=payload.title, content=payload.content, owner_id=current_user.id)
        db.add(note)
        db.commit()
        db.refresh(note)
        return note
    except Exception as exc:
        logger.error("Unexpected create note error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.") from exc


@router.get("/", response_model=list[NoteResponse])
def list_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NoteResponse]:
    try:
        # Enforce ownership (OWASP A01)
        return db.query(Note).filter(Note.owner_id == current_user.id).all()
    except Exception as exc:
        logger.error("Unexpected list notes error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.") from exc


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteResponse:
    try:
        note = db.query(Note).filter(Note.id == note_id, Note.owner_id == current_user.id).first()
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")
        return note
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected get note error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.") from exc


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteResponse:
    try:
        note = db.query(Note).filter(Note.id == note_id, Note.owner_id == current_user.id).first()
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")

        if payload.title is not None:
            note.title = payload.title
        if payload.content is not None:
            note.content = payload.content

        db.commit()
        db.refresh(note)
        return note
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected update note error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.") from exc


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        note = db.query(Note).filter(Note.id == note_id, Note.owner_id == current_user.id).first()
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")

        db.delete(note)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected delete note error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.") from exc
