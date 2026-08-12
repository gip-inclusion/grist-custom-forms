"""Repository contracts used by the current analytics engine."""

from __future__ import annotations

from abc import ABC, abstractmethod

from fagerh_analytics.domain import RawQuestionnaireRecord
from fagerh_analytics.schema import SchemaValidationResult, assume_schema_compatible


class RepositoryError(RuntimeError):
    """Base class for controlled repository failures."""


class RepositoryConfigurationError(RepositoryError):
    """Raised when the analytics data source is not configured correctly."""


class RepositoryConnectionError(RepositoryError):
    """Raised when the analytics data source cannot be reached."""


class RepositoryResponseError(RepositoryError):
    """Raised when the analytics data source returns an invalid response."""


class QuestionnaireRepository(ABC):
    """Minimal questionnaire repository contract for the current analytics phase."""

    repository_name = "unknown"

    @abstractmethod
    def list_raw_questionnaires(self) -> list[RawQuestionnaireRecord]:
        """Return raw questionnaire rows normalized for the analytics engine."""

    def get_freshness_at(self) -> str | None:
        """Return source freshness when the repository can prove it."""

        return None

    def check_connection(self) -> None:
        """Perform a light read-only probe when supported by the repository."""

        return None

    def validate_schema(self) -> SchemaValidationResult:
        """Return the minimal schema compatibility for this repository."""

        return assume_schema_compatible()

    def list_available_campaign_years(self) -> tuple[int, ...]:
        """Return campaign years visible through the repository."""

        campaigns = sorted({
            record.campaign_year
            for record in self.list_raw_questionnaires()
            if isinstance(record.campaign_year, int) and record.campaign_year > 0
        })
        return tuple(campaigns)
