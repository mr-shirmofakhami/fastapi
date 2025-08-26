from sqlalchemy.orm import Session
from app.models.token import RefreshToken


def revoke_all_tokens_for_user(db: Session, user_id: int):
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.commit()