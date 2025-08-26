from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.token import revoke_all_tokens_for_user
from app.crud.user import update_user_by_id, delete_user_by_id
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.crud import user as user_crud
from app.utils.security import get_current_user, get_current_admin, owner_or_admin
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_crud.create_user(db, user)


@router.get("/", response_model=list[UserResponse])
def list_users(
    current_user: User = Depends(get_current_admin),  # 🔹 Only admins
    db: Session = Depends(get_db)
):
    return db.query(User).all()


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# @router.put("/{user_id}", response_model=UserResponse)
# def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
#     db_user = user_crud.update_user(db, user_id, user)
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user

@router.put("/{user_id}", summary="Update a user (owner or admin)")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(owner_or_admin)  # The "_" means we don't reuse the return value
):
    updated_user = update_user_by_id(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


# @router.delete("/{user_id}")
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     if not user_crud.delete_user(db, user_id):
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"message": f"User {user_id} deleted successfully"}


@router.delete("/{user_id}", summary="Delete a user (Owner or Admin)")
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        _: object = Depends(owner_or_admin)
):
    # Revoke refresh tokens first
    revoke_all_tokens_for_user(db, user_id)

    # Delete the user
    success = delete_user_by_id(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User {user_id} deleted successfully"}


# @router.get("/me", response_model=UserResponse)
# def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user
