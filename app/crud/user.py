from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password, verify_password

def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password_hash=hashed_pw, role=user.role or "user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# def authenticate_user(db: Session, email: str, password: str):
#     db_user = db.query(User).filter(User.email == email).first()
#     if not db_user or not verify_password(password, db_user.password_hash):
#         return None
#     return db_user


def get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_name(db, username)  # 🔹 change happens here
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


# def update_user(db: Session, user_id: int, user: UserUpdate):
#     db_user = db.query(User).filter(User.id == user_id).first()
#     if not db_user:
#         return None
#     if user.name is not None:
#         db_user.name = user.name
#     if user.email is not None:
#         db_user.email = user.email
#     db.commit()
#     db.refresh(db_user)
#     return db_user


def update_user_by_id(db: Session, user_id: int, user_data):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user
