from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .database import Base, engine
from .deps import get_db, get_current_user
from .models import User
from .schemas import (
    UserRegister, UserLogin, TokenResponse,
    NoteCreate, NoteUpdate, NoteResponse,
    ShareRequest, MessageResponse
)
from .auth import hash_password, verify_password, create_access_token
from . import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Notes Vault API")


@app.get("/")
def root():
    return {"message": "Secure Notes Vault API is running"}


@app.post("/auth/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    crud.create_user(db, payload.username, hash_password(payload.password))
    return {"message": "User registered successfully"}


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = crud.create_note(db, current_user.id, payload.content)
    return {
        "id": note.id,
        "owner_id": note.owner_id,
        "content": note.content,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "access": "owner",
    }


@app.get("/notes", response_model=list[NoteResponse])
def list_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notes = crud.list_owned_notes(db, current_user.id)
    return [
        {
            "id": n.id,
            "owner_id": n.owner_id,
            "content": n.content,
            "created_at": n.created_at,
            "updated_at": n.updated_at,
            "access": "owner",
        }
        for n in notes
    ]


@app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note, access = crud.get_note_if_authorized(db, note_id, current_user.id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if access is None:
        raise HTTPException(status_code=403, detail="Not authorized to access this note")

    return {
        "id": note.id,
        "owner_id": note.owner_id,
        "content": note.content,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "access": access,
    }


@app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note, access = crud.get_note_if_authorized(db, note_id, current_user.id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if access != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can update this note")

    note = crud.update_note(db, note, payload.content)
    return {
        "id": note.id,
        "owner_id": note.owner_id,
        "content": note.content,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "access": "owner",
    }


@app.delete("/notes/{note_id}", response_model=MessageResponse)
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note, access = crud.get_note_if_authorized(db, note_id, current_user.id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if access != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can delete this note")

    crud.delete_note(db, note)
    return {"message": "Note deleted successfully"}


@app.post("/notes/{note_id}/share", response_model=MessageResponse)
def share_note(
    note_id: int,
    payload: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note, access = crud.get_note_if_authorized(db, note_id, current_user.id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if access != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can share this note")

    target_user = crud.get_user_by_username(db, payload.username)
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot share note with yourself")

    try:
        crud.share_note(db, note_id, target_user.id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Note already shared with this user")

    return {"message": f"Note shared with {payload.username} as read-only"}
