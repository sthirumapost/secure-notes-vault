from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .models import User, Note, Share


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, password_hash: str):
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_note(db: Session, owner_id: int, content: str):
    note = Note(
        owner_id=owner_id,
        content=content,
        updated_at=datetime.now(timezone.utc)
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_owned_notes(db: Session, user_id: int):
    return db.query(Note).filter(Note.owner_id == user_id).all()


def get_note_if_authorized(db: Session, note_id: int, user_id: int):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        return None, None

    if note.owner_id == user_id:
        return note, "owner"

    share = db.query(Share).filter(
        Share.note_id == note_id,
        Share.shared_with_user_id == user_id
    ).first()

    if share:
        return note, "read"

    return note, None


def update_note(db: Session, note: Note, content: str):
    note.content = content
    note.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note: Note):
    db.delete(note)
    db.commit()


def share_note(db: Session, note_id: int, shared_with_user_id: int):
    share = Share(note_id=note_id, shared_with_user_id=shared_with_user_id)
    db.add(share)
    db.commit()
    db.refresh(share)
    return share
