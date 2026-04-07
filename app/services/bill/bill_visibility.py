from app.models.core_models.user import User, UserRole
from app.models.lookup.village import Village 


def apply_bill_visibility(stmt, current_user: User):
    """
    RBAC rules:
    - AGENT → only own villages
    - ADMIN, TEST → full access
    - Others → denied
    """
    FULL_ACCESS_ROLES = {UserRole.ADMIN, UserRole.TEST_USER}

    if current_user.role == UserRole.AGENT:
        stmt = stmt.where(Village.agent_id == current_user.id)
    
    if current_user.role in FULL_ACCESS_ROLES:
        return stmt
    
    raise PermissionError("Unauthorized role")