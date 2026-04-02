from app.models.core_models.user import User, UserRole

def apply_user_code_rules(role, user_code, is_update=False):

    # Normalize input once
    user_code = user_code.strip() if user_code else None

    if role == UserRole.ADMIN:
        if is_update:
            raise ValueError("user_code cannot be modified for ADMIN")
        
        # ✅ Auto-assign if not provided
        if not user_code:
            return "KVR"
        
        if user_code != "KVR":
            raise ValueError("ADMIN user_code must be 'KVR'")
        return "KVR"

    elif role == UserRole.TEST_USER:
        if is_update:
            raise ValueError("user_code cannot be modified for TEST_USER")
        
        if not user_code:
            return "TST"

        if user_code != "TST":
            raise ValueError("TEST_USER user_code must be 'TST'")
        return "TST"

    elif role == UserRole.AGENT:
        if not user_code:
            raise ValueError("user_code is required for AGENT")
        user_code = user_code.upper()

        if len(user_code) != 3:
            raise ValueError("user_code must be exactly 3 characters")

        return user_code