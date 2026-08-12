"""Minimal analytics engine for the FAGERH phase 1 MVP."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re
import unicodedata

from .catalog import get_indicator_definition
from .domain import (
    EstablishmentServiceKey,
    EvaluationActivityKey,
    IndicatorResult,
    PermissionScope,
    QuestionnaireRecord,
    RawQuestionnaireRecord,
    ResolvedFilters,
    UserContext,
)
from .evaluation_projection import project_evaluation_activities
from .filters import build_filter_context, record_matches_evaluation, record_matches_questionnaire, record_matches_raw, resolve_filters
from .permissions import ensure_indicator_scope_allowed, get_scope
from .prestations import DEVICE_VOLUME_DEFINITIONS, project_received_people_records
from .repositories.base import QuestionnaireRepository


class UnknownIndicatorError(ValueError):
    """Raised when an indicator is not registered in the catalog."""


class DataConsistencyError(ValueError):
    """Raised when two rows disagree on the same business key."""


class DataQualityError(ValueError):
    """Raised when a single row is internally incoherent."""


class AnalyticsEngine:
    """Compute analytics indicators without any Flask or Grist dependency."""

    def __init__(self, repository: QuestionnaireRepository) -> None:
        self._repository = repository

    def compute_indicator(
        self,
        indicator_id: str,
        filters: dict[str, object] | None = None,
        user_context: UserContext | None = None,
    ) -> IndicatorResult:
        """Compute a registered indicator."""

        definition = get_indicator_definition(indicator_id)
        if definition is None:
            raise UnknownIndicatorError(f"Unknown indicator: {indicator_id}")
        raw_records = tuple(self._repository.list_raw_questionnaires())
        permission_scope = get_scope(user_context)
        ensure_indicator_scope_allowed(indicator_id, permission_scope, definition.compatible_filters)
        resolved_filters = resolve_filters(
            filters,
            compatible_filters=definition.compatible_filters,
            indicator_id=indicator_id,
            context=build_filter_context(raw_records),
            permission_scope=permission_scope,
        )

        if indicator_id == "people.received.all":
            return self._compute_people_received_all(definition, resolved_filters, user_context)

        if indicator_id == "questionnaires.count":
            value = self._count_distinct_questionnaires(raw_records, resolved_filters)
            return IndicatorResult(
                indicator_id=definition.id,
                label=definition.label,
                value=value,
                unit=definition.unit,
                privacy_status="visible",
                confidence_level=definition.confidence_level,
                source={
                    "dataset": definition.dataset_id,
                    "repository": self._repository.repository_name,
                },
                breakdown={},
                resolved_filters=resolved_filters,
                user_role=permission_scope.role,
                permission_scope=permission_scope,
            )

        if indicator_id in {"profile.dui.yes.count", "profile.dui.no.count"}:
            value = self._count_dui_responses(
                raw_records,
                resolved_filters,
                expected_value="Oui" if indicator_id.endswith(".yes.count") else "Non",
            )
            return IndicatorResult(
                indicator_id=definition.id,
                label=definition.label,
                value=value,
                unit=definition.unit,
                privacy_status="visible",
                confidence_level=definition.confidence_level,
                source={
                    "dataset": definition.dataset_id,
                    "repository": self._repository.repository_name,
                    "field": "q38_dui",
                },
                breakdown={},
                resolved_filters=resolved_filters,
                user_role=permission_scope.role,
                permission_scope=permission_scope,
            )

        remuneration_category_by_indicator = {
            "profile.remuneration.docaposte.count": "docaposte",
            "profile.remuneration.asp.count": "asp",
            "profile.remuneration.other.count": "other",
            "profile.remuneration.none.count": "none",
            "profile.remuneration.unknown.count": "unknown",
        }
        if indicator_id in remuneration_category_by_indicator:
            category = remuneration_category_by_indicator[indicator_id]
            value = self._count_remuneration_responses(raw_records, resolved_filters, expected_category=category)
            return IndicatorResult(
                indicator_id=definition.id,
                label=definition.label,
                value=value,
                unit=definition.unit,
                privacy_status="visible",
                confidence_level=definition.confidence_level,
                source={
                    "dataset": definition.dataset_id,
                    "repository": self._repository.repository_name,
                    "fields": "q40_remuneration,q40_operateur",
                    "business_key": "campaign_year+finess_main+dispositif",
                    "category": category,
                },
                breakdown={},
                resolved_filters=resolved_filters,
                user_role=permission_scope.role,
                permission_scope=permission_scope,
            )

        mdph_block_by_indicator = {
            "institution.mdph.epe.count": "epe",
            "institution.mdph.cdaph.count": "cdaph",
            "institution.mdph.working_groups.count": "groupes_travail",
        }
        if indicator_id in mdph_block_by_indicator:
            block_key = mdph_block_by_indicator[indicator_id]
            value = self._count_mdph_participations(raw_records, resolved_filters, block_key=block_key)
            return IndicatorResult(
                indicator_id=definition.id,
                label=definition.label,
                value=value,
                unit=definition.unit,
                privacy_status="visible",
                confidence_level=definition.confidence_level,
                source={
                    "dataset": definition.dataset_id,
                    "repository": self._repository.repository_name,
                    "field": "prestations_json",
                    "block": block_key,
                    "subfields": "origine,limitrophes",
                    "business_key": "campaign_year+finess_main+dispositif",
                },
                breakdown={},
                resolved_filters=resolved_filters,
                user_role=permission_scope.role,
                permission_scope=permission_scope,
            )

        received_people_indicator_config = {
            "people.received.esrp": {
                "field_name": "q53_accompagnes__esrp",
                "device_definition": DEVICE_VOLUME_DEFINITIONS[0],
                "source_type": "prestations_json_with_flat_fallback",
            },
            "people.received.espo": {
                "field_name": "q53_accompagnes__espo",
                "device_definition": DEVICE_VOLUME_DEFINITIONS[1],
                "source_type": "prestations_json_with_flat_fallback",
            },
            "people.received.ueros": {
                "field_name": "q53_accompagnes__ueros",
                "device_definition": DEVICE_VOLUME_DEFINITIONS[2],
                "source_type": "prestations_json_with_flat_fallback",
            },
            "people.received.deac": {
                "field_name": "q53_accompagnes__deac",
                "device_definition": None,
                "source_type": "flat_annual_field",
            },
        }
        if indicator_id in received_people_indicator_config:
            config = received_people_indicator_config[indicator_id]
            field_name = config["field_name"]
            if config["device_definition"] is None:
                value = self._count_flat_annual_people_received(raw_records, resolved_filters, field_name=field_name)
                source = {
                    "dataset": definition.dataset_id,
                    "repository": self._repository.repository_name,
                    "field": field_name,
                    "business_key": "campaign_year+finess_main+dispositif",
                    "source_type": config["source_type"],
                }
            else:
                value = self._count_device_people_received(
                    raw_records,
                    resolved_filters,
                    definition_id=indicator_id,
                )
                source = {
                    "dataset": definition.dataset_id,
                    "repository": self._repository.repository_name,
                    "field": field_name,
                    "fallback_field": field_name,
                    "business_key": "campaign_year+finess_main+dispositif",
                    "source_type": config["source_type"],
                    "prestations_paths": "prestations_json.<conditional_id>.fileActive",
                    "conditional_defs_path": "prestations_details_json.__wizard_v3_state.runtime.conditionalDefs",
                }
            return IndicatorResult(
                indicator_id=definition.id,
                label=definition.label,
                value=value,
                unit=definition.unit,
                privacy_status="visible",
                confidence_level=definition.confidence_level,
                source=source,
                breakdown={},
                resolved_filters=resolved_filters,
                user_role=permission_scope.role,
                permission_scope=permission_scope,
            )

        evaluation_type_by_indicator = {
            "people.received.pec": ("pec", None),
            "people.received.other_eval.professional_assessment": ("other_eval", "professional_assessment"),
            "people.received.other_eval.without_orp_cdaph": ("other_eval", "without_orp_cdaph"),
            "people.received.other_eval.with_orp_cdaph": ("other_eval", "with_orp_cdaph"),
        }
        if indicator_id in evaluation_type_by_indicator:
            evaluation_type, evaluation_detail = evaluation_type_by_indicator[indicator_id]
            value = self._count_evaluation_people_received(
                raw_records,
                resolved_filters,
                evaluation_type=evaluation_type,
                evaluation_detail=evaluation_detail,
            )
            return IndicatorResult(
                indicator_id=definition.id,
                label=definition.label,
                value=value,
                unit=definition.unit,
                privacy_status="visible",
                confidence_level=definition.confidence_level,
                source={
                    "dataset": definition.dataset_id,
                    "repository": self._repository.repository_name,
                    "field": "prestations_json",
                    "block_categories": evaluation_type,
                    "orientation_variants": "avec_orp_cdaph,sans_orp_cdaph",
                    "grain": "campaign_year+finess_main+evaluation_type+orientation_cdaph+source_block_id",
                    "business_key": "campaign_year+finess_main+evaluation_type+orientation_cdaph+source_block_id",
                    "source_type": "prestations_json",
                    "paths": ";".join(definition.source_paths),
                    **({"evaluation_detail": evaluation_detail} if evaluation_detail is not None else {}),
                },
                breakdown={},
                resolved_filters=resolved_filters,
                user_role=permission_scope.role,
                permission_scope=permission_scope,
            )

        if indicator_id == "people.received.other_eval":
            return self._compute_people_received_other_eval(definition, resolved_filters, user_context)

        if indicator_id != "questionnaires.count":
            raise UnknownIndicatorError(f"Indicator not implemented in phase 1: {indicator_id}")

        raise UnknownIndicatorError(f"Indicator not implemented: {indicator_id}")

    def _count_distinct_questionnaires(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
    ) -> int:
        uuids = {
            normalized_uuid
            for record in raw_records
            if record_matches_raw(record, resolved_filters)
            if (normalized_uuid := _normalize_uuid(record.uuid)) is not None
        }
        return len(uuids)

    def _count_dui_responses(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
        expected_value: str,
    ) -> int:
        grouped_values: dict[EstablishmentServiceKey, str] = {}
        for record in self._iter_projected_questionnaires(raw_records, resolved_filters):
            business_key = _build_establishment_service_key(record)
            normalized_dui = _normalize_dui_value(record.q38_dui)
            if business_key is None or normalized_dui is None:
                continue
            previous_value = grouped_values.get(business_key)
            if previous_value is None:
                grouped_values[business_key] = normalized_dui
                continue
            if previous_value != normalized_dui:
                raise DataConsistencyError(
                    "Contradictory q38_dui values for business key "
                    f"{business_key.campaign_year}/{business_key.finess_main}/{business_key.dispositif}: "
                    f"{previous_value} vs {normalized_dui}"
                )
        return sum(1 for value in grouped_values.values() if value == expected_value)

    def _count_remuneration_responses(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
        expected_category: str,
    ) -> int:
        grouped_categories: dict[EstablishmentServiceKey, str] = {}
        for record in self._iter_projected_questionnaires(raw_records, resolved_filters):
            business_key = _build_establishment_service_key(record)
            if business_key is None:
                continue
            category = _normalize_remuneration_category(record.q40_remuneration, record.q40_operateur)
            previous_category = grouped_categories.get(business_key)
            if previous_category is None:
                grouped_categories[business_key] = category
                continue
            if previous_category != category:
                raise DataConsistencyError(
                    "Contradictory remuneration values for business key "
                    f"{business_key.campaign_year}/{business_key.finess_main}/{business_key.dispositif}: "
                    f"{previous_category} vs {category}"
                )
        return sum(1 for category in grouped_categories.values() if category == expected_category)

    def _count_mdph_participations(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
        block_key: str,
    ) -> int:
        grouped_values: dict[EstablishmentServiceKey, tuple[int, int]] = {}
        total = 0
        for record in raw_records:
            if not record_matches_raw(record, resolved_filters):
                continue
            business_key = _build_raw_questionnaire_key(record)
            if business_key is None:
                continue
            block_values = _extract_mdph_participation_values(record, block_key)
            previous_values = grouped_values.get(business_key)
            if previous_values is None:
                grouped_values[business_key] = block_values
                total += block_values[0] + block_values[1]
                continue
            if previous_values != block_values:
                raise DataConsistencyError(
                    "Contradictory MDPH participation values for business key "
                    f"{business_key.campaign_year}/{business_key.finess_main}/{business_key.dispositif} "
                    f"and block {block_key}: {previous_values} vs {block_values}"
                )
        return total

    def _count_flat_annual_people_received(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
        field_name: str,
    ) -> int:
        grouped_values: dict[EstablishmentServiceKey, int] = {}
        total = 0
        for record in self._iter_projected_questionnaires(raw_records, resolved_filters):
            business_key = _build_establishment_service_key(record)
            if business_key is None:
                continue
            value = _normalize_non_negative_integer(getattr(record, field_name), field_name=field_name)
            previous_value = grouped_values.get(business_key)
            if previous_value is None:
                grouped_values[business_key] = value
                total += value
                continue
            if previous_value != value:
                raise DataConsistencyError(
                    "Contradictory annual people received values for business key "
                    f"{business_key.campaign_year}/{business_key.finess_main}/{business_key.dispositif} "
                    f"and field {field_name}: {previous_value} vs {value}"
                )
        return total

    def _iter_projected_questionnaires(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
    ) -> tuple[QuestionnaireRecord, ...]:
        projected: list[QuestionnaireRecord] = []
        for raw_record in raw_records:
            if not record_matches_raw(raw_record, resolved_filters):
                continue
            for projected_record in project_questionnaire(raw_record):
                if record_matches_questionnaire(projected_record, resolved_filters):
                    projected.append(projected_record)
        return tuple(projected)

    def _iter_projected_received_people_records(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
    ) -> tuple[QuestionnaireRecord, ...]:
        projected: list[QuestionnaireRecord] = []
        for raw_record in raw_records:
            if not record_matches_raw(raw_record, resolved_filters):
                continue
            for projected_record in project_received_people_records(
                raw_record,
                normalize_integer=_normalize_non_negative_integer,
                quality_error_cls=DataQualityError,
            ):
                if record_matches_questionnaire(projected_record, resolved_filters):
                    projected.append(projected_record)
        return tuple(projected)

    def _iter_projected_evaluation_activities(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
    ) -> tuple:
        projected = []
        for raw_record in raw_records:
            if not record_matches_raw(raw_record, resolved_filters):
                continue
            for projected_record in project_evaluation_activities(
                raw_record,
                normalize_integer=_normalize_non_negative_integer,
                quality_error_cls=DataQualityError,
            ):
                if record_matches_evaluation(projected_record, resolved_filters):
                    projected.append(projected_record)
        return tuple(projected)

    def _count_evaluation_people_received(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
        evaluation_type: str,
        evaluation_detail: str | None = None,
    ) -> int:
        grouped_values: dict[EvaluationActivityKey, int] = {}
        total = 0
        for record in self._iter_projected_evaluation_activities(raw_records, resolved_filters):
            business_key = _build_evaluation_activity_key(record)
            if business_key is None or business_key.evaluation_type != evaluation_type:
                continue
            if evaluation_detail is not None and record.evaluation_detail != evaluation_detail:
                continue
            value = _normalize_non_negative_integer(record.declared_volume, field_name=record.source_path or "declared_volume")
            previous_value = grouped_values.get(business_key)
            if previous_value is None:
                grouped_values[business_key] = value
                total += value
                continue
            if previous_value != value:
                raise DataConsistencyError(
                    "Contradictory evaluation activity values for business key "
                    f"{business_key.campaign_year}/{business_key.finess_main}/{business_key.evaluation_type}/"
                    f"{business_key.orientation_cdaph}/{business_key.source_block_id}: "
                    f"{previous_value} vs {value}"
                )
        return total

    def _count_device_people_received(
        self,
        raw_records: tuple[RawQuestionnaireRecord, ...],
        resolved_filters: ResolvedFilters,
        *,
        definition_id: str,
    ) -> int:
        definition_by_indicator = {
            "people.received.esrp": ("q53_accompagnes__esrp", "esrp"),
            "people.received.espo": ("q53_accompagnes__espo", "espo"),
            "people.received.ueros": ("q53_accompagnes__ueros", "ueros"),
        }
        field_name, dispositif = definition_by_indicator[definition_id]
        grouped_values: dict[EstablishmentServiceKey, int] = {}
        total = 0
        for record in self._iter_projected_received_people_records(raw_records, resolved_filters):
            business_key = _build_establishment_service_key(record)
            if business_key is None or business_key.dispositif != dispositif:
                continue
            value = _normalize_non_negative_integer(getattr(record, field_name), field_name=field_name)
            previous_value = grouped_values.get(business_key)
            if previous_value is None:
                grouped_values[business_key] = value
                total += value
                continue
            if previous_value != value:
                raise DataConsistencyError(
                    "Contradictory annual people received values for business key "
                    f"{business_key.campaign_year}/{business_key.finess_main}/{business_key.dispositif} "
                    f"and field {field_name}: {previous_value} vs {value}"
                )
        return total

    def _compute_people_received_all(
        self,
        definition,
        resolved_filters: ResolvedFilters,
        user_context: UserContext | None,
    ) -> IndicatorResult:
        component_ids = (
            "people.received.esrp",
            "people.received.espo",
            "people.received.ueros",
            "people.received.pec",
            "people.received.other_eval",
        )
        component_results = [
            self.compute_indicator(component_id, filters=resolved_filters.applied, user_context=user_context)
            for component_id in component_ids
        ]
        permission_scope = get_scope(user_context)
        breakdown = {
            "esrp": component_results[0].value,
            "espo": component_results[1].value,
            "ueros": component_results[2].value,
            "pec": component_results[3].value,
            "other_eval": component_results[4].value,
        }
        total = sum(breakdown.values())
        return IndicatorResult(
            indicator_id=definition.id,
            label=definition.label,
            value=total,
            unit=definition.unit,
            privacy_status="visible",
            confidence_level=definition.confidence_level,
            source={
                "dataset": definition.dataset_id,
                "repository": self._repository.repository_name,
                "formula": definition.aggregation_rule,
                "components": ",".join(component_ids),
                "grains": "campaign_year+finess_main+dispositif;campaign_year+finess_main+evaluation_type+orientation_cdaph+source_block_id",
                "flat_fields": "q53_accompagnes__esrp,q53_accompagnes__espo,q53_accompagnes__ueros",
                "prestations_paths": (
                    "prestations_json.<conditional_id>.fileActive;"
                    "prestations_json.<conditional_id>.directSansOrp.rows.pec.beneficiaires"
                ),
                "deduplication": "none across categories",
                "deac": "excluded from total",
                "source_type": "composed_indicator",
                "scope_role": permission_scope.role,
                "scope_dispositifs": ",".join(permission_scope.allowed_dispositifs),
            },
            breakdown=breakdown,
            resolved_filters=resolved_filters,
            user_role=permission_scope.role,
            permission_scope=permission_scope,
        )

    def _compute_people_received_other_eval(
        self,
        definition,
        resolved_filters: ResolvedFilters,
        user_context: UserContext | None,
    ) -> IndicatorResult:
        component_ids = (
            "people.received.other_eval.professional_assessment",
            "people.received.other_eval.without_orp_cdaph",
            "people.received.other_eval.with_orp_cdaph",
        )
        component_results = [
            self.compute_indicator(component_id, filters=resolved_filters.applied, user_context=user_context)
            for component_id in component_ids
        ]
        permission_scope = get_scope(user_context)
        breakdown = {
            "professional_assessment": component_results[0].value,
            "without_orp_cdaph": component_results[1].value,
            "with_orp_cdaph": component_results[2].value,
        }
        total = sum(breakdown.values())
        return IndicatorResult(
            indicator_id=definition.id,
            label=definition.label,
            value=total,
            unit=definition.unit,
            privacy_status="visible",
            confidence_level=definition.confidence_level,
            source={
                "dataset": definition.dataset_id,
                "repository": self._repository.repository_name,
                "formula": definition.aggregation_rule,
                "components": ",".join(component_ids),
                "source_type": "composed_indicator",
            },
            breakdown=breakdown,
            resolved_filters=resolved_filters,
            user_role=permission_scope.role,
            permission_scope=permission_scope,
        )


def _normalize_uuid(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_dui_value(value: str | None) -> str | None:
    normalized = _normalize_uuid(value)
    if normalized is None:
        return None
    lowered = normalized.lower()
    if lowered == "oui":
        return "Oui"
    if lowered == "non":
        return "Non"
    return None


def _normalize_remuneration_value(value: str | None) -> str | None:
    normalized = _normalize_uuid(value)
    if normalized is None:
        return None
    lowered = normalized.lower()
    if lowered == "oui":
        return "Oui"
    if lowered == "non":
        return "Non"
    return None


def _normalize_operator_name(value: str | None) -> str | None:
    normalized = _normalize_uuid(value)
    if normalized is None:
        return None
    folded = _fold_text(normalized)
    compact = re.sub(r"[^a-z0-9]+", "", folded)
    if "docaposte" in compact:
        return "docaposte"
    if compact == "asp" or compact == "agencedeservicesetdepaiement" or compact == "agencedeserviceetdepaiement":
        return "asp"
    return "other"


def _normalize_remuneration_category(remuneration_value: str | None, operator_value: str | None) -> str:
    remuneration = _normalize_remuneration_value(remuneration_value)
    operator_raw = _normalize_uuid(operator_value)
    if remuneration is None:
        return "unknown"
    if remuneration == "Non":
        if operator_raw is not None:
            raise DataQualityError(
                f"Inconsistent remuneration values: q40_remuneration=Non but q40_operateur is set to {operator_raw}"
            )
        return "none"
    if operator_raw is None:
        return "unknown"
    return _normalize_operator_name(operator_raw) or "unknown"


def _fold_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return without_accents.lower()


def project_questionnaire(raw_record: RawQuestionnaireRecord) -> tuple[QuestionnaireRecord, ...]:
    active_dispositifs = _get_active_dispositifs(raw_record)
    field_by_dispositif = {
        "esrp": "q53_accompagnes__esrp",
        "espo": "q53_accompagnes__espo",
        "ueros": "q53_accompagnes__ueros",
        "deac": "q53_accompagnes__deac",
    }
    if not active_dispositifs:
        for dispositif, field_name in field_by_dispositif.items():
            value = _normalize_non_negative_integer(getattr(raw_record, field_name), field_name=field_name)
            if value > 0:
                raise DataQualityError(
                    f"Questionnaire {raw_record.uuid or '<missing-uuid>'} has no active dispositif but {field_name} is positive"
                )
        return tuple()

    for dispositif, field_name in field_by_dispositif.items():
        value = _normalize_non_negative_integer(getattr(raw_record, field_name), field_name=field_name)
        if dispositif not in active_dispositifs and value > 0:
            if len(active_dispositifs) == 1:
                raise DataQualityError(
                    "Inconsistent annual people received values: logical dispositif "
                    f"{active_dispositifs[0]} cannot carry a positive value in {field_name}"
                )
            raise DataQualityError(
                f"Questionnaire {raw_record.uuid or '<missing-uuid>'} has inactive dispositif {dispositif} but {field_name} is positive"
            )

    projected_rows: list[QuestionnaireRecord] = []
    for dispositif in active_dispositifs:
        projected_rows.append(QuestionnaireRecord(
            uuid=raw_record.uuid,
            campaign_year=raw_record.campaign_year,
            region_code=raw_record.region_code,
            department_code=raw_record.department_code,
            finess_main=raw_record.finess_main,
            completion_status=raw_record.completion_status,
            dispositif=dispositif,
            q38_dui=raw_record.q38_dui,
            q40_remuneration=raw_record.q40_remuneration,
            q40_operateur=raw_record.q40_operateur,
            q53_accompagnes__esrp=getattr(raw_record, "q53_accompagnes__esrp") if dispositif == "esrp" else 0,
            q53_accompagnes__espo=getattr(raw_record, "q53_accompagnes__espo") if dispositif == "espo" else 0,
            q53_accompagnes__ueros=getattr(raw_record, "q53_accompagnes__ueros") if dispositif == "ueros" else 0,
            q53_accompagnes__deac=getattr(raw_record, "q53_accompagnes__deac") if dispositif == "deac" else 0,
            raw=raw_record.raw,
        ))
    return tuple(projected_rows)


def _extract_mdph_participation_values(record: RawQuestionnaireRecord, block_key: str) -> tuple[int, int]:
    origine_total = 0
    limitrophes_total = 0
    prestations = record.prestations_json or {}
    for state in prestations.values():
        rows = (((state or {}).get("indirect") or {}).get("rows") or {})
        block = rows.get(block_key) or {}
        origine_total += _normalize_non_negative_integer(block.get("origine"), field_name=f"{block_key}.origine")
        limitrophes_total += _normalize_non_negative_integer(block.get("limitrophes"), field_name=f"{block_key}.limitrophes")
    return (origine_total, limitrophes_total)


def _normalize_non_negative_integer(value: object, field_name: str) -> int:
    if value is None:
        return 0
    if isinstance(value, bool):
        raise DataQualityError(f"Invalid numeric value for {field_name}: booleans are not accepted")
    if isinstance(value, int):
        if value < 0:
            raise DataQualityError(f"Invalid numeric value for {field_name}: negative values are not accepted")
        return value
    if isinstance(value, float):
        if not value.is_integer():
            raise DataQualityError(f"Invalid numeric value for {field_name}: non-integer decimals are not accepted")
        integer_value = int(value)
        if integer_value < 0:
            raise DataQualityError(f"Invalid numeric value for {field_name}: negative values are not accepted")
        return integer_value
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return 0
        try:
            parsed = Decimal(normalized)
        except InvalidOperation as exc:
            raise DataQualityError(f"Invalid numeric value for {field_name}: {value}") from exc
        if parsed != parsed.to_integral_value():
            raise DataQualityError(f"Invalid numeric value for {field_name}: non-integer decimals are not accepted")
        integer_value = int(parsed)
        if integer_value < 0:
            raise DataQualityError(f"Invalid numeric value for {field_name}: negative values are not accepted")
        return integer_value
    raise DataQualityError(f"Invalid numeric value for {field_name}: unsupported type {type(value).__name__}")


def _normalize_activation_flag(value: object, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, int):
        if value in {0, 1}:
            return bool(value)
        raise DataQualityError(f"Invalid activation flag for {field_name}: {value}")
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"", "0", "false", "faux", "non", "no"}:
            return False
        if normalized in {"1", "true", "vrai", "oui", "yes"}:
            return True
        raise DataQualityError(f"Invalid activation flag for {field_name}: {value}")
    raise DataQualityError(f"Invalid activation flag for {field_name}: unsupported type {type(value).__name__}")


def _get_active_dispositifs(raw_record: RawQuestionnaireRecord) -> tuple[str, ...]:
    flags = {
        "esrp": _normalize_activation_flag(raw_record.check_esrp, "check_esrp"),
        "espo": _normalize_activation_flag(raw_record.check_espo, "check_espo"),
        "ueros": _normalize_activation_flag(raw_record.check_ueros, "check_ueros"),
        "deac": _normalize_activation_flag(raw_record.check_deac, "check_deac"),
    }
    return tuple(dispositif for dispositif, is_active in flags.items() if is_active)


def _build_raw_questionnaire_key(record: RawQuestionnaireRecord) -> EstablishmentServiceKey | None:
    finess_main = _normalize_uuid(record.finess_main)
    if finess_main is None:
        return None
    dispositif_hint = _normalize_uuid(record.dispositif_hint)
    if dispositif_hint is not None:
        key_component = dispositif_hint.lower()
    else:
        active_dispositifs = _get_active_dispositifs(record)
        if len(active_dispositifs) == 1:
            key_component = active_dispositifs[0]
        elif len(active_dispositifs) > 1:
            key_component = f"multi:{','.join(active_dispositifs)}"
        else:
            key_component = "questionnaire"
    return EstablishmentServiceKey(
        campaign_year=record.campaign_year,
        finess_main=finess_main,
        dispositif=key_component,
    )


def _build_establishment_service_key(record: QuestionnaireRecord) -> EstablishmentServiceKey | None:
    finess_main = _normalize_uuid(record.finess_main)
    dispositif = _normalize_uuid(record.dispositif)
    if finess_main is None or dispositif is None:
        return None
    return EstablishmentServiceKey(
        campaign_year=record.campaign_year,
        finess_main=finess_main,
        dispositif=dispositif.lower(),
    )


def _build_evaluation_activity_key(record) -> EvaluationActivityKey | None:
    finess_main = _normalize_uuid(record.finess_main)
    evaluation_type = _normalize_uuid(record.evaluation_type)
    orientation_cdaph = _normalize_uuid(record.orientation_cdaph)
    source_block_id = _normalize_uuid(record.source_block_id)
    if (
        finess_main is None
        or evaluation_type is None
        or orientation_cdaph is None
        or source_block_id is None
    ):
        return None
    return EvaluationActivityKey(
        campaign_year=record.campaign_year,
        finess_main=finess_main,
        evaluation_type=evaluation_type.lower(),
        orientation_cdaph=orientation_cdaph.lower(),
        source_block_id=source_block_id,
    )
