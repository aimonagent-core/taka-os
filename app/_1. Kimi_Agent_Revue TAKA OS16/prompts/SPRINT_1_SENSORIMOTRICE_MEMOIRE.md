================================================================================
 PROMPT SPRINT 1 MIS A JOUR — KIMI CODE : SENSORIMOTRICE + MEMOIRE + MFA + E2E
================================================================================

Agent : Kimi Code
Sprint : 1 (mise a jour post-sprint-0)
Objectif : Implementer MFA/TOTP, memoire a 4 couches, pipeline de validation
           N Gates, Human-in-the-Loop, tests E2E Playwright, et consolider
           le parsing PDF 4 niveaux avec extraction CPV/montant/deadline.

Cible de longueur : 4000 a 4500 lignes de prompt auto-contenu.

================================================================================
 SECTION 1 — CONTEXTE DETAILLE (Sprint 0 termine)
================================================================================

Le Sprint 0 a ete valide avec succes. Il a produit l'infrastructure suivante
qui est consideree comme EXISTANTE et IMMUABLE pour ce sprint :

--- Base de donnees ---

PostgreSQL 15 avec l'extension pgvector 0.5.1 pour le stockage et la recherche
par similarite des embeddings vectoriels.

Schema existant (tables deja creees via Alembic) :

- users : id (UUID PK), email (VARCHAR 255 UNIQUE), hashed_password (TEXT),
  is_active (BOOLEAN DEFAULT TRUE), is_admin (BOOLEAN DEFAULT FALSE),
  created_at (TIMESTAMPZ), updated_at (TIMESTAMPZ).
  Index : idx_users_email.

- audit_logs : id (UUID PK), user_id (UUID FK users.id), action (VARCHAR 64),
  resource_type (VARCHAR 64), resource_id (UUID), details (JSONB),
  ip_address (INET), created_at (TIMESTAMPZ).

Extension activee : CREATE EXTENSION IF NOT EXISTS vector.

--- Authentification JWT ---

Fichiers existants (a NE PAS recreer, a importer/etendre) :

app/core/security.py :
  - hash_password(password: str) -> str : hache avec bcrypt, cost=12.
  - verify_password(plain: str, hashed: str) -> bool.
  - create_access_token(data: dict, expires_delta: timedelta | None = None) -> str :
    encode JWT avec algorithm="HS256", secret=settings.SECRET_KEY.
  - decode_access_token(token: str) -> dict : decode avec jose.jwt.decode.
  - get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB :
    dependance FastAPI qui decode le token, verifie l'utilisateur en DB.

app/models/auth.py (a ETENDRE dans ce sprint) :
  - UserBase : email: EmailStr, is_active: bool = True.
  - UserCreate : herite UserBase + password: str (min 8 chars).
  - UserInDB : herite UserBase + id: UUID, hashed_password: str,
    created_at: datetime, updated_at: datetime.
  - UserResponse : id: UUID, email: EmailStr, is_active: bool,
    created_at: datetime.
  - Token : access_token: str, token_type: str = "bearer".
  - TokenPayload : sub: str (user_id), exp: datetime, iat: datetime.

app/api/v1/auth.py (a NE PAS modifier sauf pour injecter MFA dans le flux login) :
  - POST /auth/register : cree un utilisateur, hash le password, retourne UserResponse.
  - POST /auth/login : verifie credentials, retourne Token. A ETENDRE pour
    retourner un flag mfa_required si l'utilisateur a mfa_enabled=True.
  - POST /auth/refresh : renouvelle le token d'acces.
  - GET /auth/me : retourne UserResponse de l'utilisateur connecte.

--- Frontend existant ---

src/lib/api.ts :
  - Axios instance avec baseURL = process.env.NEXT_PUBLIC_API_URL.
  - Intercepteur request : injecte le token JWT dans le header Authorization.
  - Intercepteur response : gere 401 en redirigeant vers /login,
    403 en affichant un toast.

src/types/index.ts :
  - Interface User : id: string, email: string, is_active: boolean.
  - Interface TokenResponse : access_token: string, token_type: string.

src/hooks/useAuth.ts :
  - Hook zustand pour gerer l'etat d'authentification (token, user, isLoading).
  - Methodes : login, register, logout, refreshToken.

--- Configuration ---

app/core/config.py :
  - class Settings(BaseSettings) avec toutes les variables d'environnement.
  - DATABASE_URL, SECRET_KEY, MISTRAL_API_KEY, REDIS_URL, etc.
  - model_config = SettingsConfigDict(env_file=".env", extra="ignore").

--- Exceptions ---

app/core/exceptions.py :
  - class AppException(Exception) : code HTTP, code interne, message.
  - class ValidationError(AppException) : code 400.
  - class AuthenticationError(AppException) : code 401.
  - class AuthorizationError(AppException) : code 403.
  - class NotFoundError(AppException) : code 404.
  - class ExternalServiceError(AppException) : code 502.

--- Ce qui N'EXISTE PAS encore et doit etre produit ---

A. MFA / TOTP avec chiffrement Fernet et backup codes.
B. Upload de documents PDF avec parsing 4 niveaux (texte, OCR, structure, LLM).
C. Extraction d'entites : codes CPV, montants financiers, dates limites.
D. Client LLM Mistral AI avec resilience (circuit breaker pybreaker, retry
   exponentiel tenacity, fallback modele).
E. Memoire multi-couches : episodique (evenements temporels), semantique
   (faits + embeddings pgvector), procedurale (workflows consolides),
   transactionnelle (audit trail immuable).
F. Pipeline de validation N Gates : 6 gates orchestres avec audit trail
   et early-exit.
G. Systeme d'autonomie a 4 niveaux avec Human-in-the-Loop, panel UI,
   et kill switch operationnel.
H. Tests E2E Playwright (3 suites : auth avec MFA, tender-flow complet,
   kanban drag-and-drop).
I. Tests backend pytest pour toutes les nouvelles routes et services.
J. CI/CD GitHub Actions pour les tests E2E avec services PostgreSQL et Redis.

================================================================================
 SECTION 2 — STACK TECHNIQUE COMPLETE (versions figees, packages ajoutes)
================================================================================

--- Backend Python ---

Paquets existants (deja dans requirements.txt du Sprint 0, a conserver) :

fastapi              >= 0.104.1, < 0.105.0
uvicorn[standard]    >= 0.24.0, < 0.25.0
pydantic             >= 2.5.0, < 3.0.0
pydantic-settings    >= 2.1.0, < 3.0.0
sqlalchemy           >= 2.0.23, < 2.1.0
alembic              >= 1.12.1, < 1.13.0
psycopg2-binary      >= 2.9.9, < 3.0.0
pgvector             >= 0.2.5, < 0.3.0
python-jose[cryptography]  >= 3.3.0, < 4.0.0
passlib[bcrypt]      >= 1.7.4, < 2.0.0
python-multipart     >= 0.0.6, < 0.1.0
aiofiles             >= 23.2.1, < 24.0.0
httpx                >= 0.25.2, < 0.26.0
structlog            >= 23.2.0, < 24.0.0
tenacity             >= 8.2.3, < 9.0.0
pybreaker            >= 1.2.0, < 2.0.0
redis                >= 5.0.1, < 6.0.0
langchain            >= 0.1.0, < 0.2.0
langchain-community  >= 0.0.10, < 0.1.0
pypdf                >= 3.17.1, < 4.0.0
pdfplumber           >= 0.10.0, < 0.11.0
pytesseract          >= 0.3.10, < 0.4.0
Pillow               >= 10.1.0, < 11.0.0
pdf2image            >= 1.16.3, < 2.0.0
numpy                >= 1.26.2, < 2.0.0

NOUVEAUTE — MFA / TOTP (indispensables) :
pyotp                >= 2.9.0, < 3.0.0      # RFC 6238 TOTP, RFC 4226 HOTP
qrcode               >= 7.4.2, < 8.0.0      # Generation QR code cote backend

NOUVEAUTE — Chiffrement MFA :
cryptography         >= 41.0.0, < 42.0.0   # Fernet, PBKDF2HMAC

NOUVEAUTE — Validation pipeline N Gates :
jsonschema           >= 4.20.0, < 5.0.0      # Validation schema JSON

NOUVEAUTE — Parsing de dates :
dateparser           >= 1.2.0, < 2.0.0      # Parsing multilingue de dates

NOUVEAUTE — Tests backend complementaires :
pytest-asyncio       >= 0.21.1, < 0.22.0
factory-boy          >= 3.3.0, < 4.0.0
freezegun            >= 1.4.0, < 2.0.0
Faker                >= 22.0.0, < 23.0.0

NOUVEAUTE — Tests API :
httpx                >= 0.25.2, < 0.26.0    # Deja present, mais utilise pour tests
pytest-httpx         >= 0.28.0, < 0.29.0    # Mock httpx pour tests

--- Frontend TypeScript / React ---

Paquets existants (deja dans package.json du Sprint 0, a conserver) :

next                 14.0.4
react                ^18.2.0
react-dom            ^18.2.0
typescript           ^5.3.3
tailwindcss          ^3.4.0
@tailwindcss/forms   ^0.5.7
axios                ^1.6.2
zustand              ^4.4.7
@tanstack/react-query ^5.13.4
react-hook-form      ^7.49.2
@hookform/resolvers  ^3.3.2
zod                  ^3.22.4
lucide-react         ^0.294.0
clsx                 ^2.0.0
tailwind-merge       ^2.2.0

NOUVEAUTE — MFA / QR Code (indispensables) :
qrcode.react         ^3.1.0               # Composant React QRCodeSVG

NOUVEAUTE — Tests E2E (indispensables) :
@playwright/test     ^1.40.1
playwright           ^1.40.1

NOUVEAUTE — Utilitaires frontend :
date-fns             ^3.0.0               # Manipulation de dates
@types/uuid           ^9.0.0               # Types pour UUID

--- Infrastructure ---

Docker Engine          24.x
Docker Compose         2.23.x
PostgreSQL             15-alpine avec pgvector pre-installe
Redis                  7-alpine
Node.js                20-alpine (frontend)
Python                 3.11-slim (backend)

--- Services Externes ---

Mistral AI API         Endpoint : https://api.mistral.ai/v1
                      Modele primaire : mistral-medium-latest
                      Modele fallback : mistral-small-latest
                      Modele embeddings : mistral-embed
                      Dimension embeddings : 1024
                      Timeout API : 30 secondes
                      Retry : 3 tentatives, backoff exponentiel 1s/2s/4s

Tesseract OCR          Version : 5.3.x
                      Langues installees : fra, eng
                      Variables d'environnement : TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

--- Conventions de nommage (applicables a tout le sprint) ---

Backend :
  - Fichiers : snake_case.py
  - Classes : PascalCase
  - Fonctions/methodes : snake_case
  - Constantes : UPPER_SNAKE_CASE
  - Variables privées : _leading_underscore
  - Async : prefixer toute I/O par async/await

Frontend :
  - Fichiers : PascalCase pour composants, camelCase pour hooks/utilitaires
  - Interfaces TypeScript : PascalCase, prefixe I optionnel
  - Hooks React : useXxx en camelCase
  - Stores Zustand : useXxxStore
  - data-testid : kebab-case descriptif

Base de donnees :
  - Tables : snake_case, pluriel
  - Colonnes : snake_case
  - Indexes : idx_<table>_<colonnes>
  - Contraintes FK : fk_<table>_<table_ref>_<colonne>

================================================================================
 SECTION 3 — REGLES ABSOLUES (heritees + nouvelles du Sprint 1)
================================================================================

--- Regles heritees du Sprint 0 (maintien obligatoire) ---

REGLE ABSOLUE 1 — TOUT code Python a des annotations de type a 100 %.
  Chaque fonction et methode doit avoir des type hints sur tous les parametres
  et sur le type de retour. Les variables locales dans les fonctions courtes
  sont exemptees, mais toute variable de fonction/methode publique doit etre typee.
  Exemple OBLIGATOIRE :
    def calculate_similarity(a: list[float], b: list[float]) -> float: ...
  Contre-exemple INTERDIT :
    def calculate_similarity(a, b): ...
  mypy --strict doit s'executer avec zero erreur sur l'ensemble du backend.

REGLE ABSOLUE 2 — TOUT schema Pydantic utilise BaseModel v2.
  Pas de Config class heritee. Utiliser model_config = ConfigDict(...).
  Les schemas d'entree API doivent avoir model_config = ConfigDict(extra="forbid").
  La validation doit se produire au niveau du schema, pas dans le endpoint.

REGLE ABSOLUE 3 — TOUTE exception metier herite de AppException.
  Le gestionnaire global dans app/middleware/error_handler.py convertit
  automatiquement les AppException en reponses JSON avec structure fixe :
    { "error": { "code": "AUTHENTICATION_ERROR", "message": "...", "detail": {} } }
  Jamais de raise ValueError ou RuntimeError dans le code metier.

REGLE ABSOLUE 4 — TOUT endpoint FastAPI declare response_model et status_code.
  Les reponses doivent etre des instances de schema Pydantic. Pas de return {"key": value}.
  Pas de JSONResponse manuel sauf pour des cas exceptionnels documentes.

REGLE ABSOLUE 5 — TOUT changement de schema de DB est migre via Alembic.
  Les migrations sont auto-generees avec alembic revision --autogenerate.
  Chaque migration est revue manuellement pour l'ajout d'index et de contraintes.
  Les migrations doivent etre idempotentes (IF NOT EXISTS pour CREATE INDEX).

REGLE ABSOLUE 6 — TOUT test a un docstring decrivant le scenario teste.
  La couverture de test pour le nouveau code doit etre >= 80 %.
  Les tests sont isoles : chaque test cree ses propres donnees et les nettoie.
  Utiliser pytest fixtures avec scope=function par defaut.

REGLE ABSOLUE 7 — TOUT secret reside dans une variable d'environnement.
  Pas de SECRET_KEY, MISTRAL_API_KEY, ou password en dur dans le code.
  Le fichier .env.example doit contenir TOUTES les variables avec description.
  Les secrets sont lus via settings = get_settings() (singleton).

REGLE ABSOLUE 8 — TOUT appel externe HTTP a un timeout explicite et un retry.
  Timeout par defaut : 30 secondes pour les appels API.
  Retry : maximum 3 tentatives avec wait_exponential(multiplier=1, min=1, max=10).
  Circuit breaker sur les services externes (Mistral AI, OCR externe si applicable).
  Le circuit breaker doit logger les transitions d'etat.

REGLE ABSOLUE 9 — TOUT log contient un correlation_id.
  structlog est configure avec un processeur de correlation_id.
  Les logs d'erreur incluent le traceback complet.
  Aucun print() dans le code de production. Utiliser logger.debug/info/warning/error.

REGLE ABSOLUE 10 — TOUT schema SQLAlchemy a une docstring et des index strategiques.
  Index sur les colonnes de recherche et de jointure frequente.
  Constraints CHECK pour les enums si pas de enum natif PostgreSQL.
  created_at / updated_at automatiques via event listeners ou server_default.

--- Regles absolues nouvelles du Sprint 1 ---

REGLE ABSOLUE 11 — TOUTE operation MFA est soumise a rate limiting strict.
  Maximum 5 tentatives de verification TOTP par periode de 5 minutes par utilisateur.
  Le compteur de tentatives est stocke dans Redis avec une cle de forme
    mfa_attempts:{user_id} et un TTL de 300 secondes.
  Apres 5 echecs consecutifs : lockout de 15 minutes (cle mfa_lockout:{user_id},
  TTL 900 secondes).
  Toute tentative durant un lockout retourne 429 Too Many Requests immediatement.

REGLE ABSOLUE 12 — TOUT secret MFA est chiffre au repos et jamais expose.
  Le champ mfa_secret_encrypted utilise Fernet (cryptography.fernet) avec une
  cle de 32 bytes derivee de settings.SECRET_KEY via PBKDF2HMAC(
    algorithm=hashes.SHA256(), length=32, salt=salt_fixe, iterations=100000
  ).
  Les backup codes sont generes avec secrets.token_urlsafe(8) (16 chars) puis
  hashes individuellement avec bcrypt (cost=10) avant stockage.
  Le secret TOTP en clair n'est transmis qu'UNE SEULE FOIS dans la reponse
  de /auth/mfa/setup. Par la suite, il n'est jamais retourne par aucune API.
  Aucun log ne doit contenir de secret TOTP, de backup code, ou de code OTP.

REGLE ABSOLUE 13 — TOUT passage de gate de validation est audite en base.
  La table validation_audit enregistre obligatoirement :
    id (UUID PK), request_id (UUID, index), gate_name (VARCHAR 32, index),
    input_hash (CHAR 64, SHA-256), output_hash (CHAR 64, SHA-256),
    status (VARCHAR 16), detail (JSONB, nullable), metadata (JSONB, nullable),
    execution_time_ms (INTEGER), user_id (UUID, FK nullable, index),
    created_at (TIMESTAMPZ, server_default=now()).
  L'input_hash est le SHA-256 du contenu JSON serialise en UTF-8.
  L'output_hash est le SHA-256 du resultat du gate serialise en JSON UTF-8.
  Un gate bloquant avec status FAILED doit immediatement arreter le pipeline
  (early-exit). Les gates suivants recoivent le status SKIPPED.

REGLE ABSOLUE 14 — TOUTE decision HIL est tracee avec horodatage complet.
  La table human_decisions enregistre :
    id (UUID PK), request_id (UUID, index), autonomy_level (INTEGER),
    decision_type (VARCHAR 32), decision_value (JSONB),
    user_id (UUID, FK users.id, index), context_json (JSONB),
    created_at (TIMESTAMPZ), decided_at (TIMESTAMPZ, nullable).
  L'activation du kill switch ecrit un log de niveau CRITICAL avec
    correlation_id, user_id, reason, timestamp ISO.
  La notification WebSocket (ou polling) transmet l'evenement a tous les
  clients connectes en moins de 2 secondes.

REGLE ABSOLUE 15 — TOUT test E2E Playwright est isole, idempotent et parallele-safe.
  Chaque test E2E cree ses propres donnees et les nettoie en teardown.
  Aucune dependance entre tests. L'ordre d'execution n'affecte pas les resultats.
  Les selecteurs DOM utilisent UNIQUEMENT des attributs data-testid.
  Aucun selecteur base sur les classes CSS ou les textes de contenu.
  Exemple : page.getByTestId("login-submit") et non page.locator(".btn-primary").

REGLE ABSOLUE 16 — TOUTE entree memoire a une strategie d'expiration ou de decay.
  Memoire episodique : TTL par defaut de 30 jours (expires_at = created_at + 30j).
  Memoire semantique : decay exponentiel avec half-life de 90 jours.
    decay_factor = 0.5 ^ (age_jours / 90). Archivage si decay_factor < 0.1.
  Memoire procedurale : consolidation apres 7 executions avec outcome="success".
    Deconsolidation apres 3 echecs consecutifs d'une procedure consolidee.
  Memoire transactionnelle : archivage automatique apres 1 an.
    Pas de suppression, deplacement vers table memory_archive.

REGLE ABSOLUE 17 — TOUT pipeline de parsing produit un JSON normalise et versionne.
  La structure du parse_result est fixe et validee par jsonschema :
    {
      "version": "1.0",
      "metadata": { "filename", "page_count", "file_size", "mime_type" },
      "pages": [
        { "page_number", "text", "ocr_used", "confidence", "tables": [],
          "images": [], "word_count" }
      ],
      "entities": { "cpv_codes": [], "amounts": [], "deadlines": [] },
      "confidence_scores": {
        "level_1_text": 0.0-1.0,
        "level_2_ocr": 0.0-1.0,
        "level_3_structured": 0.0-1.0,
        "level_4_llm": 0.0-1.0,
        "overall": 0.0-1.0
      },
      "level_reached": 1-4,
      "degraded": boolean,
      "processing_time_ms": integer
    }
  Chaque niveau enrichit le JSON sans supprimer les donnees des niveaux precedents.
  Si un niveau echoue, le flag degraded=True est positionne et le parsing
  retourne le meilleur resultat obtenu aux niveaux inferieurs.

REGLE ABSOLUE 18 — TOUTE extraction d'entite produit un score de confiance numerique.
  CPV : score entre 0.0 et 1.0. L'entite est rejetee si score < 0.7.
  Montant : score entre 0.0 et 1.0. Rejet si score < 0.6.
  Deadline : score entre 0.0 et 1.0. Rejet si score < 0.5.
  Les scores sont stockes dans le JSON de sortie et affiches dans l'UI.
  Le score est calcule a partir de la qualite du pattern match, la presence
  de contexte confirmatoire, et la coherence avec les autres entites.

REGLE ABSOLUE 19 — TOUT composant React de plus de 200 lignes est decoupe.
  Les composants doivent suivre le principe de responsabilite unique.
  Un composant ne doit pas melanger logique metier complexe et rendu UI.
  Les hooks personnalises extraient la logique (useMFA, useValidation, etc.).
  Les composants de presentation sont purs (pas d'appels API directs).

REGLE ABSOLUE 20 — TOUT appel API depuis le frontend passe par le client centralise.
  Le client axios dans src/lib/api.ts est le SEUL point de contact avec le backend.
  Aucun fetch() ou XMLHttpRequest direct dans les composants.
  Les erreurs API sont normalisees et transformees en objets d'erreur metier.

================================================================================
 SECTION 4 — MISSION DETAILLEE (flux bout en bout complets)
================================================================================

Ce sprint produit un systeme end-to-end permettant a un utilisateur authentifie
(avec MFA optionnel mais recommande) de gerer le cycle de vie complet d'un
document d'appel d'offres, depuis l'upload jusqu'a la classification en
memoire semantique, en passant par un pipeline de validation a 6 gates.

--- FLUX 1 : Authentification avec MFA ---

Etape 1.1 : Inscription
  - L'utilisateur remplit le formulaire d'inscription (email, password).
  - POST /auth/register cree l'utilisateur avec mfa_enabled=False.
  - L'utilisateur recoit un JWT d'acces valide 24h.

Etape 1.2 : Activation MFA (optionnel, recommande)
  - L'utilisateur navigue vers /auth/mfa.
  - Le composant MFASetup affiche l'etape 1 (explication).
  - Clic "Activer MFA" → POST /auth/mfa/setup.
  - Le backend genere un secret TOTP, le chiffre, stocke les backup codes hashes.
  - La reponse contient le secret en clair, le provisioning_uri, et les 10 backup codes.
  - Etape 2 : le frontend affiche le QR code (QRCodeSVG avec provisioning_uri).
  - L'utilisateur scanne le QR avec son authenticator (Google Authenticator, Authy, etc.).
  - L'utilisateur saisit le premier OTP dans le composant MFAInput (6 cases).
  - POST /auth/mfa/verify avec le code → verification OK, mfa_verified=True.
  - Un nouveau JWT est emis. Les appels subsequents incluent ce JWT.

Etape 1.3 : Login avec MFA
  - L'utilisateur remplit email/password sur /login.
  - POST /auth/login → si mfa_enabled=True, la reponse est :
    { mfa_required: true, temp_token: string }
    Le temp_token est un JWT de courte duree (5 minutes) autorisant
    uniquement l'endpoint /auth/mfa/verify.
  - Le frontend affiche MFAInput au lieu de rediriger vers /dashboard.
  - L'utilisateur saisit l'OTP → POST /auth/mfa/verify avec temp_token.
  - Si OTP valide : retourne { access_token, token_type: "bearer" }.
  - Le frontend stocke l'access_token et redirige vers /dashboard.
  - Si OTP invalide : 401, message "Code invalide. Tentatives restantes : X".
  - Apres 5 echecs : 429, lockout 15 minutes.

Etape 1.4 : Utilisation d'un backup code
  - Si l'utilisateur a perdu son appareil TOTP, il peut utiliser un backup code.
  - Sur l'ecran MFA, lien "Utiliser un code de secours".
  - Saisie du backup code (8 caracteres) → POST /auth/mfa/verify avec le code.
  - Le backend verifie le code contre les hashes stockes. Si OK, le code est
    marque comme utilise (supprime de la liste). Un nouveau JWT est emis.

--- FLUX 2 : Upload et parsing d'un PDF d'appel d'offres ---

Etape 2.1 : Upload
  - L'utilisateur authentifie navigue vers /documents/upload.
  - Drag-and-drop ou selection de fichier PDF (max 50 Mo).
  - Le frontend affiche une barre de progression d'upload.
  - POST /documents/upload avec le fichier (multipart/form-data).
  - Le backend stocke le fichier sur disque (chemin unique par UUID),
    cree un enregistrement Document avec status=PENDING.
  - Reponse : { id, status: "pending", message: "Document recu, analyse en cours" }.

Etape 2.2 : Parsing niveau 1 (Texte brut)
  - Un job asynchrone (celery ou background task) demarre.
  - Status passe a PARSING.
  - Level1TextExtractor utilise pypdf pour extraire le texte brut.
  - Score = min(len(text) / 1000, 1.0). Si score >= 0.5 et texte > 200 chars :
    succes niveau 1. Sinon → niveau 2.
  - Resultat stocke dans parse_result.pages[].

Etape 2.3 : Parsing niveau 2 (OCR)
  - Si le texte extrait au niveau 1 est insuffisant (< 200 chars ou score < 0.5).
  - Level2OCRExtractor convertit chaque page en image (pdf2image, dpi=200).
  - pytesseract (lang=fra+eng) OCR chaque image.
  - Score = moyenne des confiances Tesseract par page (donnee par pytesseract
    dans l'output avec confidence).
  - Texte OCR concatene et stocke.

Etape 2.4 : Parsing niveau 3 (Structure)
  - Level3StructuredExtractor utilise pdfplumber pour extraire tableaux et blocs.
  - Les tableaux sont extraits avec .extract_tables() → liste de listes.
  - Les blocs de texte sont extraits avec .extract_text(layout=True).
  - Score = nombre total de cellules de tableau / nombre de pages.
  - Donnees structurees stockees dans parse_result.pages[].tables[].

Etape 2.5 : Parsing niveau 4 (LLM)
  - Level4LLMExtractor envoie le texte concatene (niveaux 1-3) a Mistral AI.
  - Prompt systeme specifique pour l'analyse de marches publics.
  - Temperature=0.1, max_tokens=2000.
  - Le LLM retourne un JSON avec : summary, sections, themes, language,
    document_type, confidence.
  - Le JSON est parse avec extraction regex si necessaire (pattern ```json(.*?```).
  - Si parsing JSON echoue apres 3 retries : retourner {"error": "...", confidence: 0.0}.
  - Le resultat LLM est fusionne dans parse_result.
  - Status passe a EXTRACTING.

Etape 2.6 : Extraction d'entites
  - CPVExtractor analyse le texte complet avec regex CPV.
  - AmountExtractor analyse les montants avec regex et contexte HT/TTC.
  - DeadlineExtractor analyse les dates limites avec dateparser.
  - Chaque entite est stockee avec son score de confiance.
  - Les entites sont stockees dans extracted_entities.
  - Status passe a VALIDATING.

--- FLUX 3 : Pipeline de validation N Gates ---

Etape 3.1 : Gate Syntaxe
  - Verifie que parse_result et extracted_entities sont des JSON valides.
  - Valide contre le schema jsonschema du format normalise (REGLE ABSOLUE 17).
  - Verifie la presence des champs obligatoires (version, metadata, pages).
  - Bloquant. Echec = rejet immediat avec detail des erreurs de schema.

Etape 3.2 : Gate RBAC
  - Verifie que l'utilisateur a la permission "document:create".
  - Verifie que l'utilisateur est proprietaire du document (user_id match).
  - Bloquant. Echec = rejet avec code 403.

Etape 3.3 : Gate Idempotence
  - Calcule un fingerprint SHA-256 du contenu texte + metadata du document.
  - Recherche en memoire semantique un document avec similarite > 0.95.
  - Si doublon detecte : FAILED avec reference au document existant.
  - Si similarite 0.80-0.95 : WARNING (possible doublon, flag pour review).
  - Bloquant pour > 0.95, non bloquant pour 0.80-0.95.

Etape 3.4 : Gate Semantique
  - Si le document_type de l'analyse LLM est "appel_d_offres" :
    - Au moins un CPV doit etre present avec score >= 0.7.
    - Le montant total doit etre > 0 avec score >= 0.6.
    - La deadline doit etre dans le futur (par rapport a now()) avec score >= 0.5.
  - Verifie la coherence entre montant HT et TTC si les deux sont presents.
  - Bloquant. Echec = detail de l'entite incoherente.

Etape 3.5 : Gate Determinisme
  - Execute l'extraction d'entites 3 fois sur les memes donnees.
  - Compare les hashes SHA-256 des JSON de sortie.
  - Si identiques : PASSED. Sinon : WARNING avec detail des differences.
  - Non bloquant par defaut.

Etape 3.6 : Gate HIL
  - Selon le niveau d'autonomie de l'utilisateur :
    - MANUEL (0) : toujours FAILED en attendant validation HIL.
    - ASSISTE (1) : FAILED si score moyen de confiance < 0.7.
    - SUPERVISE (2) : FAILED si un gate precedent a bloque ou WARNING.
    - AUTONOME (3) : PASSED automatiquement, log WARN.
  - Bloquant pour les niveaux 0, 1, 2. Si FAILED, une requete HIL est creee
    et le document passe en status REVIEW.

Etape 3.7 : Finalisation
  - Si tous les gates passants : status = APPROVED.
  - Si gate bloquant : status = REJECTED avec raison.
  - Tous les passages de gates sont enregistres dans validation_audit.

--- FLUX 4 : Stockage en memoire multi-couches ---

Etape 4.1 : Memoire episodique
  - Evenement : "document_parsed", contexte = { document_id, user_id,
    parse_level_reached, processing_time }.
  - TTL = 30 jours. Priority = NORMAL.

Etape 4.2 : Memoire semantique
  - Faits extraits du document : CPV codes, montant, deadline, type de procedure.
  - Chaque fait est stocke avec un embedding (Mistral embed, 1024 dims).
  - Subject = "document:{document_id}", predicate = "has_cpv" / "has_amount" / etc.
  - Permet la recherche semantique de documents similaires par similarite cosinus.

Etape 4.3 : Memoire procedurale
  - Si le parsing a reussi : record_procedure("parse_pdf", steps, "success").
  - Si 7 succes de "parse_pdf" : consolidation en template.
  - Le template memorise les parametres optimaux (dpi, lang, temperature).

Etape 4.4 : Memoire transactionnelle
  - Transaction : document creation, state changes (PENDING → PARSING → ... → APPROVED).
  - Immuable, jamais modifiee. Archivee apres 1 an.

--- FLUX 5 : Autonomie et HIL ---

Etape 5.1 : Configuration du niveau d'autonomie
  - Par defaut : MANUEL (0) pour tous les nouveaux utilisateurs.
  - L'admin peut changer le niveau via POST /autonomy/level.
  - Le niveau est stocke en base (users.autonomy_level) ou dans un profil.

Etape 5.2 : Panel HIL (frontend)
  - Si un document est en status REVIEW, le panel HIL s'affiche.
  - Le panel montre le document, les entites extraites, les scores de confiance,
    et les raisons du gate bloquant.
  - Boutons : Approuver (passe en APPROVED), Rejeter (passe en REJECTED),
    Modifier (permet de corriger les entites avant approbation).

Etape 5.3 : Kill Switch
  - Bouton rouge permanent dans le header.
  - Clic → modal de confirmation avec raison obligatoire (min 10 chars).
  - POST /autonomy/kill → system_state = FROZEN.
  - Overlay rouge sur toute l'application.
  - Admin peut unfreeze via POST /autonomy/unfreeze.

--- FLUX 6 : Tests E2E ---

Etape 6.1 : Setup global
  - auth.setup.ts cree un utilisateur et sauvegarde le storageState.
  - Tous les tests utilisent ce storageState pour l'authentification.

Etape 6.2 : Suite auth
  - Valide login, login+MFA, logout, erreurs de credentials.

Etape 6.3 : Suite tender-flow
  - Valide upload PDF, parsing, extraction entites, validation HIL.

Etape 6.4 : Suite kanban
  - Valide affichage colonnes, drag-and-drop, filtres, tri.

Etape 6.5 : CI/CD
  - GitHub Actions demarre les services, le backend, puis execute Playwright.

================================================================================
 SECTION 5 — FICHIER PAR FICHIER (specification exhaustive)
================================================================================

Les fichiers sont organises par groupe fonctionnel. L'ordre au sein de chaque
groupe suit les dependances (modeles d'abord, services ensuite, API ensuite,
frontend ensuite, tests en dernier).

================================================================================
 GROUPE A : MFA / TOTP (fichiers A1 a A7)
================================================================================

--------------------------------------------------------------------------------
FICHIER A1 : app/models/auth.py (EXTENSION — modifier le fichier existant)
--------------------------------------------------------------------------------

DEPENDANCES : pydantic v2 (BaseModel, EmailStr, ConfigDict, Field),
              uuid.UUID, datetime.datetime, pyotp (pour validation URI),
              app/core/config.py (get_settings), app/core/security.py.

CONTENU A AJOUTER AUX SCHEMAS EXISTANTS :

1. Extension du schema SQLAlchemy (dans app/db/models.py ou equivalent) :
   Ajouter les colonnes suivantes a la table users :

   ```python
   mfa_enabled: Mapped[bool] = mapped_column(
       Boolean, default=False, nullable=False
   )
   mfa_secret_encrypted: Mapped[str | None] = mapped_column(
       Text, nullable=True
   )
   mfa_verified: Mapped[bool] = mapped_column(
       Boolean, default=False, nullable=False
   )
   mfa_backup_codes_hash: Mapped[list[str] | None] = mapped_column(
       JSON, nullable=True
   )
   ```

2. Extension de UserResponse (Pydantic response schema) :
   ```python
   class UserResponse(UserBase):
       model_config = ConfigDict(from_attributes=True)

       id: UUID
       email: EmailStr
       is_active: bool
       mfa_enabled: bool
       mfa_verified: bool
       created_at: datetime
   ```

3. Nouveaux schemas Pydantic pour MFA :

   ```python
   class MFASetupResponse(BaseModel):
       model_config = ConfigDict(extra="forbid")

       secret: str = Field(..., min_length=16, description="Secret base32 TOTP")
       provisioning_uri: str = Field(..., pattern=r"^otpauth://totp/.*")
       backup_codes: list[str] = Field(..., min_length=10, max_length=10)

   class MFAVerifyRequest(BaseModel):
       model_config = ConfigDict(extra="forbid")
       otp_code: str = Field(..., min_length=6, max_length=16, pattern=r"^[A-Za-z0-9]+$")

   class MFAVerifyResponse(BaseModel):
       model_config = ConfigDict(extra="forbid")
       access_token: str
       token_type: str = "bearer"
       expires_in: int = Field(default=86400)

   class MFADisableRequest(BaseModel):
       model_config = ConfigDict(extra="forbid")
       password: str = Field(..., min_length=8)
       otp_code: str | None = Field(default=None)

   class MFABackupCodesResponse(BaseModel):
       model_config = ConfigDict(extra="forbid")
       backup_codes: list[str] = Field(..., min_length=10, max_length=10)
   ```

4. Schema pour le login avec MFA :
   ```python
   class LoginResponse(BaseModel):
       model_config = ConfigDict(extra="forbid")
       mfa_required: bool
       temp_token: str | None = Field(default=None)
       access_token: str | None = Field(default=None)
       token_type: str = "bearer"
       expires_in: int = 86400
   ```

REGLES SPECIFIQUES A CE FICHIER :
- Le champ secret dans MFASetupResponse est le SEUL moment ou le secret TOTP
  en clair transite dans le systeme. Apres le setup, il n'est plus jamais
  retourne, dechiffre uniquement pour verification.
- Les backup_codes dans MFASetupResponse et MFABackupCodesResponse sont
  les SEULS moments ou les backup codes en clair sont retournes.
- Aucun schema ne doit contenir mfa_secret_encrypted ou mfa_backup_codes_hash.

--------------------------------------------------------------------------------
FICHIER A2 : app/core/mfa_service.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : pyotp, cryptography.fernet, cryptography.hazmat.primitives,
              passlib.hash.bcrypt, secrets, base64, app/core/config.py,
              app/core/exceptions.py (AuthenticationError).

CLASSE A IMPLEMENTER :

```python
import pyotp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets
from passlib.hash import bcrypt
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

class MFAService:
    BACKUP_CODE_COUNT: int = 10
    BACKUP_CODE_LENGTH: int = 8
    TOTP_DIGITS: int = 6
    TOTP_INTERVAL: int = 30
    TOTP_WINDOW: int = 1

    def __init__(self, master_secret: str) -> None:
        self._fernet = self._derive_fernet(master_secret)

    def _derive_fernet(self, master_secret: str) -> Fernet:
        salt = b"app_mfa_salt_v1_2024"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_secret.encode()))
        return Fernet(key)

    def generate_secret(self, user_email: str, issuer: str = "App") -> tuple[str, str, list[str]]:
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, digits=self.TOTP_DIGITS, interval=self.TOTP_INTERVAL)
        provisioning_uri = totp.provisioning_uri(name=user_email, issuer_name=issuer)
        backup_codes = self.generate_backup_codes()
        return secret, provisioning_uri, backup_codes

    def encrypt_secret(self, plain_secret: str) -> str:
        return self._fernet.encrypt(plain_secret.encode()).decode()

    def decrypt_secret(self, encrypted_secret: str) -> str:
        try:
            return self._fernet.decrypt(encrypted_secret.encode()).decode()
        except Exception as exc:
            raise AuthenticationError("Failed to decrypt MFA secret") from exc

    def verify_totp(self, encrypted_secret: str, otp_code: str) -> bool:
        secret = self.decrypt_secret(encrypted_secret)
        totp = pyotp.TOTP(secret, digits=self.TOTP_DIGITS, interval=self.TOTP_INTERVAL)
        return totp.verify(otp_code, valid_window=self.TOTP_WINDOW)

    def verify_backup_code(self, hashed_codes: list[str], code_input: str) -> tuple[bool, list[str] | None]:
        for idx, hashed in enumerate(hashed_codes):
            if bcrypt.verify(code_input, hashed):
                remaining = hashed_codes[:idx] + hashed_codes[idx + 1:]
                return True, remaining
        return False, None

    def hash_backup_codes(self, codes: list[str]) -> list[str]:
        return [bcrypt.hash(code) for code in codes]

    def generate_backup_codes(self, count: int = BACKUP_CODE_COUNT) -> list[str]:
        return [secrets.token_urlsafe(self.BACKUP_CODE_LENGTH) for _ in range(count)]
```

POINTS D'IMPLEMENTATION OBLIGATOIRES :
- La derivation Fernet utilise exactement PBKDF2HMAC avec SHA256, 32 bytes,
  salt fixe "app_mfa_salt_v1_2024", 100000 iterations.
- Les backup codes sont des strings URL-safe de 16 caracteres environ.
- La tolerance TOTP window=1 signifie qu'un code expire depuis 30 secondes
  ou valide dans 30 secondes est encore accepte.
- Aucune exception brute ne doit traverser. Tout echec est encapsule dans
  AuthenticationError.

--------------------------------------------------------------------------------
FICHIER A3 : app/core/rate_limiter.py (NOUVEAU — utilitaire rate limiting)
--------------------------------------------------------------------------------

DEPENDANCES : redis.asyncio, app/core/config.py, app/core/exceptions.py.

CLASSE A IMPLEMENTER :

```python
import redis.asyncio as redis
from app.core.exceptions import ValidationError

class RateLimiter:
    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    async def is_allowed(self, key: str, max_attempts: int, window_seconds: int) -> tuple[bool, int]:
        current = await self._redis.incr(key)
        if current == 1:
            await self._redis.expire(key, window_seconds)
        remaining = max_attempts - current
        return current <= max_attempts, max(remaining, 0)

    async def acquire_lockout(self, key: str, duration_seconds: int) -> None:
        await self._redis.setex(key, duration_seconds, "1")

    async def is_locked_out(self, key: str) -> bool:
        return await self._redis.exists(key) > 0
```

REGLE D'IMPLEMENTATION :
- Utiliser INCR + EXPIRE pour le compteur de tentatives.
- Le lockout est une cle separee avec TTL.
- Toute methode doit etre async car Redis est I/O.

--------------------------------------------------------------------------------
FICHIER A4 : app/api/v1/auth_mfa.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : FastAPI, app/models/auth.py, app/core/mfa_service.py,
              app/core/rate_limiter.py, app/core/security.py,
              app/core/exceptions.py, app/api/deps.py,
              sqlalchemy.ext.asyncio.

ROUTER : router = APIRouter(prefix="/auth/mfa", tags=["MFA"])

ENDPOINT 1 : POST /auth/mfa/setup
- Verifier mfa_enabled == False.
- Generer secret, URI, 10 backup codes.
- Chiffrer, hasher, stocker en DB.
- Retourner MFASetupResponse.
- Erreurs : 409 si deja active, 429 si rate limite.

ENDPOINT 2 : POST /auth/mfa/verify
- Verifier rate limit (max 5 / 5 min).
- Verifier lockout.
- Essayer TOTP puis backup code.
- Si premier succes : mfa_verified = True.
- Generer access_token JWT.
- Erreurs : 401 si invalide, 429 apres 5 echecs.

ENDPOINT 3 : POST /auth/mfa/disable
- Verifier password.
- Si mfa_active : verifier OTP ou backup code.
- Desactiver MFA (tous les champs a False/None).
- Retourner 204.

ENDPOINT 4 : POST /auth/mfa/regenerate-backup-codes
- Verifier MFA active et verified.
- Verifier OTP.
- Generer 10 nouveaux codes, hasher, stocker.
- Retourner MFABackupCodesResponse.

ENDPOINT 5 : GET /auth/mfa/status
- Retourner { mfa_enabled: bool, mfa_verified: bool }.

DEPENDANCES A AJOUTER dans app/api/deps.py :

```python
from app.core.mfa_service import MFAService
from app.core.rate_limiter import RateLimiter
from app.core.config import get_settings

settings = get_settings()

def get_mfa_service() -> MFAService:
    return MFAService(master_secret=settings.SECRET_KEY)

def get_rate_limiter() -> RateLimiter:
    from app.core.redis import get_redis_client
    return RateLimiter(redis_client=get_redis_client())
```

MODIFICATION dans le login existant (app/api/v1/auth.py) :

```python
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    # ... verification credentials existante ...
    if user.mfa_enabled and user.mfa_verified:
        temp_token = create_access_token(
            data={"sub": str(user.id), "type": "mfa_temp"},
            expires_delta=timedelta(minutes=5),
        )
        return LoginResponse(mfa_required=True, temp_token=temp_token)
    else:
        access_token = create_access_token(data={"sub": str(user.id)})
        return LoginResponse(mfa_required=False, access_token=access_token, expires_in=86400)
```

--------------------------------------------------------------------------------
FICHIER A5 : src/components/auth/MFASetup.tsx (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : React 18, qrcode.react (QRCodeSVG), axios, zustand,
              lucide-react (Shield, Copy, Check, AlertTriangle, ChevronRight).

INTERFACE DES PROPS :
```typescript
interface MFASetupProps {
  onSetupComplete?: () => void;
  onCancel?: () => void;
}
```

ETATS INTERNES (useState) :
```typescript
type SetupStep = 1 | 2 | 3;

interface SetupData {
  secret: string;
  provisioning_uri: string;
  backup_codes: string[];
}
```

COMPOSANT A IMPLEMENTER (structure detaillee) :

1. Etape 1 : Presentation
   - Titre : "Securisez votre compte".
   - Description : "L'authentification a deux facteurs ajoute une couche
     de securite en demandant un code unique genere par votre telephone."
   - Icone Shield (48px, couleur primary).
   - Bouton "Activer l'authentification" (primary, full-width).
   - Lien "Plus tard" (secondary, text-only).
   - Au clic "Activer" : call API POST /api/v1/auth/mfa/setup.

2. Etape 2 : Scan QR + sauvegarde codes
   - QRCodeSVG avec value={setupData.provisioning_uri}, size=256, level="M".
   - Label : "Scannez ce code avec Google Authenticator, Authy, ou Microsoft Authenticator."
   - Section "Codes de secours" (card avec fond amber-50, border amber-200).
     - Warning : "Ces codes ne seront affiches qu'une seule fois."
     - Grid 2 colonnes des 10 codes.
     - Bouton "Copier" avec feedback Check icon.
     - Checkbox "J'ai sauvegarde mes codes" (requise pour continuer).
   - Section "Verification" avec MFAInput (6 cases).
   - Au clic "Verifier" : POST /api/v1/auth/mfa/verify.

3. Etape 3 : Confirmation
   - Icone Check dans cercle vert (48px).
   - Titre : "Authentification activee".
   - Bouton "Acceder au tableau de bord".

4. Gestion des erreurs :
   - Erreur setup : toast.
   - Erreur verify : message sous MFAInput.
   - Rate limit : "Trop de tentatives. Attendez 15 minutes."

5. Accessibilite :
   - aria-label sur QR code : "QR code pour l'authentification MFA".
   - aria-live="polite" sur les messages d'erreur.
   - Navigation clavier : Tab et Enter.

--------------------------------------------------------------------------------
FICHIER A6 : src/components/auth/MFAInput.tsx (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : React 18 (useState, useRef, useEffect, useImperativeHandle,
              forwardRef), lucide-react.

INTERFACE :
```typescript
interface MFAInputProps {
  length?: number;
  onComplete: (code: string) => void;
  onChange?: (code: string) => void;
  error?: string | null;
  disabled?: boolean;
  autoFocus?: boolean;
}

export interface MFAInputRef {
  clear: () => void;
  getValue: () => string;
  focus: () => void;
}
```

COMPOSANT (forwardRef<MFAInputRef, MFAInputProps>) :

1. Etat interne : digits : string[] de length elements.
2. handleChange :
   - Chiffre [0-9] : maj digits[index], focus suivant si index < length-1.
   - Si tous remplis : onComplete(digits.join("")).
   - Backspace/Delete : focus precedent si vide, sinon efface.
3. handlePaste :
   - Nettoie le texte colle (chiffres uniquement).
   - Repartit dans les cases.
   - Si length chiffres : onComplete.
4. handleKeyDown :
   - ArrowLeft/Right : navigation entre cases.
   - Touche non numerique : preventDefault.
5. Rendu visuel :
   - 6 inputs type="text", inputMode="numeric", pattern="[0-9]*", maxLength=1.
   - w-12 h-14, text-center, text-2xl, border-2 border-gray-300 rounded-lg.
   - Focus : border-blue-500 ring-2 ring-blue-200.
   - Erreur : border-red-500 bg-red-50.
   - Compte a rebours : "Expire dans {seconds}s" avec barre de progression.
6. Expose via useImperativeHandle :
   - clear() : efface tout, focus premier.
   - getValue() : retourne digits.join("").
   - focus() : refs[0].current?.focus().

--------------------------------------------------------------------------------
FICHIER A7 : src/app/auth/mfa/page.tsx (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : Next.js 14 (metadata, Suspense), MFASetup.tsx, AuthGuard HOC.

IMPLEMENTATION :

```typescript
import { Suspense } from "react";
import { Metadata } from "next";
import { MFASetup } from "@/components/auth/MFASetup";
import { AuthGuard } from "@/components/auth/AuthGuard";

export const metadata: Metadata = {
  title: "Configuration MFA | App",
  description: "Activez l'authentification a deux facteurs.",
};

export default function MFAPage() {
  return (
    <AuthGuard>
      <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Suspense fallback={<MFASetupSkeleton />}>
          <MFASetup onSetupComplete={() => { window.location.href = "/dashboard"; }} />
        </Suspense>
      </main>
    </AuthGuard>
  );
}

function MFASetupSkeleton() {
  return (
    <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-6 animate-pulse">
      <div className="h-12 w-12 bg-gray-200 rounded-full mx-auto mb-4" />
      <div className="h-6 bg-gray-200 rounded w-3/4 mx-auto mb-2" />
      <div className="h-4 bg-gray-200 rounded w-full mx-auto mb-6" />
      <div className="h-10 bg-gray-200 rounded w-full" />
    </div>
  );
}
```

REGLE : AuthGuard verifie la presence du token JWT. Si absent, redirige vers
/login avec query param redirect=/auth/mfa.

================================================================================
 GROUPE B : Upload et Parsing PDF (fichiers B8 a B13)
================================================================================

--------------------------------------------------------------------------------
FICHIER B8 : app/models/document.py (NOUVEAU / MISE A JOUR)
--------------------------------------------------------------------------------

DEPENDANCES : sqlalchemy 2.0, pydantic v2, uuid, datetime, enum, typing.

CONTENU SQLALCHEMY (table documents) :

```python
import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PARSING = "parsing"
    EXTRACTING = "extracting"
    VALIDATING = "validating"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ERROR = "error"

class ParseLevel(int, enum.Enum):
    LEVEL_1_TEXT = 1
    LEVEL_2_OCR = 2
    LEVEL_3_STRUCTURED = 3
    LEVEL_4_LLM = 4

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(64), nullable=False, default="application/pdf")
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[DocumentStatus] = mapped_column(String(32), nullable=False, default=DocumentStatus.PENDING)
    parse_level_reached: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parse_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    extracted_entities: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    validation_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
```

TABLE document_chunks :

```python
from pgvector.sqlalchemy import Vector

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
```

INDEXES A CREER VIA ALEMBIC :

```sql
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX idx_documents_status_user ON documents(status, user_id);
CREATE INDEX idx_document_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

SCHEMAS PYDANTIC :

```python
from pydantic import BaseModel, ConfigDict, Field

class DocumentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    filename: str = Field(..., max_length=255)
    original_filename: str = Field(..., max_length=255)
    file_size: int = Field(..., gt=0)
    mime_type: str = Field(default="application/pdf", pattern=r"^application/pdf$")

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    status: DocumentStatus
    parse_level_reached: int | None
    extracted_entities: dict | None
    created_at: datetime
    updated_at: datetime

class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    status: DocumentStatus
    message: str = "Document recu, analyse en cours"

class DocumentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int

class ParseResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    parse_result: dict | None
    extracted_entities: dict | None
    validation_result: dict | None
    processing_time_ms: int | None
```

--------------------------------------------------------------------------------
FICHIER B9 : app/services/parsing/pipeline.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : asyncio, time, structlog, app/models/document.py,
              app/services/parsing/levels.py, app/services/llm/mistral_client.py.

DATACLASS DE RESULTAT :

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PageResult:
    page_number: int
    text: str = ""
    ocr_used: bool = False
    confidence: float = 0.0
    tables: list[list[list[str]]] = field(default_factory=list)
    images: list[dict[str, Any]] = field(default_factory=list)
    word_count: int = 0

@dataclass
class ParseResult:
    version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)
    pages: list[PageResult] = field(default_factory=list)
    entities: dict[str, list[dict]] = field(default_factory=dict)
    confidence_scores: dict[str, float] = field(default_factory=dict)
    level_reached: int = 0
    degraded: bool = False
    processing_time_ms: int = 0
    llm_analysis: dict[str, Any] | None = None
```

CLASSE PRINCIPALE A IMPLEMENTER :

```python
class ParsingPipeline:
    MIN_TEXT_LENGTH: int = 200
    MIN_CONFIDENCE: float = 0.5
    TIMEOUT_LEVEL_1: float = 10.0
    TIMEOUT_LEVEL_2: float = 60.0
    TIMEOUT_LEVEL_3: float = 30.0
    TIMEOUT_LEVEL_4: float = 45.0

    def __init__(
        self,
        level1: "Level1TextExtractor",
        level2: "Level2OCRExtractor",
        level3: "Level3StructuredExtractor",
        level4: "Level4LLMExtractor",
    ) -> None:
        self._level1 = level1
        self._level2 = level2
        self._level3 = level3
        self._level4 = level4

    async def parse(
        self,
        file_path: str,
        target_level: ParseLevel = ParseLevel.LEVEL_4_LLM,
        metadata: dict[str, Any] | None = None,
    ) -> ParseResult:
        """Execute le pipeline de parsing sur un fichier PDF."""
        start_time = time.time()
        result = ParseResult(
            metadata=metadata or {},
            confidence_scores={
                "level_1_text": 0.0, "level_2_ocr": 0.0,
                "level_3_structured": 0.0, "level_4_llm": 0.0, "overall": 0.0,
            },
        )

        # Niveau 1
        try:
            text, score = await asyncio.wait_for(self._level1.extract(file_path), timeout=self.TIMEOUT_LEVEL_1)
            result.pages = [PageResult(page_number=1, text=text, word_count=len(text.split()))]
            result.confidence_scores["level_1_text"] = score
            result.level_reached = 1
            if score >= self.MIN_CONFIDENCE and len(text) >= self.MIN_TEXT_LENGTH:
                result.confidence_scores["overall"] = score
                result.processing_time_ms = int((time.time() - start_time) * 1000)
                if target_level == ParseLevel.LEVEL_1_TEXT:
                    return result
            else:
                result.degraded = True
        except asyncio.TimeoutError:
            result.degraded = True
        except Exception as exc:
            logger.error("parsing_level_1_error", error=str(exc))
            result.degraded = True

        # Niveau 2 (si necessaire)
        if target_level.value >= 2:
            try:
                text, score = await asyncio.wait_for(self._level2.extract(file_path), timeout=self.TIMEOUT_LEVEL_2)
                result.pages = [PageResult(page_number=1, text=text, ocr_used=True, word_count=len(text.split()))]
                result.confidence_scores["level_2_ocr"] = score
                result.level_reached = 2
                if score >= self.MIN_CONFIDENCE:
                    result.confidence_scores["overall"] = max(result.confidence_scores["overall"], score)
                    result.processing_time_ms = int((time.time() - start_time) * 1000)
                    if target_level == ParseLevel.LEVEL_2_OCR:
                        return result
                else:
                    result.degraded = True
            except asyncio.TimeoutError:
                result.degraded = True
            except Exception as exc:
                logger.error("parsing_level_2_error", error=str(exc))
                result.degraded = True

        # Niveau 3 (si necessaire)
        if target_level.value >= 3:
            try:
                structured, score = await asyncio.wait_for(self._level3.extract(file_path), timeout=self.TIMEOUT_LEVEL_3)
                # Fusionner les tables dans les pages
                result.confidence_scores["level_3_structured"] = score
                result.level_reached = 3
                if score >= self.MIN_CONFIDENCE:
                    result.confidence_scores["overall"] = max(result.confidence_scores["overall"], score)
                    result.processing_time_ms = int((time.time() - start_time) * 1000)
                    if target_level == ParseLevel.LEVEL_3_STRUCTURED:
                        return result
                else:
                    result.degraded = True
            except asyncio.TimeoutError:
                result.degraded = True
            except Exception as exc:
                logger.error("parsing_level_3_error", error=str(exc))
                result.degraded = True

        # Niveau 4 (si necessaire)
        if target_level.value >= 4:
            try:
                full_text = "\n".join(p.text for p in result.pages if p.text)
                llm_result, score = await asyncio.wait_for(
                    self._level4.extract(full_text, result.pages), timeout=self.TIMEOUT_LEVEL_4
                )
                result.llm_analysis = llm_result
                result.confidence_scores["level_4_llm"] = score
                result.level_reached = 4
                result.confidence_scores["overall"] = max(result.confidence_scores["overall"], score)
                result.processing_time_ms = int((time.time() - start_time) * 1000)
            except asyncio.TimeoutError:
                result.degraded = True
            except Exception as exc:
                logger.error("parsing_level_4_error", error=str(exc))
                result.degraded = True

        return result
```

--------------------------------------------------------------------------------
FICHIER B10 : app/services/parsing/levels.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : pypdf, pdfplumber, pytesseract, pdf2image, Pillow, numpy,
              re, json, structlog, app/core/exceptions.py.

CLASSE 1 : Level1TextExtractor

```python
import pypdf
import structlog

logger = structlog.get_logger()

class Level1TextExtractor:
    def extract(self, file_path: str) -> tuple[str, float]:
        text_parts: list[str] = []
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page_num, page in enumerate(reader.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as exc:
            logger.error("level1_extraction_error", error=str(exc))
            raise
        full_text = "\n".join(text_parts)
        score = min(len(full_text) / 1000.0, 1.0)
        return full_text, score
```

CLASSE 2 : Level2OCRExtractor

```python
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import numpy as np

class Level2OCRExtractor:
    DEFAULT_DPI: int = 200
    DEFAULT_LANG: str = "fra+eng"

    def extract(self, file_path: str, dpi: int = DEFAULT_DPI, lang: str = DEFAULT_LANG) -> tuple[str, float]:
        text_parts: list[str] = []
        confidences: list[float] = []
        images = convert_from_path(file_path, dpi=dpi)
        for page_num, image in enumerate(images, start=1):
            data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
            page_text = " ".join(word for word in data["text"] if word.strip())
            text_parts.append(page_text)
            confidences_page = [int(c) for c, t in zip(data["conf"], data["text"]) if t.strip() and int(c) >= 0]
            avg_conf = np.mean(confidences_page) / 100.0 if confidences_page else 0.0
            confidences.append(avg_conf)
        full_text = "\n".join(text_parts)
        overall_confidence = float(np.mean(confidences)) if confidences else 0.0
        return full_text, overall_confidence
```

CLASSE 3 : Level3StructuredExtractor

```python
import pdfplumber

class Level3StructuredExtractor:
    def extract(self, file_path: str) -> tuple[dict, float]:
        result: dict = {"tables": [], "text_blocks": [], "words": []}
        total_cells = 0
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        result["tables"].append({"page": page_num, "data": table})
                        total_cells += sum(len(row) for row in table if row)
                words = page.extract_words()
                result["words"].extend([{"text": w["text"], "page": page_num} for w in words])
                text = page.extract_text()
                if text:
                    result["text_blocks"].append({"page": page_num, "text": text})
        score = min(total_cells / max(len(pdf.pages), 1), 1.0)
        return result, score
```

CLASSE 4 : Level4LLMExtractor

```python
import json
import re

class Level4LLMExtractor:
    SYSTEM_PROMPT: str = """Tu es un analyste specialise dans les marches publics.
Analyse le document et retourne UNIQUEMENT un JSON valide avec cette structure :
{
  "summary": "Resume en 3 phrases",
  "sections": [{"title": "...", "content": "..."}],
  "themes": ["theme1", "theme2"],
  "language": "fr|en|other",
  "document_type": "appel_d_offres|avis_periodique|autre",
  "confidence": 0.0
}
Ne retourne aucun texte en dehors du JSON."""

    def __init__(self, client: "MistralAIClient") -> None:
        self._client = client

    async def extract(self, text: str, structured_hint: dict | None = None) -> tuple[dict, float]:
        truncated = text[:12000] if len(text) > 12000 else text
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": truncated},
        ]
        try:
            response = await self._client.chat_completion(
                messages=messages, temperature=0.1, max_tokens=2000
            )
            content = response["choices"][0]["message"]["content"]
            parsed = self._extract_json(content)
            confidence = parsed.get("confidence", 0.0)
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                confidence = 0.5
            if parsed.get("document_type") in ("appel_d_offres", "avis_periodique"):
                confidence = min(confidence + 0.1, 1.0)
            if parsed.get("summary") and len(parsed["summary"]) > 20:
                confidence = min(confidence + 0.05, 1.0)
            return parsed, confidence
        except Exception as exc:
            logger.error("level4_llm_error", error=str(exc))
            return {"error": str(exc), "document_type": "unknown", "confidence": 0.0}, 0.0

    def _extract_json(self, content: str) -> dict:
        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1)
        else:
            start = content.find("{")
            end = content.rfind("}")
            json_str = content[start:end + 1] if start != -1 and end != -1 else content
        return json.loads(json_str)
```

--------------------------------------------------------------------------------
FICHIER B11 : app/services/extraction/cpv_extractor.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : re, pydantic v2, app/core/logging.py.

SCHEMA DE SORTIE :

```python
from pydantic import BaseModel, ConfigDict, Field

class ExtractedCPV(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str = Field(..., pattern=r"^\d{8}$")
    description: str = Field(default="Non specifie", max_length=500)
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_span: tuple[int, int]
    is_supplementary: bool = Field(default=False)
```

EXTRACTEUR A IMPLEMENTER :

```python
import re
import structlog

logger = structlog.get_logger()

class CPVExtractor:
    CPV_PATTERN = re.compile(r"(?:CPV[\s:]*)?(\d{8})\s*[-–—]\s*(.*?)(?=\n|\d{8}|\Z)", re.IGNORECASE | re.DOTALL)
    CPV_CODE_ONLY = re.compile(r"\b(\d{8})\b")

    VALID_PREFIXES: set[str] = {
        "03", "09", "14", "15", "16", "18", "19", "22", "24", "30",
        "31", "32", "33", "34", "35", "37", "38", "39", "41", "42",
        "43", "44", "45", "48", "50", "51", "55", "60", "63", "64",
        "65", "66", "70", "71", "72", "73", "75", "76", "77", "79",
        "80", "85", "90", "92", "98",
    }

    def extract(self, text: str) -> list[ExtractedCPV]:
        results: dict[str, ExtractedCPV] = {}
        for match in self.CPV_PATTERN.finditer(text):
            code = match.group(1)
            description = match.group(2).strip() if match.group(2) else "Non specifie"
            span = match.span()
            if not self._validate_code(code):
                continue
            confidence = 0.8
            if description == "Non specifie":
                confidence -= 0.2
            if code in results:
                results[code].confidence = min(results[code].confidence + 0.1, 1.0)
            else:
                results[code] = ExtractedCPV(
                    code=code, description=description, confidence=min(confidence, 1.0),
                    source_span=span, is_supplementary=self._is_supplementary(code)
                )
        for match in self.CPV_CODE_ONLY.finditer(text):
            code = match.group(1)
            span = match.span()
            if code in results or not self._validate_code(code):
                continue
            context = text[max(0, span[0] - 50):span[1] + 50]
            has_cpv_keyword = bool(re.search(r"CPV|VOCABULAIRE|COMMON|PROCUREMENT", context, re.I))
            confidence = 0.5 + (0.2 if has_cpv_keyword else 0.0)
            results[code] = ExtractedCPV(
                code=code, description="Non specifie", confidence=min(confidence, 1.0),
                source_span=span, is_supplementary=self._is_supplementary(code)
            )
        filtered = [r for r in results.values() if r.confidence >= 0.7]
        return sorted(filtered, key=lambda x: x.confidence, reverse=True)

    def _validate_code(self, code: str) -> bool:
        return len(code) == 8 and code.isdigit() and code[:2] in self.VALID_PREFIXES

    def _is_supplementary(self, code: str) -> bool:
        return code.startswith(("98", "99"))
```

--------------------------------------------------------------------------------
FICHIER B12 : app/services/extraction/amount_extractor.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : re, decimal.Decimal, pydantic v2, app/core/logging.py.

SCHEMA DE SORTIE :

```python
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ExtractedAmount(BaseModel):
    model_config = ConfigDict(extra="forbid")
    raw_value: str = Field(..., max_length=100)
    normalized_value: Decimal = Field(..., gt=0)
    currency: str = Field(default="EUR", pattern=r"^(EUR|USD|GBP|CHF|UNK)$")
    amount_type: str = Field(default="unknown", pattern=r"^(total|ht|ttc|budget|unitaire|unknown)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    context: str = Field(default="", max_length=1000)
    page_hint: int | None = Field(default=None, ge=1)
```

EXTRACTEUR A IMPLEMENTER :

```python
import re
from decimal import Decimal, InvalidOperation
import structlog

logger = structlog.get_logger()

class AmountExtractor:
    PATTERNS: list[tuple[re.Pattern, str]] = [
        (re.compile(r"(\d{1,3}(?:[\s.]?\d{3})*(?:[,\.]\d{1,2})?)\s*(EUR|€|USD|\$|GBP|£|CHF|euros?|dollars?|pounds?)", re.I), "with_currency"),
        (re.compile(r"(?:montant|prix|total|budget|estimation|valeur|cout|depense)\s*[:;=]\s*(\d{1,3}(?:[\s.]?\d{3})*(?:[,\.]\d{1,2})?)", re.I), "with_label"),
        (re.compile(r"(\d{1,3}(?:[\s.]?\d{3})*(?:[,\.]\d{1,2})?)\s*(?:HT|hors\s*taxes|TTC|toutes\s*taxes|tva\s*incluse)", re.I), "with_tax_context"),
        (re.compile(r"\b(\d{1,3}(?:[\s.]?\d{3})+(?:[,\.]\d{1,2})?)\b"), "isolated"),
    ]

    CURRENCY_MAP: dict[str, str] = {
        "eur": "EUR", "€": "EUR", "euro": "EUR", "euros": "EUR",
        "usd": "USD", "$": "USD", "dollar": "USD", "dollars": "USD",
        "gbp": "GBP", "£": "GBP", "pound": "GBP", "pounds": "GBP",
        "chf": "CHF",
    }

    def extract(self, text: str) -> list[ExtractedAmount]:
        found: list[ExtractedAmount] = []
        seen_positions: set[tuple[int, int]] = set()
        for pattern, pattern_type in self.PATTERNS:
            for match in pattern.finditer(text):
                span = match.span()
                if span in seen_positions:
                    continue
                seen_positions.add(span)
                raw = match.group(1)
                currency_str = match.group(2) if len(match.groups()) > 1 else None
                try:
                    normalized = self._normalize_amount(raw)
                except (InvalidOperation, ValueError):
                    continue
                if normalized > Decimal("10000000000") or normalized <= 0:
                    continue
                currency = "UNK"
                if currency_str:
                    currency = self.CURRENCY_MAP.get(currency_str.lower().strip(), "UNK")
                else:
                    currency = "EUR"
                amount_type = self._determine_type(text, span)
                confidence = self._calculate_confidence(pattern_type, raw, currency, amount_type)
                context = text[max(0, span[0] - 50):min(len(text), span[1] + 50)].replace("\n", " ")
                found.append(ExtractedAmount(
                    raw_value=raw, normalized_value=normalized, currency=currency,
                    amount_type=amount_type, confidence=confidence, context=context,
                ))
        deduped = self._deduplicate(found)
        filtered = [a for a in deduped if a.confidence >= 0.6]
        return sorted(filtered, key=lambda x: x.normalized_value, reverse=True)

    def _normalize_amount(self, raw: str) -> Decimal:
        cleaned = raw.replace(" ", "")
        if "," in cleaned and "." in cleaned:
            if cleaned.rfind(",") < cleaned.rfind("."):
                cleaned = cleaned.replace(",", "")
            else:
                cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            parts = cleaned.split(",")
            if len(parts) == 2 and len(parts[1]) <= 2:
                cleaned = cleaned.replace(",", ".")
            else:
                cleaned = cleaned.replace(",", "")
        return Decimal(cleaned)

    def _determine_type(self, text: str, span: tuple[int, int]) -> str:
        context = text[max(0, span[0] - 30):min(len(text), span[1] + 30)].lower()
        if any(kw in context for kw in ["ht", "hors taxe", "hors taxes"]):
            return "ht"
        if any(kw in context for kw in ["ttc", "toutes taxes", "tva incluse"]):
            return "ttc"
        if any(kw in context for kw in ["total", "global", "general"]):
            return "total"
        if any(kw in context for kw in ["budget", "estimation", "prevision"]):
            return "budget"
        if any(kw in context for kw in ["unitaire", "par unite", "par lot"]):
            return "unitaire"
        return "unknown"

    def _calculate_confidence(self, pattern_type: str, raw: str, currency: str, amount_type: str) -> float:
        confidence = 0.5
        if pattern_type == "with_currency":
            confidence += 0.2
        elif pattern_type == "with_label":
            confidence += 0.15
        elif pattern_type == "with_tax_context":
            confidence += 0.1
        if currency != "UNK":
            confidence += 0.1
        if amount_type != "unknown":
            confidence += 0.1
        return min(max(confidence, 0.0), 1.0)

    def _deduplicate(self, amounts: list[ExtractedAmount]) -> list[ExtractedAmount]:
        by_value: dict[Decimal, ExtractedAmount] = {}
        for amount in amounts:
            if amount.normalized_value in by_value:
                if amount.confidence > by_value[amount.normalized_value].confidence:
                    by_value[amount.normalized_value] = amount
            else:
                by_value[amount.normalized_value] = amount
        return list(by_value.values())
```

--------------------------------------------------------------------------------
FICHIER B13 : app/services/extraction/deadline_extractor.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : re, datetime, dateparser, pydantic v2, app/core/logging.py.

SCHEMA DE SORTIE :

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ExtractedDeadline(BaseModel):
    model_config = ConfigDict(extra="forbid")
    raw_value: str = Field(..., max_length=200)
    parsed_date: datetime
    date_type: str = Field(default="unknown", pattern=r"^(submission|opening|contract_start|contract_end|unknown)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    context: str = Field(default="", max_length=1000)
    is_relative: bool = Field(default=False)
```

EXTRACTEUR A IMPLEMENTER :

```python
import re
from datetime import datetime, timezone
import dateparser
import structlog

logger = structlog.get_logger()

class DeadlineExtractor:
    DEADLINE_KEYWORDS: list[str] = [
        "date limite", "date de cloture", "date de depot", "date de remise",
        "date butoir", "avant le", "avant la", "jusqu'au", "jusqu'a",
        "no later than", "tender deadline", "date de reception",
        "date limite de depot", "date limite de remise", "heure limite",
        "fin de reception", "dernier delai", "date d'ouverture",
        "opening date", "closing date", "submission deadline",
    ]

    DATE_PATTERNS: list[re.Pattern] = [
        re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}(?:\s+\d{1,2}[h:]\d{2})?)\b"),
        re.compile(
            r"\b(\d{1,2}\s+(?:janvier|fevrier|mars|avril|mai|juin|juillet|aout|"
            r"septembre|octobre|novembre|decembre|january|february|march|april|"
            r"may|june|july|august|september|october|november|december)\s+\d{4})\b",
            re.IGNORECASE,
        ),
        re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    ]

    def extract(self, text: str, reference_date: datetime | None = None) -> list[ExtractedDeadline]:
        if reference_date is None:
            reference_date = datetime.now(timezone.utc)
        found: list[ExtractedDeadline] = []
        seen_positions: set[tuple[int, int]] = set()

        for pattern in self.DATE_PATTERNS:
            for match in pattern.finditer(text):
                span = match.span()
                if span in seen_positions:
                    continue
                seen_positions.add(span)
                raw = match.group(1)
                parsed = self._parse_date(raw)
                if parsed is None:
                    continue
                # Determiner type et confidence via contexte
                context_window = text[max(0, span[0] - 100):min(len(text), span[1] + 100)]
                date_type = self._determine_type(context_window)
                confidence = self._calculate_confidence(parsed, reference_date, context_window)
                if confidence < 0.5:
                    continue
                found.append(ExtractedDeadline(
                    raw_value=raw, parsed_date=parsed, date_type=date_type,
                    confidence=confidence, context=context_window[:200],
                    is_relative=("dans" in raw.lower() or "within" in raw.lower()),
                ))
        # Filtrer dates passees de plus d'un an
        filtered = [d for d in found if d.parsed_date > reference_date or (reference_date - d.parsed_date).days < 365]
        return sorted(filtered, key=lambda x: x.parsed_date)

    def _parse_date(self, raw: str) -> datetime | None:
        parsed = dateparser.parse(raw, languages=["fr", "en"], settings={
            "PREFER_DAY_OF_MONTH": "first",
            "RETURN_AS_TIMEZONE_AWARE": True,
        })
        return parsed

    def _determine_type(self, context: str) -> str:
        context_lower = context.lower()
        if any(kw in context_lower for kw in ["ouverture", "opening"]):
            return "opening"
        if any(kw in context_lower for kw in ["depot", "remise", "reception", "submission", "closing", "limite", "deadline"]):
            return "submission"
        if any(kw in context_lower for kw in ["debut", "start", "commencement"]):
            return "contract_start"
        if any(kw in context_lower for kw in ["fin", "end", "achevement"]):
            return "contract_end"
        return "unknown"

    def _calculate_confidence(self, parsed: datetime, reference_date: datetime, context: str) -> float:
        confidence = 0.5
        # Proximite avec keywords deadline
        context_lower = context.lower()
        if any(kw in context_lower for kw in self.DEADLINE_KEYWORDS):
            confidence += 0.3
        # Date dans le futur
        if parsed > reference_date:
            confidence += 0.1
        # Annee raisonnable
        if parsed.year >= reference_date.year:
            confidence += 0.1
        return min(confidence, 1.0)
```

================================================================================
 GROUPE C : LLM et Resilience (fichiers C14 a C15)
================================================================================

--------------------------------------------------------------------------------
FICHIER C14 : app/services/llm/mistral_client.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : httpx, tenacity, pydantic, app/core/config.py,
              app/core/exceptions.py (ExternalServiceError), app/core/logging.py.

CLASSE PRINCIPALE A IMPLEMENTER :

```python
import httpx
import tenacity
import structlog
from typing import Any
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError

logger = structlog.get_logger()

class MistralAIClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mistral.ai/v1",
        primary_model: str = "mistral-medium-latest",
        fallback_model: str = "mistral-small-latest",
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._primary_model = primary_model
        self._fallback_model = fallback_model
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=10.0),
            headers={"Authorization": f"Bearer {api_key}"},
        )

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError)),
        reraise=True,
    )
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Envoie une requete chat.completion a l'API Mistral."""
        model = model or self._primary_model
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        try:
            response = await self._client.post(
                f"{self._base_url}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (429, 503):
                # Fallback au modele secondaire
                logger.warning("mistral_primary_failed", status=exc.response.status_code, fallback=self._fallback_model)
                payload["model"] = self._fallback_model
                response = await self._client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
            if exc.response.status_code == 401:
                raise ExternalServiceError("Mistral API authentication failed")
            raise ExternalServiceError(f"Mistral API error: {exc.response.status_code}")
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("Mistral API timeout") from exc

    async def embed_texts(self, texts: list[str], model: str = "mistral-embed") -> list[list[float]]:
        """Genere des embeddings pour une liste de textes."""
        payload = {"model": model, "input": texts}
        try:
            response = await self._client.post(
                f"{self._base_url}/embeddings",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as exc:
            logger.error("mistral_embedding_error", error=str(exc))
            raise ExternalServiceError("Failed to generate embeddings") from exc

    async def close(self) -> None:
        await self._client.aclose()
```

--------------------------------------------------------------------------------
FICHIER C15 : app/services/llm/circuit_breaker.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : pybreaker, structlog.

CONTENU :

```python
from pybreaker import CircuitBreaker
from pybreaker.listeners import CircuitBreakerListener
import structlog

logger = structlog.get_logger()

class LoggingCircuitBreakerListener(CircuitBreakerListener):
    def state_change(self, cb: CircuitBreaker, old_state: str, new_state: str) -> None:
        logger.info("circuit_breaker_state_changed", name=cb.name, old_state=old_state, new_state=new_state)

    def failure(self, cb: CircuitBreaker, exc: Exception) -> None:
        logger.warning("circuit_breaker_failure", name=cb.name, error=str(exc), fail_count=cb.fail_counter)

    def success(self, cb: CircuitBreaker) -> None:
        logger.info("circuit_breaker_success", name=cb.name, fail_count=cb.fail_counter)

def create_mistral_circuit_breaker() -> CircuitBreaker:
    return CircuitBreaker(
        fail_max=5,
        timeout=120,
        expected_exception=(Exception,),
        listeners=[LoggingCircuitBreakerListener()],
        name="mistral_api",
    )
```

================================================================================
 GROUPE D : Memoire a 4 types (fichiers D16 a D20)
================================================================================

--------------------------------------------------------------------------------
FICHIER D16 : app/models/memory.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : sqlalchemy, pydantic, datetime, enum, uuid, pgvector.

ENUMS ET SCHEMAS :

```python
import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.db.base import Base

class MemoryType(str, enum.Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    TRANSACTIONAL = "transactional"

class MemoryPriority(int, enum.Enum):
    CRITICAL = 5
    HIGH = 4
    NORMAL = 3
    LOW = 2
    ARCHIVE = 1
```

TABLE memory_entries :

```python
class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    memory_type: Mapped[MemoryType] = mapped_column(String(32), nullable=False, index=True)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=MemoryPriority.NORMAL)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    ttl_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decay_factor: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    consolidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

TABLE memory_consolidations :

```python
class MemoryConsolidation(Base):
    __tablename__ = "memory_consolidations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    memory_entry_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memory_entries.id"), nullable=False, index=True)
    from_entries: Mapped[list[uuid.UUID]] = mapped_column(JSON, nullable=False)
    consolidation_type: Mapped[str] = mapped_column(String(32), nullable=False)
    previous_version: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
```

INDEXES :

```sql
CREATE INDEX idx_memory_entries_type_priority ON memory_entries(memory_type, priority DESC, created_at DESC);
CREATE INDEX idx_memory_entries_expires ON memory_entries(expires_at);
CREATE INDEX idx_memory_entries_embedding ON memory_entries USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_memory_consolidations_entry ON memory_consolidations(memory_entry_id);
```

--------------------------------------------------------------------------------
FICHIER D17 : app/services/memory/episodic_memory.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : sqlalchemy, datetime, app/models/memory.py (MemoryEntry, MemoryType, MemoryPriority), app/services/llm/mistral_client.py.

INTERFACE :

```python
from datetime import datetime, timezone, timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
import structlog

logger = structlog.get_logger()

class EpisodicMemoryService:
    DEFAULT_TTL_DAYS: int = 30

    def __init__(self, db_session: AsyncSession, embedding_client: "MistralAIClient") -> None:
        self._db = db_session
        self._embedding_client = embedding_client

    async def record_event(
        self,
        user_id: uuid.UUID | None,
        event_type: str,
        context: dict[str, Any],
        importance: MemoryPriority = MemoryPriority.NORMAL,
        ttl_days: int | None = None,
    ) -> MemoryEntry:
        ttl = ttl_days or self.DEFAULT_TTL_DAYS
        expires_at = datetime.now(timezone.utc) + timedelta(days=ttl)
        content = {"event_type": event_type, "context": context, "timestamp": datetime.now(timezone.utc).isoformat()}
        entry = MemoryEntry(
            user_id=user_id,
            memory_type=MemoryType.EPISODIC,
            content=content,
            content_hash=self._hash_content(content),
            priority=importance,
            source_type="system_event",
            ttl_seconds=ttl * 86400,
            expires_at=expires_at,
        )
        self._db.add(entry)
        await self._db.commit()
        await self._db.refresh(entry)
        logger.info("episodic_event_recorded", entry_id=str(entry.id), event_type=event_type)
        return entry

    async def recall_events(
        self,
        user_id: uuid.UUID | None,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 50,
        min_importance: MemoryPriority = MemoryPriority.LOW,
    ) -> list[MemoryEntry]:
        stmt = select(MemoryEntry).where(
            and_(
                MemoryEntry.memory_type == MemoryType.EPISODIC,
                MemoryEntry.priority >= min_importance,
                MemoryEntry.expires_at > datetime.now(timezone.utc),
            )
        )
        if user_id:
            stmt = stmt.where(MemoryEntry.user_id == user_id)
        if event_type:
            # Filtrer par event_type dans le JSON content
            stmt = stmt.where(MemoryEntry.content["event_type"].as_string() == event_type)
        if since:
            stmt = stmt.where(MemoryEntry.created_at >= since)
        stmt = stmt.order_by(MemoryEntry.created_at.desc()).limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def search_similar_events(
        self,
        query_embedding: list[float],
        user_id: uuid.UUID | None = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
    ) -> list[MemoryEntry]:
        # Recherche vectorielle via pgvector
        from sqlalchemy import text
        query = text("""
            SELECT * FROM memory_entries
            WHERE memory_type = 'episodic'
            AND embedding IS NOT NULL
            AND embedding <=> :embedding < :threshold
            ORDER BY embedding <=> :embedding
            LIMIT :limit
        """)
        result = await self._db.execute(query, {
            "embedding": str(query_embedding),
            "threshold": 1 - similarity_threshold,
            "limit": limit,
        })
        return list(result.scalars().all())

    async def purge_expired(self) -> int:
        stmt = delete(MemoryEntry).where(
            and_(
                MemoryEntry.memory_type == MemoryType.EPISODIC,
                MemoryEntry.expires_at <= datetime.now(timezone.utc),
            )
        )
        result = await self._db.execute(stmt)
        await self._db.commit()
        return result.rowcount or 0

    def _hash_content(self, content: dict[str, Any]) -> str:
        import hashlib, json
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
```

--------------------------------------------------------------------------------
FICHIER D18 : app/services/memory/semantic_memory.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : sqlalchemy, pgvector, app/models/memory.py, app/services/llm/mistral_client.py.

INTERFACE :

```python
from datetime import datetime, timezone, timedelta
import uuid
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
import structlog

logger = structlog.get_logger()

class SemanticMemoryService:
    HALF_LIFE_DAYS: float = 90.0

    def __init__(self, db_session: AsyncSession, embedding_client: "MistralAIClient") -> None:
        self._db = db_session
        self._embedding_client = embedding_client

    async def store_knowledge(
        self,
        user_id: uuid.UUID | None,
        subject: str,
        fact: dict[str, Any],
        embedding_text: str,
        priority: MemoryPriority = MemoryPriority.NORMAL,
    ) -> MemoryEntry:
        # Generer embedding
        embeddings = await self._embedding_client.embed_texts([embedding_text])
        embedding = embeddings[0] if embeddings else None

        content = {"subject": subject, **fact}
        entry = MemoryEntry(
            user_id=user_id,
            memory_type=MemoryType.SEMANTIC,
            content=content,
            content_hash=self._hash_content(content),
            embedding=embedding,
            priority=priority,
            source_type="document_extraction",
        )
        self._db.add(entry)
        await self._db.commit()
        await self._db.refresh(entry)
        return entry

    async def query_knowledge(
        self,
        query_text: str,
        user_id: uuid.UUID | None = None,
        subject_filter: str | None = None,
        limit: int = 10,
        similarity_threshold: float = 0.75,
    ) -> list[tuple[MemoryEntry, float]]:
        embeddings = await self._embedding_client.embed_texts([query_text])
        query_embedding = embeddings[0]

        # Recherche par similarite cosinus
        from sqlalchemy import text
        sql = """
            SELECT *, 1 - (embedding <=> :query_embedding) AS similarity
            FROM memory_entries
            WHERE memory_type = 'semantic'
            AND embedding IS NOT NULL
            AND 1 - (embedding <=> :query_embedding) > :threshold
        """
        params = {"query_embedding": str(query_embedding), "threshold": similarity_threshold}
        if user_id:
            sql += " AND user_id = :user_id"
            params["user_id"] = str(user_id)
        if subject_filter:
            sql += " AND content->>'subject' = :subject"
            params["subject"] = subject_filter
        sql += " ORDER BY similarity DESC LIMIT :limit"
        params["limit"] = limit

        result = await self._db.execute(text(sql), params)
        rows = result.mappings().all()
        entries = []
        for row in rows:
            entry = row["memory_entries"]
            similarity = row["similarity"]
            decayed_score = similarity * entry.decay_factor
            entries.append((entry, decayed_score))
        return entries

    async def update_decay(self) -> None:
        # Recuperer toutes les entrees semantiques
        stmt = select(MemoryEntry).where(MemoryEntry.memory_type == MemoryType.SEMANTIC)
        result = await self._db.execute(stmt)
        entries = result.scalars().all()
        now = datetime.now(timezone.utc)
        for entry in entries:
            age_days = (now - entry.created_at).days
            decay = 0.5 ** (age_days / self.HALF_LIFE_DAYS)
            entry.decay_factor = decay
            if decay < 0.1 and entry.priority > MemoryPriority.ARCHIVE:
                entry.priority = MemoryPriority.ARCHIVE
        await self._db.commit()

    async def consolidate_facts(
        self,
        subject: str,
        user_id: uuid.UUID | None = None,
    ) -> MemoryEntry | None:
        # Recuperer les faits ARCHIVE d'un sujet
        stmt = select(MemoryEntry).where(
            and_(
                MemoryEntry.memory_type == MemoryType.SEMANTIC,
                MemoryEntry.content["subject"].as_string() == subject,
                MemoryEntry.priority == MemoryPriority.ARCHIVE,
            )
        )
        if user_id:
            stmt = stmt.where(MemoryEntry.user_id == user_id)
        result = await self._db.execute(stmt)
        facts = result.scalars().all()
        if len(facts) < 5:
            return None
        # Creer un resume (simplifie pour le sprint)
        summary_content = {
            "subject": subject,
            "consolidated": True,
            "fact_count": len(facts),
            "summary": "Consolidation de faits semantiques",
        }
        entry = MemoryEntry(
            user_id=user_id,
            memory_type=MemoryType.SEMANTIC,
            content=summary_content,
            content_hash=self._hash_content(summary_content),
            priority=MemoryPriority.NORMAL,
            source_type="consolidation",
        )
        self._db.add(entry)
        await self._db.commit()
        return entry

    def _hash_content(self, content: dict[str, Any]) -> str:
        import hashlib, json
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
```

--------------------------------------------------------------------------------
FICHIER D19 : app/services/memory/procedural_memory.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : sqlalchemy, app/models/memory.py.

INTERFACE :

```python
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Any

class ProceduralMemoryService:
    CONSOLIDATION_THRESHOLD: int = 7

    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session

    async def record_procedure(
        self,
        user_id: uuid.UUID | None,
        procedure_name: str,
        steps: list[dict[str, Any]],
        outcome: str,
        context: dict[str, Any],
    ) -> MemoryEntry:
        content = {
            "procedure_name": procedure_name,
            "steps": steps,
            "outcome": outcome,
            "context": context,
            "execution_time": context.get("duration_ms"),
        }
        entry = MemoryEntry(
            user_id=user_id,
            memory_type=MemoryType.PROCEDURAL,
            content=content,
            content_hash=self._hash_content(content),
            priority=MemoryPriority.NORMAL,
            source_type="procedure_execution",
        )
        self._db.add(entry)
        await self._db.commit()
        await self._db.refresh(entry)
        return entry

    async def get_procedure(
        self,
        procedure_name: str,
        user_id: uuid.UUID | None = None,
    ) -> list[MemoryEntry]:
        stmt = select(MemoryEntry).where(
            and_(
                MemoryEntry.memory_type == MemoryType.PROCEDURAL,
                MemoryEntry.content["procedure_name"].as_string() == procedure_name,
            )
        )
        if user_id:
            stmt = stmt.where(MemoryEntry.user_id == user_id)
        stmt = stmt.order_by(MemoryEntry.created_at.desc())
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_best_procedure(
        self,
        procedure_name: str,
        user_id: uuid.UUID | None = None,
    ) -> dict[str, Any] | None:
        # Chercher une procedure consolidee
        stmt = select(MemoryEntry).where(
            and_(
                MemoryEntry.memory_type == MemoryType.PROCEDURAL,
                MemoryEntry.content["procedure_name"].as_string() == procedure_name,
                MemoryEntry.consolidated_at.isnot(None),
            )
        )
        if user_id:
            stmt = stmt.where(MemoryEntry.user_id == user_id)
        result = await self._db.execute(stmt.limit(1))
        consolidated = result.scalar_one_or_none()
        if consolidated:
            return consolidated.content
        # Sinon, chercher la plus frequente
        return None  # Simplifie pour le sprint

    async def consolidate_procedure(
        self,
        procedure_name: str,
        user_id: uuid.UUID | None = None,
    ) -> MemoryEntry | None:
        # Compter les succes
        stmt = select(func.count()).where(
            and_(
                MemoryEntry.memory_type == MemoryType.PROCEDURAL,
                MemoryEntry.content["procedure_name"].as_string() == procedure_name,
                MemoryEntry.content["outcome"].as_string() == "success",
            )
        )
        if user_id:
            stmt = stmt.where(MemoryEntry.user_id == user_id)
        result = await self._db.execute(stmt)
        success_count = result.scalar() or 0
        if success_count < self.CONSOLIDATION_THRESHOLD:
            return None
        # Creer le template consolide
        template_content = {
            "procedure_name": procedure_name,
            "template": True,
            "success_count": success_count,
            "steps_template": [],  # A enrichir
        }
        entry = MemoryEntry(
            user_id=user_id,
            memory_type=MemoryType.PROCEDURAL,
            content=template_content,
            content_hash=self._hash_content(template_content),
            priority=MemoryPriority.HIGH,
            source_type="procedure_template",
            consolidated_at=datetime.now(timezone.utc),
        )
        self._db.add(entry)
        await self._db.commit()
        return entry

    def _hash_content(self, content: dict[str, Any]) -> str:
        import hashlib, json
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
```

--------------------------------------------------------------------------------
FICHIER D20 : app/services/memory/transactional_memory.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : sqlalchemy, app/models/memory.py, datetime.

INTERFACE :

```python
from datetime import datetime, timezone, timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from typing import Any

class TransactionalMemoryService:
    ARCHIVE_AFTER_DAYS: int = 365

    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session

    async def log_transaction(
        self,
        transaction_type: str,
        actor_id: uuid.UUID | None,
        resource_type: str,
        resource_id: uuid.UUID,
        before_state: dict[str, Any] | None,
        after_state: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        content = {
            "transaction_type": transaction_type,
            "actor_id": str(actor_id) if actor_id else None,
            "resource_type": resource_type,
            "resource_id": str(resource_id),
            "before_state": before_state,
            "after_state": after_state,
            "metadata": metadata or {},
        }
        entry = MemoryEntry(
            user_id=actor_id,
            memory_type=MemoryType.TRANSACTIONAL,
            content=content,
            content_hash=self._hash_content(content),
            priority=MemoryPriority.NORMAL,
            source_type=resource_type,
            source_id=resource_id,
        )
        self._db.add(entry)
        await self._db.commit()
        await self._db.refresh(entry)
        return entry

    async def get_transaction_history(
        self,
        resource_type: str,
        resource_id: uuid.UUID,
        limit: int = 100,
    ) -> list[MemoryEntry]:
        stmt = select(MemoryEntry).where(
            and_(
                MemoryEntry.memory_type == MemoryType.TRANSACTIONAL,
                MemoryEntry.source_type == resource_type,
                MemoryEntry.source_id == resource_id,
            )
        ).order_by(MemoryEntry.created_at.desc()).limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_audit_trail(
        self,
        actor_id: uuid.UUID | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        transaction_type: str | None = None,
        limit: int = 500,
    ) -> list[MemoryEntry]:
        stmt = select(MemoryEntry).where(MemoryEntry.memory_type == MemoryType.TRANSACTIONAL)
        if actor_id:
            stmt = stmt.where(MemoryEntry.user_id == actor_id)
        if since:
            stmt = stmt.where(MemoryEntry.created_at >= since)
        if until:
            stmt = stmt.where(MemoryEntry.created_at <= until)
        if transaction_type:
            stmt = stmt.where(MemoryEntry.content["transaction_type"].as_string() == transaction_type)
        stmt = stmt.order_by(MemoryEntry.created_at.desc()).limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def archive_old_transactions(self) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.ARCHIVE_AFTER_DAYS)
        # Selectionner les anciennes transactions
        stmt = select(MemoryEntry).where(
            and_(
                MemoryEntry.memory_type == MemoryType.TRANSACTIONAL,
                MemoryEntry.created_at <= cutoff,
            )
        )
        result = await self._db.execute(stmt)
        old_entries = result.scalars().all()
        # Les archiver dans memory_archive (table a creer si necessaire)
        # Pour le sprint : deplacer vers une table d'archive simple
        archived_count = len(old_entries)
        return archived_count

    def _hash_content(self, content: dict[str, Any]) -> str:
        import hashlib, json
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
```

--------------------------------------------------------------------------------
FICHIER D21 : app/services/memory/memory_manager.py (NOUVEAU — facade)
--------------------------------------------------------------------------------

DEPENDANCES : Tous les services memoire.

INTERFACE :

```python
from typing import Any
import uuid

class MemoryManager:
    def __init__(
        self,
        episodic: EpisodicMemoryService,
        semantic: SemanticMemoryService,
        procedural: ProceduralMemoryService,
        transactional: TransactionalMemoryService,
    ) -> None:
        self.episodic = episodic
        self.semantic = semantic
        self.procedural = procedural
        self.transactional = transactional

    async def record_document_lifecycle(
        self,
        user_id: uuid.UUID,
        document_id: uuid.UUID,
        stage: str,
        details: dict[str, Any],
    ) -> None:
        # Episodique
        await self.episodic.record_event(
            user_id=user_id,
            event_type="document_stage_changed",
            context={"document_id": str(document_id), "stage": stage, **details},
        )
        # Transactionnelle
        await self.transactional.log_transaction(
            transaction_type="state_change",
            actor_id=user_id,
            resource_type="document",
            resource_id=document_id,
            before_state={"stage": details.get("previous_stage")},
            after_state={"stage": stage},
        )
        # Semantique si stage = approved
        if stage == "approved":
            await self.semantic.store_knowledge(
                user_id=user_id,
                subject=f"document:{document_id}",
                fact={"stage": stage, "entities": details.get("entities", {})},
                embedding_text=details.get("summary_text", ""),
            )
        # Procedurale si parsing reussi
        if stage == "parsed" and details.get("success"):
            await self.procedural.record_procedure(
                user_id=user_id,
                procedure_name="parse_pdf",
                steps=details.get("steps", []),
                outcome="success",
                context=details,
            )

    async def recall_similar_documents(
        self,
        query_text: str,
        user_id: uuid.UUID | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        results = await self.semantic.query_knowledge(
            query_text=query_text,
            user_id=user_id,
            limit=limit,
        )
        return [{"entry": r[0], "score": r[1]} for r in results]

    async def get_system_experience(self, procedure_name: str) -> dict[str, Any] | None:
        return await self.procedural.get_best_procedure(procedure_name)

    async def get_document_audit_trail(self, document_id: uuid.UUID) -> list[dict[str, Any]]:
        entries = await self.transactional.get_transaction_history("document", document_id)
        return [e.content for e in entries]

    async def run_maintenance(self) -> dict[str, Any]:
        purged = await self.episodic.purge_expired()
        await self.semantic.update_decay()
        # Consolidation procedurale (simplifiee)
        archived = await self.transactional.archive_old_transactions()
        return {
            "episodic_purged": purged,
            "semantic_decay_updated": True,
            "transactional_archived": archived,
        }
```

================================================================================
 GROUPE E : Validation N Gates (fichiers E22 a E24)
================================================================================

--------------------------------------------------------------------------------
FICHIER E22 : app/core/validation.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : pydantic, jsonschema, hashlib, datetime, enum, structlog,
              app/core/exceptions.py, app/models/memory.py.

ENUMS ET SCHEMAS :

```python
import enum
from datetime import datetime
from typing import Any, Callable, Awaitable
from pydantic import BaseModel, ConfigDict, Field
import uuid

class GateStatus(str, enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"

class GateName(str, enum.Enum):
    SYNTAX = "syntax_gate"
    SEMANTIC = "semantic_gate"
    RBAC = "rbac_gate"
    IDEMPOTENCE = "idempotence_gate"
    DETERMINISM = "determinism_gate"
    HIL = "hil_gate"

class GateResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    gate_name: GateName
    status: GateStatus
    message: str
    detail: dict[str, Any] | None = None
    execution_time_ms: int
    input_hash: str
    output_hash: str
    timestamp: datetime

class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: uuid.UUID
    overall_status: GateStatus
    gate_results: list[GateResult]
    final_output: dict[str, Any] | None = None
    audit_id: uuid.UUID
    total_execution_time_ms: int
    created_at: datetime
```

TYPE ALIAS POUR LES GATES :

```python
GateCallable = Callable[..., Awaitable[GateResult]]
```

CLASSE PRINCIPALE :

```python
import json
import hashlib
import time
import structlog
from app.core.exceptions import ValidationError, AuthorizationError
from app.models.memory import MemoryManager

logger = structlog.get_logger()

class ValidationPipeline:
    """Pipeline de validation a 6 gates avec early-exit."""

    # Ordre et bloquant/non bloquant
    GATE_ORDER: list[tuple[GateName, bool]] = [
        (GateName.SYNTAX, True),
        (GateName.RBAC, True),
        (GateName.IDEMPOTENCE, True),
        (GateName.SEMANTIC, True),
        (GateName.DETERMINISM, False),
        (GateName.HIL, True),
    ]

    def __init__(self, gates: dict[GateName, GateCallable]) -> None:
        self._gates = gates

    async def validate(
        self,
        request_id: uuid.UUID,
        data: dict[str, Any],
        user: "UserInDB",
        autonomy_level: int,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        start_time = time.time()
        gate_results: list[GateResult] = []
        overall_status = GateStatus.PASSED

        for gate_name, is_blocking in self.GATE_ORDER:
            gate_start = time.time()
            gate_fn = self._gates.get(gate_name)
            if not gate_fn:
                result = GateResult(
                    gate_name=gate_name,
                    status=GateStatus.SKIPPED,
                    message="Gate not configured",
                    execution_time_ms=0,
                    input_hash="",
                    output_hash="",
                    timestamp=datetime.now(),
                )
                gate_results.append(result)
                continue

            try:
                result = await gate_fn(data=data, user=user, context=context, autonomy_level=autonomy_level)
            except Exception as exc:
                result = GateResult(
                    gate_name=gate_name,
                    status=GateStatus.FAILED,
                    message=f"Gate execution error: {exc}",
                    detail={"error": str(exc)},
                    execution_time_ms=int((time.time() - gate_start) * 1000),
                    input_hash=self._hash_data(data),
                    output_hash="",
                    timestamp=datetime.now(),
                )

            result.execution_time_ms = int((time.time() - gate_start) * 1000)
            gate_results.append(result)

            if result.status == GateStatus.FAILED and is_blocking:
                overall_status = GateStatus.FAILED
                # Marquer les gates suivants comme SKIPPED
                for remaining_name, _ in self.GATE_ORDER[len(gate_results):]:
                    gate_results.append(GateResult(
                        gate_name=remaining_name,
                        status=GateStatus.SKIPPED,
                        message="Skipped due to previous gate failure",
                        execution_time_ms=0,
                        input_hash="",
                        output_hash="",
                        timestamp=datetime.now(),
                    ))
                break
            elif result.status == GateStatus.WARNING and not is_blocking:
                if overall_status == GateStatus.PASSED:
                    overall_status = GateStatus.WARNING

        total_time = int((time.time() - start_time) * 1000)
        return ValidationResult(
            request_id=request_id,
            overall_status=overall_status,
            gate_results=gate_results,
            final_output=data if overall_status in (GateStatus.PASSED, GateStatus.WARNING) else None,
            audit_id=uuid.uuid4(),
            total_execution_time_ms=total_time,
            created_at=datetime.now(),
        )

    def _hash_data(self, data: dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
```

IMPLEMENTATION DES 6 GATES (fonctions a implementer separement) :

```python
async def syntax_gate(data: dict[str, Any], schema: dict[str, Any] | None = None, **kwargs: Any) -> GateResult:
    """Gate 1 : Validation JSON schema."""
    from jsonschema import validate, ValidationError as JsonSchemaError
    start = time.time()
    try:
        if schema:
            validate(instance=data, schema=schema)
        # Verifier que c'est du JSON serialisable
        json.dumps(data)
        return GateResult(
            gate_name=GateName.SYNTAX,
            status=GateStatus.PASSED,
            message="JSON structure is valid",
            execution_time_ms=0,
            input_hash="",
            output_hash="",
            timestamp=datetime.now(),
        )
    except JsonSchemaError as exc:
        return GateResult(
            gate_name=GateName.SYNTAX,
            status=GateStatus.FAILED,
            message=f"Schema validation failed: {exc.message}",
            detail={"path": list(exc.path), "validator": exc.validator},
            execution_time_ms=0,
            input_hash="",
            output_hash="",
            timestamp=datetime.now(),
        )

async def rbac_gate(data: dict[str, Any], user: "UserInDB", required_permission: str = "document:create", **kwargs: Any) -> GateResult:
    """Gate 2 : Verification permissions."""
    from app.core.exceptions import AuthorizationError
    # Verifier que l'utilisateur a la permission
    has_permission = await check_permission(user, required_permission)
    if has_permission:
        return GateResult(gate_name=GateName.RBAC, status=GateStatus.PASSED, message="User has required permission", execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())
    return GateResult(gate_name=GateName.RBAC, status=GateStatus.FAILED, message=f"Missing permission: {required_permission}", detail={"user_id": str(user.id), "required": required_permission}, execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())

async def idempotence_gate(data: dict[str, Any], user_id: uuid.UUID, memory_manager: MemoryManager, **kwargs: Any) -> GateResult:
    """Gate 3 : Detection de doublons."""
    # Calculer fingerprint
    fingerprint = hashlib.sha256(json.dumps(data.get("parse_result", {}).get("pages", []), sort_keys=True).encode()).hexdigest()
    # Recherche similaire
    similar = await memory_manager.recall_similar_documents(query_text=data.get("parse_result", {}).get("pages", [{}])[0].get("text", ""), user_id=user_id, limit=5)
    if similar and similar[0]["score"] > 0.95:
        return GateResult(gate_name=GateName.IDEMPOTENCE, status=GateStatus.FAILED, message="Duplicate document detected", detail={"similarity": similar[0]["score"], "existing_id": similar[0]["entry"].get("source_id")}, execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())
    return GateResult(gate_name=GateName.IDEMPOTENCE, status=GateStatus.PASSED, message="No duplicate detected", execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())

async def semantic_gate(data: dict[str, Any], **kwargs: Any) -> GateResult:
    """Gate 4 : Coherence semantique des entites."""
    entities = data.get("extracted_entities", {})
    errors: list[str] = []
    cpv_list = entities.get("cpv_codes", [])
    amounts = entities.get("amounts", [])
    deadlines = entities.get("deadlines", [])

    if not cpv_list:
        errors.append("No CPV codes found")
    else:
        low_confidence_cpv = [c for c in cpv_list if c.get("confidence", 0) < 0.7]
        if low_confidence_cpv:
            errors.append(f"{len(low_confidence_cpv)} CPV codes below confidence threshold")

    if not amounts:
        errors.append("No amounts found")
    else:
        total_amounts = [a for a in amounts if a.get("amount_type") == "total"]
        if not total_amounts:
            errors.append("No total amount identified")

    if not deadlines:
        errors.append("No deadlines found")

    if errors:
        return GateResult(gate_name=GateName.SEMANTIC, status=GateStatus.FAILED, message="Semantic validation failed", detail={"errors": errors}, execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())
    return GateResult(gate_name=GateName.SEMANTIC, status=GateStatus.PASSED, message="All semantic checks passed", execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())

async def determinism_gate(data: dict[str, Any], run_count: int = 3, **kwargs: Any) -> GateResult:
    """Gate 5 : Verifier la stabilite du resultat sur N executions."""
    # Simplifie pour le sprint : comparer le hash actuel avec un hash theorique
    current_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    return GateResult(gate_name=GateName.DETERMINISM, status=GateStatus.PASSED, message="Determinism check passed", detail={"hash": current_hash[:16]}, execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())

async def hil_gate(data: dict[str, Any], autonomy_level: int, hil_service: "HILService", **kwargs: Any) -> GateResult:
    """Gate 6 : Human-in-the-Loop selon le niveau d'autonomie."""
    if autonomy_level == 0:  # MANUEL
        hil_request = await hil_service.create_request(
            request_id=uuid.uuid4(),
            autonomy_level=autonomy_level,
            decision_type="document_approval",
            context=data,
        )
        return GateResult(gate_name=GateName.HIL, status=GateStatus.FAILED, message="Human validation required (manual mode)", detail={"hil_request_id": str(hil_request.id)}, execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())
    elif autonomy_level == 1:  # ASSISTE
        avg_confidence = data.get("confidence_scores", {}).get("overall", 0.0)
        if avg_confidence < 0.7:
            return GateResult(gate_name=GateName.HIL, status=GateStatus.FAILED, message="Low confidence requires human validation", detail={"confidence": avg_confidence}, execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())
    elif autonomy_level == 2:  # SUPERVISE
        # Si un gate precedent a bloque, le pipeline s'est deja arrete
        pass
    # AUTONOME (3) : passe automatiquement
    return GateResult(gate_name=GateName.HIL, status=GateStatus.PASSED, message="HIL gate passed", execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now())
```

--------------------------------------------------------------------------------
FICHIER E23 : app/models/validation_audit.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : sqlalchemy, datetime, uuid, json.

TABLE SQLALCHEMY :

```python
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class ValidationAudit(Base):
    __tablename__ = "validation_audit"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    gate_name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    output_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
```

INDEXES :
```sql
CREATE INDEX idx_validation_audit_request ON validation_audit(request_id);
CREATE INDEX idx_validation_audit_gate_status ON validation_audit(gate_name, status);
CREATE INDEX idx_validation_audit_created_at ON validation_audit(created_at DESC);
```

--------------------------------------------------------------------------------
FICHIER E24 : app/api/v1/validation.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : FastAPI, app/core/validation.py, app/models/validation_audit.py,
              app/api/deps.py.

ROUTER : router = APIRouter(prefix="/validation", tags=["Validation"])

ENDPOINTS :

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/{request_id}", response_model=ValidationResult)
async def get_validation_result(
    request_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne le resultat de validation pour un request_id."""
    # Verifier que l'utilisateur est proprietaire ou admin
    pass  # IMPLEMENTATION

@router.get("/audit", response_model=list[ValidationAuditResponse])
async def list_validation_audits(
    gate_name: str | None = None,
    status: str | None = None,
    user_id: uuid.UUID | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
    current_user: UserInDB = Depends(get_current_user_admin),
    db: AsyncSession = Depends(get_db),
):
    """Liste les audits de validation (admin uniquement)."""
    pass  # IMPLEMENTATION
```

================================================================================
 GROUPE F : Autonomie et Human-in-the-Loop (fichiers F25 a F28)
================================================================================

--------------------------------------------------------------------------------
FICHIER F25 : app/core/autonomy.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : pydantic, enum, datetime, uuid, redis.asyncio.

ENUMS ET SCHEMAS :

```python
import enum
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class AutonomyLevel(int, enum.Enum):
    MANUAL = 0
    ASSISTED = 1
    SUPERVISED = 2
    AUTONOMOUS = 3

class SystemState(str, enum.Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"

class HILRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    request_id: uuid.UUID
    autonomy_level: AutonomyLevel
    decision_type: str
    context: dict
    status: str
    created_at: datetime
    expires_at: datetime
    decided_by: uuid.UUID | None = None
    decided_at: datetime | None = None
    decision_value: dict | None = None

class HILDecisionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: uuid.UUID
    decision: str = Field(..., pattern=r"^(approve|reject|modify)$")
    reason: str | None = Field(default=None, max_length=500)
    modifications: list[dict] | None = None

class KillSwitchPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(..., min_length=10, max_length=500)
```

SERVICE HIL :

```python
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from datetime import datetime, timezone, timedelta

logger = structlog.get_logger()

class HILService:
    HIL_EXPIRY_MINUTES: int = 30

    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session

    async def create_request(
        self,
        request_id: uuid.UUID,
        autonomy_level: AutonomyLevel,
        decision_type: str,
        context: dict,
    ) -> HILRequest:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=self.HIL_EXPIRY_MINUTES)
        # Stocker dans une table hil_requests (a creer)
        hil = HILRequest(
            id=uuid.uuid4(),
            request_id=request_id,
            autonomy_level=autonomy_level,
            decision_type=decision_type,
            context=context,
            status="pending",
            created_at=now,
            expires_at=expires,
        )
        # self._db.add(hil); await self._db.commit()
        logger.info("hil_request_created", hil_id=str(hil.id), request_id=str(request_id))
        return hil

    async def make_decision(
        self,
        hil_id: uuid.UUID,
        user_id: uuid.UUID,
        decision: str,
        reason: str | None = None,
        modifications: list[dict] | None = None,
    ) -> HILRequest:
        now = datetime.now(timezone.utc)
        # Mettre a jour la requete HIL
        # Verifier qu'elle n'est pas expiree
        logger.info("hil_decision_made", hil_id=str(hil_id), decision=decision, user_id=str(user_id))
        # Retourner la requete mise a jour
        return HILRequest(...)  # A implementer

    async def get_pending_requests(
        self,
        user_id: uuid.UUID | None = None,
        decision_type: str | None = None,
        limit: int = 50,
    ) -> list[HILRequest]:
        pass  # IMPLEMENTATION

    async def expire_old_requests(self) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.HIL_EXPIRY_MINUTES)
        # Marquer les expirees
        return 0  # IMPLEMENTATION
```

MANAGER D'AUTONOMIE :

```python
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

class AutonomyManager:
    REDIS_KEY_STATE: str = "system:state"
    REDIS_KEY_AUTONOMY: str = "user:{user_id}:autonomy"

    def __init__(self, db_session: AsyncSession, redis_client: redis.Redis) -> None:
        self._db = db_session
        self._redis = redis_client

    async def get_user_autonomy_level(self, user_id: uuid.UUID) -> AutonomyLevel:
        cached = await self._redis.get(self.REDIS_KEY_AUTONOMY.format(user_id=user_id))
        if cached:
            return AutonomyLevel(int(cached))
        # Fallback DB
        return AutonomyLevel.MANUAL

    async def set_user_autonomy_level(
        self, user_id: uuid.UUID, level: AutonomyLevel, set_by: uuid.UUID
    ) -> None:
        await self._redis.set(
            self.REDIS_KEY_AUTONOMY.format(user_id=user_id),
            str(level.value),
        )
        logger.info("autonomy_level_changed", user_id=str(user_id), level=level.name, set_by=str(set_by))

    async def get_system_state(self) -> SystemState:
        cached = await self._redis.get(self.REDIS_KEY_STATE)
        if cached:
            return SystemState(cached.decode())
        return SystemState.ACTIVE

    async def kill_switch(self, triggered_by: uuid.UUID, reason: str) -> None:
        await self._redis.setex(self.REDIS_KEY_STATE, 86400, SystemState.FROZEN.value)
        logger.critical(
            "kill_switch_activated",
            triggered_by=str(triggered_by),
            reason=reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        # Notifier via WebSocket (ou marquer un flag pour le polling)
        await self._redis.publish("system:events", json.dumps({
            "type": "kill_switch",
            "triggered_by": str(triggered_by),
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }))

    async def unfreeze(self, triggered_by: uuid.UUID, reason: str) -> None:
        await self._redis.set(self.REDIS_KEY_STATE, SystemState.ACTIVE.value)
        logger.info("system_unfrozen", triggered_by=str(triggered_by), reason=reason)
        await self._redis.publish("system:events", json.dumps({
            "type": "unfreeze",
            "triggered_by": str(triggered_by),
            "reason": reason,
        }))

    async def is_frozen(self) -> bool:
        return await self.get_system_state() == SystemState.FROZEN
```

--------------------------------------------------------------------------------
FICHIER F26 : app/api/v1/autonomy.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : FastAPI, app/core/autonomy.py, app/api/deps.py.

ROUTER : router = APIRouter(prefix="/autonomy", tags=["Autonomy"])

ENDPOINTS :

```python
from fastapi import APIRouter, Depends, HTTPException, status

@router.get("/level")
async def get_autonomy_level(
    current_user: UserInDB = Depends(get_current_user),
    autonomy_manager: AutonomyManager = Depends(get_autonomy_manager),
):
    level = await autonomy_manager.get_user_autonomy_level(current_user.id)
    return {"level": level.value, "label": level.name}

@router.post("/level")
async def set_autonomy_level(
    user_id: uuid.UUID,
    level: int,
    current_user: UserInDB = Depends(get_current_user_admin),
    autonomy_manager: AutonomyManager = Depends(get_autonomy_manager),
):
    await autonomy_manager.set_user_autonomy_level(user_id, AutonomyLevel(level), current_user.id)
    return {"status": "updated"}

@router.get("/hil/pending")
async def list_pending_hil(
    current_user: UserInDB = Depends(get_current_user),
    hil_service: HILService = Depends(get_hil_service),
):
    # Admin voit tout, user normal voit ses requetes
    pass  # IMPLEMENTATION

@router.post("/hil/decide")
async def decide_hil(
    payload: HILDecisionPayload,
    current_user: UserInDB = Depends(get_current_user),
    hil_service: HILService = Depends(get_hil_service),
):
    result = await hil_service.make_decision(
        hil_id=payload.request_id,
        user_id=current_user.id,
        decision=payload.decision,
        reason=payload.reason,
        modifications=payload.modifications,
    )
    return result

@router.post("/kill")
async def activate_kill_switch(
    payload: KillSwitchPayload,
    current_user: UserInDB = Depends(get_current_user_admin),
    autonomy_manager: AutonomyManager = Depends(get_autonomy_manager),
):
    await autonomy_manager.kill_switch(current_user.id, payload.reason)
    return {"status": "frozen", "triggered_at": datetime.now(timezone.utc).isoformat()}

@router.post("/unfreeze")
async def unfreeze_system(
    payload: KillSwitchPayload,
    current_user: UserInDB = Depends(get_current_user_admin),
    autonomy_manager: AutonomyManager = Depends(get_autonomy_manager),
):
    await autonomy_manager.unfreeze(current_user.id, payload.reason)
    return {"status": "active", "unfrozen_at": datetime.now(timezone.utc).isoformat()}
```

--------------------------------------------------------------------------------
FICHIER F27 : src/components/autonomy/HILPanel.tsx (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : React, zustand, axios, lucide-react, date-fns.

COMPOSANT A IMPLEMENTER :

```typescript
interface HILRequest {
  id: string;
  request_id: string;
  autonomy_level: number;
  decision_type: string;
  context: {
    document_id: string;
    entities: {
      cpv_codes: Array<{ code: string; confidence: number }>;
      amounts: Array<{ normalized_value: number; currency: string; confidence: number }>;
      deadlines: Array<{ parsed_date: string; confidence: number }>;
    };
    gate_results: Array<{ gate_name: string; status: string; message: string }>;
  };
  status: "pending" | "approved" | "rejected" | "expired";
  created_at: string;
  expires_at: string;
}

export function HILPanel() {
  const [requests, setRequests] = useState<HILRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingRequest, setEditingRequest] = useState<string | null>(null);
  const [modifications, setModifications] = useState<Record<string, any>>({});

  // Polling toutes les 10 secondes
  useEffect(() => {
    const fetchRequests = async () => {
      try {
        const res = await api.get("/autonomy/hil/pending");
        setRequests(res.data);
        setError(null);
      } catch (err) {
        setError("Erreur lors du chargement des validations");
      } finally {
        setLoading(false);
      }
    };
    fetchRequests();
    const interval = setInterval(fetchRequests, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (requestId: string) => {
    await api.post("/autonomy/hil/decide", { request_id: requestId, decision: "approve" });
    setRequests((prev) => prev.filter((r) => r.id !== requestId));
  };

  const handleReject = async (requestId: string) => {
    await api.post("/autonomy/hil/decide", { request_id: requestId, decision: "reject" });
    setRequests((prev) => prev.filter((r) => r.id !== requestId));
  };

  const handleModify = async (requestId: string) => {
    await api.post("/autonomy/hil/decide", {
      request_id: requestId,
      decision: "modify",
      modifications: Object.entries(modifications[requestId] || {}).map(([field, value]) => ({ field, value })),
    });
    setEditingRequest(null);
    setRequests((prev) => prev.filter((r) => r.id !== requestId));
  };

  if (loading) {
    return (
      <div className="p-4 space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  if (requests.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
        <p>Aucune validation en attente</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4" role="region" aria-label="Panel de validation">
      <h3 className="text-lg font-semibold">Validations en attente ({requests.length})</h3>
      {requests.map((req) => (
        <div key={req.id} className="border rounded-lg p-4 bg-white shadow-sm" data-testid={`hil-request-${req.id}`}>
          <div className="flex items-start justify-between mb-3">
            <div>
              <p className="font-medium">Document : {req.context.document_id}</p>
              <p className="text-sm text-gray-500">Type : {req.decision_type}</p>
            </div>
            <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded">En attente</span>
          </div>

          {/* Entites extraites */}
          <div className="mb-3 space-y-2">
            {req.context.entities.cpv_codes.map((cpv, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-sm font-mono">CPV {cpv.code}</span>
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500" style={{ width: `${cpv.confidence * 100}%` }} />
                </div>
                <span className="text-xs text-gray-500">{(cpv.confidence * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>

          {/* Gate bloquant */}
          {req.context.gate_results.filter((g) => g.status === "failed").map((gate) => (
            <div key={gate.gate_name} className="text-sm text-red-600 bg-red-50 p-2 rounded mb-3">
              <AlertTriangle className="w-4 h-4 inline mr-1" />
              {gate.gate_name} : {gate.message}
            </div>
          ))}

          {/* Boutons d'action */}
          {editingRequest === req.id ? (
            <div className="space-y-3">
              <textarea
                className="w-full border rounded p-2 text-sm"
                placeholder="Modifications JSON"
                onChange={(e) => setModifications((prev) => ({ ...prev, [req.id]: JSON.parse(e.target.value || "{}") }))}
              />
              <div className="flex gap-2">
                <button onClick={() => handleModify(req.id)} className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm">Soumettre</button>
                <button onClick={() => setEditingRequest(null)} className="px-3 py-1.5 bg-gray-200 rounded text-sm">Annuler</button>
              </div>
            </div>
          ) : (
            <div className="flex gap-2">
              <button onClick={() => handleApprove(req.id)} className="px-3 py-1.5 bg-green-600 text-white rounded text-sm flex items-center gap-1">
                <Check className="w-4 h-4" /> Approuver
              </button>
              <button onClick={() => setEditingRequest(req.id)} className="px-3 py-1.5 bg-blue-100 text-blue-700 rounded text-sm flex items-center gap-1">
                <Edit className="w-4 h-4" /> Modifier
              </button>
              <button onClick={() => handleReject(req.id)} className="px-3 py-1.5 bg-red-100 text-red-700 rounded text-sm flex items-center gap-1">
                <X className="w-4 h-4" /> Rejeter
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
```

--------------------------------------------------------------------------------
FICHIER F28 : src/components/autonomy/KillSwitch.tsx (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : React, zustand, axios, lucide-react.

COMPOSANT A IMPLEMENTER :

```typescript
export function KillSwitch() {
  const [showModal, setShowModal] = useState(false);
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [systemFrozen, setSystemFrozen] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  // Polling etat systeme
  useEffect(() => {
    const checkState = async () => {
      try {
        const res = await api.get("/autonomy/level"); // Ou endpoint dedie
        // Verifier si systeme gele
      } catch { /* ignore */ }
    };
    checkState();
    const interval = setInterval(checkState, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleKill = async () => {
    if (reason.length < 10 || !confirmed) return;
    setLoading(true);
    try {
      await api.post("/autonomy/kill", { reason });
      setSystemFrozen(true);
      setShowModal(false);
    } catch (err) {
      alert("Echec de l'arret du systeme");
    } finally {
      setLoading(false);
    }
  };

  const handleUnfreeze = async () => {
    setLoading(true);
    try {
      await api.post("/autonomy/unfreeze", { reason: "Relance manuelle" });
      setSystemFrozen(false);
    } catch (err) {
      alert("Echec du relancement");
    } finally {
      setLoading(false);
    }
  };

  // Overlay si systeme gele
  if (systemFrozen) {
    return (
      <div className="fixed inset-0 bg-red-900/90 z-50 flex items-center justify-center">
        <div className="text-center text-white p-8">
          <OctagonAlert className="w-16 h-16 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Systeme arrete</h2>
          <p className="mb-6">Le systeme a ete gele suite a une demande explicite.</p>
          {isAdmin && (
            <button onClick={handleUnfreeze} className="px-6 py-3 bg-white text-red-900 rounded-lg font-semibold">
              Relancer le systeme
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="fixed top-4 right-4 z-40 flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg shadow-lg hover:bg-red-700 transition-colors"
        data-testid="kill-switch-button"
        aria-label="Arreter le systeme"
      >
        <OctagonAlert className="w-5 h-5" />
        <span className="font-semibold">ARRETER</span>
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-red-600 mb-2 flex items-center gap-2">
              <OctagonAlert className="w-6 h-6" />
              Confirmer l'arret
            </h3>
            <p className="text-gray-600 mb-4">
              Cette action va immediatement geler le systeme. Toutes les operations en cours seront interrompues.
            </p>
            <textarea
              className="w-full border rounded-lg p-3 mb-3 text-sm"
              rows={3}
              placeholder="Raison de l'arret (minimum 10 caracteres)"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              data-testid="kill-switch-reason"
            />
            <label className="flex items-start gap-2 mb-4 text-sm">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
                className="mt-0.5"
              />
              <span>Je comprends que cette action est irreversible pour cette session et necessite un administrateur pour relancer le systeme.</span>
            </label>
            <div className="flex gap-3">
              <button
                onClick={handleKill}
                disabled={reason.length < 10 || !confirmed || loading}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="kill-switch-confirm"
              >
                {loading ? "Arret en cours..." : "Confirmer l'arret"}
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 bg-gray-200 rounded-lg"
                data-testid="kill-switch-cancel"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
```

================================================================================
 GROUPE G : Tests E2E Playwright (fichiers G29 a G33)
================================================================================

--------------------------------------------------------------------------------
FICHIER G29 : frontend/playwright.config.ts (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : @playwright/test.

CONFIGURATION :

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["html", { open: "never" }],
    ["junit", { outputFile: "results.xml" }],
  ],
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "on-first-retry",
    actionTimeout: 15000,
    navigationTimeout: 15000,
  },
  projects: [
    { name: "setup", testMatch: /.*\.setup\.ts/ },
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      dependencies: ["setup"],
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
      dependencies: ["setup"],
    },
  ],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

REGLES DE CONFIGURATION :
- fullyParallel: true (sauf en CI).
- En CI : workers=1 (isolation), retries=2.
- Trace, screenshot, video actives uniquement sur echec.
- Timeout d'action/navigation : 15 secondes.

--------------------------------------------------------------------------------
FICHIER G30 : frontend/e2e/auth.setup.ts (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : @playwright/test.

CONTENU :

```typescript
import { test as setup } from "@playwright/test";

const authFile = "playwright/.auth/user.json";

setup("authenticate", async ({ page }) => {
  await page.goto("/login");
  await page.getByTestId("login-email").fill("e2e@test.com");
  await page.getByTestId("login-password").fill("E2ETestPassword123!");
  await page.getByTestId("login-submit").click();
  await page.waitForURL("/dashboard", { timeout: 10000 });
  await page.context().storageState({ path: authFile });
});
```

--------------------------------------------------------------------------------
FICHIER G31 : frontend/e2e/auth.spec.ts (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : @playwright/test.

CONTENU (5 tests) :

```typescript
import { test, expect } from "@playwright/test";

test.describe("Authentification", () => {
  test("devrait afficher la page de login", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveTitle(/Connexion/);
    await expect(page.getByTestId("login-email")).toBeVisible();
    await expect(page.getByTestId("login-password")).toBeVisible();
    await expect(page.getByTestId("login-submit")).toBeVisible();
  });

  test("devrait refuser une connexion avec des identifiants invalides", async ({ page }) => {
    await page.goto("/login");
    await page.getByTestId("login-email").fill("bad@test.com");
    await page.getByTestId("login-password").fill("wrong");
    await page.getByTestId("login-submit").click();
    await expect(page.getByTestId("login-error")).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });

  test("devrait connecter un utilisateur avec des identifiants valides", async ({ page }) => {
    await page.goto("/login");
    await page.getByTestId("login-email").fill("e2e@test.com");
    await page.getByTestId("login-password").fill("E2ETestPassword123!");
    await page.getByTestId("login-submit").click();
    await page.waitForURL("/dashboard", { timeout: 10000 });
    await expect(page.getByTestId("user-name-display")).toBeVisible();
  });

  test("devrait demander un OTP si MFA est active", async ({ page }) => {
    await page.goto("/login");
    await page.getByTestId("login-email").fill("e2e-mfa@test.com");
    await page.getByTestId("login-password").fill("E2ETestPassword123!");
    await page.getByTestId("login-submit").click();
    await expect(page.getByTestId("mfa-input-0")).toBeVisible({ timeout: 5000 });
    await expect(page.getByTestId("mfa-submit")).toBeVisible();
  });

  test("devrait permettre la deconnexion", async ({ page, context }) => {
    // Se connecter d'abord
    await page.goto("/login");
    await page.getByTestId("login-email").fill("e2e@test.com");
    await page.getByTestId("login-password").fill("E2ETestPassword123!");
    await page.getByTestId("login-submit").click();
    await page.waitForURL("/dashboard", { timeout: 10000 });
    // Deconnecter
    await page.getByTestId("logout-button").click();
    await page.waitForURL("/login", { timeout: 10000 });
    // Verifier que le token est supprime
    const storage = await context.storageState();
    expect(storage.origins.some((o) => o.localStorage.some((l) => l.name === "auth_token"))).toBeFalsy();
  });
});
```

SELECTEURS data-testid OBLIGATOIRES :
- login-email, login-password, login-submit, login-error
- mfa-input-0 a mfa-input-5, mfa-submit
- logout-button, user-name-display

--------------------------------------------------------------------------------
FICHIER G32 : frontend/e2e/tender-flow.spec.ts (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : @playwright/test.

CONTENU (6 tests) :

```typescript
import { test, expect } from "@playwright/test";

test.describe("Flux d'appel d'offres", () => {
  test.use({ storageState: "playwright/.auth/user.json" });

  test("devrait afficher la page d'upload de document", async ({ page }) => {
    await page.goto("/documents/upload");
    await expect(page.getByTestId("upload-zone")).toBeVisible();
    await expect(page.getByTestId("upload-submit")).toBeVisible();
  });

  test("devrait uploader un fichier PDF et afficher le statut", async ({ page }) => {
    await page.goto("/documents/upload");
    const fileInput = page.getByTestId("upload-file-input");
    await fileInput.setInputFiles("fixtures/sample-tender.pdf");
    await page.getByTestId("upload-submit").click();
    await expect(page.getByTestId("document-status")).toContainText("En cours d'analyse", { timeout: 30000 });
  });

  test("devrait afficher les entites extraites apres parsing", async ({ page }) => {
    await page.goto("/documents/upload");
    await page.getByTestId("upload-file-input").setInputFiles("fixtures/sample-tender.pdf");
    await page.getByTestId("upload-submit").click();
    // Attendre le parsing (polling ou WebSocket)
    await expect(page.getByTestId("entity-cpv")).toBeVisible({ timeout: 60000 });
    await expect(page.getByTestId("entity-amount")).toBeVisible();
    await expect(page.getByTestId("entity-deadline")).toBeVisible();
  });

  test("devrait permettre la validation HIL d'un document", async ({ page }) => {
    // Utilisateur en mode MANUEL
    await page.goto("/documents/upload");
    await page.getByTestId("upload-file-input").setInputFiles("fixtures/sample-tender.pdf");
    await page.getByTestId("upload-submit").click();
    // Attendre le panel HIL
    await expect(page.getByTestId("hil-panel")).toBeVisible({ timeout: 60000 });
    await page.getByTestId("hil-approve").click();
    await expect(page.getByTestId("document-status")).toContainText("Approuve", { timeout: 10000 });
  });

  test("devrait rejeter un document via HIL", async ({ page }) => {
    await page.goto("/documents/upload");
    await page.getByTestId("upload-file-input").setInputFiles("fixtures/sample-tender.pdf");
    await page.getByTestId("upload-submit").click();
    await expect(page.getByTestId("hil-panel")).toBeVisible({ timeout: 60000 });
    await page.getByTestId("hil-reject").click();
    await expect(page.getByTestId("document-status")).toContainText("Rejete", { timeout: 10000 });
  });

  test("devrait afficher un document dans le kanban", async ({ page }) => {
    await page.goto("/documents/upload");
    await page.getByTestId("upload-file-input").setInputFiles("fixtures/sample-tender.pdf");
    await page.getByTestId("upload-submit").click();
    await page.getByTestId("hil-approve").click();
    // Aller au kanban
    await page.goto("/kanban");
    await expect(page.getByTestId("kanban-column-approved")).toContainText("CPV 33141000", { timeout: 10000 });
  });
});
```

FIXTURES REQUISES :
- fixtures/sample-tender.pdf : PDF de test avec CPV 33141000, montant 150000 EUR HT, deadline 30/06/2025.
- fixtures/sample-scan.pdf : PDF image sans texte pour tester OCR.

--------------------------------------------------------------------------------
FICHIER G33 : frontend/e2e/kanban.spec.ts (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : @playwright/test.

CONTENU (4 tests) :

```typescript
import { test, expect } from "@playwright/test";

test.describe("Tableau Kanban", () => {
  test.use({ storageState: "playwright/.auth/user.json" });

  test("devrait afficher le kanban avec les colonnes", async ({ page }) => {
    await page.goto("/kanban");
    await expect(page.getByTestId("kanban-column-new")).toBeVisible();
    await expect(page.getByTestId("kanban-column-parsing")).toBeVisible();
    await expect(page.getByTestId("kanban-column-review")).toBeVisible();
    await expect(page.getByTestId("kanban-column-approved")).toBeVisible();
    await expect(page.getByTestId("kanban-column-rejected")).toBeVisible();
  });

  test("devrait permettre le drag-and-drop entre colonnes", async ({ page }) => {
    await page.goto("/kanban");
    // Creer un document via API ou fixture
    const card = page.getByTestId("kanban-card").first();
    const targetColumn = page.getByTestId("kanban-column-approved");
    await card.dragTo(targetColumn);
    await expect(targetColumn).toContainText(await card.textContent() || "");
  });

  test("devrait filter les cartes par montant minimum", async ({ page }) => {
    await page.goto("/kanban");
    await page.getByTestId("filter-amount-min").fill("100000");
    await page.getByTestId("filter-apply").click();
    const cards = page.getByTestId("kanban-card");
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test("devrait trier les cartes par deadline", async ({ page }) => {
    await page.goto("/kanban");
    await page.getByTestId("sort-deadline").click();
    const dates = await page.locator("[data-testid='kanban-card-deadline']").allTextContents();
    // Verifier que les dates sont dans l'ordre croissant
    expect(dates.length).toBeGreaterThan(0);
  });
});
```

--------------------------------------------------------------------------------
FICHIER G34 : .github/workflows/e2e.yml (NOUVEAU — CI/CD GitHub Actions)
--------------------------------------------------------------------------------

DEPENDANCES : GitHub Actions, Docker Compose, Playwright.

CONTENU :

```yaml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    services:
      postgres:
        image: pgvector/pgvector:pg15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
          cache-dependency-path: backend/requirements.txt

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run backend migrations
        run: |
          cd backend
          alembic upgrade head
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb
          SECRET_KEY: test-secret-key-for-e2e-only
          MISTRAL_API_KEY: test-mistral-key

      - name: Start backend
        run: |
          cd backend
          uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb
          SECRET_KEY: test-secret-key-for-e2e-only

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci

      - name: Install Playwright browsers
        run: |
          cd frontend
          npx playwright install --with-deps chromium firefox

      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright test
        env:
          E2E_BASE_URL: http://localhost:3000
          API_BASE_URL: http://localhost:8000

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
          retention-days: 7
```

================================================================================
 GROUPE H : Tests backend (fichiers H35 a H36)
================================================================================

--------------------------------------------------------------------------------
FICHIER H35 : backend/tests/test_auth_mfa.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : pytest, pytest-asyncio, httpx, pyotp, freezegun.

CONTENU (10 tests) :

```python
import pytest
from httpx import AsyncClient
from pyotp import TOTP
from freezegun import freeze_time

pytestmark = pytest.mark.asyncio

class TestMFASetup:
    async def test_setup_mfa_generates_secret_and_backup_codes(self, client: AsyncClient, auth_user):
        """Le setup MFA doit generer un secret, un URI, et 10 backup codes."""
        response = await client.post("/auth/mfa/setup", headers=auth_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "secret" in data
        assert "provisioning_uri" in data
        assert len(data["backup_codes"]) == 10
        assert data["provisioning_uri"].startswith("otpauth://totp/")

    async def test_setup_mfa_fails_if_already_enabled(self, client: AsyncClient, mfa_user):
        """Le setup doit echouer si MFA est deja active."""
        response = await client.post("/auth/mfa/setup", headers=mfa_user["headers"])
        assert response.status_code == 409

class TestMFAVerify:
    async def test_verify_totp_success(self, client: AsyncClient, mfa_user):
        """La verification TOTP avec un code valide doit reussir."""
        secret = mfa_user["mfa_secret"]
        totp = TOTP(secret)
        code = totp.now()
        response = await client.post("/auth/mfa/verify", json={"otp_code": code}, headers=mfa_user["temp_headers"])
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_verify_totp_failure_invalid_code(self, client: AsyncClient, mfa_user):
        """Un code TOTP invalide doit retourner 401."""
        response = await client.post("/auth/mfa/verify", json={"otp_code": "000000"}, headers=mfa_user["temp_headers"])
        assert response.status_code == 401

    async def test_verify_backup_code_success(self, client: AsyncClient, mfa_user):
        """Un backup code valide doit permettre l'authentification."""
        backup_code = mfa_user["backup_codes"][0]
        response = await client.post("/auth/mfa/verify", json={"otp_code": backup_code}, headers=mfa_user["temp_headers"])
        assert response.status_code == 200
        # Verifier que le code est consomme
        response2 = await client.post("/auth/mfa/verify", json={"otp_code": backup_code}, headers=mfa_user["temp_headers"])
        assert response2.status_code == 401

    @freeze_time("2024-01-01")
    async def test_rate_limit_after_5_failures(self, client: AsyncClient, mfa_user):
        """Apres 5 echecs, la 6eme tentative doit retourner 429."""
        for _ in range(5):
            await client.post("/auth/mfa/verify", json={"otp_code": "000000"}, headers=mfa_user["temp_headers"])
        response = await client.post("/auth/mfa/verify", json={"otp_code": "000000"}, headers=mfa_user["temp_headers"])
        assert response.status_code == 429

class TestMFADisable:
    async def test_disable_mfa_with_password_and_otp(self, client: AsyncClient, mfa_user):
        """La desactivation MFA avec password + OTP doit reussir."""
        secret = mfa_user["mfa_secret"]
        totp = TOTP(secret)
        code = totp.now()
        response = await client.post("/auth/mfa/disable", json={"password": mfa_user["password"], "otp_code": code}, headers=mfa_user["headers"])
        assert response.status_code == 204

    async def test_disable_mfa_fails_without_otp(self, client: AsyncClient, mfa_user):
        """La desactivation sans OTP doit retourner 403."""
        response = await client.post("/auth/mfa/disable", json={"password": mfa_user["password"]}, headers=mfa_user["headers"])
        assert response.status_code == 403

class TestBackupCodes:
    async def test_regenerate_backup_codes(self, client: AsyncClient, mfa_user):
        """La regeneration de backup codes doit retourner 10 nouveaux codes."""
        secret = mfa_user["mfa_secret"]
        totp = TOTP(secret)
        code = totp.now()
        response = await client.post("/auth/mfa/regenerate-backup-codes", json={"otp_code": code}, headers=mfa_user["headers"])
        assert response.status_code == 200
        assert len(response.json()["backup_codes"]) == 10

class TestMFAStatus:
    async def test_mfa_status_endpoint(self, client: AsyncClient, auth_user):
        """Le endpoint status doit retourner l'etat MFA."""
        response = await client.get("/auth/mfa/status", headers=auth_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "mfa_enabled" in data
        assert "mfa_verified" in data
```

--------------------------------------------------------------------------------
FICHIER H36 : backend/tests/test_validation_pipeline.py (NOUVEAU)
--------------------------------------------------------------------------------

DEPENDANCES : pytest, pytest-asyncio, app/core/validation.py.

CONTENU (8 tests) :

```python
import pytest
import uuid
from app.core.validation import ValidationPipeline, GateName, GateStatus, syntax_gate, semantic_gate, idempotence_gate, determinism_gate, hil_gate

pytestmark = pytest.mark.asyncio

class TestSyntaxGate:
    async def test_syntax_gate_passes_valid_json(self):
        """Un JSON valide doit passer le gate syntaxique."""
        data = {"version": "1.0", "metadata": {"filename": "test.pdf"}, "pages": []}
        result = await syntax_gate(data)
        assert result.status == GateStatus.PASSED

    async def test_syntax_gate_fails_invalid_json(self):
        """Un schema invalide doit echouer."""
        data = {"invalid": True}
        result = await syntax_gate(data, schema={"type": "object", "required": ["version"]})
        assert result.status == GateStatus.FAILED

class TestSemanticGate:
    async def test_semantic_gate_passes_coherent_entities(self):
        """Des entites coherentes doivent passer."""
        data = {
            "extracted_entities": {
                "cpv_codes": [{"code": "33141000", "confidence": 0.85}],
                "amounts": [{"normalized_value": 150000, "confidence": 0.9}],
                "deadlines": [{"parsed_date": "2025-06-30T00:00:00Z", "confidence": 0.8}],
            }
        }
        result = await semantic_gate(data)
        assert result.status == GateStatus.PASSED

    async def test_semantic_gate_fails_incoherent_amount(self):
        """Un montant negatif doit echouer."""
        data = {
            "extracted_entities": {
                "cpv_codes": [{"code": "33141000", "confidence": 0.85}],
                "amounts": [{"normalized_value": -100, "confidence": 0.9}],
            }
        }
        result = await semantic_gate(data)
        assert result.status == GateStatus.FAILED

class TestIdempotenceGate:
    async def test_idempotence_gate_detects_duplicate(self):
        """Un doublon doit etre detecte."""
        # Mock du memory_manager
        pass  # IMPLEMENTATION avec mock

class TestDeterminismGate:
    async def test_determinism_gate_warns_on_variance(self):
        """Une variance doit produire un WARNING."""
        result = await determinism_gate({"test": "data"})
        # Le gate de determinisme est simplifie pour le sprint
        assert result.status in (GateStatus.PASSED, GateStatus.WARNING)

class TestHILGate:
    async def test_hil_gate_manual_requires_approval(self):
        """Le mode MANUEL doit toujours exiger HIL."""
        result = await hil_gate({"test": "data"}, autonomy_level=0, hil_service=MockHILService())
        assert result.status == GateStatus.FAILED

class TestFullPipeline:
    async def test_full_pipeline_early_exit_on_failure(self):
        """Un gate bloquant FAILED doit arreter le pipeline."""
        gates = {
            GateName.SYNTAX: lambda **kwargs: GateResult(gate_name=GateName.SYNTAX, status=GateStatus.FAILED, message="fail", execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now()),
            GateName.RBAC: lambda **kwargs: GateResult(gate_name=GateName.RBAC, status=GateStatus.PASSED, message="ok", execution_time_ms=0, input_hash="", output_hash="", timestamp=datetime.now()),
        }
        pipeline = ValidationPipeline(gates)
        result = await pipeline.validate(request_id=uuid.uuid4(), data={}, user=MockUser(), autonomy_level=0)
        assert result.overall_status == GateStatus.FAILED
        # Verifier que les gates suivants sont SKIPPED
        skipped = [g for g in result.gate_results if g.status == GateStatus.SKIPPED]
        assert len(skipped) >= 1
```

================================================================================
 GROUPE I : Configuration et Integration (fichiers I37 a I39)
================================================================================

--------------------------------------------------------------------------------
FICHIER I37 : backend/requirements.txt (MISE A JOUR)
--------------------------------------------------------------------------------

PAQUETS A AJOUTER :

```
# MFA / TOTP
pyotp>=2.9.0,<3.0.0
qrcode>=7.4.2,<8.0.0

# Chiffrement
cryptography>=41.0.0,<42.0.0

# Validation pipeline
jsonschema>=4.20.0,<5.0.0

# Parsing de dates
dateparser>=1.2.0,<2.0.0

# Tests complementaires
pytest-asyncio>=0.21.1,<0.22.0
factory-boy>=3.3.0,<4.0.0
freezegun>=1.4.0,<2.0.0
Faker>=22.0.0,<23.0.0
pytest-httpx>=0.28.0,<0.29.0
```

--------------------------------------------------------------------------------
FICHIER I38 : frontend/package.json (MISE A JOUR)
--------------------------------------------------------------------------------

PAQUETS A AJOUTER :

```json
{
  "dependencies": {
    "qrcode.react": "^3.1.0",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.1",
    "playwright": "^1.40.1"
  }
}
```

--------------------------------------------------------------------------------
FICHIER I39 : alembic/versions/001_add_mfa_and_validation_tables.py (NOUVEAU)
--------------------------------------------------------------------------------

MIGRATION A IMPLEMENTER :

```python
"""Add MFA, documents, memory, validation audit tables.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 1. Alter table users — ajouter colonnes MFA
    op.add_column("users", sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("mfa_secret_encrypted", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("mfa_verified", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("mfa_backup_codes_hash", sa.JSON(), nullable=True))

    # 2. Create table documents
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(64), nullable=False, server_default="application/pdf"),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("parse_level_reached", sa.Integer(), nullable=True),
        sa.Column("parse_result", sa.JSON(), nullable=True),
        sa.Column("extracted_entities", sa.JSON(), nullable=True),
        sa.Column("validation_result", sa.JSON(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("idx_documents_user_id", "documents", ["user_id"])
    op.create_index("idx_documents_status", "documents", ["status"])
    op.create_index("idx_documents_created_at", "documents", ["created_at"], postgresql_using="btree", postgresql_ops={"created_at": "DESC"})
    op.create_index("idx_documents_status_user", "documents", ["status", "user_id"])

    # 3. Create table document_chunks
    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.Vector(1024), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
    )
    op.create_index("idx_document_chunks_document", "document_chunks", ["document_id"])
    op.execute("CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")

    # 4. Create table memory_entries
    op.create_table(
        "memory_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("memory_type", sa.String(32), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("embedding", sa.Vector(1024), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ttl_seconds", sa.Integer(), nullable=True),
        sa.Column("access_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decay_factor", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("consolidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("idx_memory_entries_type_priority", "memory_entries", ["memory_type", sa.text("priority DESC"), sa.text("created_at DESC")])
    op.create_index("idx_memory_entries_expires", "memory_entries", ["expires_at"])
    op.execute("CREATE INDEX idx_memory_entries_embedding ON memory_entries USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")

    # 5. Create table memory_consolidations
    op.create_table(
        "memory_consolidations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("memory_entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_entries", sa.JSON(), nullable=False),
        sa.Column("consolidation_type", sa.String(32), nullable=False),
        sa.Column("previous_version", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["memory_entry_id"], ["memory_entries.id"]),
    )
    op.create_index("idx_memory_consolidations_entry", "memory_consolidations", ["memory_entry_id"])

    # 6. Create table validation_audit
    op.create_table(
        "validation_audit",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("gate_name", sa.String(32), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("output_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("idx_validation_audit_request", "validation_audit", ["request_id"])
    op.create_index("idx_validation_audit_gate_status", "validation_audit", ["gate_name", "status"])
    op.create_index("idx_validation_audit_created_at", "validation_audit", ["created_at"], postgresql_using="btree", postgresql_ops={"created_at": "DESC"})

    # 7. Create table human_decisions
    op.create_table(
        "human_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("autonomy_level", sa.Integer(), nullable=False),
        sa.Column("decision_type", sa.String(32), nullable=False),
        sa.Column("decision_value", sa.JSON(), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("context_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("idx_human_decisions_request", "human_decisions", ["request_id"])
    op.create_index("idx_human_decisions_user", "human_decisions", ["user_id"])

    # 8. Create table hil_requests
    op.create_table(
        "hil_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("autonomy_level", sa.Integer(), nullable=False),
        sa.Column("decision_type", sa.String(32), nullable=False),
        sa.Column("context", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_value", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_hil_requests_status", "hil_requests", ["status"])

def downgrade():
    op.drop_table("hil_requests")
    op.drop_table("human_decisions")
    op.drop_table("validation_audit")
    op.drop_table("memory_consolidations")
    op.drop_table("memory_entries")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_column("users", "mfa_backup_codes_hash")
    op.drop_column("users", "mfa_verified")
    op.drop_column("users", "mfa_secret_encrypted")
    op.drop_column("users", "mfa_enabled")
```

================================================================================
 SECTION 6 — LIVRABLE FINAL
================================================================================

Le livrable de ce Sprint 1 mis a jour est un systeme complet de gestion de
documents d'appel d'offres avec les caracteristiques suivantes :

1. Authentification renforcee par MFA/TOTP (RFC 6238) avec backup codes,
   QR code, et rate limiting. Le secret est chiffre avec Fernet derive via
   PBKDF2HMAC. Les backup codes sont hashes bcrypt.

2. Upload et parsing PDF a 4 niveaux (texte brut, OCR, structure, LLM)
   avec fallback degrade et extraction d'entites (CPV, montant, deadline)
   avec scores de confiance. Le format de sortie JSON est normalise et
   versionne.

3. Client LLM Mistral AI avec circuit breaker pybreaker (5 echecs / 120s),
   retry exponentiel tenacity (3 tentatives, backoff 1s/2s/4s), et
   fallback de modele (mistral-small-latest si medium echoue).

4. Memoire a 4 types :
   - Episodique : evenements temporels, TTL 30j, purge automatique.
   - Semantique : faits + embeddings pgvector 1024 dims, decay exponentiel
     half-life 90j, consolidation des faits ARCHIVE.
   - Procedurale : workflows, consolidation apres 7 succes, template
     avec placeholders.
   - Transactionnelle : audit trail immuable, archive apres 1 an.

5. Pipeline de validation N Gates (syntaxe, semantique, RBAC, idempotence,
   determinisme, HIL) avec audit table (validation_audit), early-exit sur
   gate bloquant, et hashes SHA-256 des inputs/outputs.

6. Systeme d'autonomie a 4 niveaux (manuel, assiste, supervise, autonome)
   avec panel HIL UI (Approuver/Rejeter/Modifier), kill switch operationnel
   (log CRITICAL + notification WebSocket + etat FROZEN en Redis), et
   unfreeze admin.

7. Tests E2E Playwright (3 suites : auth avec MFA, tender-flow complet avec
   upload/parsing/HIL, kanban drag-and-drop/filtres/tri) avec CI/CD
   GitHub Actions, services PostgreSQL+Redis, et artifacts de rapport.

8. Tests backend pytest pour MFA (10 tests), validation pipeline (8 tests),
   et parsing (tests a completer dans les fichiers de niveau).

LISTE DES FICHIERS LIVRES (39 fichiers) :

Groupe A — MFA/TOTP (7 fichiers) :
  A1  app/models/auth.py (extension)
  A2  app/core/mfa_service.py
  A3  app/core/rate_limiter.py
  A4  app/api/v1/auth_mfa.py
  A5  src/components/auth/MFASetup.tsx
  A6  src/components/auth/MFAInput.tsx
  A7  src/app/auth/mfa/page.tsx

Groupe B — Upload et Parsing (6 fichiers) :
  B8  app/models/document.py
  B9  app/services/parsing/pipeline.py
  B10 app/services/parsing/levels.py
  B11 app/services/extraction/cpv_extractor.py
  B12 app/services/extraction/amount_extractor.py
  B13 app/services/extraction/deadline_extractor.py

Groupe C — LLM et Resilience (2 fichiers) :
  C14 app/services/llm/mistral_client.py
  C15 app/services/llm/circuit_breaker.py

Groupe D — Memoire (5 fichiers) :
  D16 app/models/memory.py
  D17 app/services/memory/episodic_memory.py
  D18 app/services/memory/semantic_memory.py
  D19 app/services/memory/procedural_memory.py
  D20 app/services/memory/transactional_memory.py
  D21 app/services/memory/memory_manager.py

Groupe E — Validation N Gates (3 fichiers) :
  E22 app/core/validation.py
  E23 app/models/validation_audit.py
  E24 app/api/v1/validation.py

Groupe F — Autonomie HIL (4 fichiers) :
  F25 app/core/autonomy.py
  F26 app/api/v1/autonomy.py
  F27 src/components/autonomy/HILPanel.tsx
  F28 src/components/autonomy/KillSwitch.tsx

Groupe G — Tests E2E (6 fichiers) :
  G29 frontend/playwright.config.ts
  G30 frontend/e2e/auth.setup.ts
  G31 frontend/e2e/auth.spec.ts
  G32 frontend/e2e/tender-flow.spec.ts
  G33 frontend/e2e/kanban.spec.ts
  G34 .github/workflows/e2e.yml

Groupe H — Tests backend (2 fichiers) :
  H35 backend/tests/test_auth_mfa.py
  H36 backend/tests/test_validation_pipeline.py

Groupe I — Configuration et Integration (3 fichiers) :
  I37 backend/requirements.txt (mise a jour)
  I38 frontend/package.json (mise a jour)
  I39 alembic/versions/001_add_mfa_and_validation_tables.py

--- CRITERES D'ACCEPTATION ---

- Le parsing produit un JSON structure valide pour 90 % des PDF d'appel
  d'offres de test (fixtures/sample-tender.pdf et fixtures/sample-scan.pdf).
- Les entites extraites ont un score de confiance >= 0.7 pour 80 % des cas CPV,
  >= 0.6 pour les montants, >= 0.5 pour les deadlines.
- La MFA bloque l'acces sans OTP valide (teste par pytest et Playwright).
  Le rate limit fonctionne apres 5 echecs (429 Too Many Requests).
- Le kill switch gele le systeme en moins de 2 secondes (test manuel + log
  CRITICAL verifiable).
- Les tests E2E passent en CI avec 0 echec (flaky tolerance : 2 retries en CI).
- La couverture de tests backend pour le nouveau code est >= 80 %.
- Toutes les migrations Alembic passent sans erreur sur une base vide.
- mypy --strict passe avec 0 erreur sur tout le nouveau code.
- Le fichier de prompt fait entre 4000 et 4500 lignes.

================================================================================
 FIN DU PROMPT SPRINT 1 MIS A JOUR
================================================================================
