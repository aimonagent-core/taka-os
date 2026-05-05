# TAKA OS — Blueprint Technique

## Section 2 : API REST & Sécurité

---

## 1. Spécification API REST Complète

### Conventions Globales

| Aspect | Spécification |
|--------|---------------|
| **Format** | JSON strict (`Content-Type: application/json`) |
| **Encodage** | UTF-8 |
| **Dates** | ISO 8601 (ex: `2025-01-15T14:30:00Z`) |
| **Pagination** | `limit` (max 100, défaut 20) + `offset` |
| **Tri** | `sort_by` (champ) + `sort_order` (`asc` ou `desc`) |
| **Authentification** | Header `Authorization: Bearer <access_token>` |
| **Refresh Token** | Cookie `refresh_token` (httpOnly, Secure, SameSite=Strict) |
| **Idempotence** | Header `Idempotency-Key` pour POST sensibles |

### Structure de Réponse Uniforme

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2025-01-15T14:30:00Z",
    "request_id": "req_abc123",
    "pagination": {
      "limit": 20,
      "offset": 0,
      "total": 150
    }
  }
}
```

### Structure d'Erreur Uniforme

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Champ 'email' invalide",
    "details": [
      { "field": "email", "issue": "Format d'email invalide" }
    ],
    "request_id": "req_abc123",
    "timestamp": "2025-01-15T14:30:00Z"
  }
}
```

### Codes d'Erreur Internes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | Token manquant ou invalide | 401 |
| `TOKEN_EXPIRED` | Access token expiré | 401 |
| `TOKEN_REVOKED` | Token révoqué (logout) | 401 |
| `INSUFFICIENT_PERMISSIONS` | Rôle insuffisant | 403 |
| `CROSS_TENANT_ACCESS` | Tentative d'accès à un autre tenant | 403 |
| `RESOURCE_NOT_FOUND` | Ressource inexistante | 404 |
| `VALIDATION_ERROR` | Données d'entrée invalides | 422 |
| `RATE_LIMIT_EXCEEDED` | Trop de requêtes | 429 |
| `INTERNAL_ERROR` | Erreur serveur | 500 |
| `SERVICE_UNAVAILABLE` | Service temporairement indisponible | 503 |

---

## 1.1 Endpoints — Authentification (`/auth`)

### POST `/auth/dev-login` — Login Développement (sans mot de passe)

> ⚠️ **DANGER** — Endpoint activé uniquement si `ENV=development`. Retourne 404 en production.

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Authentification de développement sans mot de passe. Permet aux développeurs de tester l'API sans configurer de credentials. |
| **Rôle requis** | Aucun (public, dev uniquement) |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `email` | string | Oui | Email de l'utilisateur dev |
| `tenant_id` | string (UUID) | Non | Tenant à utiliser (défaut: tenant dev) |

**Exemple Requête :**
```json
POST /auth/dev-login
Content-Type: application/json

{
  "email": "dev@taka.local",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_001",
      "email": "dev@taka.local",
      "full_name": "Dev User",
      "role": "admin",
      "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  },
  "meta": { "timestamp": "2025-01-15T14:30:00Z", "request_id": "req_001" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Succès — JWT retourné |
| 400 | `ENV != development` — endpoint désactivé |
| 404 | Utilisateur non trouvé |
| 422 | Email invalide |

---

### POST `/auth/login` — Authentification

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Authentification avec email et mot de passe (bcrypt). Retourne un access token (JWT) et un refresh token (cookie httpOnly). |
| **Rôle requis** | Aucun (public) |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `email` | string | Oui | Email de l'utilisateur |
| `password` | string | Oui | Mot de passe (8-128 caractères) |

**Exemple Requête :**
```json
POST /auth/login
Content-Type: application/json

{
  "email": "manager@client.fr",
  "password": "SuperSecret123!"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfMDAxIiwidGVuYW50X2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwicm9sZSI6Im1hbmFnZXIiLCJleHAiOjE3MDUzMjYwMDAsImlhdCI6MTcwNTMyNTEwMH0...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_001",
      "email": "manager@client.fr",
      "full_name": "Jean Dupont",
      "role": "manager",
      "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
      "tenant_name": "Acme Corp"
    }
  },
  "meta": { "timestamp": "2025-01-15T14:30:00Z", "request_id": "req_002" }
}
```

**Headers de Réponse :**
```
Set-Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh; Max-Age=604800
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Authentification réussie |
| 400 | Compte désactivé ou verrouillé |
| 401 | Email ou mot de passe incorrect |
| 422 | Validation échouée (email malformé, password trop court) |
| 429 | Trop de tentatives (rate limiting) |
| 500 | Erreur serveur |

**Sécurité :**
- Comparaison bcrypt en **constant-time** pour prévenir les timing attacks
- Incrémentation du compteur d'échecs après chaque tentative → lockout après 5 échecs
- Audit log de chaque tentative (succès + échec)
- Rate limit : 5 req/min par IP

---

### POST `/auth/refresh` — Rafraîchissement du JWT

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Échange un refresh token valide (cookie) contre un nouveau access token + nouveau refresh token (rotation). |
| **Rôle requis** | Aucun (refresh token requis) |

**Paramètres :** Aucun (le refresh token est lu depuis le cookie `refresh_token`)

**Exemple Requête :**
```
POST /auth/refresh
Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.NOUVEAU...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "meta": { "timestamp": "2025-01-15T14:35:00Z", "request_id": "req_003" }
}
```

**Headers de Réponse :**
```
Set-Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.NOUVEAU...; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh; Max-Age=604800
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Refresh réussi — nouveau access token |
| 401 | Refresh token manquant, invalide ou expiré |
| 401 | Refresh token révoqué (logout effectué) |
| 401 | Refresh token déjà utilisé (détection de vol) |

**Sécurité — Rotation des Refresh Tokens :**
- Chaque refresh invalide l'ancien token et en génère un nouveau
- Si un refresh token déjà utilisé est représenté → révocation immédiate de toute la famille de tokens + alerte sécurité
- `token_family` UUID lié ensemble tous les refresh tokens d'une session

---

### GET `/auth/me` — Profil Utilisateur Connecté

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Retourne le profil complet de l'utilisateur authentifié. |
| **Rôle requis** | `viewer`, `manager`, `admin` (tout rôle authentifié) |

**Paramètres :** Aucun (auth via Bearer token)

**Exemple Requête :**
```
GET /auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "usr_001",
    "email": "manager@client.fr",
    "full_name": "Jean Dupont",
    "role": "manager",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_name": "Acme Corp",
    "is_active": true,
    "created_at": "2024-12-01T10:00:00Z",
    "last_login_at": "2025-01-15T14:30:00Z",
    "permissions": ["tenders:read", "tenders:create", "tenders:update", "documents:read", "documents:create", "pipeline:read", "memory:read", "memory:create"]
  },
  "meta": { "timestamp": "2025-01-15T14:30:00Z", "request_id": "req_004" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Profil retourné |
| 401 | Token manquant ou invalide |
| 401 | Token expiré |
| 403 | Compte désactivé |

---

### POST `/auth/logout` — Déconnexion

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Révoque le refresh token (cookie) et invalide l'access token (blacklist). |
| **Rôle requis** | `viewer`, `manager`, `admin` (tout rôle authentifié) |

**Paramètres :** Aucun

**Exemple Requête :**
```
POST /auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": { "message": "Déconnexion réussie" },
  "meta": { "timestamp": "2025-01-15T14:40:00Z", "request_id": "req_005" }
}
```

**Headers de Réponse :**
```
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Déconnexion réussie — tokens révoqués |
| 401 | Token manquant |
| 500 | Erreur lors de la révocation |

---

## 1.2 Endpoints — Appels d'Offres (`/tenders`)

### GET `/tenders` — Liste des Appels d'Offres

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Liste paginée des appels d'offres du tenant courant avec filtres avancés. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `limit` | integer | Non | Nombre de résultats (max 100) | 20 |
| `offset` | integer | Non | Offset pour pagination | 0 |
| `search` | string | Non | Recherche textuelle (titre, description, client) | — |
| `pipeline_stage` | string | Non | Filtrer par stage (e.g. `new`, `qualified`, `submitted`) | — |
| `qualification_result` | string | Non | `eligible`, `ineligible`, `pending` | — |
| `deadline_from` | ISO date | Non | Date limite de réponse (début) | — |
| `deadline_to` | ISO date | Non | Date limite de réponse (fin) | — |
| `cpv_code` | string | Non | Code CPV (Common Procurement Vocabulary) | — |
| `sort_by` | string | Non | Champ de tri (`created_at`, `deadline`, `title`, `estimated_value`) | `created_at` |
| `sort_order` | string | Non | `asc` ou `desc` | `desc` |
| `is_archived` | boolean | Non | Inclure les soft-deleted | `false` |

**Exemple Requête :**
```
GET /tenders?limit=10&offset=0&search=informatique&pipeline_stage=new&deadline_from=2025-02-01&sort_by=deadline&sort_order=asc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "tdr_001",
        "title": "Fourniture de matériel informatique — Lot 1",
        "reference_number": "2025-INFORMATIQUE-042",
        "issuing_organization": "Ministère de la Transition Écologique",
        "description": "Fourniture et installation de postes de travail...",
        "pipeline_stage": "new",
        "qualification_result": "pending",
        "estimated_value": 150000.00,
        "currency": "EUR",
        "deadline": "2025-02-15T17:00:00Z",
        "cpv_code": "30210000",
        "cpv_description": "Matériel informatique",
        "notice_url": "https://www.boamp.fr/avis/20250115042",
        "document_count": 3,
        "created_at": "2025-01-10T09:00:00Z",
        "updated_at": "2025-01-12T14:30:00Z"
      },
      {
        "id": "tdr_002",
        "title": "Développement d'une application métier",
        "reference_number": "2025-DEV-018",
        "issuing_organization": "Région Occitanie",
        "description": "Conception et développement d'une application web...",
        "pipeline_stage": "qualified",
        "qualification_result": "eligible",
        "estimated_value": 250000.00,
        "currency": "EUR",
        "deadline": "2025-03-01T12:00:00Z",
        "cpv_code": "72267000",
        "cpv_description": "Services de développement de logiciels",
        "notice_url": "https://www.marches-publics.gov.fr/2025018018",
        "document_count": 5,
        "created_at": "2025-01-08T11:00:00Z",
        "updated_at": "2025-01-14T16:45:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T14:30:00Z",
    "request_id": "req_010",
    "pagination": { "limit": 10, "offset": 0, "total": 47 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Liste retournée (peut être vide) |
| 401 | Non authentifié |
| 403 | Cross-tenant détecté |
| 422 | Paramètre de filtre invalide |

---

### POST `/tenders` — Création d'un Appel d'Offres

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Création manuelle d'un appel d'offres. Le `tenant_id` est injecté automatiquement depuis le JWT. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Body) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `title` | string | Oui | Titre de l'AO | 5-500 caractères |
| `reference_number` | string | Non | Numéro de référence | 1-100 caractères, unique par tenant |
| `issuing_organization` | string | Non | Organisme émetteur | 1-300 caractères |
| `description` | string | Non | Description | Max 50000 caractères |
| `deadline` | ISO date | Non | Date limite de réponse | Doit être dans le futur |
| `estimated_value` | decimal | Non | Valeur estimée | ≥ 0 |
| `currency` | string | Non | Devise (ISO 4217) | `EUR` par défaut |
| `cpv_code` | string | Non | Code CPV | 8 caractères max |
| `notice_url` | string | Non | URL de l'avis | URL valide |
| `pipeline_stage` | string | Non | Stage initial | Défaut: `new` |

**Exemple Requête :**
```json
POST /tenders
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "title": "Maintenance des équipements réseau 2025",
  "reference_number": "2025-RESEAU-003",
  "issuing_organization": "Département de la Gironde",
  "description": "Prestation de maintenance préventive et corrective...",
  "deadline": "2025-04-30T17:00:00Z",
  "estimated_value": 80000.00,
  "currency": "EUR",
  "cpv_code": "32561000",
  "notice_url": "https://www.boamp.fr/avis/20250003"
}
```

**Exemple Réponse (201) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_003",
    "title": "Maintenance des équipements réseau 2025",
    "reference_number": "2025-RESEAU-003",
    "issuing_organization": "Département de la Gironde",
    "description": "Prestation de maintenance préventive et corrective...",
    "pipeline_stage": "new",
    "qualification_result": "pending",
    "estimated_value": 80000.00,
    "currency": "EUR",
    "deadline": "2025-04-30T17:00:00Z",
    "cpv_code": "32561000",
    "notice_url": "https://www.boamp.fr/avis/20250003",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "document_count": 0,
    "created_at": "2025-01-15T14:45:00Z",
    "updated_at": "2025-01-15T14:45:00Z"
  },
  "meta": { "timestamp": "2025-01-15T14:45:00Z", "request_id": "req_011" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 201 | Création réussie |
| 400 | `reference_number` déjà existant pour ce tenant |
| 401 | Non authentifié |
| 403 | Rôle `viewer` — insuffisant |
| 422 | Validation échouée |
| 500 | Erreur base de données |

---

### GET `/tenders/{id}` — Détail d'un Appel d'Offres

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Détail complet d'un AO avec documents associés et historique des changements. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'appel d'offres |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `include_documents` | boolean | Non | Inclure les documents | `true` |
| `include_history` | boolean | Non | Inclure l'historique | `true` |

**Exemple Requête :**
```
GET /tenders/tdr_001?include_documents=true&include_history=true
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_001",
    "title": "Fourniture de matériel informatique — Lot 1",
    "reference_number": "2025-INFORMATIQUE-042",
    "issuing_organization": "Ministère de la Transition Écologique",
    "description": "Fourniture et installation de postes de travail...",
    "pipeline_stage": "qualified",
    "qualification_result": "eligible",
    "qualification_summary": "L'AO correspond aux critères de l'entreprise. Métier aligné (IT), valeur dans la fourchette cible, délai compatible.",
    "estimated_value": 150000.00,
    "currency": "EUR",
    "deadline": "2025-02-15T17:00:00Z",
    "cpv_code": "30210000",
    "cpv_description": "Matériel informatique",
    "notice_url": "https://www.boamp.fr/avis/20250115042",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_archived": false,
    "created_at": "2025-01-10T09:00:00Z",
    "updated_at": "2025-01-14T16:30:00Z",
    "documents": [
      {
        "id": "doc_001",
        "filename": "avis-reglemente.pdf",
        "mime_type": "application/pdf",
        "file_size": 2457600,
        "uploaded_at": "2025-01-10T09:15:00Z",
        "uploaded_by": "Jean Dupont",
        "parsed": true,
        "parse_status": "completed"
      },
      {
        "id": "doc_002",
        "filename": "dce-complete.zip",
        "mime_type": "application/zip",
        "file_size": 15728640,
        "uploaded_at": "2025-01-11T10:30:00Z",
        "uploaded_by": "Marie Martin",
        "parsed": false,
        "parse_status": "pending"
      }
    ],
    "history": [
      {
        "action": "created",
        "actor": "system@taka.io",
        "timestamp": "2025-01-10T09:00:00Z",
        "details": "AO importé automatiquement depuis BOAMP"
      },
      {
        "action": "stage_changed",
        "actor": "manager@client.fr",
        "timestamp": "2025-01-12T14:30:00Z",
        "details": { "from": "new", "to": "analyzing" }
      },
      {
        "action": "qualified",
        "actor": "agent-qualifier@taka.io",
        "timestamp": "2025-01-14T16:30:00Z",
        "details": { "result": "eligible", "confidence": 0.92 }
      }
    ]
  },
  "meta": { "timestamp": "2025-01-15T14:30:00Z", "request_id": "req_012" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Détail retourné |
| 401 | Non authentifié |
| 403 | Cross-tenant (l'AO n'appartient pas au tenant du JWT) |
| 404 | AO non trouvé ou soft-deleted |

---

### PUT `/tenders/{id}` — Mise à Jour d'un Appel d'Offres

| Attribut | Valeur |
|----------|--------|
| **Méthode** | PUT |
| **Description** | Mise à jour complète (full replace) d'un AO. Champs non fournis = écrasés à NULL. Utiliser PATCH pour mise à jour partielle. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Paramètres (Body) :** Mêmes champs que POST `/tenders`, tous optionnels (partial update via PUT — on garde les champs non fournis).

> **Note** : L'implémentation utilise un merge (PATCH sémantique) — seuls les champs fournis sont mis à jour.

**Exemple Requête :**
```json
PUT /tenders/tdr_001
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "pipeline_stage": "submitted",
  "qualification_summary": "Dossier soumis le 15/01. Attente de réponse."
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_001",
    "title": "Fourniture de matériel informatique — Lot 1",
    "pipeline_stage": "submitted",
    "qualification_result": "eligible",
    "qualification_summary": "Dossier soumis le 15/01. Attente de réponse.",
    "updated_at": "2025-01-15T15:00:00Z"
  },
  "meta": { "timestamp": "2025-01-15T15:00:00Z", "request_id": "req_013" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Mise à jour réussie |
| 400 | `reference_number` déjà utilisé |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO non trouvé |
| 422 | Validation échouée |
| 500 | Erreur base de données |

---

### DELETE `/tenders/{id}` — Suppression (Soft Delete)

| Attribut | Valeur |
|----------|--------|
| **Méthode** | DELETE |
| **Description** | Soft delete d'un AO (marqué `is_archived=true`). Les données restent en base pour l'audit. Un hard delete nécessite le rôle admin + confirmation explicite. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `hard` | boolean | Non | Force la suppression définitive (admin uniquement) |

**Exemple Requête :**
```
DELETE /tenders/tdr_001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_001",
    "is_archived": true,
    "archived_at": "2025-01-15T15:30:00Z",
    "archived_by": "manager@client.fr",
    "message": "Appel d'offres archivé avec succès"
  },
  "meta": { "timestamp": "2025-01-15T15:30:00Z", "request_id": "req_014" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Soft delete réussi |
| 204 | Hard delete réussi (aucun body) |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO non trouvé |
| 403 | Hard delete demandé sans rôle admin |

---

### PUT `/tenders/{id}/stage` — Changement de Pipeline Stage

| Attribut | Valeur |
|----------|--------|
| **Méthode** | PUT |
| **Description** | Transition d'un AO vers un nouveau stage du pipeline. Vérifie que le stage cible existe pour le tenant courant. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `stage` | string | Oui | Nouveau stage (doit exister dans `pipeline_stages`) |
| `reason` | string | Non | Motif du changement (max 1000 caractères) |

**Exemple Requête :**
```json
PUT /tenders/tdr_001/stage
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "stage": "qualified",
  "reason": "Qualification positive — tous les critères sont remplis"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_001",
    "pipeline_stage": "qualified",
    "previous_stage": "new",
    "stage_changed_at": "2025-01-15T16:00:00Z",
    "stage_changed_by": "manager@client.fr",
    "reason": "Qualification positive — tous les critères sont remplis"
  },
  "meta": { "timestamp": "2025-01-15T16:00:00Z", "request_id": "req_015" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Transition réussie |
| 400 | Stage cible inexistant pour ce tenant |
| 400 | Transition non autorisée (workflow invalide) |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO non trouvé |
| 422 | Validation échouée |

---

### POST `/tenders/{id}/qualify` — Lancer la Qualification (Agent Qualifieur)

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Déclenche l'agent qualifieur en arrière-plan. Analyse l'AO et les documents associés pour déterminer l'éligibilité. Retourne immédiatement un job ID pour suivi. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Exemple Requête :**
```
POST /tenders/tdr_001/qualify
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (202) :**
```json
{
  "success": true,
  "data": {
    "job_id": "job_001",
    "status": "queued",
    "message": "Qualification démarrée. Utilisez GET /tenders/tdr_001/qualification pour suivre la progression.",
    "estimated_duration_seconds": 30
  },
  "meta": { "timestamp": "2025-01-15T16:05:00Z", "request_id": "req_016" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 202 | Qualification acceptée (en file d'attente) |
| 400 | Qualification déjà en cours pour cet AO |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO non trouvé |
| 409 | Aucun document à analyser |
| 500 | Erreur lors du déclenchement de l'agent |

---

### GET `/tenders/{id}/qualification` — Résultat de Qualification

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Retourne le résultat complet de la dernière qualification d'un AO. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Exemple Requête :**
```
GET /tenders/tdr_001/qualification
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) — Qualification terminée :**
```json
{
  "success": true,
  "data": {
    "qualification_id": "qual_001",
    "tender_id": "tdr_001",
    "status": "completed",
    "result": "eligible",
    "confidence": 0.92,
    "started_at": "2025-01-15T16:05:00Z",
    "completed_at": "2025-01-15T16:05:28Z",
    "criteria_analysis": [
      {
        "criterion": "métier_aligné",
        "passed": true,
        "confidence": 0.98,
        "explanation": "Le code CPV 30210000 (Matériel informatique) correspond au cœur de métier."
      },
      {
        "criterion": "seuils_financiers",
        "passed": true,
        "confidence": 0.95,
        "explanation": "Valeur estimée (150k€) dans la fourchette acceptable (50k€ - 500k€)."
      },
      {
        "criterion": "délais_réalisables",
        "passed": true,
        "confidence": 0.88,
        "explanation": "Délai de 35 jours suffisant pour préparer la réponse."
      },
      {
        "criterion": "critères_techniques",
        "passed": true,
        "confidence": 0.85,
        "explanation": "Tous les critères techniques sont satisfaits."
      }
    ],
    "overall_summary": "Cet AO est fortement recommandé. Score de confiance élevé (92%).",
    "raw_agent_output": "[sortie brute du LLM — tronquée si > 10000 caractères]"
  },
  "meta": { "timestamp": "2025-01-15T16:10:00Z", "request_id": "req_017" }
}
```

**Exemple Réponse (200) — Qualification en cours :**
```json
{
  "success": true,
  "data": {
    "qualification_id": "qual_001",
    "tender_id": "tdr_001",
    "status": "running",
    "result": null,
    "started_at": "2025-01-15T16:05:00Z",
    "completed_at": null,
    "progress_percent": 45,
    "current_step": "Analyse des critères techniques..."
  },
  "meta": { "timestamp": "2025-01-15T16:06:00Z", "request_id": "req_018" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Résultat retourné (status: completed / running / failed) |
| 401 | Non authentifié |
| 403 | Cross-tenant |
| 404 | AO non trouvé OU aucune qualification lancée |

---

## 1.3 Endpoints — Documents (`/documents`)

### POST `/tenders/{id}/documents` — Upload de Document

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Content-Type** | `multipart/form-data` |
| **Description** | Upload d'un document associé à un AO. Validation stricte du type MIME et des magic bytes. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO parent |

**Paramètres (Body — multipart) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `file` | File | Oui | Fichier à uploader | Max 50MB, types autorisés vérifiés |
| `description` | string | Non | Description du document | Max 500 caractères |
| `document_type` | string | Non | `notice`, `dce`, `cctp`, `rc`, `other` | Énuméré |

**Types MIME Autorisés :**

| Extension | MIME Type | Magic Bytes |
|-----------|-----------|-------------|
| `.pdf` | `application/pdf` | `%PDF-` |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `PK\x03\x04` |
| `.doc` | `application/msword` | `\xD0\xCF\x11\xE0` |
| `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `PK\x03\x04` |
| `.xls` | `application/vnd.ms-excel` | `\xD0\xCF\x11\xE0` |
| `.zip` | `application/zip` | `PK\x03\x04` |
| `.txt` | `text/plain` | — |
| `.csv` | `text/csv` | — |

**Exemple Requête :**
```
POST /tenders/tdr_001/documents
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="dce-complete.pdf"
Content-Type: application/pdf

[binary data]
------WebKitFormBoundary
Content-Disposition: form-data; name="description"

Dossier de consultation des entreprises complet
------WebKitFormBoundary
Content-Disposition: form-data; name="document_type"

dce
------WebKitFormBoundary--
```

**Exemple Réponse (201) :**
```json
{
  "success": true,
  "data": {
    "id": "doc_003",
    "tender_id": "tdr_001",
    "filename": "dce-complete.pdf",
    "original_filename": "dce-complete.pdf",
    "mime_type": "application/pdf",
    "file_size": 5242880,
    "file_size_human": "5.0 MB",
    "description": "Dossier de consultation des entreprises complet",
    "document_type": "dce",
    "storage_path": "tenants/550e8400-e29b-41d4-a716-446655440000/tenders/tdr_001/doc_003_dce-complete.pdf",
    "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "parsed": false,
    "parse_status": "pending",
    "uploaded_by": "manager@client.fr",
    "uploaded_at": "2025-01-15T16:30:00Z"
  },
  "meta": { "timestamp": "2025-01-15T16:30:00Z", "request_id": "req_020" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 201 | Upload réussi |
| 400 | Type de fichier non autorisé |
| 400 | Fichier trop volumineux (> 50MB) |
| 400 | Magic bytes ne correspondent pas à l'extension |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO parent non trouvé |
| 413 | Payload trop grand |
| 422 | Paramètre `document_type` invalide |

---

### GET `/documents/{id}` — Détail d'un Document

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Métadonnées d'un document (sans le contenu binaire). |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID du document |

**Exemple Requête :**
```
GET /documents/doc_003
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "doc_003",
    "tender_id": "tdr_001",
    "filename": "dce-complete.pdf",
    "original_filename": "dce-complete.pdf",
    "mime_type": "application/pdf",
    "file_size": 5242880,
    "file_size_human": "5.0 MB",
    "description": "Dossier de consultation des entreprises complet",
    "document_type": "dce",
    "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "parsed": true,
    "parse_status": "completed",
    "parse_result": {
      "text_extracted": true,
      "pages_count": 45,
      "word_count": 15230,
      "extracted_sections": ["objet", "prix", "délai", "critères_attribution"]
    },
    "uploaded_by": "manager@client.fr",
    "uploaded_at": "2025-01-15T16:30:00Z"
  },
  "meta": { "timestamp": "2025-01-15T16:35:00Z", "request_id": "req_021" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Détail retourné |
| 401 | Non authentifié |
| 403 | Cross-tenant |
| 404 | Document non trouvé |

---

### GET `/documents/{id}/download` — Téléchargement du Fichier

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Téléchargement du fichier binaire. Retourne le fichier avec le bon Content-Type. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID du document |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `disposition` | string | Non | `attachment` (force download) ou `inline` | `attachment` |

**Exemple Requête :**
```
GET /documents/doc_003/download?disposition=attachment
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Réponse (200) :**
```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="dce-complete.pdf"
Content-Length: 5242880
X-Checksum-Sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

[binary data]
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Fichier retourné |
| 401 | Non authentifié |
| 403 | Cross-tenant |
| 404 | Document ou fichier non trouvé |
| 410 | Fichier supprimé du stockage |

---

### DELETE `/documents/{id}` — Suppression d'un Document

| Attribut | Valeur |
|----------|--------|
| **Méthode** | DELETE |
| **Description** | Suppression d'un document (fichier + métadonnées). Suppression physique du fichier de stockage. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID du document |

**Exemple Requête :**
```
DELETE /documents/doc_003
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "doc_003",
    "deleted": true,
    "file_removed": true,
    "deleted_by": "manager@client.fr",
    "deleted_at": "2025-01-15T17:00:00Z"
  },
  "meta": { "timestamp": "2025-01-15T17:00:00Z", "request_id": "req_022" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Suppression réussie |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | Document non trouvé |

---

### POST `/documents/{id}/parse` — Lancer le Parsing Asynchrone

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Déclenche le parsing asynchrone d'un document (extraction de texte, structuration). Retourne un job ID. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID du document |

**Exemple Requête :**
```
POST /documents/doc_003/parse
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (202) :**
```json
{
  "success": true,
  "data": {
    "job_id": "job_002",
    "document_id": "doc_003",
    "status": "queued",
    "message": "Parsing démarré. Le document sera analysé en arrière-plan.",
    "estimated_duration_seconds": 15
  },
  "meta": { "timestamp": "2025-01-15T17:05:00Z", "request_id": "req_023" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 202 | Parsing accepté (en file d'attente) |
| 400 | Parsing déjà en cours ou déjà complété |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | Document non trouvé |
| 409 | Type de fichier non pris en charge pour le parsing |

---

## 1.4 Endpoints — Pipeline (`/pipeline-stages`)

### GET `/pipeline-stages` — Liste des Stages du Tenant

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Retourne les stages du pipeline configurés pour le tenant courant, dans l'ordre. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Exemple Requête :**
```
GET /pipeline-stages
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "stages": [
      { "id": "stage_001", "name": "new", "label": "Nouveau", "color": "#3498db", "order": 1, "is_default": true },
      { "id": "stage_002", "name": "analyzing", "label": "En analyse", "color": "#f39c12", "order": 2, "is_default": false },
      { "id": "stage_003", "name": "qualified", "label": "Qualifié", "color": "#2ecc71", "order": 3, "is_default": false },
      { "id": "stage_004", "name": "submitted", "label": "Soumis", "color": "#9b59b6", "order": 4, "is_default": false },
      { "id": "stage_005", "name": "won", "label": "Remporté", "color": "#27ae60", "order": 5, "is_default": false },
      { "id": "stage_006", "name": "lost", "label": "Perdu", "color": "#e74c3c", "order": 6, "is_default": false },
      { "id": "stage_007", "name": "abandoned", "label": "Abandonné", "color": "#95a5a6", "order": 7, "is_default": false }
    ]
  },
  "meta": { "timestamp": "2025-01-15T17:10:00Z", "request_id": "req_030" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Liste retournée |
| 401 | Non authentifié |

---

### PUT `/pipeline-stages/reorder` — Réordonner les Stages

| Attribut | Valeur |
|----------|--------|
| **Méthode** | PUT |
| **Description** | Réordonne les stages du pipeline. L'ordre détermine le flux de travail. |
| **Rôle requis** | `admin` uniquement |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `stage_orders` | array | Oui | Liste d'objets `{id, order}` |

**Exemple Requête :**
```json
PUT /pipeline-stages/reorder
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "stage_orders": [
    { "id": "stage_001", "order": 1 },
    { "id": "stage_002", "order": 2 },
    { "id": "stage_003", "order": 3 },
    { "id": "stage_004", "order": 4 },
    { "id": "stage_006", "order": 5 },
    { "id": "stage_005", "order": 6 },
    { "id": "stage_007", "order": 7 }
  ]
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "stages": [
      { "id": "stage_001", "name": "new", "label": "Nouveau", "order": 1 },
      { "id": "stage_002", "name": "analyzing", "label": "En analyse", "order": 2 },
      { "id": "stage_003", "name": "qualified", "label": "Qualifié", "order": 3 },
      { "id": "stage_004", "name": "submitted", "label": "Soumis", "order": 4 },
      { "id": "stage_006", "name": "lost", "label": "Perdu", "order": 5 },
      { "id": "stage_005", "name": "won", "label": "Remporté", "order": 6 },
      { "id": "stage_007", "name": "abandoned", "label": "Abandonné", "order": 7 }
    ]
  },
  "meta": { "timestamp": "2025-01-15T17:15:00Z", "request_id": "req_031" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Réordonnancement réussi |
| 400 | Un stage ID n'existe pas pour ce tenant |
| 400 | Ordres en doublon |
| 401 | Non authentifié |
| 403 | Rôle non-admin |
| 422 | Structure invalide |

---

## 1.5 Endpoints — Mémoire Vectorielle (`/memory`)

### POST `/memory/search` — Recherche par Similarité

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Recherche sémantique dans la mémoire vectorielle : la requête textuelle est convertie en embedding puis recherchée via pgvector (similarity search cosine). |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Body) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `query` | string | Oui | Requête textuelle | 1-1000 caractères |
| `limit` | integer | Non | Nombre de résultats (max 50) | 1-50, défaut: 10 |
| `threshold` | float | Non | Score minimum de similarité | 0.0-1.0, défaut: 0.7 |
| `filter_type` | string | Non | Filtrer par type d'entrée | `tender`, `document`, `qualification`, `company_knowledge` |
| `filter_tender_id` | string | Non | Restreindre à un AO spécifique | UUID valide |

**Exemple Requête :**
```json
POST /memory/search
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "query": "matériel informatique et prestations de maintenance réseau",
  "limit": 10,
  "threshold": 0.75,
  "filter_type": "tender"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "query_embedding_duration_ms": 245,
    "results": [
      {
        "id": "mem_001",
        "content": "Fourniture de matériel informatique — Lot 1. Postes de travail, écrans, claviers...",
        "source_type": "tender",
        "source_id": "tdr_001",
        "source_title": "Fourniture de matériel informatique — Lot 1",
        "similarity_score": 0.92,
        "metadata": {
          "tender_reference": "2025-INFORMATIQUE-042",
          "issuing_organization": "Ministère de la Transition Écologique",
          "deadline": "2025-02-15T17:00:00Z"
        },
        "created_at": "2025-01-10T09:05:00Z"
      },
      {
        "id": "mem_002",
        "content": "Maintenance préventive et corrective des équipements réseau et informatiques...",
        "source_type": "tender",
        "source_id": "tdr_003",
        "source_title": "Maintenance des équipements réseau 2025",
        "similarity_score": 0.84,
        "metadata": {
          "tender_reference": "2025-RESEAU-003",
          "issuing_organization": "Département de la Gironde",
          "deadline": "2025-04-30T17:00:00Z"
        },
        "created_at": "2025-01-15T14:50:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T17:20:00Z",
    "request_id": "req_040",
    "pagination": { "limit": 10, "offset": 0, "total": 2 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Résultats retournés (liste peut être vide) |
| 401 | Non authentifié |
| 422 | `query` vide ou trop long |
| 500 | Erreur du service d'embedding |

---

### GET `/memory/{id}` — Détail d'une Entrée Mémoire

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Retourne le détail d'une entrée mémoire vectorielle. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'entrée mémoire |

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "mem_001",
    "content": "Fourniture de matériel informatique — Lot 1. Postes de travail, écrans, claviers...",
    "embedding_model": "text-embedding-3-small",
    "embedding_dimensions": 1536,
    "source_type": "tender",
    "source_id": "tdr_001",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "metadata": {
      "tender_reference": "2025-INFORMATIQUE-042",
      "issuing_organization": "Ministère de la Transition Écologique"
    },
    "created_at": "2025-01-10T09:05:00Z",
    "chunk_index": 0,
    "total_chunks": 3
  },
  "meta": { "timestamp": "2025-01-15T17:25:00Z", "request_id": "req_041" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Détail retourné |
| 401 | Non authentifié |
| 403 | Cross-tenant |
| 404 | Entrée non trouvée |

---

### DELETE `/memory/{id}` — Suppression (RGPD)

| Attribut | Valeur |
|----------|--------|
| **Méthode** | DELETE |
| **Description** | Suppression d'une entrée mémoire (droit à l'oubli RGPD). L'entrée est définitivement supprimée de pgvector. Nécessite le rôle admin ou une justification RGPD. |
| **Rôle requis** | `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'entrée mémoire |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `deletion_reason` | string | Oui | Motif de suppression (`rgpd_request`, `data_error`, `other`) |
| `justification` | string | Non | Détails (requis si `other`) |

**Exemple Requête :**
```json
DELETE /memory/mem_001
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "deletion_reason": "rgpd_request",
  "justification": "Demande d'exercice du droit à l'oubli — email du demandeur"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "mem_001",
    "deleted": true,
    "deletion_reason": "rgpd_request",
    "deleted_by": "admin@client.fr",
    "deleted_at": "2025-01-15T17:30:00Z",
    "rgpd_compliant": true
  },
  "meta": { "timestamp": "2025-01-15T17:30:00Z", "request_id": "req_042" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Suppression réussie |
| 401 | Non authentifié |
| 403 | Rôle non-admin |
| 404 | Entrée non trouvée |
| 422 | `deletion_reason` manquant |

---

## 1.6 Endpoints — Administration (`/admin`)

> Tous les endpoints `/admin/*` nécessitent le rôle `admin`. Un `viewer` ou `manager` reçoit systématiquement un **403**.

### GET `/admin/tenants` — Liste des Tenants

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Liste tous les tenants (pour super-admin) ou le tenant courant (pour admin de tenant). |
| **Rôle requis** | `admin` |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `limit` | integer | Non | Pagination | 20 |
| `offset` | integer | Non | Offset | 0 |
| `is_active` | boolean | Non | Filtrer par statut | — |

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Acme Corp",
        "slug": "acme-corp",
        "contact_email": "contact@acme.fr",
        "is_active": true,
        "user_count": 5,
        "tender_count": 47,
        "storage_used_mb": 256.5,
        "created_at": "2024-11-01T08:00:00Z",
        "updated_at": "2025-01-10T12:00:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T17:35:00Z",
    "request_id": "req_050",
    "pagination": { "limit": 20, "offset": 0, "total": 1 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Liste retournée |
| 401 | Non authentifié |
| 403 | Rôle non-admin |

---

### POST `/admin/tenants` — Création d'un Tenant

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Crée un nouveau tenant avec ses stages de pipeline par défaut. |
| **Rôle requis** | `admin` (super-admin uniquement) |

**Paramètres (Body) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `name` | string | Oui | Nom du tenant | 2-200 caractères |
| `slug` | string | Oui | Identifiant URL-friendly | `^[a-z0-9-]+$`, unique |
| `contact_email` | string | Oui | Email de contact | Email valide |
| `plan` | string | Non | `free`, `starter`, `pro`, `enterprise` | Défaut: `free` |

**Exemple Requête :**
```json
POST /admin/tenants
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "name": "Construction Dupont SARL",
  "slug": "construction-dupont",
  "contact_email": "admin@dupont-construction.fr",
  "plan": "starter"
}
```

**Exemple Réponse (201) :**
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Construction Dupont SARL",
    "slug": "construction-dupont",
    "contact_email": "admin@dupont-construction.fr",
    "plan": "starter",
    "is_active": true,
    "pipeline_stages": [
      { "name": "new", "label": "Nouveau", "order": 1, "is_default": true },
      { "name": "analyzing", "label": "En analyse", "order": 2 },
      { "name": "qualified", "label": "Qualifié", "order": 3 },
      { "name": "submitted", "label": "Soumis", "order": 4 },
      { "name": "won", "label": "Remporté", "order": 5 },
      { "name": "lost", "label": "Perdu", "order": 6 },
      { "name": "abandoned", "label": "Abandonné", "order": 7 }
    ],
    "created_at": "2025-01-15T17:40:00Z"
  },
  "meta": { "timestamp": "2025-01-15T17:40:00Z", "request_id": "req_051" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 201 | Tenant créé |
| 400 | `slug` déjà utilisé |
| 401 | Non authentifié |
| 403 | Rôle non-admin ou non super-admin |
| 422 | Validation échouée |

---

### GET `/admin/users` — Liste des Utilisateurs

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Liste les utilisateurs du tenant courant (admin de tenant) ou de tous les tenants (super-admin). |
| **Rôle requis** | `admin` |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `limit` | integer | Non | Pagination | 20 |
| `offset` | integer | Non | Offset | 0 |
| `tenant_id` | UUID | Non | Filtrer par tenant (super-admin) | — |
| `role` | string | Non | Filtrer par rôle | — |
| `is_active` | boolean | Non | Filtrer par statut | — |

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "usr_001",
        "email": "manager@client.fr",
        "full_name": "Jean Dupont",
        "role": "manager",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant_name": "Acme Corp",
        "is_active": true,
        "last_login_at": "2025-01-15T14:30:00Z",
        "created_at": "2024-12-01T10:00:00Z"
      },
      {
        "id": "usr_002",
        "email": "viewer@client.fr",
        "full_name": "Marie Martin",
        "role": "viewer",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant_name": "Acme Corp",
        "is_active": true,
        "last_login_at": "2025-01-14T09:00:00Z",
        "created_at": "2024-12-15T11:00:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T17:45:00Z",
    "request_id": "req_052",
    "pagination": { "limit": 20, "offset": 0, "total": 5 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Liste retournée |
| 401 | Non authentifié |
| 403 | Rôle non-admin |
| 403 | Admin de tenant tentant de voir les users d'un autre tenant |

---

### POST `/admin/users` — Création d'un Utilisateur

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Crée un nouvel utilisateur dans un tenant. Le mot de passe est généré automatiquement et envoyé par email (ou retourné en dev). |
| **Rôle requis** | `admin` |

**Paramètres (Body) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `email` | string | Oui | Email | Unique, email valide |
| `full_name` | string | Oui | Nom complet | 2-200 caractères |
| `role` | string | Oui | `viewer`, `manager`, `admin` | Énuméré |
| `tenant_id` | UUID | Non | Tenant (défaut: tenant de l'admin) | — |
| `password` | string | Non | Mot de passe temporaire | 8-128 caractères, auto-généré si absent |
| `is_active` | boolean | Non | Compte actif | `true` |

**Exemple Requête :**
```json
POST /admin/users
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "email": "nouveau@client.fr",
  "full_name": "Pierre Lefebvre",
  "role": "viewer",
  "password": "TempPass2025!"
}
```

**Exemple Réponse (201) :**
```json
{
  "success": true,
  "data": {
    "id": "usr_006",
    "email": "nouveau@client.fr",
    "full_name": "Pierre Lefebvre",
    "role": "viewer",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_active": true,
    "created_at": "2025-01-15T17:50:00Z",
    "message": "Utilisateur créé. Mot de passe temporaire envoyé par email."
  },
  "meta": { "timestamp": "2025-01-15T17:50:00Z", "request_id": "req_053" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 201 | Utilisateur créé |
| 400 | Email déjà utilisé |
| 401 | Non authentifié |
| 403 | Rôle non-admin OU tentative de créer un user dans un autre tenant (non super-admin) |
| 422 | Validation échouée |

---

### GET `/admin/audit-logs` — Audit Trail Complet

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Accès complet au journal d'audit. Filtres par date, utilisateur, action, ressource. Supporte l'export CSV/PDF. |
| **Rôle requis** | `admin` |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `limit` | integer | Non | Pagination (max 1000) | 50 |
| `offset` | integer | Non | Offset | 0 |
| `from_date` | ISO date | Non | Date de début | — |
| `to_date` | ISO date | Non | Date de fin | — |
| `user_id` | UUID | Non | Filtrer par utilisateur | — |
| `action` | string | Non | `create`, `update`, `delete`, `login`, `logout`, `qualify`, `stage_change`, `cross_tenant_attempt` | — |
| `resource_type` | string | Non | `tender`, `document`, `user`, `tenant`, `memory` | — |
| `resource_id` | string | Non | ID de la ressource | — |
| `format` | string | Non | `json`, `csv`, `pdf` | `json` |

**Exemple Requête :**
```
GET /admin/audit-logs?from_date=2025-01-01&action=login&limit=5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) — Format JSON :**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "audit_001",
        "timestamp": "2025-01-15T14:30:00Z",
        "user_id": "usr_001",
        "user_email": "manager@client.fr",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "action": "login",
        "resource_type": "session",
        "resource_id": "sess_001",
        "details": {
          "ip_address": "192.168.1.100",
          "user_agent": "Mozilla/5.0 (X11; Linux x86_64)...",
          "method": "password",
          "success": true
        },
        "hash_chain": "sha256:abc123...def456",
        "previous_hash": "sha256:xyz789...uvw012"
      },
      {
        "id": "audit_002",
        "timestamp": "2025-01-15T14:45:00Z",
        "user_id": "usr_001",
        "user_email": "manager@client.fr",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "action": "create",
        "resource_type": "tender",
        "resource_id": "tdr_003",
        "details": {
          "title": "Maintenance des équipements réseau 2025",
          "reference_number": "2025-RESEAU-003"
        },
        "hash_chain": "sha256:def456...ghi789",
        "previous_hash": "sha256:abc123...def456"
      },
      {
        "id": "audit_003",
        "timestamp": "2025-01-15T15:02:00Z",
        "user_id": "usr_002",
        "user_email": "viewer@client.fr",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "action": "cross_tenant_attempt",
        "resource_type": "tender",
        "resource_id": "tdr_099",
        "details": {
          "target_tenant_id": "770e8400-e29b-41d4-a716-446655440099",
          "ip_address": "192.168.1.105",
          "blocked": true
        },
        "hash_chain": "sha256:ghi789...jkl012",
        "previous_hash": "sha256:def456...ghi789"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T17:55:00Z",
    "request_id": "req_054",
    "pagination": { "limit": 5, "offset": 0, "total": 1234 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Logs retournés (JSON) |
| 200 | Fichier CSV/PDF retourné (Content-Disposition: attachment) |
| 401 | Non authentifié |
| 403 | Rôle non-admin |
| 413 | Demande d'export trop volumineuse (> 50000 lignes) |

---


---

## 2. Architecture de Sécurité

---

### 2.1 JWT Authentication

#### 2.1.1 Structure du Token JWT

TAKA OS utilise **python-jose** avec l'algorithme **HS256** (HMAC-SHA256) en phase initiale. Migration vers RS256 recommandée en production multi-instance.

**Payload du Access Token :**

```json
{
  "sub": "usr_001",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "manager",
  "jti": "jwt_abc123unique",
  "iat": 1705325100,
  "exp": 1705326000,
  "type": "access"
}
```

| Claim | Description | Source |
|-------|-------------|--------|
| `sub` (subject) | ID utilisateur | Base de données |
| `tenant_id` | UUID du tenant | Base de données (table users) |
| `role` | Rôle de l'utilisateur | Base de données (`viewer` / `manager` / `admin`) |
| `jti` (JWT ID) | Identifiant unique du token | UUID v4 généré à la création |
| `iat` (issued at) | Timestamp de création | `datetime.utcnow()` |
| `exp` (expiration) | Timestamp d'expiration | `iat + 15 minutes` |
| `type` | Type de token | `"access"` ou `"refresh"` |

**Payload du Refresh Token :**

```json
{
  "sub": "usr_001",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "jti": "jwt_refresh_xyz789",
  "iat": 1705325100,
  "exp": 1705930800,
  "type": "refresh",
  "token_family": "fam_550e8400-e29b-41d4"
}
```

#### 2.1.2 Durée de Vie

| Token | Durée | Usage |
|-------|-------|-------|
| **Access Token** | 15 minutes (900s) | Chaque requête API — header `Authorization` |
| **Refresh Token** | 7 jours (604800s) | Renouvellement du access token — cookie httpOnly |

#### 2.1.3 Rotation des Refresh Tokens

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│  Client     │────▶│  POST /auth/refresh │────▶│  Refresh Token RT#1  │
│  (cookie    │     │  Cookie: RT#1       │     │  présenté            │
│   RT#1)     │◄────│                     │◄────│                      │
└─────────────┘     └─────────────────────┘     └──────────────────────┘
       │                                           │
       │◄── Nouveau Access Token + RT#2 (cookie)   │
       │                                           │
       │     RT#1 est INVALIDÉ (blacklist)         │ RT#2 est stocké
       │     RT#2 est stocké (nouveau cookie)      │
```

**Règles de rotation :**
- Chaque utilisation d'un refresh token valide génère un **nouveau couple** (access token, refresh token)
- L'ancien refresh token est **immédiatement révoqué** (blacklist)
- Tous les refresh tokens d'une même session partagent un `token_family` UUID
- **Détection de vol** : si un refresh token déjà utilisé est représenté → révocation de toute la famille + alerte

#### 2.1.4 Stockage Côté Client

| Token | Mécanisme | Attributs de Sécurité |
|-------|-----------|----------------------|
| **Access Token** | Header `Authorization: Bearer <token>` | Mémoire volatile (jamais localStorage) |
| **Refresh Token** | Cookie `refresh_token` | `HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh` |

**Pourquoi pas localStorage pour l'access token ?**
- localStorage est vulnérable au XSS (script malveillant peut exfiltrer les tokens)
- L'access token en mémoire volatile (React state / variable JS) réduit la fenêtre d'exposition au strict minimum
- En cas de XSS, l'attaquant ne peut pas accéder au refresh token (httpOnly cookie)

#### 2.1.5 Middleware d'Authentification (FastAPI)

```python
# app/core/security.py
from jose import jwt, JWTError
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dépendance FastAPI : extrait et valide le JWT du header Authorization.
    Retourne l'objet User ou lève une exception 401/403.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="AUTHENTICATION_REQUIRED")

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="TOKEN_EXPIRED")
    except JWTError:
        raise HTTPException(status_code=401, detail="TOKEN_INVALID")

    # Vérification du type de token
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="TOKEN_TYPE_INVALID")

    # Vérification blacklist (token révoqué suite à logout)
    jti = payload.get("jti")
    if await is_token_revoked(jti):
        raise HTTPException(status_code=401, detail="TOKEN_REVOKED")

    # Récupération de l'utilisateur
    user = await get_user_by_id(payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="USER_INACTIVE")

    # Injection du tenant_id dans le contexte de requête
    request.state.tenant_id = payload["tenant_id"]
    request.state.user_role = payload["role"]

    return user
```

#### 2.1.6 Gestion du Logout (Révocation)

```python
# app/core/security.py

# Blacklist en Redis (TTL = durée de vie restante du token)
async def revoke_token(jti: str, expires_at: datetime) -> None:
    """Ajoute un JTI à la blacklist avec le TTL approprié."""
    ttl_seconds = int((expires_at - datetime.utcnow()).total_seconds())
    if ttl_seconds > 0:
        await redis.setex(f"token_blacklist:{jti}", ttl_seconds, "revoked")

async def is_token_revoked(jti: str) -> bool:
    """Vérifie si un JTI est dans la blacklist."""
    return await redis.exists(f"token_blacklist:{jti}") > 0
```

---

### 2.2 RBAC (Role-Based Access Control)

#### 2.2.1 Les 3 Rôles

| Rôle | Description | Capacités |
|------|-------------|-----------|
| **viewer** | Lecture seule | Consulter les AO, documents, pipeline, résultats de qualification, recherche mémoire |
| **manager** | CRUD + qualification | Tout ce que viewer fait + créer/modifier/supprimer des AO, uploader des documents, lancer des qualifications, changer les stages |
| **admin** | Tout + administration | Tout ce que manager fait + gérer les utilisateurs, configurer le pipeline, accéder aux audit logs, supprimer des entrées mémoire (RGPD) |

#### 2.2.2 Héritage des Permissions

```
                    ┌─────────────┐
                    │    admin    │  ← admin hérite de manager
                    │  (tout)     │
                    └──────┬──────┘
                           │ hérite
                    ┌──────▼──────┐
                    │   manager   │  ← manager hérite de viewer
                    │  (CRUD +    │
                    │   qualif)   │
                    └──────┬──────┘
                           │ hérite
                    ┌──────▼──────┐
                    │   viewer    │  ← base : lecture seule
                    │  (read)     │
                    └─────────────┘
```

#### 2.2.3 Matrice des Permissions (Endpoint × Rôle)

| Endpoint | viewer | manager | admin |
|----------|:------:|:-------:|:-----:|
| **Auth** ||||
| `POST /auth/dev-login` | ✅ | ✅ | ✅ |
| `POST /auth/login` | ✅ | ✅ | ✅ |
| `POST /auth/refresh` | ✅ | ✅ | ✅ |
| `GET /auth/me` | ✅ | ✅ | ✅ |
| `POST /auth/logout` | ✅ | ✅ | ✅ |
| **Tenders** ||||
| `GET /tenders` | ✅ | ✅ | ✅ |
| `POST /tenders` | ❌ | ✅ | ✅ |
| `GET /tenders/{id}` | ✅ | ✅ | ✅ |
| `PUT /tenders/{id}` | ❌ | ✅ | ✅ |
| `DELETE /tenders/{id}` | ❌ | ✅ | ✅ |
| `PUT /tenders/{id}/stage` | ❌ | ✅ | ✅ |
| `POST /tenders/{id}/qualify` | ❌ | ✅ | ✅ |
| `GET /tenders/{id}/qualification` | ✅ | ✅ | ✅ |
| **Documents** ||||
| `POST /tenders/{id}/documents` | ❌ | ✅ | ✅ |
| `GET /documents/{id}` | ✅ | ✅ | ✅ |
| `GET /documents/{id}/download` | ✅ | ✅ | ✅ |
| `DELETE /documents/{id}` | ❌ | ✅ | ✅ |
| `POST /documents/{id}/parse` | ❌ | ✅ | ✅ |
| **Pipeline** ||||
| `GET /pipeline-stages` | ✅ | ✅ | ✅ |
| `PUT /pipeline-stages/reorder` | ❌ | ❌ | ✅ |
| **Memory** ||||
| `POST /memory/search` | ✅ | ✅ | ✅ |
| `GET /memory/{id}` | ✅ | ✅ | ✅ |
| `DELETE /memory/{id}` | ❌ | ❌ | ✅ |
| **Admin** ||||
| `GET /admin/tenants` | ❌ | ❌ | ✅ |
| `POST /admin/tenants` | ❌ | ❌ | ✅ |
| `GET /admin/users` | ❌ | ❌ | ✅ |
| `POST /admin/users` | ❌ | ❌ | ✅ |
| `GET /admin/audit-logs` | ❌ | ❌ | ✅ |

> **Légende** : ✅ = accès autorisé | ❌ = accès refusé (403)

#### 2.2.4 Middleware RBAC (FastAPI)

```python
# app/core/rbac.py
from fastapi import Depends, HTTPException
from functools import wraps
from enum import Enum

class Role(str, Enum):
    VIEWER = "viewer"
    MANAGER = "manager"
    ADMIN = "admin"

# Héritage : chaque rôle a un niveau numérique
ROLE_LEVELS = {
    Role.VIEWER: 1,
    Role.MANAGER: 2,
    Role.ADMIN: 3,
}

def require_role(min_role: Role):
    """
    Dépendance FastAPI qui vérifie que l'utilisateur a au moins le rôle requis.
    Gère l'héritage automatiquement (admin >= manager >= viewer).
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_LEVELS.get(Role(current_user.role), 0)
        required_level = ROLE_LEVELS[min_role]

        if user_level < required_level:
            # Log de la tentative d'accès non autorisé
            await audit_log(
                action="unauthorized_access_attempt",
                user_id=current_user.id,
                tenant_id=current_user.tenant_id,
                details={
                    "required_role": min_role.value,
                    "actual_role": current_user.role,
                    "endpoint": request.url.path
                }
            )
            raise HTTPException(
                status_code=403,
                detail="INSUFFICIENT_PERMISSIONS"
            )
        return current_user
    return role_checker

# Aliases pour plus de lisibilité
require_viewer = require_role(Role.VIEWER)      # Tout utilisateur authentifié
require_manager = require_role(Role.MANAGER)    # manager + admin
require_admin = require_role(Role.ADMIN)        # admin uniquement
```

#### 2.2.5 Utilisation dans les Routes

```python
# app/routers/tenders.py
from fastapi import APIRouter, Depends
from app.core.rbac import require_manager, require_viewer

router = APIRouter(prefix="/tenders", tags=["tenders"])

@router.get("/", dependencies=[Depends(require_viewer)])
async def list_tenders(...):
    ...

@router.post("/", dependencies=[Depends(require_manager)])
async def create_tender(...):
    ...

@router.put("/{id}/stage", dependencies=[Depends(require_manager)])
async def change_stage(...):
    ...

# app/routers/admin.py
from app.core.rbac import require_admin

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])

@router.get("/audit-logs")
async def get_audit_logs(...):
    ...
```

---

### 2.3 Multi-Tenancy

#### 2.3.1 Principe d'Isolation

TAKA OS utilise le **multi-tenancy par row-level filtering** (shared database, isolated schema logique). Chaque table contient une colonne `tenant_id`. Aucune requête ne peut contourner ce filtre.

```
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL 15                             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Schema public                          │   │
│  │                                                     │   │
│  │   tenders              documents        users       │   │
│  │   ├─ id                ├─ id            ├─ id      │   │
│  │   ├─ tenant_id  ◄──────┼─ tenant_id    ├─ tenant_id│  │
│  │   ├─ title             ├─ tender_id     ├─ email    │   │
│  │   ├─ ...               ├─ ...           ├─ role     │   │
│  │                                                      │   │
│  │   pipeline_stages      audit_logs       memory_vectors│  │
│  │   ├─ id                ├─ id            ├─ id       │   │
│  │   ├─ tenant_id  ◄──────┼─ tenant_id    ├─ tenant_id │  │
│  │   └─ ...               └─ ...           └─ embedding │  │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 2.3.2 Détermination du Tenant

Le `tenant_id` est extrait du JWT (claim `tenant_id`) à chaque requête. Il est injecté dans le `request.state` par le middleware d'authentification.

```python
# app/core/tenant.py
from fastapi import Request, HTTPException

class TenantContext:
    """Contexte de tenant injecté automatiquement dans chaque requête."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    @classmethod
    async def from_request(cls, request: Request) -> "TenantContext":
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="TENANT_NOT_DETERMINED")
        return cls(tenant_id)

# Dépendance FastAPI
async def get_tenant_context(request: Request) -> TenantContext:
    return await TenantContext.from_request(request)
```

#### 2.3.3 Row-Level Filtering (SQLAlchemy 2.0 Async)

```python
# app/db/base.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select
from fastapi import Request

class TenantScopedQuery:
    """
    Mixin qui ajoute automatiquement le filtre tenant_id
    sur toutes les requêtes SELECT, INSERT, UPDATE, DELETE.
    """

    @classmethod
    def with_tenant(cls, stmt: Select, tenant_id: str) -> Select:
        """Ajoute le filtre tenant_id à une requête SELECT."""
        return stmt.where(cls.tenant_id == tenant_id)

    @classmethod
    async def get_by_id_for_tenant(
        cls,
        session: AsyncSession,
        obj_id: str,
        tenant_id: str
    ):
        """Récupère un objet par ID en vérifiant le tenant."""
        result = await session.execute(
            select(cls).where(cls.id == obj_id, cls.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()
```

```python
# app/models/tender.py
from sqlalchemy import String, Text, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TenantScopedQuery

class Tender(Base, TenantScopedQuery):
    __tablename__ = "tenders"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)  # ULID
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    reference_number: Mapped[str] = mapped_column(String(100), nullable=True)
    issuing_organization: Mapped[str] = mapped_column(String(300), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    pipeline_stage: Mapped[str] = mapped_column(String(50), nullable=False, default="new")
    qualification_result: Mapped[str] = mapped_column(String(20), nullable=True)
    estimated_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cpv_code: Mapped[str] = mapped_column(String(8), nullable=True)
    notice_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
```

#### 2.3.4 Détection Cross-Tenant (Zero Trust)

```python
# app/core/tenant.py

async def enforce_tenant_isolation(
    resource_tenant_id: str,
    request_tenant_id: str,
    resource_type: str,
    resource_id: str,
    user_id: str
) -> None:
    """
    Vérifie que l'utilisateur accède uniquement aux ressources de son tenant.
    En cas de tentative cross-tenant : 403 + log audit immédiat.
    """
    if resource_tenant_id != request_tenant_id:
        # Log sécurité critique
        await audit_log(
            action="cross_tenant_attempt",
            user_id=user_id,
            tenant_id=request_tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details={
                "attempted_tenant_id": resource_tenant_id,
                "user_tenant_id": request_tenant_id,
                "severity": "high",
                "blocked": True
            }
        )
        raise HTTPException(
            status_code=403,
            detail="CROSS_TENANT_ACCESS"
        )
```

#### 2.3.5 Diagramme de Flux — Requête Multi-Tenant

```
┌─────────┐   ┌──────────────────────────────────────────────────────────┐
│ Client  │   │                         Serveur TAKA OS                │
└────┬────┘   └────┬──────────────┬──────────────┬──────────────┬──────┘
     │             │              │              │              │
     │  Bearer     │              │              │              │
     │  Token +    │              │              │              │
     │  Cookie     │              │              │              │
     │             │              │              │              │
     │────────────▶│  1. Auth     │              │              │
     │             │     Middleware              │              │
     │             │     (valide JWT,            │              │
     │             │      extrait tenant_id)     │              │
     │             │              │              │              │
     │             │─────────────▶│  2. RBAC     │              │
     │             │              │     Middleware              │
     │             │              │     (vérifie rôle)          │
     │             │              │              │              │
     │             │              │─────────────▶│  3. Tenant   │
     │             │              │              │     Filter   │
     │             │              │              │     (ajoute  │
     │             │              │              │      WHERE   │
     │             │              │              │      tenant) │
     │             │              │              │              │
     │             │              │              │─────────────▶│  4. DB
     │             │              │              │              │     Query
     │             │              │              │              │     (filtrée)
     │             │              │              │◄─────────────│
     │             │              │              │              │
     │             │              │◄─────────────│              │
     │             │◄─────────────│              │              │
     │◄────────────│  5. Response │              │              │
     │             │   (JSON)     │              │              │
     │             │              │              │              │
```

---

### 2.4 Audit Trail

#### 2.4.1 Philosophie : Append-Only, Immuable

L'audit trail est **sacré**. Jamais de `UPDATE` ou `DELETE` sur la table `audit_logs`. Chaque ligne est définitivement gravée.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Table audit_logs                             │
├──────────┬─────────────┬────────┬────────────┬─────────┬──────────┤
│ id (PK)  │ timestamp   │ user_id│ action     │ tenant  │ hash     │
├──────────┼─────────────┼────────┼────────────┼─────────┼──────────┤
│ audit_001│ 2025-01-15  │ usr_001│ login      │ tenant_1│ sha256:  │
│          │ 14:30:00Z   │        │            │         │  abc...  │
├──────────┼─────────────┼────────┼────────────┼─────────┼──────────┤
│ audit_002│ 2025-01-15  │ usr_001│ create     │ tenant_1│ sha256:  │
│          │ 14:45:00Z   │        │            │         │  def...  │
│          │             │        │            │         │  (hash   │
│          │             │        │            │         │  de 001) │
├──────────┼─────────────┼────────┼────────────┼─────────┼──────────┤
│ audit_003│ 2025-01-15  │ usr_002│cross_tenant│ tenant_1│ sha256:  │
│          │ 15:02:00Z   │        │_attempt    │         │  ghi...  │
│          │             │        │            │         │  (hash   │
│          │             │        │            │         │  de 002) │
└──────────┴─────────────┴────────┴────────────┴─────────┴──────────┘
```

#### 2.4.2 Schéma de la Table

```python
# app/models/audit.py
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)  # ULID
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True
    )
    user_id: Mapped[str] = mapped_column(String(26), nullable=True, index=True)
    user_email: Mapped[str] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str] = mapped_column(String(26), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)

    # Hash chain pour l'immuabilité
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False)
```

#### 2.4.3 Hash Chain (Chaîne d'Intégrité)

Chaque log contient un hash SHA-256 du log précédent, formant une chaîne cryptographique. Toute altération d'un log historique casse la chaîne.

```python
# app/core/audit.py
import hashlib
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def compute_hash_chain(
    session: AsyncSession,
    log_data: dict
) -> str:
    """
    Calcule le hash d'un log d'audit en incluant le hash du log précédent.
    Forme une chaîne immuable : alterer un log casse tous les suivants.
    """
    # Récupérer le dernier log pour ce tenant
    result = await session.execute(
        select(AuditLog)
        .where(AuditLog.tenant_id == log_data["tenant_id"])
        .order_by(AuditLog.timestamp.desc())
        .limit(1)
    )
    last_log = result.scalar_one_or_none()

    previous_hash = last_log.current_hash if last_log else "0" * 64

    # Construire le payload hashé
    hash_payload = {
        "timestamp": log_data["timestamp"].isoformat(),
        "user_id": log_data.get("user_id"),
        "action": log_data["action"],
        "resource_type": log_data.get("resource_type"),
        "resource_id": log_data.get("resource_id"),
        "details": log_data.get("details"),
        "previous_hash": previous_hash
    }

    # Hash SHA-256 canonique
    canonical = json.dumps(hash_payload, sort_keys=True, ensure_ascii=False)
    current_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return current_hash, previous_hash
```

#### 2.4.4 Middleware d'Audit Automatique

```python
# app/core/audit.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui log automatiquement toutes les actions
    de création, modification et suppression.
    """

    AUDIT_ACTIONS = {
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        method = request.method
        if method in self.AUDIT_ACTIONS and hasattr(request.state, "user"):
            action = self.AUDIT_ACTIONS[method]
            user = request.state.user

            # Extraire le resource_type et resource_id du path
            path_parts = request.url.path.strip("/").split("/")
            resource_type = path_parts[0] if path_parts else "unknown"
            resource_id = path_parts[1] if len(path_parts) > 1 else None

            await audit_log(
                action=action,
                user_id=user.id,
                user_email=user.email,
                tenant_id=user.tenant_id,
                resource_type=resource_type,
                resource_id=resource_id,
                details={
                    "method": method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )

        return response
```

#### 2.4.5 Actions Auditées

| Action | Quand | Détails loggués |
|--------|-------|-----------------|
| `login` | Connexion réussie | IP, user-agent, méthode (password/dev) |
| `login_failed` | Tentative échouée | IP, email tenté, raison de l'échec |
| `logout` | Déconnexion | Session ID révoqué |
| `create` | POST réussi | Ressource créée, champs clés |
| `update` | PUT/PATCH réussi | Champs modifiés (diff) |
| `delete` | DELETE réussi | Ressource supprimée |
| `stage_change` | Changement de pipeline | `from` → `to`, motif |
| `qualify` | Lancement qualification | Job ID, AO concerné |
| `cross_tenant_attempt` | Tentative cross-tenant | Tenant cible, IP, bloqué |
| `unauthorized_access_attempt` | 403 RBAC | Rôle requis, rôle actuel |
| `token_revoked` | Refresh token révoqué | Raison (logout / vol détecté) |
| `user_created` | Création user | Email, rôle, tenant |
| `password_changed` | Changement password | — (jamais le password en clair) |

#### 2.4.6 Export Audit (Conformité Fiscale)

```
GET /admin/audit-logs?from_date=2025-01-01&to_date=2025-01-31&format=csv

→ Retourne un fichier CSV :
timestamp, user_email, action, resource_type, resource_id, details, ip_address, hash_chain
2025-01-15T14:30:00Z,manager@client.fr,login,session,sess_001,"{...}",192.168.1.100,sha256:abc...
2025-01-15T14:45:00Z,manager@client.fr,create,tender,tdr_003,"{...}",192.168.1.100,sha256:def...

GET /admin/audit-logs?from_date=2025-01-01&to_date=2025-01-31&format=pdf

→ Retourne un PDF tamponné, signé, horodaté pour l'inspecteur fiscal.
```

---

### 2.5 Rate Limiting

#### 2.5.1 Limites par Endpoint

| Groupe | Endpoints | Limite | Fenêtre |
|--------|-----------|--------|---------|
| **Auth** | `/auth/login`, `/auth/dev-login` | 5 requêtes | 1 minute |
| **Refresh** | `/auth/refresh` | 10 requêtes | 1 minute |
| **API générale** | Tous les endpoints API | 100 requêtes | 1 minute |
| **Upload** | `/tenders/{id}/documents` | 10 requêtes | 1 minute |
| **Qualification** | `/tenders/{id}/qualify` | 5 requêtes | 1 minute |
| **Memory search** | `/memory/search` | 30 requêtes | 1 minute |
| **Admin audit** | `/admin/audit-logs` | 20 requêtes | 1 minute |

#### 2.5.2 Implémentation : Sliding Window (In-Memory)

Pour un déploiement VPS 6-8€ (mono-instance), le sliding window en mémoire est suffisant. Pour du multi-instance, migrer vers Redis.

```python
# app/core/rate_limit.py
import time
from collections import deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class SlidingWindowRateLimiter:
    """
    Rate limiter in-memory avec sliding window.
    Clé de rate limit : "<client_id>:<endpoint_group>"
    """

    def __init__(self):
        # { "key": deque([timestamp1, timestamp2, ...]) }
        self.windows: dict[str, deque] = {}
        self.limits = {
            "auth": (5, 60),        # 5 req / 60s
            "refresh": (10, 60),    # 10 req / 60s
            "api": (100, 60),       # 100 req / 60s
            "upload": (10, 60),     # 10 req / 60s
            "qualify": (5, 60),     # 5 req / 60s
            "memory": (30, 60),     # 30 req / 60s
            "admin": (20, 60),      # 20 req / 60s
        }

    def _get_client_id(self, request: Request) -> str:
        """Identifie le client par IP ou par user_id si authentifié."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_endpoint_group(self, path: str, method: str) -> str:
        """Détermine le groupe de rate limit pour un endpoint."""
        if path.startswith("/auth/login") or path.startswith("/auth/dev-login"):
            return "auth"
        if path.startswith("/auth/refresh"):
            return "refresh"
        if path.startswith("/tenders/") and path.endswith("/documents") and method == "POST":
            return "upload"
        if path.startswith("/tenders/") and path.endswith("/qualify"):
            return "qualify"
        if path.startswith("/memory/search"):
            return "memory"
        if path.startswith("/admin/audit-logs"):
            return "admin"
        return "api"

    def is_allowed(self, key: str, group: str) -> tuple[bool, int]:
        """
        Vérifie si la requête est autorisée.
        Retourne (autorisé, retry_after_seconds).
        """
        max_requests, window_seconds = self.limits.get(group, (100, 60))
        now = time.time()

        window = self.windows.setdefault(key, deque())

        # Retirer les timestamps expirés (hors fenêtre)
        while window and window[0] < now - window_seconds:
            window.popleft()

        if len(window) >= max_requests:
            retry_after = int(window[0] + window_seconds - now) + 1
            return False, max(retry_after, 1)

        window.append(now)
        return True, 0

# Instance globale
rate_limiter = SlidingWindowRateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting appliqué à toutes les requêtes."""

    async def dispatch(self, request: Request, call_next):
        client_id = rate_limiter._get_client_id(request)
        group = rate_limiter._get_endpoint_group(
            request.url.path,
            request.method
        )
        key = f"{client_id}:{group}"

        allowed, retry_after = rate_limiter.is_allowed(key, group)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="RATE_LIMIT_EXCEEDED",
                headers={"Retry-After": str(retry_after)}
            )

        response = await call_next(request)

        # Headers informatifs
        remaining = rate_limiter.limits[group][0] - len(rate_limiter.windows.get(key, []))
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.limits[group][0])
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))

        return response
```

#### 2.5.3 Réponse 429 (Rate Limit Exceeded)

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Limite de requêtes atteinte. Réessayez dans 45 secondes.",
    "retry_after": 45,
    "request_id": "req_999",
    "timestamp": "2025-01-15T18:00:00Z"
  }
}
```

---

### 2.6 Protection contre les Attaques

#### 2.6.1 SQL Injection — IMMUNISÉ par SQLAlchemy 2.0

```python
# ✅ SÉCURISÉ — SQLAlchemy 2.0 parameterized queries (obligatoire)
result = await session.execute(
    select(Tender).where(
        Tender.tenant_id == tenant_id,        # Parameterized
        Tender.title.ilike(f"%{search}%")     # Parameterized
    )
)

# ❌ INTERDIT — Jamais de f-string ou concatenation SQL
# NEVER: f"SELECT * FROM tenders WHERE title = '{user_input}'"
# NEVER: text(f"SELECT * FROM tenders WHERE id = '{tender_id}'")
```

**Règle d'or** : Toute requête SQL passe par l'ORM SQLAlchemy. `text()` n'est utilisé que pour des requêtes statiques sans paramètres dynamiques.

#### 2.6.2 XSS (Cross-Site Scripting)

```python
# ✅ SÉCURISÉ — Content-Type JSON strict, pas de HTML dans les réponses
# Toutes les réponses API retournent Content-Type: application/json
# Le frontend échappe tout rendu HTML (React fait ça par défaut)

# ❌ INTERDIT — Ne jamais retourner du HTML dans une réponse API
# NEVER: return HTMLResponse(f"<div>{user_input}</div>")

# Validation Pydantic sur tous les inputs
class TenderCreate(BaseModel):
    title: constr(min_length=5, max_length=500)  # Pas d'injection possible
    description: constr(max_length=50000)
```

#### 2.6.3 CSRF (Cross-Site Request Forgery)

```python
# ✅ SÉCURISÉ — Cookies SameSite=Strict + Header Origin validation

# Configuration des cookies refresh_token
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,          # Non accessible par JavaScript
    secure=True,            # Uniquement HTTPS (en production)
    samesite="Strict",      # Jamais envoyé en cross-site
    path="/auth/refresh",   # Scope minimal
    max_age=604800          # 7 jours
)

# Validation de l'header Origin pour les requêtes sensibles
allowed_origins = ["https://app.taka.io", "https://admin.taka.io"]
origin = request.headers.get("origin")
if origin and origin not in allowed_origins:
    raise HTTPException(status_code=403, detail="ORIGIN_NOT_ALLOWED")
```

#### 2.6.4 File Upload — Validation Multi-Couches

```python
# app/core/upload_security.py
import magic
from fastapi import UploadFile, HTTPException

# Types MIME autorisés
ALLOWED_MIME_TYPES = {
    "application/pdf": [b"%PDF-"],
    "application/zip": [b"PK\x03\x04"],
    "text/plain": [],
    "text/csv": [],
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

async def validate_upload(file: UploadFile) -> None:
    """
    Validation de sécurité d'un fichier uploadé.
    Vérifie : extension, type MIME déclaré, magic bytes, taille.
    """
    # 1. Vérifier l'extension
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    allowed_extensions = ["pdf", "docx", "doc", "xlsx", "xls", "zip", "txt", "csv"]
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="FILE_EXTENSION_NOT_ALLOWED")

    # 2. Vérifier le type MIME déclaré
    declared_mime = file.content_type
    if declared_mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="MIME_TYPE_NOT_ALLOWED")

    # 3. Lire les premiers bytes et vérifier les magic bytes
    header = await file.read(8192)
    await file.seek(0)  # Remettre le curseur au début

    detected_mime = magic.from_buffer(header, mime=True)
    if detected_mime != declared_mime:
        raise HTTPException(
            status_code=400,
            detail=f"MIME_TYPE_MISMATCH: déclaré={declared_mime}, détecté={detected_mime}"
        )

    # Vérifier les magic bytes connus
    expected_magics = ALLOWED_MIME_TYPES.get(declared_mime, [])
    if expected_magics and not any(header.startswith(m) for m in expected_magics):
        raise HTTPException(status_code=400, detail="MAGIC_BYTES_INVALID")

    # 4. Vérifier la taille (lecture complète)
    content = await file.read()
    await file.seek(0)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="FILE_TOO_LARGE")

    # 5. Stocker le checksum SHA-256 pour détecter les doublons
    import hashlib
    checksum = hashlib.sha256(content).hexdigest()

    return {
        "filename": file.filename,
        "mime_type": detected_mime,
        "file_size": len(content),
        "checksum_sha256": checksum,
        "content": content
    }
```

#### 2.6.5 Timing Attacks — Comparaison Constant-Time

```python
# ✅ SÉCURISÉ — passlib bcrypt avec comparaison constant-time intégrée
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérification bcrypt — comparaison en temps constant.
    Empêche les attaques par timing qui devinent le password caractère par caractère.
    """
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hashage bcrypt avec salt automatique."""
    return pwd_context.hash(password)

# La méthode pwd_context.verify() utilise une comparaison constant-time
# qui prend le même temps quel que soit le nombre de caractères corrects.
```

#### 2.6.6 Récapitulatif des Protections

| Attaque | Mécanisme de protection | Niveau de confiance |
|---------|------------------------|---------------------|
| **SQL Injection** | SQLAlchemy 2.0 ORM uniquement, pas de raw SQL dynamique | Élevé |
| **XSS** | Content-Type JSON strict, pas de HTML, React échappe le DOM | Élevé |
| **CSRF** | SameSite=Strict cookies, Origin validation | Élevé |
| **File Upload** | Magic bytes + MIME + extension + taille max 50MB | Élevé |
| **Timing Attack** | bcrypt constant-time via passlib | Élevé |
| **JWT Theft** | Access token court (15min), refresh rotation, httpOnly cookie | Élevé |
| **Brute Force** | Rate limiting 5 req/min sur auth, lockout après 5 échecs | Élevé |
| **Cross-Tenant** | Row-level filtering sur chaque requête, vérification JWT tenant_id | Élevé |
| **Audit Tampering** | Hash chain SHA-256, append-only, pas d'UPDATE/DELETE | Élevé |

---

## 3. Implémentation FastAPI — Ordre des Middlewares

```python
# app/main.py
from fastapi import FastAPI
from app.core.rate_limit import RateLimitMiddleware
from app.core.audit import AuditMiddleware
from app.core.security import AuthMiddleware
from app.core.tenant import TenantMiddleware

app = FastAPI(title="TAKA OS API", version="2.0.0")

# Ordre CRUCIAL des middlewares (exécution de haut en bas pour les requêtes)
app.add_middleware(RateLimitMiddleware)    # 1. Rate limit (bloque les abus)
app.add_middleware(AuditMiddleware)         # 2. Audit (logge tout)
app.add_middleware(AuthMiddleware)          # 3. Auth (vérifie JWT)
app.add_middleware(TenantMiddleware)        # 4. Tenant (isole les données)

# Routers
app.include_router(auth.router, prefix="/auth")
app.include_router(tenders.router, prefix="/tenders")
app.include_router(documents.router, prefix="/documents")
app.include_router(pipeline.router, prefix="/pipeline-stages")
app.include_router(memory.router, prefix="/memory")
app.include_router(admin.router, prefix="/admin")
```

---

## 4. Variables d'Environnement Critiques

| Variable | Description | Exemple |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Clé secrète pour signer les JWT (min 256 bits) | `openssl rand -hex 32` |
| `JWT_ALGORITHM` | Algorithme de signature | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie access token | `15` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Durée de vie refresh token | `7` |
| `ENV` | Environnement (`development`, `staging`, `production`) | `production` |
| `ALLOWED_ORIGINS` | Origines CORS autorisées | `https://app.taka.io,https://admin.taka.io` |
| `MAX_UPLOAD_SIZE_MB` | Taille max upload | `50` |
| `RATE_LIMIT_AUTH_PER_MINUTE` | Rate limit auth | `5` |
| `RATE_LIMIT_API_PER_MINUTE` | Rate limit API | `100` |
| `BCRYPT_ROUNDS` | Rounds bcrypt (cost factor) | `12` |
| `DATABASE_URL` | URL PostgreSQL | `postgresql+asyncpg://...` |
| `REDIS_URL` | URL Redis (optionnel, pour blacklist) | `redis://localhost:6379/0` |

---

## 5. Diagramme de Séquence — Authentification Complète

```
┌────────┐     ┌──────────┐     ┌─────────────────┐     ┌──────────┐     ┌──────────┐
│ Client │     │  FastAPI │     │ Auth Middleware │     │  DB      │     │  Redis   │
└───┬────┘     └────┬─────┘     └────────┬────────┘     └────┬─────┘     └────┬─────┘
    │               │                    │                   │                │
    │  POST /login  │                    │                   │                │
    │  {email, pwd} │                    │                   │                │
    │──────────────▶│                    │                   │                │
    │               │  1. Rate limit OK? │                   │                │
    │               │  (vérifier abuse)  │                   │                │
    │               │                    │                   │                │
    │               │  2. Récupérer user │                   │                │
    │               │     par email      │                   │                │
    │               │────────────────────│──────────────────▶│                │
    │               │                    │                   │                │
    │               │  3. User + hash    │                   │                │
    │               │     bcrypt         │                   │                │
    │               │◀───────────────────│───────────────────│                │
    │               │                    │                   │                │
    │               │  4. verify_password│                   │                │
    │               │     (constant-time)│                   │                │
    │               │                    │                   │                │
    │               │  5. Générer        │                   │                │
    │               │     access_token   │                   │                │
    │               │     refresh_token  │                   │                │
    │               │     (JWT signé)    │                   │                │
    │               │                    │                   │                │
    │               │  6. Stocker RT     │                   │                │
    │               │     dans Redis     │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  7. Audit log      │                   │                │
    │               │     "login"        │                   │                │
    │               │────────────────────│──────────────────▶│                │
    │               │                    │                   │                │
    │◀──────────────│  8. 200 OK +      │                   │                │
    │  access_token │     Set-Cookie:    │                   │                │
    │  (body)       │     refresh_token  │                   │                │
    │               │     (httpOnly)     │                   │                │
    │               │                    │                   │                │
    │               │                    │                   │                │
    │  GET /tenders │                    │                   │                │
    │  Authorization:                   │                   │                │
    │  Bearer <AT>  │                    │                   │                │
    │──────────────▶│                    │                   │                │
    │               │  9. Vérifier AT    │                   │                │
    │               │     (signature,    │                   │                │
    │               │      expiry, type) │                   │                │
    │               │                    │                   │                │
    │               │  10. Vérifier JTI  │                   │                │
    │               │      non révoqué   │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  11. Extraire      │                   │                │
    │               │      tenant_id     │                   │                │
    │               │      depuis JWT    │                   │                │
    │               │                    │                   │                │
    │               │  12. Query DB avec │                   │                │
    │               │      WHERE         │                   │                │
    │               │      tenant_id = ? │                   │                │
    │               │────────────────────│──────────────────▶│                │
    │               │                    │                   │                │
    │               │  13. Résultats     │                   │                │
    │               │      filtrés       │◀──────────────────│                │
    │               │                    │                   │                │
    │◀──────────────│  14. 200 OK       │                   │                │
    │  {tenders}    │     (JSON)         │                   │                │
    │               │                    │                   │                │
    │               │                    │                   │                │
    │  POST /auth/refresh                │                   │                │
    │  Cookie: RT#1 │                    │                   │                │
    │──────────────▶│                    │                   │                │
    │               │  15. Vérifier RT#1 │                   │                │
    │               │     (signature,    │                   │                │
    │               │      expiry,       │                   │                │
    │               │      family)       │                   │                │
    │               │                    │                   │                │
    │               │  16. RT#1 déjà     │                   │                │
    │               │      utilisé ?     │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  17. Si oui →      │                   │                │
    │               │      révoquer      │                   │                │
    │               │      toute la      │                   │                │
    │               │      famille !     │                   │                │
    │               │                    │                   │                │
    │               │  18. Sinon →       │                   │                │
    │               │      générer AT+   │                   │                │
    │               │      RT#2,         │                   │                │
    │               │      invalider RT#1│                   │                │
    │               │                    │                   │                │
    │◀──────────────│  19. 200 OK +     │                   │                │
    │  Nouveau AT   │     Set-Cookie:    │                   │                │
    │               │     RT#2           │                   │                │
    │               │     (RT#1 blacklist│                   │                │
    │               │      dans Redis)   │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │                    │                   │                │
    │  POST /logout │                    │                   │                │
    │  Bearer AT    │                    │                   │                │
    │  Cookie RT#2  │                    │                   │                │
    │──────────────▶│                    │                   │                │
    │               │  20. Blacklist AT  │                   │                │
    │               │      (JTI dans     │                   │                │
    │               │       Redis)       │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  21. Supprimer RT#2│                   │                │
    │               │      de Redis      │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  22. Audit log     │                   │                │
    │               │      "logout"      │                   │                │
    │               │                    │                   │                │
    │◀──────────────│  23. 200 OK +     │                   │                │
    │               │     Cookie vidé   │                   │                │
    │               │     (Max-Age=0)   │                   │                │
    │               │                    │                   │                │
```

---

## 6. Table Récapitulative — Tous les Endpoints

| # | Méthode | Endpoint | Auth | Rôle Min | Description |
|---|---------|----------|------|----------|-------------|
| 1 | POST | `/auth/dev-login` | Non | — | Login dev (env=development uniquement) |
| 2 | POST | `/auth/login` | Non | — | Login email+password |
| 3 | POST | `/auth/refresh` | Cookie | — | Refresh JWT |
| 4 | GET | `/auth/me` | Bearer | viewer | Profil connecté |
| 5 | POST | `/auth/logout` | Bearer+Cookie | viewer | Déconnexion |
| 6 | GET | `/tenders` | Bearer | viewer | Liste AO avec filtres |
| 7 | POST | `/tenders` | Bearer | manager | Création AO |
| 8 | GET | `/tenders/{id}` | Bearer | viewer | Détail AO |
| 9 | PUT | `/tenders/{id}` | Bearer | manager | Mise à jour AO |
| 10 | DELETE | `/tenders/{id}` | Bearer | manager | Suppression AO |
| 11 | PUT | `/tenders/{id}/stage` | Bearer | manager | Changer stage |
| 12 | POST | `/tenders/{id}/qualify` | Bearer | manager | Lancer qualification |
| 13 | GET | `/tenders/{id}/qualification` | Bearer | viewer | Résultat qualification |
| 14 | POST | `/tenders/{id}/documents` | Bearer | manager | Upload document |
| 15 | GET | `/documents/{id}` | Bearer | viewer | Détail document |
| 16 | GET | `/documents/{id}/download` | Bearer | viewer | Téléchargement |
| 17 | DELETE | `/documents/{id}` | Bearer | manager | Suppression document |
| 18 | POST | `/documents/{id}/parse` | Bearer | manager | Parsing asynchrone |
| 19 | GET | `/pipeline-stages` | Bearer | viewer | Liste stages |
| 20 | PUT | `/pipeline-stages/reorder` | Bearer | admin | Réordonner stages |
| 21 | POST | `/memory/search` | Bearer | viewer | Recherche vectorielle |
| 22 | GET | `/memory/{id}` | Bearer | viewer | Détail mémoire |
| 23 | DELETE | `/memory/{id}` | Bearer | admin | Suppression RGPD |
| 24 | GET | `/admin/tenants` | Bearer | admin | Liste tenants |
| 25 | POST | `/admin/tenants` | Bearer | admin | Création tenant |
| 26 | GET | `/admin/users` | Bearer | admin | Liste users |
| 27 | POST | `/admin/users` | Bearer | admin | Création user |
| 28 | GET | `/admin/audit-logs` | Bearer | admin | Audit trail (JSON/CSV/PDF) |

---

*Fin de la Section 2 — API REST & Sécurité*
*Document version : 2.0.0*
*Date de rédaction : 2025-01-15*
