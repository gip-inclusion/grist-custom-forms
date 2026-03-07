# FAGERH Suivi local (V2)

Objectif: permettre une saisie **au fil de l'eau** de 2 volets:
1. suivi individuel des personnes,
2. reunions d'information.
Chaque saisie qualifie le **type de prestation**.

## Ce que couvre cette V2

### 1) Saisie individuelle (tout au long de l'annee)
- Creation/recherche des personnes.
- Mise a jour du profil (BOETH, handicap principal/associe).
- Parcours personne:
  - situation a l'arrivee,
  - type de parcours + date de debut,
  - changement de parcours (avec date de fin du precedent),
  - suspension de parcours,
  - fin de parcours (type + motif),
  - suivi a 12 mois.
- Journal des evenements: entrees/sorties, **type de prestation**, dispositif, modalite, motif de sortie, notes.

### 2) Reunion collective (tout au long de l'annee)
- Type de prestation obligatoire.
- Saisie limitee aux themes d'informations collectives.
- Heures mobilisees
- Nombre de reunions animees
- Nombre de partenaires
- Blocs: info partenaires, info organismes de formation, info personnes, PEC, evaluations pro, MDPH.

### 3) Saisie annuelle complete
- Ecran unique pour renseigner les blocs annuels restants (suspensions, motifs de sorties, MDPH, infos collectives/indirectes, taux...).
- Valeurs pre-remplies automatiquement quand possible (a partir des saisies au fil de l'eau).
- Controle de coherence sorties (sorties declarees vs somme des motifs).
- Calcul automatique des taux:
  - taux d'acces a l'emploi
  - taux de presence en emploi

### 4) Exports
- `resume annuel` CSV
- `evenements` CSV
- `annuel complet` CSV (toutes les cles annuelles)

## Lancer localement
Depuis la racine du repo:

```bash
cd /Users/eric/Dev/grist-custom-forms
uv run flask --app tools/fagerh_suivi_local/app.py run -p 5010
```

Puis ouvrir: `http://localhost:5010`

## Donnees stockees
- Base SQLite locale: `tools/fagerh_suivi_local/data/fagerh_suivi.db`

## Sauvegarde conseillee
Copier regulierement ce fichier `.db` (quotidien ou hebdomadaire) vers un espace securise.

## Process recommande pour les equipes
1. Pendant l'annee: saisir les entrees/sorties + actions collectives.
2. Fin de mois: verifier tableau de bord + corriger oublis.
3. Fin d'annee: ouvrir `Saisie annuelle`, completer les champs restants.
4. Exporter les CSV pour preparation du questionnaire final.

## Limite actuelle
- Le mapping exact 1:1 vers tous les champs techniques du wizard FAGERH reste a finaliser (prochaine passe: export "wizard-ready").
