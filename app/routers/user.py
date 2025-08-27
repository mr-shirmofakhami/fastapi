from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from app.core.database import get_db
from app.crud.token import revoke_all_tokens_for_user
from app.crud.user import update_user_by_id, delete_user_by_id
from app.models.token import RefreshToken
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PasswordChangeRequest
from app.crud import user as user_crud
from app.utils.security import get_current_user, get_current_admin, owner_or_admin, verify_password, hash_password
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_crud.create_user(db, user)


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
_: User = Depends(get_current_admin)
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


@router.delete("/{user_id}", summary="Delete any user (Admin only)")
def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.delete(user)
    db.commit()

    return {"message": f"User with ID {user_id} deleted successfully"}


@router.post("/change-password", summary="Change your own password")
def change_password(
    password_data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Verify old password
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    # 2. Hash and store the new password
    current_user.password_hash = hash_password(password_data.new_password)
    db.commit()

    # 3. Optional: Invalidate all refresh tokens for this user
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).delete()
    db.commit()

    return {"message": "Password changed successfully. Please log in again."}


@router.delete("/me", summary="Delete your own account")
def delete_own_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Remove user's refresh tokens for security
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).delete()

    # Delete the user account
    db.delete(current_user)
    db.commit()

    return {"message": "Your account has been deleted."}