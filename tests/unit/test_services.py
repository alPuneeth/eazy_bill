from unittest.mock import MagicMock
from app.models.core_models.user import User, UserRole
from app.models.lookup.village import Village
from sqlmodel import select
import pytest

from app.services.bill.bill_visibility import apply_bill_visibility


def test_bill_visibility_when_role_admin():
    # ARRANGE
    stmt = select(Village)
    fake_user = MagicMock()
    fake_user.role = UserRole.ADMIN

    # ACT
    result = apply_bill_visibility(stmt, fake_user)

    # ASSERT
    assert result == stmt # admin gets the stmt back unchanged


def test_bill_visibility_when_role_test_user():
    stmt = select(Village)
    fake_user = MagicMock()
    fake_user.role = UserRole.TEST_USER

    result = apply_bill_visibility(stmt, fake_user)

    assert result == stmt


def test_bill_visibility_when_role_agent():
    stmt = select(Village)
    fake_user = MagicMock()
    fake_user.role = UserRole.AGENT

    result = apply_bill_visibility(stmt, fake_user)

    assert "agent_id" in str(result)


def test_bill_visibility_when_role_others():
    stmt = select(Village)
    fake_user = MagicMock()

    with pytest.raises(PermissionError):
        apply_bill_visibility(stmt, fake_user)

