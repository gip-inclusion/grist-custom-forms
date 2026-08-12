"""Department-to-region resolver for FAGERH analytics.

Mapping based on official French INSEE / territorial code conventions:
- metropolitan departments including 2A and 2B for Corse
- overseas departments and regions
"""

from __future__ import annotations

DEPARTMENT_TO_REGION_CODE: dict[str, str] = {
    "01": "84",
    "02": "32",
    "03": "84",
    "04": "93",
    "05": "93",
    "06": "93",
    "07": "84",
    "08": "44",
    "09": "76",
    "10": "44",
    "11": "76",
    "12": "76",
    "13": "93",
    "14": "28",
    "15": "84",
    "16": "75",
    "17": "75",
    "18": "24",
    "19": "75",
    "21": "27",
    "22": "53",
    "23": "75",
    "24": "75",
    "25": "27",
    "26": "84",
    "27": "28",
    "28": "24",
    "29": "53",
    "2A": "94",
    "2B": "94",
    "30": "76",
    "31": "76",
    "32": "76",
    "33": "75",
    "34": "76",
    "35": "53",
    "36": "24",
    "37": "24",
    "38": "84",
    "39": "27",
    "40": "75",
    "41": "24",
    "42": "84",
    "43": "84",
    "44": "52",
    "45": "24",
    "46": "76",
    "47": "75",
    "48": "76",
    "49": "52",
    "50": "28",
    "51": "44",
    "52": "44",
    "53": "52",
    "54": "44",
    "55": "44",
    "56": "53",
    "57": "44",
    "58": "27",
    "59": "32",
    "60": "32",
    "61": "28",
    "62": "32",
    "63": "84",
    "64": "75",
    "65": "76",
    "66": "76",
    "67": "44",
    "68": "44",
    "69": "84",
    "70": "27",
    "71": "27",
    "72": "52",
    "73": "84",
    "74": "84",
    "75": "11",
    "76": "28",
    "77": "11",
    "78": "11",
    "79": "75",
    "80": "32",
    "81": "76",
    "82": "76",
    "83": "93",
    "84": "93",
    "85": "52",
    "86": "75",
    "87": "75",
    "88": "44",
    "89": "27",
    "90": "27",
    "91": "11",
    "92": "11",
    "93": "11",
    "94": "11",
    "95": "11",
    "971": "01",
    "972": "02",
    "973": "03",
    "974": "04",
    "976": "06",
}

REGION_CODE_LABELS: dict[str, str] = {
    "01": "Guadeloupe",
    "02": "Martinique",
    "03": "Guyane",
    "04": "La Réunion",
    "06": "Mayotte",
    "11": "Île-de-France",
    "24": "Centre-Val de Loire",
    "27": "Bourgogne-Franche-Comté",
    "28": "Normandie",
    "32": "Hauts-de-France",
    "44": "Grand Est",
    "52": "Pays de la Loire",
    "53": "Bretagne",
    "75": "Nouvelle-Aquitaine",
    "76": "Occitanie",
    "84": "Auvergne-Rhône-Alpes",
    "93": "Provence-Alpes-Côte d'Azur",
    "94": "Corse",
}


def normalize_department_code(value: object) -> str | None:
    """Normalize a department code while preserving leading zeroes and Corsica codes."""

    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        normalized = str(value)
    elif isinstance(value, float):
        if not value.is_integer():
            return None
        normalized = str(int(value))
    else:
        normalized = str(value)
    normalized = normalized.replace(" ", "").strip().upper()
    if normalized.isdigit():
        if len(normalized) == 1:
            normalized = normalized.zfill(2)
        elif len(normalized) not in {2, 3}:
            return None
    return normalized or None


def resolve_region_code(department_code: str | None) -> str | None:
    """Resolve a French region code from a normalized department code."""

    normalized = normalize_department_code(department_code)
    if normalized is None:
        return None
    return DEPARTMENT_TO_REGION_CODE.get(normalized)


def get_region_label(region_code: str | None) -> str:
    normalized = str(region_code or "").strip().upper()
    return REGION_CODE_LABELS.get(normalized, normalized or "Inconnue")
