from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password, verify_password


def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,  # ✅ switched from name to username
        email=user.email,
        password_hash=hashed_pw,
        role=user.role or "user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_name(db: Session, username: str):  # ✅ param renamed
    return db.query(User).filter(User.username == username).first()  # ✅ switched to username


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_name(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def update_user_by_id(db: Session, user_id: int, user_data):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    update_data = user_data.dict(exclude_unset=True)

    # ✅ Hash the password if provided
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user_by_id(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True