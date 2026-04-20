import logging
logger = logging.getLogger(__name__)

from sqlalchemy import func, select
from sqlmodel import Session
from typing import Callable,Tuple, List, TypeVar

T = TypeVar("T")  # generic type placeholder

def paginate(stmt,
             session: Session,
             page: int,
             page_size: int,
             mapper: Callable[[dict], T]
             ) -> Tuple[int, List[T]]:

    if page < 1 or page_size < 1:
        raise ValueError("page and page_size must be positive integers")
    
    offset = (page - 1) * page_size

    subq = stmt.order_by(None).subquery() # we need only COUNT, so ORDER BY is an overhead

    total = session.exec(
        select(func.count()).select_from(subq)
    ).scalar_one()

    logger.info(
        "Pagination",
        extra={"page": page, "page_size": page_size, "total": total}
    )

    if total == 0 or offset >= total:
        return total, []

    rows = session.exec(
        stmt.offset(offset).limit(page_size)
    ).mappings().all()

    items = [
        mapper(**row) if isinstance(mapper, type)
        else mapper(row)
        for row in rows
    ]

    return total, items