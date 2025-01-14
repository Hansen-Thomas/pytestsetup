from dataclasses import dataclass
import math
from typing import Self


@dataclass
class PaginationResult:
    """
    This class is used to store the result of a paginated query.
    """

    records: list
    count_records: int
    page_size: int
    count_pages: int
    current_page: int
    has_next_page: bool
    has_previous_page: bool

    @classmethod
    def build(
        cls,
        records: list,
        count_records: int,
        page_size: int,
        current_page: int,
    ) -> Self:
        count_pages = math.ceil(count_records / page_size)
        has_next_page = current_page < count_pages
        has_previous_page = current_page > 1

        return cls(
            records=records,
            count_records=count_records,
            page_size=page_size,
            count_pages=count_pages,
            current_page=current_page,
            has_next_page=has_next_page,
            has_previous_page=has_previous_page,
        )
