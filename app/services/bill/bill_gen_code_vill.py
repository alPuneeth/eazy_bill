from sqlmodel import Session

from app.models.core_models.user import User, UserRole
from app.services.bill_service import generate_bill_code
from app.services.bill.bill_fetch_vill import get_village_by_code_or_fail
from app.services.exceptions import VillageAccessDeniedError

def generate_bill_code_for_village(
        session: Session,
        village_code: str,
        current_user: User
):
    village = get_village_by_code_or_fail(session=session,
                                         village_code=village_code)
    
    # RBAC check
    if current_user.role == UserRole.AGENT and village.agent_id != current_user.id:
        raise VillageAccessDeniedError()

    return generate_bill_code(village, session, current_user)