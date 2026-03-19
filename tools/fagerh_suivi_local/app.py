from __future__ import annotations

import csv
import io
import os
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

from flask import Flask, Response, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("FAGERH_SUIVI_DB", BASE_DIR / "data" / "fagerh_suivi.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FAGERH_SUIVI_SECRET", "dev-secret-change-me")

DISPOSITIFS = ["ESRP", "ESPO", "UEROS", "DEAc", "PEC", "Hors ORP"]
PRESTATION_TYPES = [
    "Directe avec ORP CDAPH",
    "Directe sans ORP CDAPH",
    "Indirecte",
]
MODALITES = ["Présentiel", "Hybride", "Distanciel", "Hors les murs", "Sur site", "En ambulatoire"]
HANDICAP_TYPES = [
    "Déficiences intellectuelles",
    "Autisme et autres TED",
    "Troubles psychiques",
    "Troubles langage/apprentissages",
    "Déficiences auditives",
    "Déficiences visuelles",
    "Déficiences motrices",
    "Déficiences métaboliques/nutritionnelles",
    "Cérébro-lésions",
    "Polyhandicap",
    "TCC (comportement/communication)",
    "Diagnostics en cours",
    "Autres types de déficiences",
    "Je ne sais pas",
]
GENRE_OPTIONS = [
    "Femme",
    "Homme",
    "Autre",
    "Je ne sais pas",
]
TRANCHE_AGE_OPTIONS = [
    "Moins de 20 ans",
    "20 à 24 ans",
    "25 à 29 ans",
    "30 à 39 ans",
    "40 à 49 ans",
    "50 ans et plus",
    "Je ne sais pas",
]
NIVEAU_FORMATION_OPTIONS = [
    "Infra niveau 3 (sans qualification)",
    "Niveau 3 (CAP/BEP)",
    "Niveau 4 (Bac)",
    "Niveau 5 (Bac+2)",
    "Niveau 6 (Licence/Bachelor)",
    "Niveau 7 ou plus (Master/Doctorat)",
    "Je ne sais pas",
]
RESSOURCES_ENTREE_OPTIONS = [
    "Salaire",
    "ARE / allocation chômage",
    "RSA",
    "AAH",
    "Indemnités journalières",
    "Aucune ressource",
    "Autres ressources",
    "Je ne sais pas",
]
ZONE_GEOGRAPHIQUE_OPTIONS = [
    "Département d'implantation",
    "Département limitrophe",
    "Autre département",
    "Hors région",
    "Je ne sais pas",
]
ORIGINE_HANDICAP_OPTIONS = [
    "De naissance",
    "Accident de la vie",
    "Accident du travail / maladie professionnelle",
    "Maladie évolutive",
    "Autre",
    "Je ne sais pas",
]
BLOCS_COLLECTIFS = [
    ("info_personnes_collectives", "Informations aux personnes (collectives)"),
    ("info_partenaires_collectives", "Informations à destination des partenaires (collectives)"),
    ("info_organismes_collectives", "Informations à destination des organismes de formation (collectives)"),
]
MDPH_INSTANCES = ["EPE", "CDAPH", "Groupes de travail"]
MDPH_ZONES = ["Département d'origine", "Départements limitrophes"]
MOTIFS_SORTIE = [
    "Départ volontaire",
    "Raison de santé",
    "Réorientation",
    "Raison disciplinaire",
    "Atteinte de l'objectif",
    "Reprise d'emploi",
    "Autres",
    "Je ne sais pas",
]
PRECONISATIONS = [
    "Emploi en milieu ordinaire",
    "Entreprise adaptée",
    "ESAT",
    "Création d'entreprise",
    "Maintien en emploi",
    "Formation droit commun",
    "Formation en alternance",
    "ESPO",
    "UEROS",
    "Service d'accompagnement social",
    "Vie sociale",
    "Soins",
    "Emploi accompagné",
    "Autres",
]
SITUATION_ARRIVEE_OPTIONS = [
    "En emploi secteur privé",
    "En emploi secteur public",
    "Sans emploi depuis moins d'1 an",
    "Sans emploi depuis 1 à 2 ans",
    "Sans emploi depuis 2 ans ou plus",
    "En formation",
    "Je ne sais pas",
]
DEVENIR_12M_OPTIONS = [
    "En emploi",
    "En formation",
    "Sans emploi",
    "Perdu de vue",
    "Je ne sais pas",
]
PARCOURS_TYPES = [
    "Parcours socio-professionnel • Préparation d'un projet professionnel (orientation hors ESPO)",
    "Parcours socio-professionnel • Préparation à accéder à l'emploi (remobilisation, etc.)",
    "Parcours socio-professionnel • Apprentissage/maîtrise de la langue (FLE, alpha...)",
    "Parcours socio-professionnel • Réentraînement au travail",
    "Parcours certifiant • Préparer à accéder à une formation / remise à niveau savoirs de base",
    "Parcours certifiant • Formation professionnalisante (ne débouchant pas sur un diplôme)",
    "Parcours certifiant • Formation certifiante ou diplômante",
    "Parcours certifiant • Formation accompagnée professionnalisante (ne débouchant pas sur un diplôme)",
    "Parcours certifiant • Formation accompagnée certifiante (avec titre pro ou diplôme)",
    "Participation MDPH • EPE / CDAPH / Groupes de travail",
]
FIN_PARCOURS_TYPES = ["Sortie avant terme", "Sortie à terme", "Réorientation", "Interruption", "Autre"]
SUSPENSION_MOTIFS = [
    "Raisons de santé non liée au handicap",
    "Évolution du handicap",
    "Évolution de la situation sociale/familiale",
    "Parcours contractualisé incluant des périodes de suspension",
    "Autre",
]

ANNUAL_FIELDS = [
    # Cohérence et volumes
    ("file_active_3112", "Nombre de personnes accompagnées au 31/12"),
    ("sorties_definitives", "Nombre de sorties définitives dans l'année"),
    ("journees_realisees", "Nombre de journées réalisées"),
    # Handicap / statut
    ("boeth", "Nombre de personnes BOETH"),
    ("non_boeth", "Nombre de personnes non BOETH"),
    ("sans_statut", "Nombre de personnes sans identification de statut"),
    # Sorties avant terme par motifs
    ("sortie_motif_depart_volontaire", "Sortie motif: Départ volontaire"),
    ("sortie_motif_sante", "Sortie motif: Raison de santé"),
    ("sortie_motif_reorientation", "Sortie motif: Réorientation"),
    ("sortie_motif_disciplinaire", "Sortie motif: Raison disciplinaire"),
    ("sortie_motif_objectif", "Sortie motif: Atteinte de l'objectif"),
    ("sortie_motif_reprise_emploi", "Sortie motif: Reprise d'emploi"),
    ("sortie_motif_autres", "Sortie motif: Autres"),
    ("sortie_motif_je_ne_sais_pas", "Sortie motif: Je ne sais pas"),
    # Suspensions
    ("suspension_nb", "Nombre de personnes ayant connu une suspension"),
    ("suspension_sante_non_liee", "Suspension: raisons de santé non liée au handicap"),
    ("suspension_evolution_handicap", "Suspension: évolution du handicap"),
    ("suspension_evolution_sociale", "Suspension: évolution situation sociale/familiale"),
    ("suspension_parcours_suspendu", "Suspension: parcours contractualisé incluant suspension"),
    ("suspension_autres", "Suspension: autres"),
    # Infos collectives/indirectes
    ("indirect_info_partenaires_heures", "Info partenaires: heures"),
    ("indirect_info_partenaires_reunions", "Info partenaires: réunions animées"),
    ("indirect_info_partenaires_nb", "Info partenaires: nombre de partenaires"),
    ("indirect_info_of_heures", "Info organismes formation: heures"),
    ("indirect_info_of_reunions", "Info organismes formation: réunions animées"),
    ("indirect_info_of_nb", "Info organismes formation: nombre de partenaires"),
    ("mdph_epe_origine", "Participations MDPH EPE (département d'origine)"),
    ("mdph_epe_limitrophes", "Participations MDPH EPE (départements limitrophes)"),
    ("mdph_cdaph_origine", "Participations MDPH CDAPH (département d'origine)"),
    ("mdph_cdaph_limitrophes", "Participations MDPH CDAPH (départements limitrophes)"),
    ("mdph_groupes_origine", "Participations MDPH Groupes de travail (département d'origine)"),
    ("mdph_groupes_limitrophes", "Participations MDPH Groupes de travail (départements limitrophes)"),
    # Taux emploi
    ("sorties_annee_n", "Nombre de personnes sorties année N"),
    ("sorties_annee_n_1", "Nombre de personnes sorties année N-1"),
    ("repondants_suivi", "Nombre de répondants suivi vers l'emploi"),
    ("acces_emploi", "Nombre ayant accédé à l'emploi"),
    ("presence_emploi_12m", "Nombre encore en emploi à 12 mois"),
]

TEXT_FIELDS = [
    ("sortie_motif_autres_precision", "Sortie motif: autres (préciser)"),
    ("suspension_autres_precision", "Suspension: autres (préciser)"),
    ("preconisation_autres_precision", "Préconisation: autres (préciser)"),
]


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_exc: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            date_naissance TEXT,
            identifiant_local TEXT,
            boeth_statut TEXT DEFAULT 'inconnu',
            genre TEXT,
            tranche_age_entree TEXT,
            niveau_formation_entree TEXT,
            ressources_entree TEXT,
            code_postal TEXT,
            ville TEXT,
            departement TEXT,
            zone_geographique TEXT,
            nb_pathologies INTEGER DEFAULT 0,
            origine_handicap TEXT,
            handicap_principal TEXT,
            handicap_associe TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            date_event TEXT NOT NULL,
            type_event TEXT NOT NULL CHECK (type_event IN ('entree', 'sortie')),
            type_prestation TEXT,
            dispositif TEXT NOT NULL,
            modalite TEXT,
            motif_sortie TEXT,
            preconisation_sortie TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS collective_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_log TEXT NOT NULL,
            type_prestation TEXT,
            dispositif TEXT NOT NULL,
            bloc TEXT NOT NULL,
            nature TEXT NOT NULL,
            heures REAL DEFAULT 0,
            reunions INTEGER DEFAULT 0,
            partenaires INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS mdph_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_log TEXT NOT NULL,
            type_prestation TEXT,
            dispositif TEXT NOT NULL,
            instance TEXT NOT NULL,
            zone TEXT NOT NULL,
            nb_participations INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS person_pathways (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            parcours_type TEXT NOT NULL,
            date_debut TEXT NOT NULL,
            date_fin TEXT,
            fin_type TEXT,
            fin_motif TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS pathway_suspensions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pathway_id INTEGER NOT NULL,
            date_debut TEXT NOT NULL,
            date_fin TEXT,
            motif TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (pathway_id) REFERENCES person_pathways(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS pathway_followup_12m (
            pathway_id INTEGER PRIMARY KEY,
            statut_12m TEXT,
            date_suivi TEXT,
            detail TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (pathway_id) REFERENCES person_pathways(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS annual_answers (
            year INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY(year, key)
        );

        CREATE TABLE IF NOT EXISTS person_followups (
            person_id INTEGER PRIMARY KEY,
            situation_arrivee TEXT,
            preconisation_sortie TEXT,
            devenir_12_mois TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_people_nom_prenom ON people(nom, prenom);
        CREATE INDEX IF NOT EXISTS idx_events_person_date ON events(person_id, date_event);
        CREATE INDEX IF NOT EXISTS idx_events_year ON events(date_event);
        CREATE INDEX IF NOT EXISTS idx_collective_year ON collective_logs(date_log);
        CREATE INDEX IF NOT EXISTS idx_mdph_year ON mdph_logs(date_log);
        CREATE INDEX IF NOT EXISTS idx_pathways_person ON person_pathways(person_id, date_debut);
        CREATE INDEX IF NOT EXISTS idx_suspensions_pathway ON pathway_suspensions(pathway_id, date_debut);
        """
    )
    db.commit()


def ensure_schema_updates() -> None:
    db = get_db()
    cols_people = {r["name"] for r in db.execute("PRAGMA table_info(people)").fetchall()}
    if "genre" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN genre TEXT")
    if "tranche_age_entree" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN tranche_age_entree TEXT")
    if "niveau_formation_entree" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN niveau_formation_entree TEXT")
    if "ressources_entree" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN ressources_entree TEXT")
    if "code_postal" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN code_postal TEXT")
    if "ville" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN ville TEXT")
    if "departement" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN departement TEXT")
    if "zone_geographique" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN zone_geographique TEXT")
    if "nb_pathologies" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN nb_pathologies INTEGER DEFAULT 0")
    if "origine_handicap" not in cols_people:
        db.execute("ALTER TABLE people ADD COLUMN origine_handicap TEXT")

    cols_events = {r["name"] for r in db.execute("PRAGMA table_info(events)").fetchall()}
    if "type_prestation" not in cols_events:
        db.execute("ALTER TABLE events ADD COLUMN type_prestation TEXT")
    if "preconisation_sortie" not in cols_events:
        db.execute("ALTER TABLE events ADD COLUMN preconisation_sortie TEXT")
    cols_collective = {r["name"] for r in db.execute("PRAGMA table_info(collective_logs)").fetchall()}
    if "type_prestation" not in cols_collective:
        db.execute("ALTER TABLE collective_logs ADD COLUMN type_prestation TEXT")
    db.commit()


def parse_iso(d: str) -> date | None:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


def compute_age(date_naissance: str | None, ref: date | None = None) -> int | None:
    if not date_naissance:
        return None
    dob = parse_iso(date_naissance)
    if not dob:
        return None
    today = ref or date.today()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years


def normalize_txt(v: str) -> str:
    return " ".join(str(v or "").strip().split())


def nval(v: Any) -> float:
    txt = str(v or "").strip().replace(",", ".")
    if txt == "":
        return 0.0
    try:
        return float(txt)
    except Exception:
        return 0.0


def get_answer_map(year: int) -> dict[str, str]:
    db = get_db()
    rows = db.execute("SELECT key, value FROM annual_answers WHERE year=?", (year,)).fetchall()
    return {r["key"]: (r["value"] or "") for r in rows}


def set_answer(year: int, key: str, value: str) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO annual_answers(year, key, value, updated_at)
        VALUES(?,?,?,datetime('now'))
        ON CONFLICT(year, key) DO UPDATE SET
          value=excluded.value,
          updated_at=datetime('now')
        """,
        (year, key, value),
    )
    db.commit()


def yearly_stats(year: int) -> dict[str, Any]:
    db = get_db()
    start = f"{year}-01-01"
    end = f"{year}-12-31"

    nb_entrees = db.execute(
        "SELECT COUNT(*) FROM events WHERE type_event='entree' AND date_event BETWEEN ? AND ?",
        (start, end),
    ).fetchone()[0]
    nb_sorties = db.execute(
        "SELECT COUNT(*) FROM events WHERE type_event='sortie' AND date_event BETWEEN ? AND ?",
        (start, end),
    ).fetchone()[0]

    people = db.execute("SELECT id FROM people").fetchall()
    actifs_3112 = 0
    total_days = 0
    total_sorties_with_duration = 0

    for p in people:
        pid = p["id"]
        last_event = db.execute(
            """
            SELECT type_event, date_event FROM events
            WHERE person_id=? AND date_event <= ?
            ORDER BY date_event DESC, id DESC
            LIMIT 1
            """,
            (pid, end),
        ).fetchone()
        if last_event and last_event["type_event"] == "entree":
            actifs_3112 += 1

    sorties = db.execute(
        """
        SELECT id, person_id, date_event FROM events
        WHERE type_event='sortie' AND date_event BETWEEN ? AND ?
        ORDER BY date_event ASC, id ASC
        """,
        (start, end),
    ).fetchall()

    for s in sorties:
        entree = db.execute(
            """
            SELECT date_event FROM events
            WHERE person_id=? AND type_event='entree' AND date_event <= ?
            ORDER BY date_event DESC, id DESC
            LIMIT 1
            """,
            (s["person_id"], s["date_event"]),
        ).fetchone()
        d_sortie = parse_iso(s["date_event"])
        d_entree = parse_iso(entree["date_event"]) if entree else None
        if d_entree and d_sortie and d_sortie >= d_entree:
            total_days += (d_sortie - d_entree).days + 1
            total_sorties_with_duration += 1

    duree_moyenne = round(total_days / total_sorties_with_duration, 1) if total_sorties_with_duration else 0

    boeth = db.execute("SELECT COUNT(*) FROM people WHERE boeth_statut='boeth'").fetchone()[0]
    non_boeth = db.execute("SELECT COUNT(*) FROM people WHERE boeth_statut='non_boeth'").fetchone()[0]
    sans_statut = db.execute("SELECT COUNT(*) FROM people WHERE boeth_statut='inconnu'").fetchone()[0]

    motif_counts: dict[str, int] = {}
    for m in MOTIFS_SORTIE:
        motif_counts[m] = db.execute(
            "SELECT COUNT(*) FROM events WHERE type_event='sortie' AND date_event BETWEEN ? AND ? AND motif_sortie=?",
            (start, end, m),
        ).fetchone()[0]

    return {
        "year": year,
        "nb_entrees": nb_entrees,
        "nb_sorties": nb_sorties,
        "actifs_3112": actifs_3112,
        "duree_moyenne_jours": duree_moyenne,
        "sorties_calculees": total_sorties_with_duration,
        "boeth": boeth,
        "non_boeth": non_boeth,
        "sans_statut": sans_statut,
        "motif_counts": motif_counts,
    }


def collective_rollup(year: int) -> dict[str, dict[str, float]]:
    db = get_db()
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    rows = db.execute(
        """
        SELECT bloc, nature,
               SUM(COALESCE(heures,0)) AS heures,
               SUM(COALESCE(reunions,0)) AS reunions,
               SUM(COALESCE(partenaires,0)) AS partenaires
        FROM collective_logs
        WHERE date_log BETWEEN ? AND ?
        GROUP BY bloc, nature
        """,
        (start, end),
    ).fetchall()
    out: dict[str, dict[str, float]] = {}
    for r in rows:
        key = f"{r['bloc']}::{r['nature']}"
        out[key] = {
            "heures": float(r["heures"] or 0),
            "reunions": float(r["reunions"] or 0),
            "partenaires": float(r["partenaires"] or 0),
        }
    return out


def rollup_value(rollup: dict[str, dict[str, float]], bloc: str, nature: str) -> dict[str, float]:
    target = f"{bloc}::{nature}".lower()
    for key, value in rollup.items():
        if key.lower() == target:
            return value
    return {"heures": 0, "reunions": 0, "partenaires": 0}


def mdph_rollup(year: int) -> dict[str, float]:
    db = get_db()
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    rows = db.execute(
        """
        SELECT instance, zone, SUM(COALESCE(nb_participations,0)) AS total
        FROM mdph_logs
        WHERE date_log BETWEEN ? AND ?
        GROUP BY instance, zone
        """,
        (start, end),
    ).fetchall()
    out = {
        "mdph_epe_origine": 0.0,
        "mdph_epe_limitrophes": 0.0,
        "mdph_cdaph_origine": 0.0,
        "mdph_cdaph_limitrophes": 0.0,
        "mdph_groupes_origine": 0.0,
        "mdph_groupes_limitrophes": 0.0,
    }
    for r in rows:
        instance = (r["instance"] or "").strip()
        zone = (r["zone"] or "").strip()
        total = float(r["total"] or 0)
        if instance == "EPE" and zone == "Département d'origine":
            out["mdph_epe_origine"] = total
        elif instance == "EPE" and zone == "Départements limitrophes":
            out["mdph_epe_limitrophes"] = total
        elif instance == "CDAPH" and zone == "Département d'origine":
            out["mdph_cdaph_origine"] = total
        elif instance == "CDAPH" and zone == "Départements limitrophes":
            out["mdph_cdaph_limitrophes"] = total
        elif instance == "Groupes de travail" and zone == "Département d'origine":
            out["mdph_groupes_origine"] = total
        elif instance == "Groupes de travail" and zone == "Départements limitrophes":
            out["mdph_groupes_limitrophes"] = total
    return out


def build_person_timeline(person_id: int) -> list[dict[str, str]]:
    db = get_db()
    timeline: list[dict[str, str]] = []

    events = db.execute(
        """
        SELECT date_event, type_event, type_prestation, dispositif, modalite, motif_sortie, preconisation_sortie, notes
        FROM events
        WHERE person_id=?
        """,
        (person_id,),
    ).fetchall()
    for e in events:
        label = "Entrée en prestation" if e["type_event"] == "entree" else "Sortie de prestation"
        details = [f"Prestation: {e['type_prestation'] or '-'}", f"Dispositif: {e['dispositif'] or '-'}"]
        if e["modalite"]:
            details.append(f"Modalité: {e['modalite']}")
        if e["motif_sortie"]:
            details.append(f"Motif de sortie: {e['motif_sortie']}")
        if e["preconisation_sortie"]:
            details.append(f"Préconisation: {e['preconisation_sortie']}")
        if e["notes"]:
            details.append(f"Notes: {e['notes']}")
        timeline.append({"date": e["date_event"], "type": label, "details": " | ".join(details)})

    pathways = db.execute(
        "SELECT id, parcours_type, date_debut, date_fin, fin_type, fin_motif FROM person_pathways WHERE person_id=?",
        (person_id,),
    ).fetchall()
    for p in pathways:
        timeline.append({"date": p["date_debut"], "type": "Changement de parcours", "details": f"Nouveau parcours: {p['parcours_type']}"})
        if p["date_fin"]:
            fin = f"Type: {p['fin_type'] or '-'}"
            if p["fin_motif"]:
                fin += f" | Motif: {p['fin_motif']}"
            timeline.append({"date": p["date_fin"], "type": "Fin de parcours", "details": fin})

    suspensions = db.execute(
        """
        SELECT s.date_debut, s.date_fin, s.motif, s.notes, p.parcours_type
        FROM pathway_suspensions s
        JOIN person_pathways p ON p.id = s.pathway_id
        WHERE p.person_id=?
        """,
        (person_id,),
    ).fetchall()
    for s in suspensions:
        d = f"Parcours: {s['parcours_type']}"
        if s["motif"]:
            d += f" | Motif: {s['motif']}"
        if s["date_fin"]:
            d += f" | Fin suspension: {s['date_fin']}"
        if s["notes"]:
            d += f" | Notes: {s['notes']}"
        timeline.append({"date": s["date_debut"], "type": "Suspension de parcours", "details": d})

    followups = db.execute(
        """
        SELECT f.date_suivi, f.statut_12m, f.detail, p.parcours_type
        FROM pathway_followup_12m f
        JOIN person_pathways p ON p.id = f.pathway_id
        WHERE p.person_id=?
        """,
        (person_id,),
    ).fetchall()
    for f in followups:
        if not f["date_suivi"]:
            continue
        d = f"Parcours: {f['parcours_type']} | Statut: {f['statut_12m'] or '-'}"
        if f["detail"]:
            d += f" | Détail: {f['detail']}"
        timeline.append({"date": f["date_suivi"], "type": "Suivi à 12 mois", "details": d})

    timeline = [t for t in timeline if t["date"]]
    timeline.sort(key=lambda x: x["date"], reverse=True)
    return timeline


@app.route("/")
def home() -> str:
    y = request.args.get("year", str(date.today().year))
    try:
        year = int(y)
    except Exception:
        year = date.today().year
    stats = yearly_stats(year)
    db = get_db()
    recent = db.execute(
        """
        SELECT e.id, e.date_event, e.type_event, e.dispositif, p.nom, p.prenom, p.id AS person_id
        FROM events e
        JOIN people p ON p.id = e.person_id
        ORDER BY e.date_event DESC, e.id DESC
        LIMIT 20
        """
    ).fetchall()
    return render_template("home.html", stats=stats, recent=recent, current_year=year)


@app.route("/people")
def people_list() -> str:
    q = normalize_txt(request.args.get("q", ""))
    db = get_db()
    if q:
        like = f"%{q}%"
        rows = db.execute(
            """
            SELECT p.*, COUNT(e.id) AS nb_events
            FROM people p
            LEFT JOIN events e ON e.person_id = p.id
            WHERE p.nom LIKE ? OR p.prenom LIKE ? OR COALESCE(p.identifiant_local, '') LIKE ?
            GROUP BY p.id
            ORDER BY p.nom, p.prenom
            """,
            (like, like, like),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT p.*, COUNT(e.id) AS nb_events
            FROM people p
            LEFT JOIN events e ON e.person_id = p.id
            GROUP BY p.id
            ORDER BY p.nom, p.prenom
            LIMIT 500
            """
        ).fetchall()
    return render_template("people_list.html", people=rows, q=q, current_year=date.today().year)


@app.route("/people/new", methods=["GET", "POST"])
def people_new() -> str | Response:
    if request.method == "POST":
        nom = normalize_txt(request.form.get("nom", "")).upper()
        prenom = normalize_txt(request.form.get("prenom", ""))
        date_naissance = normalize_txt(request.form.get("date_naissance", ""))
        identifiant_local = normalize_txt(request.form.get("identifiant_local", ""))
        boeth_statut = normalize_txt(request.form.get("boeth_statut", "inconnu"))
        genre = normalize_txt(request.form.get("genre", ""))
        tranche_age_entree = normalize_txt(request.form.get("tranche_age_entree", ""))
        niveau_formation_entree = normalize_txt(request.form.get("niveau_formation_entree", ""))
        ressources_entree = normalize_txt(request.form.get("ressources_entree", ""))
        code_postal = normalize_txt(request.form.get("code_postal", ""))
        ville = normalize_txt(request.form.get("ville", ""))
        departement = normalize_txt(request.form.get("departement", ""))
        nb_pathologies = int(nval(request.form.get("nb_pathologies", "0")))
        origine_handicap = normalize_txt(request.form.get("origine_handicap", ""))
        handicap_principal = normalize_txt(request.form.get("handicap_principal", ""))
        handicap_associe = normalize_txt(request.form.get("handicap_associe", ""))

        if not nom or not prenom:
            flash("Nom et prénom sont requis.", "error")
            return render_template(
                "people_new.html",
                dispositifs=DISPOSITIFS,
                handicap_types=HANDICAP_TYPES,
                genre_options=GENRE_OPTIONS,
                tranche_age_options=TRANCHE_AGE_OPTIONS,
                niveau_formation_options=NIVEAU_FORMATION_OPTIONS,
                ressources_entree_options=RESSOURCES_ENTREE_OPTIONS,
                origine_handicap_options=ORIGINE_HANDICAP_OPTIONS,
                current_year=date.today().year,
            )

        if date_naissance and not parse_iso(date_naissance):
            flash("Date de naissance invalide (format AAAA-MM-JJ).", "error")
            return render_template(
                "people_new.html",
                dispositifs=DISPOSITIFS,
                handicap_types=HANDICAP_TYPES,
                genre_options=GENRE_OPTIONS,
                tranche_age_options=TRANCHE_AGE_OPTIONS,
                niveau_formation_options=NIVEAU_FORMATION_OPTIONS,
                ressources_entree_options=RESSOURCES_ENTREE_OPTIONS,
                origine_handicap_options=ORIGINE_HANDICAP_OPTIONS,
                current_year=date.today().year,
            )

        if boeth_statut not in {"boeth", "non_boeth", "inconnu"}:
            boeth_statut = "inconnu"
        if genre and genre not in GENRE_OPTIONS:
            genre = ""
        if tranche_age_entree and tranche_age_entree not in TRANCHE_AGE_OPTIONS:
            tranche_age_entree = ""
        if niveau_formation_entree and niveau_formation_entree not in NIVEAU_FORMATION_OPTIONS:
            niveau_formation_entree = ""
        if ressources_entree and ressources_entree not in RESSOURCES_ENTREE_OPTIONS:
            ressources_entree = ""
        if nb_pathologies < 0:
            nb_pathologies = 0
        if origine_handicap and origine_handicap not in ORIGINE_HANDICAP_OPTIONS:
            origine_handicap = ""
        if handicap_principal and handicap_principal not in HANDICAP_TYPES:
            handicap_principal = ""
        if handicap_associe and handicap_associe not in HANDICAP_TYPES:
            handicap_associe = ""

        db = get_db()
        cur = db.execute(
            """
            INSERT INTO people(
              nom, prenom, date_naissance, identifiant_local, boeth_statut,
              genre, tranche_age_entree, niveau_formation_entree, ressources_entree,
              code_postal, ville, departement, nb_pathologies, origine_handicap,
              handicap_principal, handicap_associe
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                nom,
                prenom,
                date_naissance or None,
                identifiant_local or None,
                boeth_statut,
                genre or None,
                tranche_age_entree or None,
                niveau_formation_entree or None,
                ressources_entree or None,
                code_postal or None,
                ville or None,
                departement or None,
                nb_pathologies,
                origine_handicap or None,
                handicap_principal or None,
                handicap_associe or None,
            ),
        )
        db.commit()
        flash("Personne créée.", "success")
        return redirect(url_for("person_detail", person_id=cur.lastrowid))

    return render_template(
        "people_new.html",
        dispositifs=DISPOSITIFS,
        handicap_types=HANDICAP_TYPES,
        genre_options=GENRE_OPTIONS,
        tranche_age_options=TRANCHE_AGE_OPTIONS,
        niveau_formation_options=NIVEAU_FORMATION_OPTIONS,
        ressources_entree_options=RESSOURCES_ENTREE_OPTIONS,
        origine_handicap_options=ORIGINE_HANDICAP_OPTIONS,
        current_year=date.today().year,
    )


@app.route("/people/<int:person_id>")
def person_detail(person_id: int) -> str:
    db = get_db()
    person = db.execute("SELECT * FROM people WHERE id=?", (person_id,)).fetchone()
    if not person:
        flash("Personne introuvable.", "error")
        return redirect(url_for("people_list"))

    events = db.execute(
        "SELECT * FROM events WHERE person_id=? ORDER BY date_event DESC, id DESC",
        (person_id,),
    ).fetchall()
    followup = db.execute("SELECT * FROM person_followups WHERE person_id=?", (person_id,)).fetchone()
    pathways = db.execute(
        """
        SELECT p.*, f.statut_12m, f.date_suivi, f.detail AS followup_detail
        FROM person_pathways p
        LEFT JOIN pathway_followup_12m f ON f.pathway_id = p.id
        WHERE p.person_id=?
        ORDER BY p.date_debut DESC, p.id DESC
        """,
        (person_id,),
    ).fetchall()
    suspensions = db.execute(
        """
        SELECT s.*, p.parcours_type
        FROM pathway_suspensions s
        JOIN person_pathways p ON p.id = s.pathway_id
        WHERE p.person_id=?
        ORDER BY s.date_debut DESC, s.id DESC
        """,
        (person_id,),
    ).fetchall()
    active_pathway = next((row for row in pathways if not row["date_fin"]), None)
    timeline = build_person_timeline(person_id)
    age = compute_age(person["date_naissance"])
    return render_template(
        "person_detail.html",
        person=person,
        age=age,
        followup=followup,
        pathways=pathways,
        active_pathway=active_pathway,
        suspensions=suspensions,
        events=events,
        timeline=timeline,
        prestation_types=PRESTATION_TYPES,
        dispositifs=DISPOSITIFS,
        modalites=MODALITES,
        motifs_sortie=MOTIFS_SORTIE,
        handicap_types=HANDICAP_TYPES,
        genre_options=GENRE_OPTIONS,
        tranche_age_options=TRANCHE_AGE_OPTIONS,
        niveau_formation_options=NIVEAU_FORMATION_OPTIONS,
        ressources_entree_options=RESSOURCES_ENTREE_OPTIONS,
        origine_handicap_options=ORIGINE_HANDICAP_OPTIONS,
        situation_arrivee_options=SITUATION_ARRIVEE_OPTIONS,
        preconisations=PRECONISATIONS,
        devenir_12m_options=DEVENIR_12M_OPTIONS,
        parcours_types=PARCOURS_TYPES,
        fin_parcours_types=FIN_PARCOURS_TYPES,
        suspension_motifs=SUSPENSION_MOTIFS,
        current_year=date.today().year,
    )


@app.route("/people/<int:person_id>/update", methods=["POST"])
def person_update(person_id: int) -> Response:
    db = get_db()
    person = db.execute("SELECT id FROM people WHERE id=?", (person_id,)).fetchone()
    if not person:
        flash("Personne introuvable.", "error")
        return redirect(url_for("people_list"))

    boeth_statut = normalize_txt(request.form.get("boeth_statut", "inconnu"))
    genre = normalize_txt(request.form.get("genre", ""))
    tranche_age_entree = normalize_txt(request.form.get("tranche_age_entree", ""))
    niveau_formation_entree = normalize_txt(request.form.get("niveau_formation_entree", ""))
    ressources_entree = normalize_txt(request.form.get("ressources_entree", ""))
    code_postal = normalize_txt(request.form.get("code_postal", ""))
    ville = normalize_txt(request.form.get("ville", ""))
    departement = normalize_txt(request.form.get("departement", ""))
    nb_pathologies = int(nval(request.form.get("nb_pathologies", "0")))
    origine_handicap = normalize_txt(request.form.get("origine_handicap", ""))
    handicap_principal = normalize_txt(request.form.get("handicap_principal", ""))
    handicap_associe = normalize_txt(request.form.get("handicap_associe", ""))
    if boeth_statut not in {"boeth", "non_boeth", "inconnu"}:
        boeth_statut = "inconnu"
    if genre and genre not in GENRE_OPTIONS:
        genre = ""
    if tranche_age_entree and tranche_age_entree not in TRANCHE_AGE_OPTIONS:
        tranche_age_entree = ""
    if niveau_formation_entree and niveau_formation_entree not in NIVEAU_FORMATION_OPTIONS:
        niveau_formation_entree = ""
    if ressources_entree and ressources_entree not in RESSOURCES_ENTREE_OPTIONS:
        ressources_entree = ""
    if nb_pathologies < 0:
        nb_pathologies = 0
    if origine_handicap and origine_handicap not in ORIGINE_HANDICAP_OPTIONS:
        origine_handicap = ""
    if handicap_principal and handicap_principal not in HANDICAP_TYPES:
        handicap_principal = ""
    if handicap_associe and handicap_associe not in HANDICAP_TYPES:
        handicap_associe = ""

    db.execute(
        """
        UPDATE people
        SET boeth_statut=?, genre=?, tranche_age_entree=?, niveau_formation_entree=?, ressources_entree=?,
            code_postal=?, ville=?, departement=?, nb_pathologies=?, origine_handicap=?,
            handicap_principal=?, handicap_associe=?
        WHERE id=?
        """,
        (
            boeth_statut,
            genre or None,
            tranche_age_entree or None,
            niveau_formation_entree or None,
            ressources_entree or None,
            code_postal or None,
            ville or None,
            departement or None,
            nb_pathologies,
            origine_handicap or None,
            handicap_principal or None,
            handicap_associe or None,
            person_id,
        ),
    )
    db.commit()
    flash("Profil personne mis à jour.", "success")
    return redirect(url_for("person_detail", person_id=person_id))


@app.route("/people/<int:person_id>/parcours", methods=["POST"])
def person_parcours_update(person_id: int) -> Response:
    db = get_db()
    person = db.execute("SELECT id FROM people WHERE id=?", (person_id,)).fetchone()
    if not person:
        flash("Personne introuvable.", "error")
        return redirect(url_for("people_list"))

    situation_arrivee = normalize_txt(request.form.get("situation_arrivee", ""))
    if situation_arrivee and situation_arrivee not in SITUATION_ARRIVEE_OPTIONS:
        situation_arrivee = ""

    db.execute(
        """
        INSERT INTO person_followups(person_id, situation_arrivee, updated_at)
        VALUES(?,?,datetime('now'))
        ON CONFLICT(person_id) DO UPDATE SET
          situation_arrivee=excluded.situation_arrivee,
          updated_at=datetime('now')
        """,
        (person_id, situation_arrivee or None),
    )
    db.commit()
    flash("Situation à l'entrée mise à jour.", "success")
    return redirect(url_for("person_detail", person_id=person_id))


@app.route("/people/<int:person_id>/preconisation", methods=["POST"])
def person_preconisation_update(person_id: int) -> Response:
    db = get_db()
    person = db.execute("SELECT id FROM people WHERE id=?", (person_id,)).fetchone()
    if not person:
        flash("Personne introuvable.", "error")
        return redirect(url_for("people_list"))

    preconisation_sortie = normalize_txt(request.form.get("preconisation_sortie", ""))
    if preconisation_sortie and preconisation_sortie not in PRECONISATIONS:
        preconisation_sortie = ""

    db.execute(
        """
        INSERT INTO person_followups(person_id, preconisation_sortie, updated_at)
        VALUES(?,?,datetime('now'))
        ON CONFLICT(person_id) DO UPDATE SET
          preconisation_sortie=excluded.preconisation_sortie,
          updated_at=datetime('now')
        """,
        (person_id, preconisation_sortie or None),
    )
    db.commit()
    flash("Préconisation à la sortie enregistrée.", "success")
    return redirect(url_for("person_detail", person_id=person_id))


@app.route("/people/<int:person_id>/pathway/start", methods=["POST"])
def person_pathway_start(person_id: int) -> Response:
    db = get_db()
    person = db.execute("SELECT id FROM people WHERE id=?", (person_id,)).fetchone()
    if not person:
        flash("Personne introuvable.", "error")
        return redirect(url_for("people_list"))

    parcours_type = normalize_txt(request.form.get("parcours_type", ""))
    date_debut = normalize_txt(request.form.get("date_debut", ""))
    date_fin_precedent = normalize_txt(request.form.get("date_fin_precedent", ""))
    if parcours_type not in PARCOURS_TYPES:
        flash("Type de parcours invalide.", "error")
        return redirect(url_for("person_detail", person_id=person_id))
    if not parse_iso(date_debut):
        flash("Date de début invalide.", "error")
        return redirect(url_for("person_detail", person_id=person_id))

    active = db.execute(
        "SELECT id, date_debut FROM person_pathways WHERE person_id=? AND date_fin IS NULL ORDER BY date_debut DESC, id DESC LIMIT 1",
        (person_id,),
    ).fetchone()
    if active:
        if not parse_iso(date_fin_precedent):
            flash("Renseignez la date de fin du parcours actuel avant de démarrer le nouveau.", "error")
            return redirect(url_for("person_detail", person_id=person_id))
        if parse_iso(date_fin_precedent) < parse_iso(active["date_debut"]):
            flash("Date de fin précédente incohérente.", "error")
            return redirect(url_for("person_detail", person_id=person_id))
        db.execute("UPDATE person_pathways SET date_fin=? WHERE id=?", (date_fin_precedent, active["id"]))

    db.execute(
        "INSERT INTO person_pathways(person_id, parcours_type, date_debut) VALUES(?,?,?)",
        (person_id, parcours_type, date_debut),
    )
    db.commit()
    flash("Parcours démarré.", "success")
    return redirect(url_for("person_detail", person_id=person_id))


@app.route("/pathway/<int:pathway_id>/suspension", methods=["POST"])
def pathway_add_suspension(pathway_id: int) -> Response:
    db = get_db()
    pathway = db.execute("SELECT id, person_id FROM person_pathways WHERE id=?", (pathway_id,)).fetchone()
    if not pathway:
        flash("Parcours introuvable.", "error")
        return redirect(url_for("home"))
    date_debut = normalize_txt(request.form.get("susp_date_debut", ""))
    date_fin = normalize_txt(request.form.get("susp_date_fin", ""))
    motif = normalize_txt(request.form.get("susp_motif", ""))
    notes = normalize_txt(request.form.get("susp_notes", ""))
    if not parse_iso(date_debut):
        flash("Date de début suspension invalide.", "error")
        return redirect(url_for("person_detail", person_id=pathway["person_id"]))
    if date_fin and not parse_iso(date_fin):
        flash("Date de fin suspension invalide.", "error")
        return redirect(url_for("person_detail", person_id=pathway["person_id"]))
    if motif and motif not in SUSPENSION_MOTIFS:
        motif = ""
    db.execute(
        "INSERT INTO pathway_suspensions(pathway_id, date_debut, date_fin, motif, notes) VALUES(?,?,?,?,?)",
        (pathway_id, date_debut, date_fin or None, motif or None, notes or None),
    )
    db.commit()
    flash("Suspension ajoutée.", "success")
    return redirect(url_for("person_detail", person_id=pathway["person_id"]))


@app.route("/pathway/<int:pathway_id>/close", methods=["POST"])
def pathway_close(pathway_id: int) -> Response:
    db = get_db()
    pathway = db.execute("SELECT id, person_id, date_debut FROM person_pathways WHERE id=?", (pathway_id,)).fetchone()
    if not pathway:
        flash("Parcours introuvable.", "error")
        return redirect(url_for("home"))
    date_fin = normalize_txt(request.form.get("date_fin", ""))
    fin_type = normalize_txt(request.form.get("fin_type", ""))
    fin_motif = normalize_txt(request.form.get("fin_motif", ""))
    if not parse_iso(date_fin):
        flash("Date de fin invalide.", "error")
        return redirect(url_for("person_detail", person_id=pathway["person_id"]))
    if parse_iso(date_fin) < parse_iso(pathway["date_debut"]):
        flash("Date de fin incohérente (avant la date de début).", "error")
        return redirect(url_for("person_detail", person_id=pathway["person_id"]))
    if fin_type and fin_type not in FIN_PARCOURS_TYPES:
        fin_type = ""
    db.execute(
        "UPDATE person_pathways SET date_fin=?, fin_type=?, fin_motif=? WHERE id=?",
        (date_fin, fin_type or None, fin_motif or None, pathway_id),
    )
    db.commit()
    flash("Fin de parcours enregistrée.", "success")
    return redirect(url_for("person_detail", person_id=pathway["person_id"]))


@app.route("/pathway/<int:pathway_id>/followup12", methods=["POST"])
def pathway_followup12(pathway_id: int) -> Response:
    db = get_db()
    pathway = db.execute("SELECT id, person_id FROM person_pathways WHERE id=?", (pathway_id,)).fetchone()
    if not pathway:
        flash("Parcours introuvable.", "error")
        return redirect(url_for("home"))
    statut_12m = normalize_txt(request.form.get("statut_12m", ""))
    date_suivi = normalize_txt(request.form.get("date_suivi", ""))
    detail = normalize_txt(request.form.get("detail", ""))
    if statut_12m and statut_12m not in DEVENIR_12M_OPTIONS:
        statut_12m = ""
    if date_suivi and not parse_iso(date_suivi):
        flash("Date de suivi 12 mois invalide.", "error")
        return redirect(url_for("person_detail", person_id=pathway["person_id"]))
    db.execute(
        """
        INSERT INTO pathway_followup_12m(pathway_id, statut_12m, date_suivi, detail, updated_at)
        VALUES(?,?,?,?,datetime('now'))
        ON CONFLICT(pathway_id) DO UPDATE SET
          statut_12m=excluded.statut_12m,
          date_suivi=excluded.date_suivi,
          detail=excluded.detail,
          updated_at=datetime('now')
        """,
        (pathway_id, statut_12m or None, date_suivi or None, detail or None),
    )
    db.commit()
    flash("Suivi à 12 mois enregistré.", "success")
    return redirect(url_for("person_detail", person_id=pathway["person_id"]))


@app.route("/people/<int:person_id>/event", methods=["POST"])
def person_add_event(person_id: int) -> Response:
    db = get_db()
    person = db.execute("SELECT id FROM people WHERE id=?", (person_id,)).fetchone()
    if not person:
        flash("Personne introuvable.", "error")
        return redirect(url_for("people_list"))

    date_event = normalize_txt(request.form.get("date_event", ""))
    type_event = normalize_txt(request.form.get("type_event", "")).lower()
    type_prestation = normalize_txt(request.form.get("type_prestation", ""))
    dispositif = normalize_txt(request.form.get("dispositif", ""))
    modalite = normalize_txt(request.form.get("modalite", ""))
    motif_sortie = normalize_txt(request.form.get("motif_sortie", ""))
    preconisation_sortie = normalize_txt(request.form.get("preconisation_sortie", ""))
    parcours_type_entree = normalize_txt(request.form.get("parcours_type_entree", ""))
    notes = normalize_txt(request.form.get("notes", ""))

    if type_event not in {"entree", "sortie"}:
        flash("Type d'évènement invalide.", "error")
        return redirect(url_for("person_detail", person_id=person_id))
    if not parse_iso(date_event):
        flash("Date évènement invalide (AAAA-MM-JJ).", "error")
        return redirect(url_for("person_detail", person_id=person_id))
    if not dispositif:
        flash("Dispositif requis.", "error")
        return redirect(url_for("person_detail", person_id=person_id))
    if type_prestation not in PRESTATION_TYPES:
        flash("Type de prestation requis.", "error")
        return redirect(url_for("person_detail", person_id=person_id))
    if type_event == "entree" and dispositif == "ESRP" and parcours_type_entree not in PARCOURS_TYPES:
        flash("Type de parcours requis pour une entrée ESRP.", "error")
        return redirect(url_for("person_detail", person_id=person_id))
    if type_event == "entree" and dispositif != "ESRP":
        parcours_type_entree = ""
    if modalite and modalite not in MODALITES:
        modalite = ""
    if preconisation_sortie and preconisation_sortie not in PRECONISATIONS:
        preconisation_sortie = ""

    db.execute(
        """
        INSERT INTO events(person_id, date_event, type_event, type_prestation, dispositif, modalite, motif_sortie, preconisation_sortie, notes)
        VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            person_id,
            date_event,
            type_event,
            type_prestation,
            dispositif,
            modalite or None,
            motif_sortie if type_event == "sortie" else None,
            preconisation_sortie if type_event == "sortie" else None,
            notes or None,
        ),
    )
    if type_event == "sortie" and preconisation_sortie:
        db.execute(
            """
            INSERT INTO person_followups(person_id, preconisation_sortie, updated_at)
            VALUES(?,?,datetime('now'))
            ON CONFLICT(person_id) DO UPDATE SET
              preconisation_sortie=excluded.preconisation_sortie,
              updated_at=datetime('now')
            """,
            (person_id, preconisation_sortie),
        )
    if type_event == "entree" and dispositif == "ESRP":
        active = db.execute(
            "SELECT id FROM person_pathways WHERE person_id=? AND date_fin IS NULL ORDER BY date_debut DESC, id DESC LIMIT 1",
            (person_id,),
        ).fetchone()
        if not active:
            db.execute(
                "INSERT INTO person_pathways(person_id, parcours_type, date_debut) VALUES(?,?,?)",
                (person_id, parcours_type_entree, date_event),
            )
    db.commit()
    flash("Évènement enregistré.", "success")
    return redirect(url_for("person_detail", person_id=person_id))


@app.route("/events/<int:event_id>/delete", methods=["POST"])
def event_delete(event_id: int) -> Response:
    db = get_db()
    row = db.execute("SELECT person_id FROM events WHERE id=?", (event_id,)).fetchone()
    if not row:
        flash("Évènement introuvable.", "error")
        return redirect(url_for("home"))
    person_id = row["person_id"]
    db.execute("DELETE FROM events WHERE id=?", (event_id,))
    db.commit()
    flash("Évènement supprimé.", "success")
    return redirect(url_for("person_detail", person_id=person_id))


@app.route("/collectif", methods=["GET", "POST"])
def collectif() -> str | Response:
    db = get_db()
    if request.method == "POST":
        date_log = normalize_txt(request.form.get("date_log", ""))
        type_prestation = normalize_txt(request.form.get("type_prestation", ""))
        dispositif = normalize_txt(request.form.get("dispositif", ""))
        bloc = normalize_txt(request.form.get("bloc", ""))
        nature = "Collectives"
        heures = nval(request.form.get("heures", "0"))
        reunions = int(nval(request.form.get("reunions", "0")))
        partenaires = int(nval(request.form.get("partenaires", "0")))
        notes = normalize_txt(request.form.get("notes", ""))

        if not parse_iso(date_log):
            flash("Date invalide.", "error")
            return redirect(url_for("collectif"))
        if not type_prestation or not dispositif or not bloc:
            flash("Type de prestation, dispositif et thème sont requis.", "error")
            return redirect(url_for("collectif"))
        if type_prestation not in PRESTATION_TYPES:
            flash("Type de prestation invalide.", "error")
            return redirect(url_for("collectif"))
        if bloc not in {b[0] for b in BLOCS_COLLECTIFS}:
            flash("Bloc invalide.", "error")
            return redirect(url_for("collectif"))

        db.execute(
            """
            INSERT INTO collective_logs(date_log, type_prestation, dispositif, bloc, nature, heures, reunions, partenaires, notes)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (date_log, type_prestation, dispositif, bloc, nature, heures, reunions, partenaires, notes or None),
        )
        db.commit()
        flash("Réunion collective enregistrée.", "success")
        return redirect(url_for("collectif"))

    logs = db.execute(
        "SELECT * FROM collective_logs ORDER BY date_log DESC, id DESC LIMIT 200"
    ).fetchall()
    return render_template(
        "collectif.html",
        logs=logs,
        prestation_types=PRESTATION_TYPES,
        dispositifs=DISPOSITIFS,
        blocs_collectifs=BLOCS_COLLECTIFS,
        blocs_collectifs_map={k: v for k, v in BLOCS_COLLECTIFS},
        current_year=date.today().year,
    )


@app.route("/collectif/<int:log_id>/delete", methods=["POST"])
def collectif_delete(log_id: int) -> Response:
    db = get_db()
    db.execute("DELETE FROM collective_logs WHERE id=?", (log_id,))
    db.commit()
    flash("Ligne de réunion collective supprimée.", "success")
    return redirect(url_for("collectif"))


@app.route("/mdph", methods=["GET", "POST"])
def mdph() -> str | Response:
    db = get_db()
    if request.method == "POST":
        date_log = normalize_txt(request.form.get("date_log", ""))
        type_prestation = normalize_txt(request.form.get("type_prestation", ""))
        dispositif = normalize_txt(request.form.get("dispositif", ""))
        instance = normalize_txt(request.form.get("instance", ""))
        zone = normalize_txt(request.form.get("zone", ""))
        nb_participations = int(nval(request.form.get("nb_participations", "0")))
        notes = normalize_txt(request.form.get("notes", ""))

        if not parse_iso(date_log):
            flash("Date invalide.", "error")
            return redirect(url_for("mdph"))
        if type_prestation not in PRESTATION_TYPES:
            flash("Type de prestation invalide.", "error")
            return redirect(url_for("mdph"))
        if dispositif not in DISPOSITIFS:
            flash("Dispositif invalide.", "error")
            return redirect(url_for("mdph"))
        if instance not in MDPH_INSTANCES:
            flash("Instance MDPH invalide.", "error")
            return redirect(url_for("mdph"))
        if zone not in MDPH_ZONES:
            flash("Zone MDPH invalide.", "error")
            return redirect(url_for("mdph"))
        if nb_participations < 0:
            nb_participations = 0

        db.execute(
            """
            INSERT INTO mdph_logs(date_log, type_prestation, dispositif, instance, zone, nb_participations, notes)
            VALUES(?,?,?,?,?,?,?)
            """,
            (date_log, type_prestation, dispositif, instance, zone, nb_participations, notes or None),
        )
        db.commit()
        flash("Participation MDPH enregistrée.", "success")
        return redirect(url_for("mdph"))

    logs = db.execute("SELECT * FROM mdph_logs ORDER BY date_log DESC, id DESC LIMIT 300").fetchall()
    return render_template(
        "mdph.html",
        logs=logs,
        prestation_types=PRESTATION_TYPES,
        dispositifs=DISPOSITIFS,
        mdph_instances=MDPH_INSTANCES,
        mdph_zones=MDPH_ZONES,
        current_year=date.today().year,
    )


@app.route("/mdph/<int:log_id>/delete", methods=["POST"])
def mdph_delete(log_id: int) -> Response:
    db = get_db()
    db.execute("DELETE FROM mdph_logs WHERE id=?", (log_id,))
    db.commit()
    flash("Ligne MDPH supprimée.", "success")
    return redirect(url_for("mdph"))


def _annual_defaults(year: int) -> dict[str, str]:
    stats = yearly_stats(year)
    coll = collective_rollup(year)
    mdph_stats = mdph_rollup(year)

    values: dict[str, str] = {k: "0" for k, _ in ANNUAL_FIELDS}
    values.update({k: "" for k, _ in TEXT_FIELDS})

    values["file_active_3112"] = str(stats["actifs_3112"])
    values["sorties_definitives"] = str(stats["nb_sorties"])
    values["sorties_annee_n"] = str(stats["nb_sorties"])
    values["journees_realisees"] = str(int(stats["duree_moyenne_jours"] * max(stats["sorties_calculees"], 1)) if stats["sorties_calculees"] else "0")

    values["boeth"] = str(stats["boeth"])
    values["non_boeth"] = str(stats["non_boeth"])
    values["sans_statut"] = str(stats["sans_statut"])

    map_motif = {
        "Départ volontaire": "sortie_motif_depart_volontaire",
        "Raison de santé": "sortie_motif_sante",
        "Réorientation": "sortie_motif_reorientation",
        "Raison disciplinaire": "sortie_motif_disciplinaire",
        "Atteinte de l'objectif": "sortie_motif_objectif",
        "Reprise d'emploi": "sortie_motif_reprise_emploi",
        "Autres": "sortie_motif_autres",
        "Je ne sais pas": "sortie_motif_je_ne_sais_pas",
    }
    for motif, cnt in stats["motif_counts"].items():
        key = map_motif.get(motif)
        if key:
            values[key] = str(cnt)

    pk = rollup_value(coll, "info_partenaires_collectives", "Collectives")
    values["indirect_info_partenaires_heures"] = str(round(pk["heures"], 2))
    values["indirect_info_partenaires_reunions"] = str(int(pk["reunions"]))
    values["indirect_info_partenaires_nb"] = str(int(pk["partenaires"]))

    of = rollup_value(coll, "info_organismes_collectives", "Collectives")
    values["indirect_info_of_heures"] = str(round(of["heures"], 2))
    values["indirect_info_of_reunions"] = str(int(of["reunions"]))
    values["indirect_info_of_nb"] = str(int(of["partenaires"]))
    values["mdph_epe_origine"] = str(int(mdph_stats["mdph_epe_origine"]))
    values["mdph_epe_limitrophes"] = str(int(mdph_stats["mdph_epe_limitrophes"]))
    values["mdph_cdaph_origine"] = str(int(mdph_stats["mdph_cdaph_origine"]))
    values["mdph_cdaph_limitrophes"] = str(int(mdph_stats["mdph_cdaph_limitrophes"]))
    values["mdph_groupes_origine"] = str(int(mdph_stats["mdph_groupes_origine"]))
    values["mdph_groupes_limitrophes"] = str(int(mdph_stats["mdph_groupes_limitrophes"]))

    prev_stats = yearly_stats(year - 1)
    values["sorties_annee_n_1"] = str(prev_stats["nb_sorties"])

    return values


def compute_rates(values: dict[str, str]) -> dict[str, float]:
    sorties_n = nval(values.get("sorties_annee_n", "0"))
    repondants = nval(values.get("repondants_suivi", "0"))
    acces = nval(values.get("acces_emploi", "0"))
    presence12 = nval(values.get("presence_emploi_12m", "0"))

    taux_acces = (acces / sorties_n * 100.0) if sorties_n > 0 else 0.0
    taux_presence = (presence12 / acces * 100.0) if acces > 0 else 0.0

    return {
        "sorties_n": sorties_n,
        "repondants": repondants,
        "acces": acces,
        "presence12": presence12,
        "taux_acces": round(taux_acces, 1),
        "taux_presence": round(taux_presence, 1),
    }


@app.route("/annual/<int:year>", methods=["GET", "POST"])
def annual(year: int) -> str | Response:
    defaults = _annual_defaults(year)
    saved = get_answer_map(year)
    values = {**defaults, **saved}

    if request.method == "POST":
        for key, _ in ANNUAL_FIELDS + TEXT_FIELDS:
            raw = request.form.get(key, "")
            set_answer(year, key, normalize_txt(raw))
        flash("Saisie annuelle enregistrée.", "success")
        return redirect(url_for("annual", year=year))

    rates = compute_rates(values)
    coh_nb_sorties = nval(values.get("sorties_definitives", "0"))
    coh_sum_motifs = sum(
        nval(values.get(k, "0"))
        for k in [
            "sortie_motif_depart_volontaire",
            "sortie_motif_sante",
            "sortie_motif_reorientation",
            "sortie_motif_disciplinaire",
            "sortie_motif_objectif",
            "sortie_motif_reprise_emploi",
            "sortie_motif_autres",
            "sortie_motif_je_ne_sais_pas",
        ]
    )
    coherence_ok = abs(coh_nb_sorties - coh_sum_motifs) < 0.0001

    return render_template(
        "annual_form.html",
        year=year,
        values=values,
        annual_fields=ANNUAL_FIELDS,
        text_fields=TEXT_FIELDS,
        preconisations=PRECONISATIONS,
        rates=rates,
        coherence_ok=coherence_ok,
        coh_nb_sorties=coh_nb_sorties,
        coh_sum_motifs=coh_sum_motifs,
        current_year=year,
    )


def _csv_response(filename: str, headers: list[str], rows: list[list[Any]]) -> Response:
    buff = io.StringIO()
    writer = csv.writer(buff, delimiter=";")
    writer.writerow(headers)
    writer.writerows(rows)
    data = buff.getvalue().encode("utf-8-sig")
    return Response(
        data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/export/summary.csv")
def export_summary() -> Response:
    year = int(request.args.get("year", date.today().year))
    stats = yearly_stats(year)
    headers = ["annee", "nb_entrees", "nb_sorties", "actifs_au_31_12", "duree_moyenne_jours_sorties"]
    rows = [[year, stats["nb_entrees"], stats["nb_sorties"], stats["actifs_3112"], stats["duree_moyenne_jours"]]]
    return _csv_response(f"fagerh_resume_{year}.csv", headers, rows)


@app.route("/export/events.csv")
def export_events() -> Response:
    year = int(request.args.get("year", date.today().year))
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    db = get_db()
    rows_db = db.execute(
        """
        SELECT p.nom, p.prenom, p.date_naissance, p.identifiant_local, p.boeth_statut, p.handicap_principal, p.handicap_associe,
               e.date_event, e.type_event, e.type_prestation, e.dispositif, e.modalite, e.motif_sortie, e.preconisation_sortie, e.notes
        FROM events e
        JOIN people p ON p.id = e.person_id
        WHERE e.date_event BETWEEN ? AND ?
        ORDER BY e.date_event ASC, p.nom ASC, p.prenom ASC
        """,
        (start, end),
    ).fetchall()
    headers = [
        "nom", "prenom", "date_naissance", "identifiant_local", "boeth_statut", "handicap_principal", "handicap_associe",
        "date_event", "type_event", "type_prestation", "dispositif", "modalite", "motif_sortie", "preconisation_sortie", "notes",
    ]
    rows = [[r[h] or "" for h in headers] for r in rows_db]
    return _csv_response(f"fagerh_evenements_{year}.csv", headers, rows)


@app.route("/export/annual_full.csv")
def export_annual_full() -> Response:
    year = int(request.args.get("year", date.today().year))
    defaults = _annual_defaults(year)
    saved = get_answer_map(year)
    values = {**defaults, **saved}
    rates = compute_rates(values)
    values["taux_acces_emploi_pct"] = str(rates["taux_acces"])
    values["taux_presence_emploi_pct"] = str(rates["taux_presence"])

    headers = ["annee", "cle", "valeur"]
    rows = [[year, k, v] for k, v in values.items()]
    return _csv_response(f"fagerh_annuel_complet_{year}.csv", headers, rows)


with app.app_context():
    init_db()
    ensure_schema_updates()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
