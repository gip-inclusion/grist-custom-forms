# Déploiements EURES / FAGERH

Ce dépôt sert deux applications Scalingo qui ne doivent pas être poussées de la même façon.

## Règle

- EURES beta se déploie vers `scalingo-eures` (`eures-beta.git`).
- FAGERH se déploie vers `scalingo` (`fagerh.git`).
- Ne jamais pousser manuellement vers Scalingo sans passer par les scripts ci-dessous.

## EURES

Contrôle seul :

```bash
node tools/deploy-eures.mjs
```

Déploiement :

```bash
node tools/deploy-eures.mjs --push
```

Le script vérifie :

- que le dépôt est propre ;
- que le remote `scalingo-eures` pointe vers `eures-beta.git` ;
- que les marqueurs critiques EURES sont présents ;
- que `app.py` compile.

## FAGERH

Important : FAGERH doit être déployé depuis une branche FAGERH isolée, pas depuis `main` si `main` contient les fichiers EURES.

Contrôle seul :

```bash
node tools/deploy-fagerh.mjs
```

Déploiement :

```bash
node tools/deploy-fagerh.mjs --push
```

Le script vérifie :

- que le dépôt est propre ;
- que le remote `scalingo` pointe vers `fagerh.git` ;
- que les pages Analytics / Observatoire / Livret existent ;
- que les liens admin FAGERH existent ;
- que les routes Flask FAGERH existent ;
- que le module `fagerh_analytics` existe ;
- que la branche ne contient pas les fichiers EURES principaux ;
- que `app.py` compile.

## Pourquoi cette règle existe

FAGERH et EURES ont des historiques de déploiement divergents. Un push manuel vers le mauvais remote peut faire disparaître des pages ou mélanger les deux périmètres.

Ces scripts ne garantissent pas qu’aucun bug métier n’existera jamais, mais ils bloquent le type de régression déjà rencontré : disparition de pages, routes ou liens critiques après déploiement.
