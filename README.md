# Assistant documentaire IA - démo

Chatbot qui répond aux questions des clients d'une agence immobilière **fictive**
(Rivelune Immobilier, Lyon) à partir de ses documents PDF, en citant ses sources.
Il refuse le hors sujet et n'invente pas quand l'information manque.

Conception détaillée : [docs/CONCEPTION.md](docs/CONCEPTION.md).

## Architecture

```mermaid
flowchart LR
  V[Visiteur] --> F[Front Angular]
  F -->|HTTPS JSON| A[API Flask]
  A --> S[Services RAG + chat]
  S --> I[(Index en mémoire<br/>numpy)]
  S --> E[Mistral embeddings]
  S --> L[Mistral LLM<br/>ministral-14b]
```

Backend Flask en 3 couches :

| Couche | Rôle |
|---|---|
| `app/api/` | Routes, validation (pydantic), format d'erreur unique, rate limiting |
| `app/services/` | Découpage des PDF, recherche hybride (sens + références exactes comme `L-104`), prompt, filtrage des sources citées |
| `app/infra/` | Lecture PDF, clients Mistral, index numpy, quota journalier |

Changer de fournisseur IA = remplacer `llm_client.py` et `embeddings_client.py`.

Pas de base vectorielle : environ 30 morceaux de texte, une recherche numpy prend
moins d'une milliseconde. Au-delà de quelques milliers de morceaux : pgvector ou Qdrant.

## Lancer en local

```sh
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt     # Linux/macOS : .venv/bin/pip
cp .env.example .env                                 # renseigner MISTRAL_API_KEY

python scripts/generate_pdfs.py    # crée les 4 PDF de l'agence fictive
python scripts/build_index.py      # découpe + embeddings -> data/index/
python scripts/eval.py             # 7 questions tests, score attendu 7/7
python wsgi.py                     # API sur http://localhost:5000
```

Tests (sans clé ni réseau, faux clients IA) :

```sh
python -m pytest -q
```

### Front (Angular 21)

```sh
cd frontend
npm install
npm start          # http://localhost:4200, /api passe par le proxy vers Flask (port 5000)
npm test           # tests unitaires (Vitest)
npm run build      # production, dans dist/frontend
```

Angular 21 plutôt que 22 : la 22 exige Node 24.15 ou plus.

| Dossier | Rôle |
|---|---|
| `src/app/core/` | Appels API, conversation (`ChatStore`), réveil du serveur (`ServerStatus`), découpage des renvois `[1]` |
| `src/app/features/assistant/` | Page de l'assistant : bulles, sources, documents, saisie, états d'erreur |
| `src/app/features/how-it-works/` | Page "Comment ça marche", à l'identité du développeur |
| `src/styles.css` | Tokens du design system Rivelune (thèmes Jour et Nuit) |

L'URL de l'API en production est dans `src/environments/environment.ts`.

## API

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/api/health` | État et nombre de morceaux indexés |
| GET | `/api/documents` | Liste des documents de l'agence |
| GET | `/api/documents/<id>/file` | Le PDF source |
| POST | `/api/ask` | `{question, history}` -> `{answer, sources, latency_ms}` |

Erreurs : `{"error": {"code", "message"}}` avec `invalid_question` (400),
`rate_limited` (429), `demo_paused` (503, quota du jour atteint),
`llm_unavailable` (502).

## Sécurité et coûts

- Clé API uniquement côté serveur (`.env`, jamais commité).
- Rate limit par IP (20/heure, 5/minute) et quota global de 300 questions par jour.
- Réponses limitées à 400 tokens, plafond de dépense à régler chez Mistral.
- CORS limité au domaine du front, `ProxyFix` pour la vraie IP derrière Render.
- Le prompt impose de répondre uniquement depuis les extraits et ignore les
  demandes de changement de rôle.

## Déploiement

En ligne sur https://demo-assistant.maximenkengato.com, dans l'app Sevalla qui
héberge toutes les démos du portfolio (dépôt `portfolio-demos`, dossier
`sevalla/`) : ce dépôt y est figé par `vendor.sh`, le front est compilé dans
l'image et servi par nginx avec l'API sur le même domaine.

- API : `gunicorn wsgi:app --workers 1 --threads 4`
  (1 worker : le rate limit et le quota sont en mémoire)
- Variable obligatoire : `MISTRAL_API_KEY` ; les autres ont une valeur par défaut (`.env.example`)
- L'index `data/index/` est commité : aucun recalcul au démarrage.
- Python 3.11 ou plus (numpy 2.4).
