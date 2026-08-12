"""Minimal Grist schema validation for the FAGERH analytics module."""

from __future__ import annotations

from dataclasses import dataclass


class IndicatorUnavailableError(RuntimeError):
    """Raised when an indicator cannot be computed from the current schema."""


@dataclass(frozen=True)
class CapabilityDefinition:
    """Declarative schema capability definition."""

    name: str
    required_columns: tuple[str, ...] = ()
    alternative_column_groups: tuple[tuple[str, ...], ...] = ()
    indicator_ids: tuple[str, ...] = ()
    mandatory: bool = False


@dataclass(frozen=True)
class SchemaValidationResult:
    """Structured schema validation outcome."""

    is_compatible: bool
    core_status: str
    available_capabilities: tuple[str, ...]
    unavailable_capabilities: tuple[str, ...]
    missing_required_columns: tuple[str, ...]
    missing_optional_columns: tuple[str, ...]
    warnings: tuple[str, ...]


CAPABILITIES: tuple[CapabilityDefinition, ...] = (
    CapabilityDefinition(
        name="core",
        required_columns=("uuid", "finess_main"),
        indicator_ids=tuple(),
        mandatory=True,
    ),
    CapabilityDefinition(
        name="campaign",
        alternative_column_groups=(("campaign_year", "annee", "campagne"),),
        indicator_ids=tuple(),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="geography",
        alternative_column_groups=(
            ("department_code", "es_departement", "departement"),
        ),
        indicator_ids=tuple(),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="devices",
        required_columns=("check_esrp", "check_espo", "check_ueros", "check_deac"),
        indicator_ids=("questionnaires.count",),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="dui",
        required_columns=("q38_dui",),
        indicator_ids=("profile.dui.yes.count", "profile.dui.no.count"),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="remuneration",
        required_columns=("q40_remuneration", "q40_operateur"),
        indicator_ids=(
            "profile.remuneration.docaposte.count",
            "profile.remuneration.asp.count",
            "profile.remuneration.other.count",
            "profile.remuneration.none.count",
            "profile.remuneration.unknown.count",
        ),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="annual_volumes_esrp",
        required_columns=("q53_accompagnes__esrp",),
        indicator_ids=("people.received.esrp",),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="annual_volumes_espo",
        required_columns=("q53_accompagnes__espo",),
        indicator_ids=("people.received.espo",),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="annual_volumes_ueros",
        required_columns=("q53_accompagnes__ueros",),
        indicator_ids=("people.received.ueros",),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="annual_volumes_deac",
        required_columns=("q53_accompagnes__deac",),
        indicator_ids=("people.received.deac",),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="evaluation_activities",
        required_columns=("prestations_json", "prestations_details_json"),
        indicator_ids=("people.received.pec", "people.received.other_eval"),
        mandatory=False,
    ),
    CapabilityDefinition(
        name="mdph_activities",
        required_columns=("prestations_json",),
        indicator_ids=(
            "institution.mdph.epe.count",
            "institution.mdph.cdaph.count",
            "institution.mdph.working_groups.count",
        ),
        mandatory=False,
    ),
)


def validate_schema_columns(column_ids: set[str]) -> SchemaValidationResult:
    """Validate a Grist table column set against the current analytics MVP contract."""

    available_capabilities: list[str] = []
    unavailable_capabilities: list[str] = []
    missing_required: set[str] = set()
    missing_optional: set[str] = set()
    warnings: list[str] = []

    for capability in CAPABILITIES:
        missing = _missing_columns_for_capability(column_ids, capability)
        if missing:
            unavailable_capabilities.append(capability.name)
            if capability.mandatory:
                missing_required.update(missing)
            else:
                missing_optional.update(missing)
                warnings.append(f"Capability {capability.name} is unavailable.")
        else:
            available_capabilities.append(capability.name)

    return SchemaValidationResult(
        is_compatible=not missing_required,
        core_status="ok" if not missing_required else "error",
        available_capabilities=tuple(sorted(available_capabilities)),
        unavailable_capabilities=tuple(sorted(unavailable_capabilities)),
        missing_required_columns=tuple(sorted(missing_required)),
        missing_optional_columns=tuple(sorted(missing_optional)),
        warnings=tuple(warnings),
    )


def assume_schema_compatible() -> SchemaValidationResult:
    """Return a fully compatible schema result for repositories without schema metadata."""

    return SchemaValidationResult(
        is_compatible=True,
        core_status="ok",
        available_capabilities=tuple(sorted(capability.name for capability in CAPABILITIES)),
        unavailable_capabilities=(),
        missing_required_columns=(),
        missing_optional_columns=(),
        warnings=(),
    )


def is_indicator_available(indicator_id: str, schema: SchemaValidationResult) -> bool:
    """Return whether an indicator can be computed from the validated schema."""

    if not schema.is_compatible:
        return False
    from .catalog import get_indicator_required_capabilities

    required_capabilities = get_indicator_required_capabilities(indicator_id)
    return all(capability in schema.available_capabilities for capability in required_capabilities)


def ensure_indicator_schema_available(indicator_id: str, schema: SchemaValidationResult) -> None:
    """Raise when an indicator is unavailable because of the current schema."""

    if is_indicator_available(indicator_id, schema):
        return
    raise IndicatorUnavailableError(
        f"Indicator {indicator_id} is unavailable because the configured FAGERH Grist schema is incomplete."
    )
def _missing_columns_for_capability(column_ids: set[str], capability: CapabilityDefinition) -> set[str]:
    missing = {column for column in capability.required_columns if column not in column_ids}
    for group in capability.alternative_column_groups:
        if not any(candidate in column_ids for candidate in group):
            missing.add(group[0])
    return missing
