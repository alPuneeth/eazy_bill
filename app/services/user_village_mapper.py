from app.schemas.user import UserRead
from app.services.village_mapper import to_village_read
from app.models.core_models.user import User

def to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        public_id=user.public_id,
        name=user.name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        villages=[to_village_read(v) for v in user.villages],
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at
    )