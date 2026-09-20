# TourneyHub — Frontend Web

Interface web pour TourneyHub, connectée à l'API REST FastAPI définie dans `src/`.

## Structure

```
web/
├── index.html   — Page principale (SPA mono-fichier)
├── styles.css   — Styles (fidèle à tourneyhub_v1_1.html)
├── api.js       — Client API REST (wrapper fetch)
└── app.js       — Logique UI, navigation, interactions
```

## Démarrage rapide

### 1. Démarrez l'API backend

```bash
# Depuis la racine du projet
docker compose up db -d           # Lance PostgreSQL
uv run alembic upgrade head       # Applique les migrations
uv run uvicorn src.api.app:app --reload --port 8000
```

### 2. Ouvrez le frontend

**Option A — Directement dans le navigateur**
```bash
open web/index.html
# ou double-cliquez sur index.html
```

**Option B — Serveur HTTP local (recommandé)**
```bash
cd web
python3 -m http.server 3000
# puis ouvrez http://localhost:3000
```

**Option C — Live Server (VS Code)**
Clic droit sur `index.html` → "Open with Live Server"

## Configuration API

Par défaut, l'application pointe vers `http://localhost:8000/api/v1`.

Pour changer l'URL :
```js
// Dans la console du navigateur
localStorage.setItem('tm_api_base', 'http://mon-serveur:8000/api/v1');
location.reload();
```

## Fonctionnalités

### Tableau de bord
- Métriques globales (total tournois, joueurs, ouverts, terminés)
- Aperçu des derniers tournois avec statut et barre de progression
- Tableau des derniers joueurs inscrits

### Tournois (`GET/POST/PUT/DELETE /api/v1/tournaments`)
- Liste paginée avec filtres (statut, mode) et tri
- Recherche full-text
- Création de tournoi (formulaire complet)
- Détail avec modification (uniquement statut DRAFT)
- Ouverture des inscriptions (DRAFT → OPEN)
- Suppression avec confirmation

### Joueurs (`GET/POST/PUT/DELETE /api/v1/players`)
- Liste paginée avec tri et recherche
- Création de joueur
- Profil avec modification
- Suppression avec confirmation

### API REST
- Documentation des endpoints disponibles

### Discord
- Aperçu des commandes slash disponibles (Phase 1 → 3)
- Configuration des notifications

## Endpoints utilisés

| Méthode | Endpoint | Usage |
|---------|----------|-------|
| GET | `/api/v1/health` | Vérification status API |
| GET | `/api/v1/tournaments` | Liste paginée |
| POST | `/api/v1/tournaments` | Création |
| GET | `/api/v1/tournaments/{id}` | Détail |
| PUT | `/api/v1/tournaments/{id}` | Modification |
| DELETE | `/api/v1/tournaments/{id}` | Suppression |
| POST | `/api/v1/tournaments/{id}/open` | Ouverture |
| GET | `/api/v1/players` | Liste paginée |
| POST | `/api/v1/players` | Création |
| GET | `/api/v1/players/{id}` | Profil |
| PUT | `/api/v1/players/{id}` | Modification |
| DELETE | `/api/v1/players/{id}` | Suppression |

## CORS

L'API est configurée avec `allow_origins=["*"]` dans `src/api/app.py`, donc aucune configuration supplémentaire n'est nécessaire pour le développement local.
