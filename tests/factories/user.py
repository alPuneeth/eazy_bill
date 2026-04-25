from sqlalchemy.exc import IntegrityError
import uuid
import random
import string

from app.models.core_models.user import UserRole, User
from app.core.security import get_password_hash

TEST_PASSWORD = "test_Password@123"

def create_user(
        session,
        public_id=None, 
        phone=None,
        user_code=None,
        role=UserRole.AGENT,
        is_active=True
        ):
    """
    Create and persist a user for tests.
    Default role = AGENT (safe default).
    """

    public_id = public_id or str(uuid.uuid4())
    phone = phone or "".join(random.choices(string.digits, k=10))
    hashed_password=get_password_hash(TEST_PASSWORD)

    if role == UserRole.ADMIN and not user_code:
        user_code="KVR"
    
    elif role == UserRole.TEST_USER and not user_code:
        user_code="TST"

    if user_code:
        codes = [user_code]
    else:
        codes = [
            ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            for _ in range(5)
        ]
    
    for code in codes:
        try:
            with session.begin_nested():  # begin_nested() - savepoint(mini transaction inside main transaction)
                user = User(
                    public_id=public_id,
                    name="Fake User",
                    phone=phone,
                    hashed_password=hashed_password,
                    role=role,
                    user_code=code,
                    is_active=is_active
                    )
                
                session.add(user) # staged in memory

            
                session.flush() # assigns PK without final commit 
                return user
        
        except IntegrityError: 
            if user_code:
                raise  # explicit failure if user passed invalid code
            continue # retry safely
    
    raise RuntimeError("Failed to generate unique user_code")


def create_agent(session, public_id=None, phone=None, user_code=None):
    return create_user(
        session=session,
        public_id=public_id,
        phone=phone,
        user_code=user_code,
        role=UserRole.AGENT
        )


def create_admin(session, public_id=None, phone=None, user_code=None):
    return create_user(
        session=session,
        public_id=public_id,
        phone=phone,
        user_code=user_code,
        role=UserRole.ADMIN
    )