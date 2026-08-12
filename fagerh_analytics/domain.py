"""Public domain contracts for the FAGERH analytics MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RawQuestionnaireRecord:
    """Minimal raw questionnaire row as stored by the FAGERH form."""

    uuid: str | None
    campaign_year: int | None = None
    region_code: str | None = None
    department_code: str | None = None
    finess_main: str | None = None
    completion_status: str | None = None
    dispositif_hint: str | None = None
    check_esrp: object | None = None
    check_espo: object | None = None
    check_ueros: object | None = None
    check_deac: object | None = None
    q38_dui: str | None = None
    q40_remuneration: str | None = None
    q40_operateur: str | None = None
    q53_accompagnes__esrp: object | None = None
    q53_accompagnes__espo: object | None = None
    q53_accompagnes__ueros: object | None = None
    q53_accompagnes__deac: object | None = None
    prestations_json: dict[str, Any] = field(default_factory=dict)
    prestations_details_json: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QuestionnaireRecord:
    """Analytical row projected from a raw questionnaire for a single dispositif."""

    uuid: str | None
    campaign_year: int | None = None
    region_code: str | None = None
    department_code: str | None = None
    finess_main: str | None = None
    completion_status: str | None = None
    dispositif: str | None = None
    q38_dui: str | None = None
    q40_remuneration: str | None = None
    q40_operateur: str | None = None
    q53_accompagnes__esrp: object | None = None
    q53_accompagnes__espo: object | None = None
    q53_accompagnes__ueros: object | None = None
    q53_accompagnes__deac: object | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationActivityRecord:
    """Analytical row projected from a raw questionnaire for evaluation volumes."""

    uuid: str | None
    campaign_year: int | None = None
    region_code: str | None = None
    department_code: str | None = None
    finess_main: str | None = None
    completion_status: str | None = None
    evaluation_type: str | None = None
    evaluation_detail: str | None = None
    orientation_cdaph: str | None = None
    declared_volume: object | None = None
    source_block_id: str | None = None
    source_block_name: str | None = None
    source_path: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IndicatorDefinition:
    """Canonical indicator definition stored in the catalog."""

    id: str
    label: str
    definition: str
    unit: str
    grain: str
    dataset_id: str
    confidence_level: str
    required_capabilities: tuple[str, ...] = ()
    source_fields: tuple[str, ...] = ()
    source_paths: tuple[str, ...] = ()
    component_indicators: tuple[str, ...] = ()
    aggregation_rule: str = ""
    provenance: str = ""
    double_counting_policy: str = ""
    visibility: str = "internal"
    business_warnings: tuple[str, ...] = ()
    compatible_filters: tuple[str, ...] = ()
    exportable: bool = True


@dataclass(frozen=True)
class ResolvedFilters:
    """Validated analytical filters independent from delivery layers."""

    requested: dict[str, object] = field(default_factory=dict)
    applied: dict[str, object] = field(default_factory=dict)
    rejected: dict[str, str] = field(default_factory=dict)
    scope_constraints: dict[str, object] = field(default_factory=dict)
    user_role: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class UserContext:
    """Minimal analytical user context independent from delivery layers."""

    user_id: str | None
    role: str
    region_codes: tuple[str, ...] = ()
    department_codes: tuple[str, ...] = ()
    finess_values: tuple[str, ...] = ()
    allowed_dispositifs: tuple[str, ...] = ()
    can_export: bool = False


@dataclass(frozen=True)
class PermissionScope:
    """Resolved analytical permission scope for a user."""

    is_global: bool
    region_codes: tuple[str, ...] = ()
    department_codes: tuple[str, ...] = ()
    finess_values: tuple[str, ...] = ()
    allowed_dispositifs: tuple[str, ...] = ()
    can_export: bool = False
    role: str = ""


@dataclass(frozen=True)
class IndicatorResult:
    """Normalized indicator payload returned by the engine."""

    indicator_id: str
    label: str
    value: int
    unit: str
    privacy_status: str
    confidence_level: str
    source: dict[str, str]
    breakdown: dict[str, int] = field(default_factory=dict)
    resolved_filters: ResolvedFilters = field(default_factory=ResolvedFilters)
    user_role: str | None = None
    permission_scope: PermissionScope | None = None


@dataclass(frozen=True)
class EstablishmentServiceKey:
    """Business key for analytics aggregated by campaign, FINESS, and dispositif."""

    campaign_year: int | None
    finess_main: str
    dispositif: str


@dataclass(frozen=True)
class EvaluationActivityKey:
    """Business key for evaluation activity rows."""

    campaign_year: int | None
    finess_main: str
    evaluation_type: str
    orientation_cdaph: str
    source_block_id: str
