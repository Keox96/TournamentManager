# tests/unit/test_sort_request.py

"""
Test module for test sort request.
"""

import pytest

from src.api.v1.tournaments.tournaments_schema import TournamentSortRequest
from src.domain.entities.tournaments import TournamentSortField
from src.domain.exceptions.error_codes import GenericErrorCodes
from src.domain.exceptions.generic_exceptions import InvalidSortFormatError
from src.domain.repositories.filters import SortOrder


class TestTournamentSortRequest:
    """
    Schema representing a test tournament sort request payload.
    """

    def test_valid_single_sort(self) -> None:
        """
        Execute test valid single sort.
        """
        request = TournamentSortRequest(sort=["name:asc"])
        result = request.to_domain()
        assert result.sorts is not None
        assert len(result.sorts) == 1
        assert result.sorts[0].field == TournamentSortField.NAME
        assert result.sorts[0].order == SortOrder.ASC

    def test_valid_multiple_sorts(self) -> None:
        """
        Execute test valid multiple sorts.
        """
        request = TournamentSortRequest(sort=["name:asc", "created_at:desc"])
        result = request.to_domain()
        assert result.sorts is not None
        assert len(result.sorts) == 2
        assert result.sorts[0].field == TournamentSortField.NAME
        assert result.sorts[0].order == SortOrder.ASC
        assert result.sorts[1].field == TournamentSortField.CREATED_AT
        assert result.sorts[1].order == SortOrder.DESC

    def test_valid_sort_without_order_uses_default(self) -> None:
        """
        Execute test valid sort without order uses default.
        """
        request = TournamentSortRequest(sort=["name"])
        result = request.to_domain()
        assert result.sorts is not None
        assert result.sorts[0].field == TournamentSortField.NAME
        assert result.sorts[0].order == SortOrder.DESC  # ordre par défaut

    def test_invalid_sort_extra_segment(self) -> None:
        """
        Execute test invalid sort extra segment.
        """
        request = TournamentSortRequest(sort=["name:asc:extra"])
        with pytest.raises(InvalidSortFormatError) as exc_info:
            request.to_domain()
        assert exc_info.value.code == GenericErrorCodes.INVALID_SORT_FORMAT

    def test_invalid_sort_order(self) -> None:
        """
        Execute test invalid sort order.
        """
        request = TournamentSortRequest(sort=["name:descg"])
        with pytest.raises(InvalidSortFormatError) as exc_info:
            request.to_domain()
        assert exc_info.value.code == GenericErrorCodes.INVALID_SORT_FORMAT

    def test_invalid_sort_field(self) -> None:
        """
        Execute test invalid sort field.
        """
        request = TournamentSortRequest(sort=["invalid_field:asc"])
        with pytest.raises(InvalidSortFormatError) as exc_info:
            request.to_domain()
        assert exc_info.value.code == GenericErrorCodes.INVALID_SORT_FORMAT

    def test_invalid_sort_field_without_order(self) -> None:
        """
        Execute test invalid sort field without order.
        """
        request = TournamentSortRequest(sort=["invalid_field"])
        with pytest.raises(InvalidSortFormatError) as exc_info:
            request.to_domain()
        assert exc_info.value.code == GenericErrorCodes.INVALID_SORT_FORMAT

    def test_default_sort_when_none(self) -> None:
        """
        Execute test default sort when none.
        """
        request = TournamentSortRequest(sort=None)
        result = request.to_domain()
        assert result.sorts is not None
        assert len(result.sorts) == 1
        assert result.sorts[0].field == TournamentSortField.CREATED_AT
        assert result.sorts[0].order == SortOrder.DESC
