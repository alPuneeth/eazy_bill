from typing import cast

from app.schemas.common import IdValueRead
from app.schemas.device_info import DeviceInfoRead
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.status import Status
from app.models.lookup.tv_type import TVType


def build_deviceinfo_read(device: DeviceInfo) -> DeviceInfoRead:

    """
    Assemble DeviceInfoRead from DeviceInfo ORM instance.

    RULES:
    - ORM provides relationships
    - Service assembles meaning
    - Router must not construct this
    """

    status = cast(Status, device.status)
    tvtype = cast(TVType, device.tvtype)

    return DeviceInfoRead(
        public_id=device.public_id,

        account_number=device.account_number,
        stb_id=device.stb_id,
        vc_number=device.vc_number,
        previous_vc_number=device.previous_vc_number,
        tv_name=device.tv_name,

        # derived / relationship-based fields
        customer_public_id=device.customer.public_id,

        tvtype=IdValueRead(
            id=cast(int, tvtype.id),
            value=device.tvtype.name
        ),

        status=IdValueRead(
            id=cast(int, status.id),
            value=device.status.name
        ),

        created_at=device.created_at,
        updated_at=device.updated_at,
    )