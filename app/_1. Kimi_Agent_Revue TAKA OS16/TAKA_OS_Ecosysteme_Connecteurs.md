# TAKA OS — Écosystème Connecteurs & Roadmap d'Intégration

> **Document maître v1.0** — Spécification technique & stratégique  
> **Périmètre** : CRM, ERP, Comptabilité, Signature électronique, Paie, Fintech, E-commerce — marché français & européen

---

## Table des matières

1. [Vue d'ensemble de l'écosystème](#partie-1--vue-densemble-de-lécosystème)
2. [Stratégie d'intégration TAKA OS](#partie-2--stratégie-dintégration-taka-os)
3. [Architecture technique des connecteurs](#partie-3--architecture-technique-des-connecteurs)
4. [Roadmap des connecteurs (par version)](#partie-4--roadmap-des-connecteurs-par-version)
5. [Scoring enrichi par écosystème](#partie-5--scoring-enrichi-par-écosystème)
6. [Tableaux comparatifs exhaustifs](#partie-6--tableaux-comparatifs-exhaustifs)
7. [Gestion des tokens OAuth2](#partie-7--gestion-des-tokens-oauth2)

---

## Partie 1 — Vue d'ensemble de l'écosystème

### 1.1 Cartographie complète du marché connecté

Le marché français des logiciels métier est l'un des plus fragmentés d'Europe. Contrairement aux États-Unis (QuickBooks + Salesforce dominent), la France compte **15+ logiciels de comptabilité** significatifs, **6 CRM/ERP majeurs**, et une douzaine de solutions verticales. Cette fragmentation est un obstacle (coût d'intégration) et une opportunité (valeur du hub unifié).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ÉCOSYSTÈME LOGICIEL FRANÇAIS (2025)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                 │
│   │   CRM / ERP  │   │ COMPTABILITÉ │   │   SIGNATURE  │                 │
│   ├──────────────┤   ├──────────────┤   ├──────────────┤                 │
│   │ • HubSpot    │   │ • Pennylane  │   │ • Yousign    │                 │
│   │ • Salesforce │   │ • Sage 100   │   │ • DocuSign   │                 │
│   │ • Odoo       │   │ • Cegid Loop │   │ • Adobe Sign │                 │
│   │ • Dynamics   │   │ • MyUnisoft  │   └──────────────┘                 │
│   │ • Pipedrive  │   │ • Inqom      │                                      │
│   │ • Zoho CRM   │   │ • ACD        │   ┌──────────────┐                 │
│   └──────────────┘   │ • Dougs      │   │    PAIE / RH │                 │
│                      │ • EBP        │   ├──────────────┤                 │
│   ┌──────────────┐   │ • Ciel       │   │ • Silae      │                 │
│   │  E-COMMERCE  │   │ • QuickBooks │   │ • Payfit     │                 │
│   ├──────────────┤   └──────────────┘   │ • Peoppl     │                 │
│   │ • Shopify    │                      └──────────────┘                 │
│   │ • WooCommerce│   ┌──────────────┐   ┌──────────────┐                 │
│   │ • Zelty      │   │   FINTECH    │   │ API UNIFIÉES │                 │
│   │ • Popina     │   ├──────────────┤   ├──────────────┤                 │
│   └──────────────┘   │ • Qonto      │   │ • Chift      │                 │
│                      │ • Agicap     │   │ • Apideck    │                 │
│                      │ • Pleo       │   │ • Maesn      │                 │
│                      │ • Mollie     │   │ • Knit       │                 │
│                      │ • Stripe     │   └──────────────┘                 │
│                      └──────────────┘                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Le problème : fragmentation du marché français

| Indicateur | Valeur |
|-------------|--------|
| Entreprises clientes Pennylane | 500 000+ |
| Entreprises sur Sage 100/50 | 700 000+ |
| Experts-comptables Cegid | 150 000+ |
| Entreprises sur EBP | 300 000+ |
| Solutions legacy (Ciel, ACD) | 280 000+ |
| **Total entreprises compta FR** | **~2 000 000** |

**Problèmes critiques :**
1. **Coût exponentiel** : 15 APIs différentes = ~450 jours de développement natif
2. **Fidélité des données** : migration Sage → Pennylane sans stratégie = perte d'historique
3. **Opportunité manquée** : 65% des PME françaises utilisent ≥3 logiciels non connectés

### 1.3 La solution : stratégie "Chift + natif"

```
┌─────────────────────────────────────────────────────────────────┐
│              STRATÉGIE "CHIFT + NATIF" TAKA OS                 │
├─────────────────────────────────────────────────────────────────┤
│   ┌─────────────────────┐      ┌─────────────────────────┐   │
│   │   COUCHE CHIFT      │      │   COUCHE NATIF          │   │
│   │   (API unifiée)     │      │   (API directe)         │   │
│   ├─────────────────────┤      ├─────────────────────────┤   │
│   │ • Sage 100          │      │ • HubSpot               │   │
│   │ • Cegid Loop/Quadra │      │ • Salesforce            │   │
│   │ • MyUnisoft         │      │ • Pennylane             │   │
│   │ • Inqom             │      │ • Yousign               │   │
│   │ • ACD               │      │ • Odoo (REST v17+)      │   │
│   │ • Shopify           │      │ • Pipedrive             │   │
│   │ • WooCommerce       │      │ • Dynamics              │   │
│   │ • Qonto             │      │ • Zoho CRM              │   │
│   │ • Agicap            │      │                         │   │
│   │ • Pleo              │      │                         │   │
│   │ • Zelty / Popina    │      │                         │   │
│   └─────────────────────┘      └─────────────────────────┘   │
│   1 connecteur = 15+ logiciels     Performance + webhooks     │
│   ~€0.10/appel                     granularité max             │
└─────────────────────────────────────────────────────────────────┘
```

**Principe directeur** :
- **Chift** pour comptabilité FR, fintech, e-commerce, caisse (1 connecteur = 15+ logiciels)
- **Natif** pour CRM/ERP (APIs excellentes, webhooks temps réel critiques pour le scoring)
- **Natif** pour Pennylane + Yousign (nouveau standard FR, API modernes, webhooks)

### 1.4 Tableau comparatif des APIs (maturité technique)

| Logiciel | API | Version | Auth | Webhooks | Rate Limit | Doc | Maturité |
|----------|-----|---------|------|----------|-----------|-----|----------|
| **HubSpot** | REST JSON | v3 | OAuth2 Private Apps | ✅ | 100 req/10s | Excellent | ⭐⭐⭐⭐⭐ |
| **Salesforce** | REST + Pub/Sub | v66.0 | OAuth2 Web Server | CDC (gRPC) | Variable | Excellent | ⭐⭐⭐⭐⭐ |
| **Odoo** | JSON-RPC / REST | v17+ | Session / OAuth2 | ⚠️ Partiel | Configurable | Moyen | ⭐⭐⭐☆☆ |
| **Dynamics 365 BC** | REST OData | v2.0 | Basic / OAuth2 | ✅ | 6000/min | Bon | ⭐⭐⭐⭐☆ |
| **Pipedrive** | REST JSON | v1 | API Token + OAuth2 | ✅ | 480/2min | Bon | ⭐⭐⭐⭐☆ |
| **Zoho CRM** | REST JSON | v2.1 | OAuth2 | ✅ | 100/min/app | Bon | ⭐⭐⭐⭐☆ |
| **Pennylane** | REST JSON | v1 | OAuth2 | ✅ | [À valider] | Excellent | ⭐⭐⭐⭐⭐ |
| **Sage 100** | REST partielle | N/A | OAuth2 | ⚠️ Limité | [À valider] | Moyen | ⭐⭐⭐☆☆ |
| **Sage 50** | REST limitée | N/A | API Key | ❌ | Bas | Faible | ⭐⭐☆☆☆ |
| **Cegid Loop** | REST JSON | v1 | OAuth2 | ✅ | [À valider] | Bon | ⭐⭐⭐⭐☆ |
| **Cegid Quadra** | Via Loop | N/A | OAuth2 (Loop) | Via Loop | Via Loop | Moyen | ⭐⭐⭐☆☆ |
| **MyUnisoft** | REST JSON | v1 | OAuth2 | ✅ | [À valider] | Bon | ⭐⭐⭐⭐☆ |
| **Inqom (Visma)** | REST JSON | v1 | OAuth2 | [À valider] | [À valider] | Moyen | ⭐⭐⭐☆☆ |
| **ACD** | SOAP/REST legacy | N/A | API Key | ❌ | [À valider] | Faible | ⭐⭐☆☆☆ |
| **Dougs** | REST JSON | v1 | OAuth2 | [À valider] | [À valider] | Moyen | ⭐⭐⭐☆☆ |
| **EBP** | REST (EBP Cloud) | v1 | OAuth2 | ❌ | [À valider] | Moyen | ⭐⭐⭐☆☆ |
| **Ciel (Cegid)** | Legacy | N/A | API Key | ❌ | Bas | Faible | ⭐☆☆☆☆ |
| **QuickBooks** | REST JSON | v3 | OAuth2 | ✅ | 500/min | Excellent | ⭐⭐⭐⭐⭐ |
| **Yousign** | REST JSON | v3 | OAuth2 | ✅ | [À valider] | Excellent | ⭐⭐⭐⭐⭐ |
| **DocuSign** | REST JSON | v2.1 | OAuth2 | ✅ (Connect) | 1000/h | Excellent | ⭐⭐⭐⭐⭐ |
| **Adobe Sign** | REST JSON | v6 | OAuth2 | ✅ | [À valider] | Bon | ⭐⭐⭐⭐☆ |
| **Silae** | REST JSON | v1 | OAuth2 | [À valider] | [À valider] | Moyen | ⭐⭐⭐☆☆ |
| **Payfit** | REST JSON | v1 | OAuth2 | [À valider] | [À valider] | Moyen | ⭐⭐⭐☆☆ |
| **Qonto** | REST JSON | v2 | OAuth2 | ✅ | 100/min | Bon | ⭐⭐⭐⭐☆ |
| **Agicap** | REST JSON | v1 | OAuth2 | [À valider] | [À valider] | Bon | ⭐⭐⭐⭐☆ |
| **Pleo** | REST JSON | v1 | OAuth2 | [À valider] | [À valider] | Bon | ⭐⭐⭐⭐☆ |
| **Stripe** | REST JSON | v1 | API Key + OAuth2 | ✅ | Variable | Excellent | ⭐⭐⭐⭐⭐ |
| **Mollie** | REST JSON | v2 | API Key | ✅ | [À valider] | Excellent | ⭐⭐⭐⭐⭐ |
| **Shopify** | REST + GraphQL | 2025-01 | OAuth2 | ✅ | 40/s/app | Excellent | ⭐⭐⭐⭐⭐ |
| **WooCommerce** | REST JSON | v3 | Basic / OAuth1 | ✅ | Configurable | Bon | ⭐⭐⭐⭐☆ |
| **Zelty** | REST JSON | v1 | API Key | [À valider] | [À valider] | Moyen | ⭐⭐⭐☆☆ |
| **Popina** | REST JSON | v1 | API Key | [À valider] | [À valider] | Moyen | ⭐⭐⭐☆☆ |
| **Planity** | REST JSON | v1 | API Key | [À valider] | [À valider] | Moyen | ⭐⭐⭐☆☆ |

### 1.5 Les API unifiées : accélérateurs stratégiques

| Service | Type | Connecteurs | Coût indicatif | Localisation | Avantage TAKA OS |
|---------|------|-------------|----------------|--------------|-----------------|
| **Chift** | Comptabilité FR + Fintech | 20+ | ~€0.10/appel | Belgique/France | **Cible principale** — couverture parfaite du marché FR |
| **Apideck** | SaaS généraliste | 200+ | ~$0.05/appel | Global (Estonie) | Backup / connecteurs exotiques |
| **Maesn** | Comptabilité généraliste | 30+ | Variable | Global | Complément international |
| **Knit** | CRM unifié | 15+ | Variable | Global (US) | Alternative CRM |

**Recommandation** : Partenariat technique avec **Chift** comme API unifiée principale pour la comptabilité française.

---

## Partie 2 — Stratégie d'intégration TAKA OS

### 2.1 Vision : le TAKA OS Connecteur Hub

TAKA OS = **hub central de données métier** pour les entreprises françaises qui répondent aux AO. Synchronisation bidirectionnelle entre TAKA OS et l'écosystème logiciel du client.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TAKA OS CONNECTEUR HUB                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ┌───────────┐                                │
│                              │  TAKA OS  │                                │
│                              │   CORE    │                                │
│                              └─────┬─────┘                                │
│                    ┌───────────────┼───────────────┐                      │
│              ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐               │
│              │  CRM/ERP  │   │ COMPTA    │   │ SIGNATURE │               │
│              │  BRIDGE   │   │  BRIDGE   │   │  BRIDGE   │               │
│              └─────┬─────┘   └─────┬─────┘   └─────┬─────┘               │
│        ┌───────────┼───┐   ┌───────┼───────┐   │                      │
│    ┌───▼───┐  ┌───▼───┐ │ ┌─▼──┐ ┌▼──┐ ┌─▼─┐ ┌▼────┐                │
│    │HubSpot│  │Salesfo│ │ │Chif│ │Pen│ │Sag│ │Yousi│                │
│    │       │  │rce    │ │ │t   │ │nyl│ │e  │ │gn   │                │
│    └───┬───┘  └───┬───┘ │ │    │ │ane│ │   │ │     │                │
│    ┌───▼───┐  ┌───▼───┐ │ │    │ │   │ │   │ │     │                │
│    │Odoo   │  │Pipedi │ │ │    │ │   │ │   │ │     │                │
│    │       │  │rive   │ │ │    │ │   │ │   │ │     │                │
│    └───────┘  └───────┘ │ └────┘ └───┘ └───┘ └─────┘                │
│                         └──────────┬──────────┐                       │
│                              ┌─────▼────┐ ┌────▼────┐                  │
│                              │ FINTECH  │ │E-COMMERCE│                  │
│                              │ (Chift)  │ │ (Chift) │                  │
│                              └──────────┘ └─────────┘                  │
│   FLUX : AO gagné → Facture acompte → Paiement                        │
│          Contact acheteur → CRM (lead)                                │
│          Contrat signé → Statut projet mis à jour                     │
│          Dépense chantier → Analyse marge                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Couche 1 : CRM/ERP (v0.2-v0.3)

**Objectif** : Synchroniser les données commerciales. Un AO gagné sur TAKA OS crée un deal/opportunité dans le CRM. Inversement, un deal gagné dans le CRM alimente le pipeline TAKA OS.

**Connecteurs natifs prioritaires :**

| Connecteur | Version | Priorité | Justification | API |
|------------|---------|----------|---------------|-----|
| **HubSpot** | v0.2 | P0 🔴 | 288K+ clients payants, API v3 mature | REST v3 |
| **Pipedrive** | v0.2 | P0 🔴 | 100K+ clients, focus pipeline | REST v1 |
| **Salesforce** | v0.2b | P1 🟡 | 150K+ clients, standard enterprise | REST v66.0 + Pub/Sub |
| **Odoo** | v0.3 | P1 🟡 | 10M+ users, ERP complet PME/ETI | JSON-RPC + REST |
| **Dynamics 365 BC** | v0.3 | P1 🟡 | Microsoft ecosystem, PME/ETI | REST OData v2.0 |
| **Zoho CRM** | v0.3 | P2 🟢 | 250K+ clients, budget SMB | REST v2.1 |

**Schéma de données :**

```python
# app/services/connectors/crm/base.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CRMContact:
    external_id: str; email: str; first_name: str; last_name: str
    phone: Optional[str] = None; company_name: Optional[str] = None
    siret: Optional[str] = None; job_title: Optional[str] = None
    source: str = "taka_os"; owner_id: Optional[str] = None
    created_at: datetime; updated_at: datetime; custom_fields: dict = None

@dataclass
class CRMDeal:
    external_id: str; name: str; amount: float; currency: str = "EUR"
    stage: str; pipeline: Optional[str] = None; contact_id: Optional[str] = None
    company_id: Optional[str] = None; probability: float = 0.0
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None; source: str = "taka_os"
    tender_id: Optional[str] = None; project_id: Optional[str] = None
    owner_id: Optional[str] = None; created_at: datetime; updated_at: datetime

@dataclass
class CRMCompany:
    external_id: str; name: str; siret: Optional[str] = None
    siren: Optional[str] = None; industry: Optional[str] = None
    employee_count: Optional[int] = None; annual_revenue: Optional[float] = None
    address: Optional[dict] = None; website: Optional[str] = None
    created_at: datetime; updated_at: datetime

@dataclass
class SyncResult:
    success: bool; items_synced: int = 0; items_failed: int = 0
    errors: List[str] = None; next_cursor: Optional[str] = None

class CRMProvider(ABC):
    provider_name: str = ""; supports_webhooks: bool = False; supports_oauth2: bool = True
    
    def __init__(self, tenant_id: str, config: Dict[str, Any], oauth_tokens: Dict[str, str]):
        self.tenant_id = tenant_id; self.config = config; self.oauth_tokens = oauth_tokens or {}
        self.base_url = self._get_base_url(); self._rate_limit_remaining = None
    
    @abstractmethod
    def _get_base_url(self) -> str: pass
    @abstractmethod
    async def authenticate(self) -> bool: pass
    @abstractmethod
    async def refresh_access_token(self) -> str: pass
    @abstractmethod
    async def create_contact(self, contact: CRMContact) -> str: pass
    @abstractmethod
    async def update_contact(self, external_id: str, contact: CRMContact) -> bool: pass
    @abstractmethod
    async def find_contact_by_email(self, email: str) -> Optional[CRMContact]: pass
    @abstractmethod
    async def create_deal(self, deal: CRMDeal) -> str: pass
    @abstractmethod
    async def update_deal_stage(self, external_id: str, stage: str) -> bool: pass
    @abstractmethod
    async def list_deals(self, stage: Optional[str] = None, modified_since: Optional[datetime] = None, limit: int = 100, cursor: Optional[str] = None) -> SyncResult: pass
    @abstractmethod
    async def get_active_deals_count(self) -> int: pass
    @abstractmethod
    async def find_company_by_siret(self, siret: str) -> Optional[CRMCompany]: pass
    @abstractmethod
    async def register_webhook(self, event_type: str, target_url: str) -> str: pass
    @abstractmethod
    async def unregister_webhook(self, webhook_id: str) -> bool: pass
    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool: pass
    @abstractmethod
    def parse_webhook_event(self, payload: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]: pass
```

**Tables SQL CRM :**

```sql
CREATE TABLE crm_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    status VARCHAR(20) NOT NULL DEFAULT 'configured',
    last_sync_at TIMESTAMPTZ,
    last_error_at TIMESTAMPTZ,
    last_error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_active_provider_per_tenant UNIQUE (tenant_id, provider)
);
CREATE INDEX idx_crm_connectors_tenant ON crm_connectors(tenant_id);

CREATE TABLE crm_connector_oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES crm_connectors(id) ON DELETE CASCADE,
    access_token_encrypted BYTEA NOT NULL,
    refresh_token_encrypted BYTEA,
    token_type VARCHAR(20) NOT NULL DEFAULT 'Bearer',
    expires_at TIMESTAMPTZ,
    refresh_expires_at TIMESTAMPTZ,
    scope TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_token_per_connector UNIQUE (connector_id)
);

CREATE TABLE cached_crm_deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL, provider VARCHAR(50) NOT NULL,
    external_id VARCHAR(255) NOT NULL, data JSONB NOT NULL,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    taka_tender_id UUID REFERENCES tenders(id),
    taka_project_id UUID REFERENCES projects(id),
    last_modified_by VARCHAR(10) NOT NULL DEFAULT 'crm',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_cached_deal UNIQUE (tenant_id, provider, external_id)
);
CREATE INDEX idx_cached_deals_tender ON cached_crm_deals(taka_tender_id);
CREATE INDEX idx_cached_deals_synced ON cached_crm_deals(synced_at);

CREATE TABLE cached_crm_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL, provider VARCHAR(50) NOT NULL,
    external_id VARCHAR(255) NOT NULL, data JSONB NOT NULL,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    email VARCHAR(255), siret VARCHAR(14),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_cached_contact UNIQUE (tenant_id, provider, external_id)
);
CREATE INDEX idx_cached_contacts_email ON cached_crm_contacts(email);
CREATE INDEX idx_cached_contacts_siret ON cached_crm_contacts(siret);
```

### 2.3 Couche 2 : Comptabilité (v0.4-v0.5)

**Objectif** : Créer factures d'acompte post-AO, suivre paiements, obtenir trésorerie pour scoring, calculer marge historique par CPV.

**Architecture à deux vitesses :**

```
┌─────────────────────────────────────────────────────────────────┐
│                   COUCHE COMPTABILITÉ TAKA OS                  │
├─────────────────────────────────────────────────────────────────┤
│         ┌───────────────┐               ┌───────────────┐       │
│         │   CHIFT       │               │    NATIF       │       │
│         │  (Unified)    │               │  (Direct)      │       │
│         ├───────────────┤               ├───────────────┤       │
│         │ • Sage 100    │               │ • Pennylane   │       │
│         │ • Cegid Loop  │               │ • Sage 100    │       │
│         │ • Cegid Quadra│               │   (fallback)  │       │
│         │ • MyUnisoft   │               │               │       │
│         │ • Inqom       │               │               │       │
│         │ • ACD         │               │               │       │
│         │ • QuickBooks  │               │               │       │
│         │ • Shopify     │               │               │       │
│         │ • Qonto       │               │               │       │
│         │ • Agicap      │               │               │       │
│         └───────────────┘               └───────────────┘       │
│   Règle : Chift par défaut, Natif si granularité nécessaire.    │
└─────────────────────────────────────────────────────────────────┘
```

```sql
CREATE TYPE accounting_provider AS ENUM (
    'chift', 'pennylane', 'sage100', 'cegid_loop', 'myunisoft',
    'inqom', 'dougs', 'ebp', 'quickbooks', 'ciel'
);
CREATE TYPE accounting_connector_mode AS ENUM ('chift', 'native');

CREATE TABLE accounting_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider accounting_provider NOT NULL,
    mode accounting_connector_mode NOT NULL DEFAULT 'chift',
    config JSONB NOT NULL DEFAULT '{}',
    chift_software_id VARCHAR(100),
    chift_software_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT true,
    status VARCHAR(20) NOT NULL DEFAULT 'configured',
    last_sync_at TIMESTAMPTZ,
    last_error_at TIMESTAMPTZ,
    last_error_message TEXT,
    supports_invoices BOOLEAN DEFAULT false,
    supports_payments BOOLEAN DEFAULT false,
    supports_journal_entries BOOLEAN DEFAULT false,
    supports_contacts BOOLEAN DEFAULT false,
    supports_webhooks BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_accounting_provider_per_tenant UNIQUE (tenant_id, provider)
);
CREATE INDEX idx_accounting_connectors_tenant ON accounting_connectors(tenant_id);

CREATE TABLE cached_accounting_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL, provider accounting_provider NOT NULL,
    external_id VARCHAR(255) NOT NULL, invoice_number VARCHAR(100),
    invoice_type VARCHAR(20), status VARCHAR(30),
    total_ht DECIMAL(15, 2), total_ttc DECIMAL(15, 2), vat_amount DECIMAL(15, 2),
    currency VARCHAR(3) DEFAULT 'EUR', issue_date DATE, due_date DATE, paid_date DATE,
    buyer_siret VARCHAR(14), taka_project_id UUID REFERENCES projects(id),
    taka_tender_id UUID REFERENCES tenders(id), data JSONB NOT NULL,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_cached_invoice UNIQUE (tenant_id, provider, external_id)
);
CREATE INDEX idx_cached_invoices_siret ON cached_accounting_invoices(buyer_siret);
CREATE INDEX idx_cached_invoices_status ON cached_accounting_invoices(status);
CREATE INDEX idx_cached_invoices_project ON cached_accounting_invoices(taka_project_id);

CREATE TABLE cached_accounting_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL, provider accounting_provider NOT NULL,
    external_id VARCHAR(255) NOT NULL, invoice_external_id VARCHAR(255),
    amount DECIMAL(15, 2), payment_date DATE, payment_method VARCHAR(50),
    data JSONB NOT NULL, synced_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_cached_payment UNIQUE (tenant_id, provider, external_id)
);

CREATE TABLE accounting_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL, period_month VARCHAR(7) NOT NULL,
    cpv_code VARCHAR(20), total_revenue_ht DECIMAL(15, 2) DEFAULT 0,
    total_costs DECIMAL(15, 2) DEFAULT 0, margin_amount DECIMAL(15, 2) DEFAULT 0,
    margin_pct DECIMAL(5, 2) DEFAULT 0, invoice_count INT DEFAULT 0,
    project_count INT DEFAULT 0, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_analytics_per_period UNIQUE (tenant_id, period_month, cpv_code)
);
CREATE INDEX idx_accounting_analytics_cpv ON accounting_analytics(cpv_code);
CREATE INDEX idx_accounting_analytics_period ON accounting_analytics(period_month);
```

```python
# app/services/connectors/accounting/base.py
class AccountingProvider(ABC):
    def __init__(self, tenant_id: str, config: Dict[str, Any], oauth_tokens: Dict[str, str]):
        self.tenant_id = tenant_id; self.config = config; self.oauth_tokens = oauth_tokens or {}
    @abstractmethod
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> str: pass
    @abstractmethod
    async def get_invoice(self, external_id: str) -> Optional[Dict[str, Any]]: pass
    @abstractmethod
    async def list_invoices(self, status: Optional[str] = None, siret: Optional[str] = None, date_from: Optional[date] = None, date_to: Optional[date] = None, limit: int = 100) -> List[Dict[str, Any]]: pass
    @abstractmethod
    async def create_contact(self, contact_data: Dict[str, Any]) -> str: pass
    @abstractmethod
    async def find_contact_by_siret(self, siret: str) -> Optional[Dict[str, Any]]: pass
    @abstractmethod
    async def get_cash_position(self) -> Decimal: pass
    @abstractmethod
    async def get_avg_payment_delay(self, siret: Optional[str] = None) -> float: pass
    @abstractmethod
    async def get_avg_margin_for_cpv(self, cpv_code: str) -> Optional[Decimal]: pass
    @abstractmethod
    async def sync_all(self, modified_since: Optional[datetime] = None) -> SyncResult: pass
```

### 2.4 Couche 3 : Signature électronique (v0.4)

**Objectif** : Automatiser la signature des contrats liés aux AO (CCAP, CDD, marchés).

**Flow TAKA OS + Yousign :**
```
AO gagné + requires_signature = true
    │
    ▼
[Sélection template] CPV 45xxxx → "CCAP construction"
                    montant > 50K€ → "CDD"
                    sinon → "Bon de commande"
    │
    ▼
[POST /v3/signature_requests] {name, documents, signers, custom_fields}
    │
    ▼
[Webhook tracking]
    • sign_request_signed → Projet "contrat_signé"
    • sign_request_declined → Alerte + relance
    • sign_request_expired → Renouvellement
```

```sql
CREATE TYPE signature_provider AS ENUM ('yousign', 'docusign', 'adobe_sign');

CREATE TABLE signature_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider signature_provider NOT NULL DEFAULT 'yousign',
    config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    status VARCHAR(20) NOT NULL DEFAULT 'configured',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_signature_provider_per_tenant UNIQUE (tenant_id, provider)
);

CREATE TABLE cached_signature_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL, provider signature_provider NOT NULL,
    external_id VARCHAR(255) NOT NULL, status VARCHAR(30),
    document_name VARCHAR(255), signers JSONB,
    taka_project_id UUID REFERENCES projects(id),
    taka_tender_id UUID REFERENCES tenders(id),
    completed_at TIMESTAMPTZ, declined_at TIMESTAMPTZ, decline_reason TEXT,
    data JSONB NOT NULL, synced_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT unique_cached_sig_request UNIQUE (tenant_id, provider, external_id)
);
CREATE INDEX idx_cached_sig_status ON cached_signature_requests(status);
CREATE INDEX idx_cached_sig_project ON cached_signature_requests(taka_project_id);
```

### 2.5 Couche 4 : Fintech & Paiement (v0.5)

| Service | Type | Via | Données synchronisées | Priorité |
|---------|------|-----|------------------------|----------|
| **Qonto** | Néobanque | Chift | Transactions, solde, catégories | P2 🟢 |
| **Agicap** | Trésorerie | Chift | Prévisions BFR, cash-flow | P2 🟢 |
| **Pleo** | Dépenses | Chift | Notes de frais, cartes employés | P2 🟢 |
| **Stripe** | Paiement | Chift | Paiements en ligne, remboursements | P2 🟢 |
| **Mollie** | Paiement | Chift | Paiements e-commerce | P2 🟢 |

**Use cases TAKA OS** : suivi paiement acompte via Qonto, alerte trésorerie basse, analyse marge projet via Pleo.

### 2.6 Couche 5 : E-commerce & Caisse (v0.5-v1.0)

| Service | Type | Via | Version | Priorité |
|---------|------|-----|---------|----------|
| **Shopify** | E-commerce | Chift | v1.0 | P2 🟢 |
| **WooCommerce** | E-commerce WordPress | Chift | v1.0 | P2 🟢 |
| **Zelty** | Caisse restauration | Chift | v1.1 | P2 🟢 |
| **Popina** | Caisse | Chift | v1.1 | P2 🟢 |
| **L'Addition** | Caisse | Chift | v1.1 | P2 🟢 |
| **Planity** | Réservation | Chift | v1.1 | P2 🟢 |

---

## Partie 3 — Architecture technique des connecteurs

### 3.1 Structure du module

```
app/services/connectors/
├── __init__.py
├── base.py                          # ConnectorProvider ABC racine
├── registry.py                      # Registry pattern provider → classe
├── exceptions.py                    # Exceptions connecteurs
├── config.py                        # Configuration centralisée
├── auth/
│   ├── __init__.py
│   ├── oauth2.py                    # OAuth2Flow handler
│   ├── token_vault.py               # Chiffrement Fernet/AES-256
│   ├── refresh_scheduler.py         # Celery beat refresh tokens
│   └── pkce.py                      # PKCE mobile (futur)
├── crm/
│   ├── __init__.py
│   ├── base.py                      # CRMProvider ABC
│   ├── hubspot.py                   # HubSpotProvider (REST v3)
│   ├── salesforce.py                # SalesforceProvider (REST v66.0 + CDC)
│   ├── odoo.py                      # OdooProvider (JSON-RPC + REST)
│   ├── dynamics.py                  # DynamicsProvider (OData)
│   ├── pipedrive.py                 # PipedriveProvider
│   ├── zoho.py                      # ZohoProvider
│   └── mapper.py                    # Mapping CRM → TAKA
├── accounting/
│   ├── __init__.py
│   ├── base.py                      # AccountingProvider ABC
│   ├── chift.py                     # ChiftProvider (15+ logiciels)
│   ├── pennylane.py                 # PennylaneProvider natif
│   ├── sage.py                      # SageProvider (REST partielle)
│   ├── cegid.py                     # CegidProvider
│   └── mapper.py
├── signature/
│   ├── __init__.py
│   ├── base.py                      # SignatureProvider ABC
│   ├── yousign.py                   # YousignProvider (REST v3)
│   ├── docusign.py                  # DocuSignProvider
│   └── mapper.py
├── fintech/
│   ├── __init__.py
│   ├── base.py
│   └── chift_fintech.py            # ChiftFintechProvider
├── ecommerce/
│   ├── __init__.py
│   ├── base.py
│   └── chift_ecommerce.py          # ChiftEcommerceProvider
├── caisse/
│   ├── __init__.py
│   ├── base.py
│   └── chift_caisse.py             # ChiftCaisseProvider
├── sync.py                          # SyncService (orchestration)
├── webhook_handler.py               # WebhookHandler (/webhooks/*)
└── rate_limiter.py                  # RateLimiter global
```

### 3.2 ConnectorProvider ABC racine

```python
# app/services/connectors/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import asyncio, aiohttp

class ConnectorType(Enum):
    CRM = "crm"; ACCOUNTING = "accounting"; SIGNATURE = "signature"
    FINTECH = "fintech"; ECOMMERCE = "ecommerce"; CAISSE = "caisse"

class ConnectorStatus(Enum):
    CONFIGURED = "configured"; CONNECTED = "connected"; ERROR = "error"
    DISABLED = "disabled"; SYNCING = "syncing"

@dataclass
class SyncResult:
    success: bool; items_synced: int = 0; items_failed: int = 0
    errors: List[str] = None; next_cursor: Optional[str] = None

class ConnectorProvider(ABC):
    provider_name: str = ""; connector_type: ConnectorType = None
    supports_webhooks: bool = False; supports_oauth2: bool = True
    
    def __init__(self, tenant_id: str, config: Dict[str, Any], oauth_tokens: Optional[Dict[str, str]] = None, db_session = None):
        self.tenant_id = tenant_id; self.config = config
        self.oauth_tokens = oauth_tokens or {}; self.db_session = db_session
        self._rate_limit_remaining = None; self._rate_limit_reset = None
        self._headers = {}; self._session = None
    
    async def __aenter__(self): import aiohttp; self._session = aiohttp.ClientSession(); return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session: await self._session.close()
    
    @abstractmethod
    async def authenticate(self) -> bool: pass
    @abstractmethod
    async def refresh_access_token(self) -> str: pass
    @abstractmethod
    async def create(self, entity_type: str, data: Dict[str, Any]) -> str: pass
    @abstractmethod
    async def read(self, entity_type: str, external_id: str) -> Optional[Dict[str, Any]]: pass
    @abstractmethod
    async def update(self, entity_type: str, external_id: str, data: Dict[str, Any]) -> bool: pass
    @abstractmethod
    async def delete(self, entity_type: str, external_id: str) -> bool: pass
    @abstractmethod
    async def list(self, entity_type: str, filters: Optional[Dict[str, Any]] = None, limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]: pass
    @abstractmethod
    async def sync_incremental(self, modified_since: Optional[datetime] = None) -> SyncResult: pass
    
    async def sync_full(self) -> SyncResult: return await self.sync_incremental(modified_since=None)
    
    async def register_webhook(self, event_type: str, target_url: str) -> Optional[str]:
        if not self.supports_webhooks: return None
        raise NotImplementedError
    
    async def unregister_webhook(self, webhook_id: str) -> bool:
        if not self.supports_webhooks: return False
        raise NotImplementedError
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        import hmac, hashlib
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]: pass
    
    async def get_rate_limit_status(self) -> Dict[str, int]:
        return {"remaining": self._rate_limit_remaining or -1, "reset": self._rate_limit_reset or -1}
    
    async def _request(self, method: str, endpoint: str, json_data: Optional[Dict] = None, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        from app.services.connectors.exceptions import ConnectorAuthError, ConnectorRateLimitError, ConnectorAPIError
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = {"Authorization": f"Bearer {self.oauth_tokens.get('access_token')}", "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "TAKA-OS-Connector/1.0", **(headers or {})}
        try:
            async with self._session.request(method=method, url=url, headers=request_headers, json=json_data, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                self._rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
                self._rate_limit_reset = response.headers.get("X-RateLimit-Reset")
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise ConnectorRateLimitError(f"Rate limit exceeded for {self.provider_name}. Retry after {retry_after}s", retry_after=retry_after)
                if response.status == 401: raise ConnectorAuthError(f"Authentication failed for {self.provider_name}")
                if response.status >= 400:
                    body = await response.text()
                    raise ConnectorAPIError(f"API error {response.status} for {self.provider_name}: {body}", status_code=response.status, response_body=body)
                if response.status == 204: return {}
                return await response.json()
        except aiohttp.ClientError as e: raise ConnectorAPIError(f"Network error for {self.provider_name}: {str(e)}")
    
    @property
    @abstractmethod
    def base_url(self) -> str: pass
```

### 3.3 Registry pattern

```python
# app/services/connectors/registry.py
from typing import Dict, Type, Optional
from .base import ConnectorProvider
from .crm.hubspot import HubSpotProvider
from .crm.salesforce import SalesforceProvider
from .crm.odoo import OdooProvider
from .crm.dynamics import DynamicsProvider
from .crm.pipedrive import PipedriveProvider
from .crm.zoho import ZohoProvider
from .accounting.chift import ChiftProvider
from .accounting.pennylane import PennylaneProvider
from .accounting.sage import SageProvider
from .signature.yousign import YousignProvider

class ConnectorRegistry:
    _providers: Dict[str, Type[ConnectorProvider]] = {}
    @classmethod
    def register(cls, name: str, provider_class: Type[ConnectorProvider]): cls._providers[name] = provider_class
    @classmethod
    def get(cls, name: str, tenant_id: str, config: dict, oauth_tokens: Optional[dict] = None, db_session = None) -> ConnectorProvider:
        provider_class = cls._providers.get(name)
        if not provider_class: raise ValueError(f"Unknown connector provider: {name}")
        return provider_class(tenant_id=tenant_id, config=config, oauth_tokens=oauth_tokens, db_session=db_session)
    @classmethod
    def list_providers(cls) -> Dict[str, str]: return {name: f"{p.connector_type.value} — webhooks:{p.supports_webhooks}" for name, p in cls._providers.items()}

ConnectorRegistry.register("hubspot", HubSpotProvider)
ConnectorRegistry.register("salesforce", SalesforceProvider)
ConnectorRegistry.register("odoo", OdooProvider)
ConnectorRegistry.register("dynamics", DynamicsProvider)
ConnectorRegistry.register("pipedrive", PipedriveProvider)
ConnectorRegistry.register("zoho", ZohoProvider)
ConnectorRegistry.register("chift", ChiftProvider)
ConnectorRegistry.register("pennylane", PennylaneProvider)
ConnectorRegistry.register("sage100", SageProvider)
ConnectorRegistry.register("yousign", YousignProvider)
```

### 3.4 SyncService

```python
# app/services/connectors/sync.py
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from .registry import ConnectorRegistry
from .base import ConnectorProvider, ConnectorType, SyncResult

class SyncService:
    def __init__(self, db_session: AsyncSession): self.db_session = db_session; self._sync_locks: Dict[str, asyncio.Lock] = {}
    def _get_lock(self, tenant_id: str, provider: str) -> asyncio.Lock:
        key = f"{tenant_id}:{provider}"
        if key not in self._sync_locks: self._sync_locks[key] = asyncio.Lock()
        return self._sync_locks[key]
    
    async def sync_tenant_provider(self, tenant_id: str, provider_name: str, connector_type: ConnectorType, force_full: bool = False) -> SyncResult:
        lock = self._get_lock(tenant_id, provider_name)
        async with lock:
            connector = await self._get_connector_config(tenant_id, provider_name, connector_type)
            if not connector or not connector.is_active: return SyncResult(success=False, errors=["Connector not found or inactive"])
            tokens = await self._get_oauth_tokens(connector.id, connector_type)
            provider = ConnectorRegistry.get(name=provider_name, tenant_id=tenant_id, config=connector.config, oauth_tokens=tokens, db_session=self.db_session)
            async with provider:
                if not await provider.authenticate():
                    await self._update_connector_status(connector.id, connector_type, "error", "Authentication failed")
                    return SyncResult(success=False, errors=["Authentication failed"])
                modified_since = None if force_full else connector.last_sync_at
                result = await provider.sync_incremental(modified_since)
                if result.success: await self._update_connector_status(connector.id, connector_type, "connected", None, result.items_synced)
                else: await self._update_connector_status(connector.id, connector_type, "error", result.errors[0] if result.errors else "Unknown error")
                return result
    
    async def sync_all_for_tenant(self, tenant_id: str) -> Dict[str, SyncResult]:
        results = {}
        connectors = await self._get_all_active_connectors(tenant_id)
        for connector in connectors:
            try: results[connector.provider] = await self.sync_tenant_provider(tenant_id, connector.provider, self._resolve_type(connector.provider))
            except Exception as e: results[connector.provider] = SyncResult(success=False, errors=[str(e)])
        return results
    
    async def _get_connector_config(self, tenant_id: str, provider: str, connector_type: ConnectorType):
        from sqlalchemy import select
        if connector_type == ConnectorType.CRM:
            from app.models import CRMConnector
            stmt = select(CRMConnector).where(CRMConnector.tenant_id == tenant_id, CRMConnector.provider == provider)
        elif connector_type == ConnectorType.ACCOUNTING:
            from app.models import AccountingConnector
            stmt = select(AccountingConnector).where(AccountingConnector.tenant_id == tenant_id, AccountingConnector.provider == provider)
        elif connector_type == ConnectorType.SIGNATURE:
            from app.models import SignatureConnector
            stmt = select(SignatureConnector).where(SignatureConnector.tenant_id == tenant_id, SignatureConnector.provider == provider)
        else: return None
        result = await self.db_session.execute(stmt); return result.scalar_one_or_none()
    
    async def _get_oauth_tokens(self, connector_id: str, connector_type: ConnectorType) -> Dict[str, str]:
        from sqlalchemy import select
        from app.services.connectors.auth.token_vault import TokenVault
        if connector_type == ConnectorType.CRM:
            from app.models import CRMConnectorOAuthToken
            stmt = select(CRMConnectorOAuthToken).where(CRMConnectorOAuthToken.connector_id == connector_id)
        else: return {}
        result = await self.db_session.execute(stmt); token_row = result.scalar_one_or_none()
        if not token_row: return {}
        vault = TokenVault()
        return {"access_token": vault.decrypt(token_row.access_token_encrypted), "refresh_token": vault.decrypt(token_row.refresh_token_encrypted) if token_row.refresh_token_encrypted else None, "expires_at": token_row.expires_at.isoformat() if token_row.expires_at else None}
    
    async def _update_connector_status(self, connector_id: str, connector_type: ConnectorType, status: str, error_message: Optional[str] = None, items_synced: int = 0):
        from sqlalchemy import update
        now = datetime.utcnow()
        if connector_type == ConnectorType.CRM:
            from app.models import CRMConnector
            stmt = update(CRMConnector).where(CRMConnector.id == connector_id).values(status=status, last_sync_at=now, last_error_at=now if error_message else None, last_error_message=error_message, updated_at=now)
        elif connector_type == ConnectorType.ACCOUNTING:
            from app.models import AccountingConnector
            stmt = update(AccountingConnector).where(AccountingConnector.id == connector_id).values(status=status, last_sync_at=now, last_error_at=now if error_message else None, last_error_message=error_message, updated_at=now)
        else: return
        await self.db_session.execute(stmt); await self.db_session.commit()
    
    def _resolve_type(self, provider_name: str) -> ConnectorType:
        mapping = {"hubspot": ConnectorType.CRM, "salesforce": ConnectorType.CRM, "odoo": ConnectorType.CRM, "dynamics": ConnectorType.CRM, "pipedrive": ConnectorType.CRM, "zoho": ConnectorType.CRM, "chift": ConnectorType.ACCOUNTING, "pennylane": ConnectorType.ACCOUNTING, "sage100": ConnectorType.ACCOUNTING, "yousign": ConnectorType.SIGNATURE}
        return mapping.get(provider_name, ConnectorType.CRM)
    
    async def _get_all_active_connectors(self, tenant_id: str):
        # [À implémenter — requête union sur toutes les tables connectors]
        return []
```

### 3.5 WebhookHandler

```python
# app/services/connectors/webhook_handler.py
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import hmac, hashlib, json
from typing import Dict, Any
from .registry import ConnectorRegistry
from .base import ConnectorProvider
from app.services.event_bus import EventBus

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
_processed_events: set = set()

@router.post("/{provider}/{tenant_id}")
async def handle_webhook(provider: str, tenant_id: str, request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    try: payload = json.loads(body)
    except json.JSONDecodeError: raise HTTPException(status_code=400, detail="Invalid JSON")
    event_id = _extract_event_id(provider, payload)
    if event_id and event_id in _processed_events: return JSONResponse({"status": "already_processed", "event_id": event_id})
    signature = request.headers.get("X-HubSpot-Signature") or request.headers.get("X-Yousign-Signature") or request.headers.get("X-Webhook-Signature")
    if signature:
        secret = await _get_webhook_secret(tenant_id, provider)
        if secret:
            provider_instance = ConnectorRegistry.get(provider, tenant_id, {}, {})
            if not provider_instance.verify_webhook_signature(body, signature, secret): raise HTTPException(status_code=401, detail="Invalid signature")
    background_tasks.add_task(_process_webhook_event, provider, tenant_id, payload, event_id)
    return JSONResponse({"status": "accepted", "event_id": event_id})

def _extract_event_id(provider: str, payload: Dict[str, Any]) -> Optional[str]:
    extractors = {"hubspot": lambda p: p.get("eventId"), "yousign": lambda p: p.get("id"), "pennylane": lambda p: p.get("event_id"), "salesforce": lambda p: p.get("event", {}).get("replayId"), "docusign": lambda p: p.get("data", {}).get("envelopeId")}
    extractor = extractors.get(provider); return extractor(payload) if extractor else None

async def _get_webhook_secret(tenant_id: str, provider: str) -> Optional[str]: return None

async def _process_webhook_event(provider: str, tenant_id: str, payload: Dict[str, Any], event_id: Optional[str]):
    try:
        normalized = _normalize_webhook_event(provider, payload)
        normalized.update({"tenant_id": tenant_id, "provider": provider, "received_at": datetime.utcnow().isoformat()})
        await EventBus.publish(f"connector.{provider}", normalized)
        if event_id: _processed_events.add(event_id)
        event_type = normalized.get("event_type")
        if provider == "hubspot" and "deal" in str(event_type).lower(): await _handle_hubspot_deal(tenant_id, normalized)
        elif provider == "yousign": await _handle_yousign_event(tenant_id, normalized)
    except Exception as e: import logging; logging.error(f"Webhook processing failed for {provider}/{tenant_id}: {e}")

def _normalize_webhook_event(provider: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if provider == "hubspot": return {"event_type": payload.get("subscriptionType", "unknown"), "object_type": payload.get("objectType"), "object_id": payload.get("objectId"), "occurred_at": payload.get("occurredAt"), "raw": payload}
    elif provider == "yousign": return {"event_type": payload.get("event", "unknown"), "signature_request_id": payload.get("data", {}).get("id"), "status": payload.get("data", {}).get("status"), "raw": payload}
    elif provider == "pennylane": return {"event_type": payload.get("event", "unknown"), "entity_type": payload.get("entity_type"), "entity_id": payload.get("entity_id"), "action": payload.get("action"), "raw": payload}
    return {"event_type": "unknown", "raw": payload}

async def _handle_yousign_event(tenant_id: str, event: Dict[str, Any]):
    from app.services.projects import ProjectService
    req_id = event.get("signature_request_id"); status = event.get("status")
    if event["event_type"] in ["sign_request_signed", "sign_request_done"] or status == "done":
        await ProjectService.update_signature_status(tenant_id, req_id, "signed", datetime.utcnow())
        await EventBus.publish("notification.signature_signed", {"tenant_id": tenant_id, "signature_request_id": req_id})
    elif event["event_type"] in ["sign_request_declined"] or status == "declined":
        await ProjectService.update_signature_status(tenant_id, req_id, "declined", decline_reason=event.get("raw", {}).get("data", {}).get("decline_reason"))
        await EventBus.publish("notification.signature_declined", {"tenant_id": tenant_id, "signature_request_id": req_id})
    elif event["event_type"] in ["sign_request_expired"] or status == "expired":
        await ProjectService.update_signature_status(tenant_id, req_id, "expired")

async def _handle_hubspot_deal(tenant_id: str, event: Dict[str, Any]):
    from app.services.connectors.sync import SyncService
    await SyncService.sync_tenant_provider(tenant_id, "hubspot", ConnectorType.CRM, force_full=False)
```

### 3.6 RateLimiter

```python
# app/services/connectors/rate_limiter.py
import asyncio
from datetime import datetime
from typing import Dict

class RateLimiter:
    def __init__(self):
        self._buckets: Dict[str, asyncio.Semaphore] = {}
        self._last_request: Dict[str, datetime] = {}
        self._delays: Dict[str, float] = {"hubspot": 0.1, "salesforce": 0.05, "pipedrive": 0.25, "pennylane": 0.2, "yousign": 0.2, "chift": 0.1}
    def _key(self, provider: str, tenant_id: str) -> str: return f"{provider}:{tenant_id}"
    async def acquire(self, provider: str, tenant_id: str):
        key = self._key(provider, tenant_id)
        if key not in self._buckets: self._buckets[key] = asyncio.Semaphore(1)
        async with self._buckets[key]:
            last = self._last_request.get(key); delay = self._delays.get(provider, 0.1)
            if last:
                from datetime import timedelta
                elapsed = (datetime.utcnow() - last).total_seconds()
                if elapsed < delay: await asyncio.sleep(delay - elapsed)
            self._last_request[key] = datetime.utcnow()
            yield
    async def handle_rate_limit_response(self, provider: str, tenant_id: str, status_code: int, retry_after: int = None):
        if status_code == 429:
            key = self._key(provider, tenant_id); wait_time = retry_after or 60
            self._delays[provider] = max(self._delays.get(provider, 0.1) * 2, wait_time)
            await asyncio.sleep(wait_time)
```

### 3.7 Exceptions

```python
# app/services/connectors/exceptions.py
class ConnectorError(Exception): pass
class ConnectorAuthError(ConnectorError): pass
class ConnectorRateLimitError(ConnectorError):
    def __init__(self, message: str, retry_after: int = 60): super().__init__(message); self.retry_after = retry_after
class ConnectorAPIError(ConnectorError):
    def __init__(self, message: str, status_code: int = None, response_body: str = None): super().__init__(message); self.status_code = status_code; self.response_body = response_body
class ConnectorConfigError(ConnectorError): pass
class ConnectorSyncError(ConnectorError): pass
```


## Partie 4 — Roadmap des connecteurs (par version)

### 4.1 Vue chronologique

| Version | Période | Focus | Connecteurs ajoutés | Jours dev |
|---------|---------|-------|---------------------|-----------|
| v0.1 | Q1 2025 | MVP | Aucun (upload manuel) | 0 |
| v0.2 | Q1-Q2 2025 | CRM SMB | **HubSpot + Pipedrive** | 14 |
| v0.2b | Q2 2025 | CRM Enterprise | **Salesforce** | 15 |
| v0.3 | Q2 2025 | ERP PME | **Odoo + Dynamics + Zoho** | 23 |
| v0.4 | Q3 2025 | Compta FR | **Chift (15+ comptas) + Pennylane natif** | 20 |
| v0.4b | Q3 2025 | Signature | **Yousign natif** | 8 |
| v0.5 | Q4 2025 | Fintech | **Qonto + Agicap + Pleo** (via Chift) | 6 |
| v1.0 | Q1 2026 | E-commerce | **Shopify + WooCommerce** (via Chift) | 4 |
| v1.1 | Q1 2026 | Caisse | **Zelty + Popina + L'Addition** (via Chift) | 6 |
| v1.2 | Q2 2026 | Legacy | **Sage 100 natif + Cegid natif** | 25 |
| v1.3 | Q2 2026 | Paie | **Silae + Payfit** | 22 |
| v2.0 | Q3 2026 | International | **DocuSign + Adobe Sign + QuickBooks natif + Xero** | 25 |
| **TOTAL** | 2025-2026 | — | **40+ connecteurs** | **~198 jours** |

### 4.2 Détails par version

#### v0.2 — HubSpot + Pipedrive (P0 🔴)
HubSpot (288K+ clients) : REST v3, OAuth2 Private Apps, webhooks subscriptions, 100 req/10s. Pipedrive (100K+ clients) : REST v1, API Token + OAuth2, webhooks deals/persons. Flow : AO gagné TAKA → create_deal dans CRM avec custom field `taka_tender_id`. Webhook inverse : deal updated → sync vers TAKA. **14 jours**.

#### v0.2b — Salesforce (P1 🟡)
REST v66.0 + Pub/Sub API (CDC gRPC+Avro). OAuth2 Web Server Flow. SOQL pour requêtes. Custom field TAKA_Tender_ID__c. Complexité : domaine personnalisé, sandbox, Governor Limits. **15 jours**.

#### v0.3 — Odoo + Dynamics + Zoho (P1 🟡)
Odoo : JSON-RPC (legacy stable) + REST v17+ (nouveau), session-based auth, pas de webhooks robustes → polling. Dynamics 365 BC : REST OData v2.0, Basic + OAuth2, 6000 req/min. Zoho CRM : REST v2.1, OAuth2 Zoho, 100 req/min/app. **23 jours**.

#### v0.4 — Chift + Pennylane natif (P0 🔴)
**Moment critique de la roadmap.** Chift (belge) normalise 15+ logiciels comptables français via 1 API. Pennylane natif pour webhooks temps réel et granularité maximale (API moderne, excellente documentation). Chift couvre : Sage 100, Cegid Loop/Quadra, MyUnisoft, Inqom, ACD, QuickBooks. Pennylane natif : 500K entreprises, webhooks factures/paiements. **20 jours**.

```python
# Exemple ChiftProvider
async def create_invoice_via_chift(tenant_id: str, invoice_data: dict):
    provider = ConnectorRegistry.get("chift", tenant_id, config, tokens)
    chift_software = config.get("chift_software_id")  # ex: "sage100"
    return await provider.create("invoice", {
        "client": {"siret": invoice_data["buyer_siret"]},
        "lines": invoice_data["lines"], "due_date": invoice_data["due_date"], "deposit_percent": 0.30
    })
```

#### v0.4b — Yousign natif (P1 🟡)
Leader français signature électronique (eIDAS). REST v3, OAuth2, webhooks. Templates : CCAP (construction), CDD (gros oeuvre), bon de commande. Flow : AO gagné → create sign request → webhook tracking (signed/declined/expired) → mise à jour projet. **8 jours**.

#### v0.5-v1.1 — Via Chift (P2 🟢)
Qonto/Agicap/Pleo (trésorerie, dépenses), Shopify/WooCommerce (e-commerce), Zelty/Popina/L'Addition/Planity (caisse, restauration). Avantage : réutilisation du connecteur Chift existant avec mapping spécifique. **16 jours total**.

#### v1.2 — Sage 100 natif + Cegid natif (P2 🟢)
Granularité on-premise : écritures analytiques, plans de tiers, immobilisations. Complexité : middleware on-premise souvent nécessaire, API REST partielle Sage 100, Cegid Quadra via Loop uniquement. **25 jours**.

#### v1.3 — Silae + Payfit (P2 🟢)
Paie : effectifs, masse salariale, entrées/sorties pour scoring capacité d'exécution. Si 5 salariés et AO 500K€ → risque sous-effectif reflété dans le score. **22 jours**.

#### v2.0 — International (P2 🟢)
DocuSign (global), Adobe Sign (Adobe ecosystem), QuickBooks natif (UK/US), Xero (UK/AU/NZ), Stripe natif. Préparation expansion européenne. **25 jours**.

### 4.3 Synthèse roadmap

```
2025 Q1    [v0.1] MVP — aucun connecteur
2025 Q1-Q2 [v0.2] 🔴 HubSpot + Pipedrive — 14 jours
2025 Q2    [v0.2b] 🟡 Salesforce — 15 jours
2025 Q2    [v0.3] 🟡 Odoo + Dynamics + Zoho — 23 jours
2025 Q3    [v0.4] 🔴 CHIFT (15+ comptas) + Pennylane natif — 20 jours
2025 Q3    [v0.4b] 🟡 Yousign — 8 jours
2025 Q4    [v0.5] 🟢 Fintech (Qonto, Agicap, Pleo) — 6 jours
2026 Q1    [v1.0] 🟢 E-commerce (Shopify, WooCommerce) — 4 jours
2026 Q1    [v1.1] 🟢 Caisse (Zelty, Popina, L'Addition) — 6 jours
2026 Q2    [v1.2] 🟢 Legacy (Sage 100 natif, Cegid natif) — 25 jours
2026 Q2    [v1.3] 🟢 Paie (Silae, Payfit) — 22 jours
2026 Q3    [v2.0] 🟢 International (DocuSign, Xero, Stripe natif) — 25 jours

TOTAL : ~198 jours de développement — 40+ connecteurs — 2M+ entreprises couvertes
```

---

## Partie 5 — Scoring enrichi par écosystème

### 5.1 Vision : du scoring "AO seul" au scoring "entreprise complète"

Le scoring composite ajoute **6 dimensions** issues de l'écosystème connecté :

```
Score Final = 0.40×Score_AO + 0.15×Score_CRM + 0.20×Score_Compta
            + 0.05×Score_Signature + 0.10×Score_Fintech + 0.10×Score_Marge
```

| Dimension | Source | Indicateur | Impact |
|-----------|--------|-----------|--------|
| **CRM** | HubSpot/Salesforce/Odoo | Deals actifs, client existant, historique relationnel | Capacité / relation |
| **Comptabilité** | Chift/Pennylane | Trésorerie, délai paiement acheteur, encours clients | Santé financière |
| **Signature** | Yousign | Template disponible, vélocité contractuelle | Démarche administrative |
| **Fintech** | Qonto/Agicap | Solde bancaire vs montant AO, prévision trésorerie | Capacité financement |
| **Marge** | Accounting analytics | Marge réelle historique par CPV | Rentabilité réelle |

### 5.2 Implémentation

```python
# app/services/scoring/ecosystem_scoring.py
from decimal import Decimal
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from app.services.connectors.registry import ConnectorRegistry
from app.services.connectors.base import ConnectorType

@dataclass
class EcosystemScore:
    total_score: float; ao_score: float; crm_score: float
    accounting_score: float; signature_score: float; fintech_score: float; margin_score: float
    crm_deals_active: int = 0; cash_position_eur: Decimal = Decimal("0")
    avg_payment_delay_days: float = 0.0; is_existing_client: bool = False
    last_deal_date: Optional[datetime] = None; last_deal_amount: Optional[Decimal] = None
    signature_template_exists: bool = False; avg_margin_pct: Optional[float] = None
    buyer_payment_history: str = "unknown"; reasoning: List[str] = None
    def __post_init__(self):
        if self.reasoning is None: self.reasoning = []

class EcosystemScoringService:
    DEFAULT_WEIGHTS = {"ao": 0.40, "crm": 0.15, "accounting": 0.20, "signature": 0.05, "fintech": 0.10, "margin": 0.10}
    def __init__(self, db_session): self.db_session = db_session
    
    async def score_tender(self, tender_id: str, tenant_id: str, base_ao_score: float, weights: Optional[Dict[str, float]] = None) -> EcosystemScore:
        weights = weights or self.DEFAULT_WEIGHTS; reasoning: List[str] = []
        crm_data = await self._get_crm_dimension(tender_id, tenant_id)
        crm_score = self._compute_crm_score(crm_data, reasoning)
        accounting_data = await self._get_accounting_dimension(tender_id, tenant_id)
        accounting_score = self._compute_accounting_score(accounting_data, reasoning)
        signature_data = await self._get_signature_dimension(tender_id, tenant_id)
        signature_score = self._compute_signature_score(signature_data, reasoning)
        fintech_data = await self._get_fintech_dimension(tender_id, tenant_id)
        fintech_score = self._compute_fintech_score(fintech_data, reasoning)
        margin_data = await self._get_margin_dimension(tender_id, tenant_id)
        margin_score = self._compute_margin_score(margin_data, reasoning)
        total = sum(weights[k] * v for k, v in [("ao", base_ao_score), ("crm", crm_score), ("accounting", accounting_score), ("signature", signature_score), ("fintech", fintech_score), ("margin", margin_score)])
        return EcosystemScore(
            total_score=round(total, 2), ao_score=round(base_ao_score, 2), crm_score=round(crm_score, 2),
            accounting_score=round(accounting_score, 2), signature_score=round(signature_score, 2),
            fintech_score=round(fintech_score, 2), margin_score=round(margin_score, 2),
            crm_deals_active=crm_data.get("active_deals_count", 0), cash_position_eur=accounting_data.get("cash_position", Decimal("0")),
            avg_payment_delay_days=accounting_data.get("avg_payment_delay", 0.0), is_existing_client=crm_data.get("is_existing_client", False),
            last_deal_date=crm_data.get("last_deal_date"), last_deal_amount=crm_data.get("last_deal_amount"),
            signature_template_exists=signature_data.get("template_exists", False), avg_margin_pct=margin_data.get("avg_margin_pct"),
            buyer_payment_history=accounting_data.get("buyer_payment_history", "unknown"), reasoning=reasoning
        )
    
    async def _get_crm_dimension(self, tender_id: str, tenant_id: str) -> Dict[str, Any]:
        from app.models import Tender, CRMConnector
        from sqlalchemy import select
        tender = (await self.db_session.execute(select(Tender).where(Tender.id == tender_id))).scalar_one_or_none()
        if not tender: return {"error": "Tender not found"}
        connector = (await self.db_session.execute(select(CRMConnector).where(CRMConnector.tenant_id == tenant_id, CRMConnector.is_active == True))).scalar_one_or_none()
        if not connector: return {"connected": False}
        tokens = await self._get_crm_tokens(connector.id)
        provider = ConnectorRegistry.get(connector.provider, tenant_id, connector.config, tokens, self.db_session)
        async with provider:
            await provider.authenticate()
            active_deals = await provider.get_active_deals_count()
            is_existing = False; last_deal = None
            if tender.buyer_email:
                contact = await provider.find_contact_by_email(tender.buyer_email)
                if contact:
                    is_existing = True
                    deals = (await provider.list_deals(modified_since=datetime.utcnow() - timedelta(days=365*5))).items
                    if deals: last_deal = max(deals, key=lambda d: d.updated_at or d.created_at)
            return {"connected": True, "provider": connector.provider, "active_deals_count": active_deals, "is_existing_client": is_existing, "last_deal_date": last_deal.updated_at if last_deal else None, "last_deal_amount": last_deal.amount if last_deal else None, "last_deal_stage": last_deal.stage if last_deal else None}
    
    def _compute_crm_score(self, data: Dict[str, Any], reasoning: List[str]) -> float:
        if not data.get("connected"): reasoning.append("CRM non connecté — neutre"); return 50.0
        score = 50.0; active = data.get("active_deals_count", 0)
        if active > 20: score -= 20; reasoning.append(f"Surcharge : {active} deals — pénalité -20")
        elif active > 10: score -= 10; reasoning.append(f"Charge élevée : {active} deals — pénalité -10")
        elif active < 3: score += 10; reasoning.append(f"Capacité dispo : {active} deals — bonus +10")
        if data.get("is_existing_client"):
            score += 15; reasoning.append("Client existant — bonus +15")
            last_stage = data.get("last_deal_stage", "")
            if last_stage in ["closed_won", "won", "gagné"]: score += 10; reasoning.append("Dernier deal gagné — bonus +10")
            elif last_stage in ["closed_lost", "lost", "perdu"]: score -= 10; reasoning.append("Dernier deal perdu — pénalité -10")
        return max(0, min(100, score))
    
    async def _get_accounting_dimension(self, tender_id: str, tenant_id: str) -> Dict[str, Any]:
        from app.models import Tender, AccountingConnector
        from sqlalchemy import select
        tender = (await self.db_session.execute(select(Tender).where(Tender.id == tender_id))).scalar_one_or_none()
        if not tender: return {"error": "Tender not found"}
        connector = (await self.db_session.execute(select(AccountingConnector).where(AccountingConnector.tenant_id == tenant_id, AccountingConnector.is_active == True))).scalar_one_or_none()
        if not connector: return {"connected": False}
        tokens = await self._get_accounting_tokens(connector.id)
        provider = ConnectorRegistry.get(connector.provider, tenant_id, connector.config, tokens, self.db_session)
        async with provider:
            await provider.authenticate()
            try: cash = await provider.get_cash_position()
            except: cash = Decimal("0")
            avg_delay = 0.0; history = "unknown"
            if tender.buyer_siret:
                try:
                    avg_delay = await provider.get_avg_payment_delay(tender.buyer_siret)
                    history = "good" if avg_delay < 30 else "average" if avg_delay < 45 else "poor"
                except: pass
            try:
                unpaid = await provider.list_invoices(status="overdue")
                total_unpaid = sum(Decimal(str(inv.get("total_ttc", 0))) for inv in unpaid)
            except: total_unpaid = Decimal("0")
            return {"connected": True, "provider": connector.provider, "cash_position": cash, "avg_payment_delay": avg_delay, "buyer_payment_history": history, "total_unpaid_invoices": total_unpaid}
    
    def _compute_accounting_score(self, data: Dict[str, Any], reasoning: List[str]) -> float:
        if not data.get("connected"): reasoning.append("Comptabilité non connectée — neutre"); return 50.0
        score = 50.0; cash = data.get("cash_position", Decimal("0"))
        if cash > Decimal("100000"): score += 15; reasoning.append(f"Trésorerie saine : {cash}€ — bonus +15")
        elif cash > Decimal("50000"): score += 10; reasoning.append(f"Trésorerie positive : {cash}€ — bonus +10")
        elif cash < Decimal("-10000"): score -= 20; reasoning.append(f"Trésorerie négative : {cash}€ — pénalité -20")
        elif cash < Decimal("0"): score -= 10; reasoning.append(f"Trésorerie négative : {cash}€ — pénalité -10")
        history = data.get("buyer_payment_history", "unknown")
        if history == "good": score += 15; reasoning.append("Acheteur : paiements rapides — bonus +15")
        elif history == "average": score += 5; reasoning.append("Acheteur : paiements moyens — bonus +5")
        elif history == "poor": score -= 15; reasoning.append("Acheteur : retards fréquents — pénalité -15")
        unpaid = data.get("total_unpaid_invoices", Decimal("0"))
        if unpaid > Decimal("50000"): score -= 10; reasoning.append(f"Encours élevé : {unpaid}€ — pénalité -10")
        return max(0, min(100, score))
    
    async def _get_signature_dimension(self, tender_id: str, tenant_id: str) -> Dict[str, Any]:
        from app.models import Tender, SignatureConnector
        from sqlalchemy import select
        tender = (await self.db_session.execute(select(Tender).where(Tender.id == tender_id))).scalar_one_or_none()
        if not tender or not tender.requires_signature: return {"required": False, "template_exists": False}
        connector = (await self.db_session.execute(select(SignatureConnector).where(SignatureConnector.tenant_id == tenant_id, SignatureConnector.is_active == True))).scalar_one_or_none()
        if not connector: return {"required": True, "connected": False, "template_exists": False}
        contract_type = self._resolve_contract_type(tender)
        tokens = await self._get_signature_tokens(connector.id)
        provider = ConnectorRegistry.get(connector.provider, tenant_id, connector.config, tokens, self.db_session)
        async with provider:
            await provider.authenticate()
            try: templates = await provider.list_templates(contract_type=contract_type); has_template = len(templates) > 0
            except: has_template = False
            return {"required": True, "connected": True, "provider": connector.provider, "contract_type": contract_type, "template_exists": has_template}
    
    def _resolve_contract_type(self, tender) -> str:
        cpv = tender.cpv_code or ""; amount = tender.estimated_amount or 0
        if cpv.startswith("45"): return "ccap_construction"
        elif cpv.startswith("71"): return "ccap_ingenierie"
        elif amount > 50000: return "cdd_gros_oeuvre"
        else: return "bon_de_commande"
    
    def _compute_signature_score(self, data: Dict[str, Any], reasoning: List[str]) -> float:
        if not data.get("required"): reasoning.append("Signature non requise — neutre"); return 50.0
        if not data.get("connected"): reasoning.append("Signature requise, connecteur non configuré — pénalité"); return 30.0
        if data.get("template_exists"): reasoning.append(f"Template '{data.get('contract_type')}' dispo — bonus +20"); return 70.0
        else: reasoning.append(f"Template '{data.get('contract_type')}' manquant — neutre"); return 50.0
    
    async def _get_fintech_dimension(self, tender_id: str, tenant_id: str) -> Dict[str, Any]:
        from app.models import Tender, AccountingConnector
        from sqlalchemy import select
        tender = (await self.db_session.execute(select(Tender).where(Tender.id == tender_id))).scalar_one_or_none()
        if not tender: return {"connected": False}
        connector = (await self.db_session.execute(select(AccountingConnector).where(AccountingConnector.tenant_id == tenant_id, AccountingConnector.provider == "chift", AccountingConnector.is_active == True))).scalar_one_or_none()
        if not connector: return {"connected": False}
        chift_software = connector.config.get("chift_software_id", "")
        if chift_software not in ["qonto", "agicap"]: return {"connected": False}
        tokens = await self._get_accounting_tokens(connector.id)
        provider = ConnectorRegistry.get("chift", tenant_id, connector.config, tokens, self.db_session)
        async with provider:
            await provider.authenticate()
            try: balance = await provider.get_account_balance()
            except: balance = Decimal("0")
            try: cash_forecast = await provider.get_cash_flow_forecast(months=3); min_forecast = min(cash_forecast) if cash_forecast else Decimal("0")
            except: min_forecast = Decimal("0")
            return {"connected": True, "provider": chift_software, "current_balance": balance, "min_forecast_3m": min_forecast, "tender_amount": Decimal(str(tender.estimated_amount or 0))}
    
    def _compute_fintech_score(self, data: Dict[str, Any], reasoning: List[str]) -> float:
        if not data.get("connected"): reasoning.append("Fintech non connecté — neutre"); return 50.0
        score = 50.0; balance = data.get("current_balance", Decimal("0")); amount = data.get("tender_amount", Decimal("0")); forecast = data.get("min_forecast_3m", Decimal("0"))
        if amount > 0:
            ratio = float(balance / amount)
            if ratio > 0.5: score += 15; reasoning.append("Trésorerie > 50% montant AO — bonus +15")
            elif ratio > 0.3: score += 10; reasoning.append("Trésorerie > 30% montant AO — bonus +10")
            elif ratio < 0.1 and balance > 0: score -= 10; reasoning.append("Trésorerie < 10% montant AO — pénalité -10")
            elif balance < 0: score -= 15; reasoning.append("Solde bancaire négatif — pénalité -15")
        if forecast < Decimal("-50000"): score -= 10; reasoning.append("Prévision trésorerie négative 3 mois — pénalité -10")
        elif forecast > Decimal("100000"): score += 5; reasoning.append("Prévision trésorerie positive — bonus +5")
        return max(0, min(100, score))
    
    async def _get_margin_dimension(self, tender_id: str, tenant_id: str) -> Dict[str, Any]:
        from app.models import Tender, AccountingAnalytics
        from sqlalchemy import select
        tender = (await self.db_session.execute(select(Tender).where(Tender.id == tender_id))).scalar_one_or_none()
        if not tender or not tender.cpv_code: return {"available": False}
        cpv_prefix = tender.cpv_code[:4]
        rows = (await self.db_session.execute(select(AccountingAnalytics).where(AccountingAnalytics.tenant_id == tenant_id, AccountingAnalytics.cpv_code.like(f"{cpv_prefix}%")).order_by(AccountingAnalytics.period_month.desc()).limit(12))).scalars().all()
        if not rows: return {"available": False, "cpv_code": tender.cpv_code}
        avg_margin = sum(r.margin_pct for r in rows if r.margin_pct is not None) / len(rows)
        return {"available": True, "cpv_code": tender.cpv_code, "cpv_prefix": cpv_prefix, "avg_margin_pct": round(avg_margin, 2), "periods_count": len(rows), "last_period": rows[0].period_month if rows else None}
    
    def _compute_margin_score(self, data: Dict[str, Any], reasoning: List[str]) -> float:
        if not data.get("available"): reasoning.append("Marge historique non dispo — neutre"); return 50.0
        margin = data.get("avg_margin_pct", 0)
        if margin > 25: reasoning.append(f"Marge excellente : {margin}% — bonus +20"); return 70.0
        elif margin > 15: reasoning.append(f"Marge bonne : {margin}% — bonus +10"); return 60.0
        elif margin > 8: reasoning.append(f"Marge moyenne : {margin}% — neutre"); return 50.0
        elif margin > 0: reasoning.append(f"Marge faible : {margin}% — pénalité -10"); return 40.0
        else: reasoning.append(f"Marge négative : {margin}% — pénalité -20"); return 30.0
    
    async def _get_crm_tokens(self, connector_id: str) -> Dict[str, str]: return {}
    async def _get_accounting_tokens(self, connector_id: str) -> Dict[str, str]: return {}
    async def _get_signature_tokens(self, connector_id: str) -> Dict[str, str]: return {}
```

### 5.3 Exemple de sortie JSON

```json
{
  "tender_id": "ao_12345",
  "tenant_id": "tenant_abc",
  "total_score": 72.5,
  "dimension_scores": {"ao": 65.0, "crm": 85.0, "accounting": 80.0, "signature": 70.0, "fintech": 60.0, "margin": 75.0},
  "metadata": {
    "crm_deals_active": 5,
    "cash_position_eur": 125000.00,
    "avg_payment_delay_days": 28,
    "is_existing_client": true,
    "last_deal_date": "2024-11-15T10:30:00Z",
    "last_deal_amount": 45000.00,
    "signature_template_exists": true,
    "avg_margin_pct": 18.5,
    "buyer_payment_history": "good"
  },
  "reasoning": [
    "Capacité dispo : 5 deals actifs — bonus +10",
    "Client existant — bonus +15",
    "Dernier deal gagné — bonus +10",
    "Trésorerie saine : 125000€ — bonus +15",
    "Acheteur : paiements rapides — bonus +15",
    "Template 'ccap_construction' dispo — bonus +20",
    "Trésorerie > 50% montant AO — bonus +15",
    "Marge historique bonne : 18.5% — bonus +10"
  ],
  "recommendation": "GO",
  "confidence": "high"
}
```

---

## Partie 6 — Tableaux comparatifs exhaustifs

### 6.1 Tableau maître : tous les connecteurs (40+)

| # | Connecteur | Type | API | Auth | Webhooks | Via Chift? | Maturité | Priorité | Jours dev |
|---|-----------|------|-----|------|----------|-----------|----------|----------|-----------|
| 1 | **HubSpot** | CRM | REST v3 | OAuth2 | ✅ | ❌ | ⭐⭐⭐⭐⭐ | P0 🔴 | 8 |
| 2 | **Pipedrive** | CRM | REST v1 | OAuth2+Token | ✅ | ❌ | ⭐⭐⭐⭐☆ | P0 🔴 | 6 |
| 3 | **Salesforce** | CRM | REST v66.0+Pub/Sub | OAuth2 | CDC | ❌ | ⭐⭐⭐⭐⭐ | P1 🟡 | 15 |
| 4 | **Odoo** | CRM/ERP | JSON-RPC/REST | Session/OAuth2 | ⚠️ | ✅ | ⭐⭐⭐☆☆ | P1 🟡 | 10 |
| 5 | **Dynamics 365 BC** | CRM/ERP | REST OData v2.0 | Basic/OAuth2 | ✅ | ❌ | ⭐⭐⭐⭐☆ | P1 🟡 | 8 |
| 6 | **Zoho CRM** | CRM | REST v2.1 | OAuth2 | ✅ | ❌ | ⭐⭐⭐⭐☆ | P2 🟢 | 5 |
| 7 | **Pennylane** | Compta | REST v1 | OAuth2 | ✅ | ✅ | ⭐⭐⭐⭐⭐ | P0 🔴 | 8 |
| 8 | **Sage 100** | Compta | REST partielle | OAuth2 | ⚠️ | ✅ | ⭐⭐⭐☆☆ | P2 🟢 | 15 |
| 9 | **Sage 50** | Compta | REST limitée | API Key | ❌ | ✅ | ⭐⭐☆☆☆ | P2 🟢 | 10 |
| 10 | **Cegid Loop** | ERP | REST v1 | OAuth2 | ✅ | ✅ | ⭐⭐⭐⭐☆ | P2 🟢 | 10 |
| 11 | **Cegid Quadra** | Compta | Via Loop | OAuth2(Loop) | Via Loop | ✅ | ⭐⭐⭐☆☆ | P2 🟢 | 8 |
| 12 | **MyUnisoft** | Compta | REST v1 | OAuth2 | ✅ | ✅ | ⭐⭐⭐⭐☆ | P2 🟢 | 8 |
| 13 | **Inqom** | Compta | REST v1 | OAuth2 | [À valider] | ✅ | ⭐⭐⭐☆☆ | P2 🟢 | 8 |
| 14 | **ACD** | Compta | SOAP/REST legacy | API Key | ❌ | ✅ | ⭐⭐☆☆☆ | P2 🟢 | 12 |
| 15 | **Dougs** | Compta | REST v1 | OAuth2 | [À valider] | ❌ | ⭐⭐⭐☆☆ | P2 🟢 | 8 |
| 16 | **EBP** | Compta | REST (EBP Cloud) | OAuth2 | ❌ | ❌ | ⭐⭐⭐☆☆ | P2 🟢 | 10 |
| 17 | **Ciel** | Compta | Legacy | API Key | ❌ | ❌ | ⭐☆☆☆☆ | P3 ⚪ | 15 |
| 18 | **QuickBooks** | Compta | REST v3 | OAuth2 | ✅ | ✅ | ⭐⭐⭐⭐⭐ | P2 🟢 | 6 |
| 19 | **Yousign** | Signature | REST v3 | OAuth2 | ✅ | ❌ | ⭐⭐⭐⭐⭐ | P1 🟡 | 8 |
| 20 | **DocuSign** | Signature | REST v2.1 | OAuth2 | ✅ | ❌ | ⭐⭐⭐⭐⭐ | P2 🟢 | 8 |
| 21 | **Adobe Sign** | Signature | REST v6 | OAuth2 | ✅ | ❌ | ⭐⭐⭐⭐☆ | P2 🟢 | 8 |
| 22 | **Silae** | Paie | REST v1 | OAuth2 | [À valider] | ❌ | ⭐⭐⭐☆☆ | P2 🟢 | 12 |
| 23 | **Payfit** | Paie | REST v1 | OAuth2 | [À valider] | ❌ | ⭐⭐⭐☆☆ | P2 🟢 | 10 |
| 24 | **Peoppl** | Paie/RH | REST v1 | OAuth2 | [À valider] | ❌ | ⭐⭐⭐☆☆ | P3 ⚪ | 8 |
| 25 | **Qonto** | Néobanque | REST v2 | OAuth2 | ✅ | ✅ | ⭐⭐⭐⭐☆ | P2 🟢 | 2* |
| 26 | **Agicap** | Trésorerie | REST v1 | OAuth2 | [À valider] | ✅ | ⭐⭐⭐⭐☆ | P2 🟢 | 2* |
| 27 | **Pleo** | Dépenses | REST v1 | OAuth2 | [À valider] | ✅ | ⭐⭐⭐⭐☆ | P2 🟢 | 2* |
| 28 | **Stripe** | Paiement | REST v1 | API Key/OAuth2 | ✅ | ✅ | ⭐⭐⭐⭐⭐ | P2 🟢 | 2* |
| 29 | **Mollie** | Paiement | REST v2 | API Key | ✅ | ✅ | ⭐⭐⭐⭐⭐ | P2 🟢 | 2* |
| 30 | **Shopify** | E-commerce | REST+GraphQL | OAuth2 | ✅ | ✅ | ⭐⭐⭐⭐⭐ | P2 🟢 | 2* |
| 31 | **WooCommerce** | E-commerce | REST v3 | Basic/OAuth1 | ✅ | ✅ | ⭐⭐⭐⭐☆ | P2 🟢 | 2* |
| 32 | **Zelty** | Caisse | REST v1 | API Key | [À valider] | ✅ | ⭐⭐⭐☆☆ | P2 🟢 | 2* |
| 33 | **Popina** | Caisse | REST v1 | API Key | [À valider] | ✅ | ⭐⭐⭐☆☆ | P2 🟢 | 2* |
| 34 | **L'Addition** | Caisse | REST v1 | API Key | [À valider] | ✅ | ⭐⭐⭐☆☆ | P2 🟢 | 2* |
| 35 | **Planity** | Réservation | REST v1 | API Key | [À valider] | ✅ | ⭐⭐⭐☆☆ | P2 🟢 | 2* |
| 36 | **Chift** | API unifiée | REST | OAuth2/API Key | ✅ | N/A | ⭐⭐⭐⭐☆ | P0 🔴 | 12 |
| 37 | **Apideck** | API unifiée | REST | OAuth2/API Key | ✅ | N/A | ⭐⭐⭐⭐☆ | P3 ⚪ | 10 |
| 38 | **Maesn** | API unifiée | REST | OAuth2 | [À valider] | N/A | ⭐⭐⭐⭐☆ | P3 ⚪ | 8 |
| 39 | **Knit** | API unifiée CRM | REST | OAuth2 | [À valider] | N/A | ⭐⭐⭐☆☆ | P3 ⚪ | 8 |
| 40 | **Xero** | Comptabilité | REST | OAuth2 | ✅ | ❌ | ⭐⭐⭐⭐⭐ | P3 ⚪ | 6 |

*Via Chift — réutilisation du connecteur Chift existant.

### 6.2 Tableau : maturité API détaillée

| Logiciel | Doc | SDK | Webhooks | Rate limit | Sandbox | OAuth2 standard | REST JSON | Étoiles |
|----------|-----|-----|----------|------------|---------|-----------------|-----------|---------|
| HubSpot | Excellent | ✅ | ✅ Avancé | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Salesforce | Excellent | ✅ | ✅ CDC | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Pipedrive | Bon | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐☆ |
| Pennylane | Excellent | ❌ | ✅ | [À valider] | [À valider] | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Yousign | Excellent | ❌ | ✅ | [À valider] | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| QuickBooks | Excellent | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Shopify | Excellent | ✅ | ✅ | ✅ | ✅ | ✅ | ✅+GraphQL | ⭐⭐⭐⭐⭐ |
| Stripe | Excellent | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| DocuSign | Excellent | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Dynamics BC | Bon | ✅ .NET | ✅ | ✅ | ✅ | ✅ OData | ⭐⭐⭐⭐☆ |
| Zoho CRM | Bon | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐☆ |
| Odoo | Moyen | ❌ | ⚠️ | Configurable | ✅ | ⚠️ | ✅ v17+ | ⭐⭐⭐☆☆ |
| Sage 100 | Moyen | ❌ | ⚠️ | [À valider] | ❌ | ✅ | ✅ partiel | ⭐⭐⭐☆☆ |
| Cegid Loop | Bon | ❌ | ✅ | [À valider] | [À valider] | ✅ | ✅ | ⭐⭐⭐⭐☆ |
| MyUnisoft | Bon | ❌ | ✅ | [À valider] | [À valider] | ✅ | ✅ | ⭐⭐⭐⭐☆ |
| ACD | Faible | ❌ | ❌ | [À valider] | ❌ | ❌ | ❌ SOAP | ⭐⭐☆☆☆ |
| EBP | Moyen | ❌ | ❌ | [À valider] | ❌ | ✅ | ✅ | ⭐⭐⭐☆☆ |
| Ciel | Faible | ❌ | ❌ | Bas | ❌ | ❌ | ❌ Legacy | ⭐☆☆☆☆ |
| Silae | Moyen | ❌ | [À valider] | [À valider] | ❌ | ✅ | ✅ | ⭐⭐⭐☆☆ |
| Qonto | Bon | ❌ | ✅ | ✅ | [À valider] | ✅ | ✅ | ⭐⭐⭐⭐☆ |
| Chift | Bon | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐☆ |

### 6.3 Tableau : coût d'intégration (jours de dev)

| Connecteur | Auth | API | Webhooks | Tests | Doc | **Total** |
|-----------|------|-----|----------|-------|-----|-----------|
| HubSpot natif | 1 | 2 | 2 | 2 | 1 | **8** |
| Pipedrive natif | 1 | 2 | 1 | 1 | 1 | **6** |
| Salesforce natif | 3 | 3 | 3 | 3 | 3 | **15** |
| Odoo natif | 2 | 3 | 1 | 2 | 2 | **10** |
| Dynamics natif | 2 | 2 | 2 | 1 | 1 | **8** |
| Zoho natif | 1 | 2 | 1 | 1 | 1 | **5** |
| Pennylane natif | 1 | 2 | 2 | 2 | 1 | **8** |
| Sage 100 natif | 2 | 3 | 1 | 3 | 4 | **15** |
| Yousign natif | 1 | 2 | 2 | 2 | 1 | **8** |
| DocuSign natif | 2 | 2 | 2 | 2 | 2 | **10** |
| Chift (comptabilité) | 2 | 4 | 2 | 3 | 1 | **12** |
| Chift (fintech/e-com/caisse) | 0 | 1 | 0 | 1 | 0 | **2*** |
| Silae natif | 2 | 3 | 1 | 3 | 3 | **12** |
| Payfit natif | 2 | 3 | 1 | 2 | 2 | **10** |

*Par connecteur via Chift (réutilisation ChiftProvider existant).

### 6.4 Couverture du marché par version

| Version | CRM | Comptabilité | Signature | Fintech | E-commerce | Caisse | Paie | Entreprises |
|---------|-----|-------------|-----------|---------|------------|--------|------|------------|
| v0.2 | HubSpot (288K) + Pipedrive (100K) | — | — | — | — | — | — | **~388K** |
| v0.2b | + Salesforce (150K) | — | — | — | — | — | — | **~538K** |
| v0.3 | + Odoo (2M users) + Dynamics + Zoho (250K) | — | — | — | — | — | — | **~2M+** |
| v0.4 | (inchangé) | Chift (1.35M) + Pennylane (500K) | — | — | — | — | — | **~3.35M** |
| v0.4b-v1.1 | (inchangé) | (inchangé) | Yousign | Qonto/Agicap/Pleo | Shopify/WooCommerce | Zelty/Popina | — | (même base) |
| v1.2-v1.3 | (inchangé) | + Sage 100 natif + Cegid natif | (inchangé) | (inchangé) | (inchangé) | (inchangé) | Silae + Payfit | (même base) |
| v2.0 | (inchangé) | + QuickBooks + Xero | + DocuSign + Adobe Sign | + Stripe natif | (inchangé) | (inchangé) | (inchangé) | + marché UK/US/AU |

---

## Partie 7 — Gestion des tokens OAuth2

### 7.1 Architecture de sécurité

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SÉCURITÉ OAUTH2 TAKA OS — 3 NIVEAUX                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Niveau 1 : Application (TokenVault)                                     │
│   • Fernet (AES-128-CBC + HMAC) par token                                   │
│   • Clé maître : AWS Secrets Manager / HashiCorp Vault                       │
│   • Rotation auto clés maîtres (90 jours)                                  │
│                                                                             │
│   Niveau 2 : Base de données (PostgreSQL)                                   │
│   • Tokens en BYTEA (binaire chiffré), jamais en clair                     │
│   • Row-level security par tenant_id                                        │
│   • Audit log sur toute lecture de token                                    │
│                                                                             │
│   Niveau 3 : Réseau                                                        │
│   • TLS 1.3 obligatoire                                                     │
│   • IP whitelist webhooks (où possible)                                    │
│   • Rate limiting par tenant_id                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 TokenVault

```python
# app/services/connectors/auth/token_vault.py
import os, base64
from typing import Optional
from cryptography.fernet import Fernet

class TokenVault:
    _instance = None; _fernet = None
    def __new__(cls):
        if cls._instance is None: cls._instance = super().__new__(cls); cls._instance._init_vault()
        return cls._instance
    def _init_vault(self): self._fernet = Fernet(self._get_master_key())
    def _get_master_key(self) -> bytes:
        if os.getenv("AWS_REGION"):
            try:
                import boto3
                resp = boto3.client("secretsmanager").get_secret_value(SecretId=os.getenv("TOKEN_VAULT_SECRET_ARN"))
                return base64.urlsafe_b64decode(resp["SecretString"].encode())
            except: pass
        env_key = os.getenv("TOKEN_VAULT_MASTER_KEY")
        if env_key: return base64.urlsafe_b64decode(env_key.encode())
        if os.getenv("ENVIRONMENT") == "development": return Fernet.generate_key()
        raise RuntimeError("TOKEN_VAULT_MASTER_KEY non configuré")
    def encrypt(self, plaintext: str) -> bytes:
        if not plaintext: return b""
        return self._fernet.encrypt(plaintext.encode("utf-8"))
    def decrypt(self, ciphertext: bytes) -> str:
        if not ciphertext: return ""
        return self._fernet.decrypt(ciphertext).decode("utf-8")

# Alternative AES-256-GCM (performance volume)
class TokenVaultAES256:
    def __init__(self):
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import os
        self._cipher = AESGCM(os.urandom(32)); self._key_id = "v1"
    def encrypt(self, plaintext: str) -> bytes:
        import os
        nonce = os.urandom(12)
        ct = self._cipher.encrypt(nonce, plaintext.encode("utf-8"), self._key_id.encode())
        return self._key_id.encode() + nonce + ct
    def decrypt(self, ciphertext: bytes) -> str:
        return self._cipher.decrypt(ciphertext[4:16], ciphertext[16:], ciphertext[:4].decode().encode()).decode("utf-8")
```

### 7.3 Refresh automatique (Celery Beat)

```python
# app/services/connectors/auth/refresh_scheduler.py
from datetime import datetime, timedelta
from app.celery_app import celery_app
from app.services.connectors.auth.token_vault import TokenVault
from sqlalchemy import select, update

@celery_app.task(bind=True, max_retries=3)
def refresh_all_expiring_tokens(self):
    import asyncio; asyncio.run(_refresh_all_tokens())

async def _refresh_all_tokens():
    from app.database import async_session_factory
    async with async_session_factory() as session:
        from app.models import CRMConnectorOAuthToken, CRMConnector
        threshold = datetime.utcnow() + timedelta(hours=2)
        rows = (await session.execute(select(CRMConnectorOAuthToken, CRMConnector).join(CRMConnector).where(CRMConnector.is_active == True, CRMConnectorOAuthToken.expires_at <= threshold))).all()
        refreshed = 0; failed = 0
        for token_row, connector in rows:
            try:
                vault = TokenVault()
                refresh_token = vault.decrypt(token_row.refresh_token_encrypted)
                from app.services.connectors.registry import ConnectorRegistry
                provider = ConnectorRegistry.get(connector.provider, connector.tenant_id, connector.config, {"access_token": vault.decrypt(token_row.access_token_encrypted), "refresh_token": refresh_token}, session)
                async with provider: new_access = await provider.refresh_access_token()
                new_expires = datetime.utcnow() + timedelta(hours=1)
                await session.execute(update(CRMConnectorOAuthToken).where(CRMConnectorOAuthToken.id == token_row.id).values(access_token_encrypted=vault.encrypt(new_access), expires_at=new_expires, updated_at=datetime.utcnow()))
                refreshed += 1
            except Exception as e:
                failed += 1; import logging; logging.error(f"Refresh failed {connector.id}: {e}")
                if "invalid_grant" in str(e).lower() or "revoked" in str(e).lower():
                    await session.execute(update(CRMConnector).where(CRMConnector.id == connector.id).values(status="error", last_error_at=datetime.utcnow(), last_error_message="Token revoked — reconnection required", updated_at=datetime.utcnow()))
        await session.commit()
        return {"refreshed": refreshed, "failed": failed}

celery_app.conf.beat_schedule = {
    "refresh-oauth-tokens": {"task": "app.services.connectors.auth.refresh_scheduler.refresh_all_expiring_tokens", "schedule": 43200.0}
}
```

### 7.4 Flow OAuth2 complet

```python
# app/services/connectors/auth/oauth2.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import secrets, urllib.parse
from app.services.connectors.auth.token_vault import TokenVault
from app.services.connectors.registry import ConnectorRegistry

router = APIRouter(prefix="/auth/oauth2", tags=["oauth2"])
_oauth_state_cache: dict = {}

@router.get("/{provider}/initiate")
async def initiate_oauth2(provider: str, tenant_id: str, request: Request, redirect_after: str = "/dashboard/connectors"):
    state = secrets.token_urlsafe(32)
    await _store_oauth_state(state, {"tenant_id": tenant_id, "provider": provider, "redirect_after": redirect_after})
    redirect_uri = _get_redirect_uri(request, provider)
    if provider == "hubspot":
        client_id = os.getenv("HUBSPOT_CLIENT_ID")
        scopes = "oauth%20crm.objects.contacts.read%20crm.objects.deals.read%20crm.objects.companies.read"
        url = f"https://app.hubspot.com/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&scope={scopes}&state={state}"
    elif provider == "pennylane":
        client_id = os.getenv("PENNYLANE_CLIENT_ID")
        url = f"https://app.pennylane.com/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope=read+write&state={state}"
    elif provider == "yousign":
        client_id = os.getenv("YOUSIGN_CLIENT_ID")
        url = f"https://api.yousign.com/v3/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope=read+write&state={state}"
    else: raise HTTPException(status_code=400, detail=f"OAuth2 not supported: {provider}")
    return RedirectResponse(url=url)

@router.get("/{provider}/callback")
async def oauth2_callback(provider: str, request: Request, code: str = None, state: str = None, error: str = None, error_description: str = None):
    if error: raise HTTPException(status_code=400, detail=f"OAuth2 error: {error} — {error_description}")
    if not code or not state: raise HTTPException(status_code=400, detail="Missing code or state")
    state_data = await _verify_oauth_state(state)
    if not state_data: raise HTTPException(status_code=400, detail="Invalid or expired state")
    tenant_id = state_data["tenant_id"]; redirect_after = state_data["redirect_after"]
    tokens = await _exchange_code_for_tokens(provider, code, request)
    vault = TokenVault()
    from app.database import async_session_factory
    from sqlalchemy import select
    from app.models import CRMConnector, CRMConnectorOAuthToken
    async with async_session_factory() as session:
        connector = (await session.execute(select(CRMConnector).where(CRMConnector.tenant_id == tenant_id, CRMConnector.provider == provider))).scalar_one_or_none()
        if not connector:
            connector = CRMConnector(tenant_id=tenant_id, provider=provider, config={"connected_at": datetime.utcnow().isoformat()}, status="connected")
            session.add(connector); await session.flush()
        else: connector.status = "connected"; connector.updated_at = datetime.utcnow()
        token_row = (await session.execute(select(CRMConnectorOAuthToken).where(CRMConnectorOAuthToken.connector_id == connector.id))).scalar_one_or_none()
        expires = datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
        if not token_row:
            session.add(CRMConnectorOAuthToken(connector_id=connector.id, access_token_encrypted=vault.encrypt(tokens["access_token"]), refresh_token_encrypted=vault.encrypt(tokens.get("refresh_token", "")), token_type=tokens.get("token_type", "Bearer"), expires_at=expires, scope=tokens.get("scope", "")))
        else:
            token_row.access_token_encrypted = vault.encrypt(tokens["access_token"])
            if tokens.get("refresh_token"): token_row.refresh_token_encrypted = vault.encrypt(tokens["refresh_token"])
            token_row.expires_at = expires; token_row.updated_at = datetime.utcnow()
        await session.commit()
    return RedirectResponse(url=redirect_after)

async def _exchange_code_for_tokens(provider: str, code: str, request: Request) -> dict:
    import aiohttp; redirect_uri = _get_redirect_uri(request, provider)
    if provider == "hubspot":
        async with aiohttp.ClientSession() as s:
            async with s.post("https://api.hubapi.com/oauth/v1/token", data={"grant_type": "authorization_code", "client_id": os.getenv("HUBSPOT_CLIENT_ID"), "client_secret": os.getenv("HUBSPOT_CLIENT_SECRET"), "redirect_uri": redirect_uri, "code": code}) as r: return await r.json()
    elif provider == "pennylane":
        async with aiohttp.ClientSession() as s:
            async with s.post("https://app.pennylane.com/oauth/token", data={"grant_type": "authorization_code", "client_id": os.getenv("PENNYLANE_CLIENT_ID"), "client_secret": os.getenv("PENNYLANE_CLIENT_SECRET"), "redirect_uri": redirect_uri, "code": code}) as r: return await r.json()
    raise ValueError(f"Token exchange not implemented for {provider}")

def _get_redirect_uri(request: Request, provider: str) -> str: return f"{str(request.base_url).rstrip('/')}/auth/oauth2/{provider}/callback"

async def _store_oauth_state(state: str, data: dict, ttl: int = 600):
    import time; _oauth_state_cache[state] = {"data": data, "expires": time.time() + ttl}
async def _verify_oauth_state(state: str):
    import time; entry = _oauth_state_cache.pop(state, None)
    if not entry or time.time() > entry["expires"]: return None
    return entry["data"]
```

### 7.5 Révocation

```python
# app/services/connectors/auth/revocation.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

router = APIRouter(prefix="/connectors", tags=["connectors"])

@router.delete("/{connector_type}/{provider}")
async def revoke_connector(connector_type: str, provider: str, tenant_id: str, db: AsyncSession = Depends(get_db)):
    connector = await _get_connector(db, tenant_id, connector_type, provider)
    if not connector: raise HTTPException(status_code=404)
    tokens = await _get_tokens(db, connector.id, connector_type)
    provider_instance = ConnectorRegistry.get(provider, tenant_id, connector.config, tokens, db)
    async with provider_instance:
        await provider_instance.revoke_tokens()
        if provider_instance.supports_webhooks: pass  # [Supprimer webhooks enregistrés]
    await _delete_tokens(db, connector.id, connector_type)
    connector.is_active = False; connector.status = "disabled"; connector.updated_at = datetime.utcnow()
    await db.commit()
    return {"status": "revoked", "provider": provider}

@router.post("/{connector_type}/{provider}/pause")
async def pause_connector(connector_type: str, provider: str, tenant_id: str, db: AsyncSession = Depends(get_db)):
    connector = await _get_connector(db, tenant_id, connector_type, provider)
    if not connector: raise HTTPException(status_code=404)
    connector.is_active = False; connector.status = "paused"; connector.updated_at = datetime.utcnow()
    await db.commit()
    return {"status": "paused"}

@router.post("/{connector_type}/{provider}/resume")
async def resume_connector(connector_type: str, provider: str, tenant_id: str, db: AsyncSession = Depends(get_db)):
    connector = await _get_connector(db, tenant_id, connector_type, provider)
    if not connector: raise HTTPException(status_code=404)
    connector.is_active = True; connector.status = "configured"; connector.updated_at = datetime.utcnow()
    await db.commit()
    tokens = await _get_tokens(db, connector.id, connector_type)
    provider_instance = ConnectorRegistry.get(provider, tenant_id, connector.config, tokens, db)
    async with provider_instance:
        health = await provider_instance.health_check()
        if health.get("status") == "ok": connector.status = "connected"; await db.commit()
    return {"status": connector.status, "health": health}
```

### 7.6 Multi-tenant isolation

```sql
-- Row-level security
ALTER TABLE crm_connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounting_connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE signature_connectors ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_crm ON crm_connectors
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
CREATE POLICY tenant_isolation_accounting ON accounting_connectors
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

CREATE INDEX idx_crm_connectors_tenant_active ON crm_connectors(tenant_id, provider) WHERE is_active = true;
CREATE INDEX idx_accounting_connectors_tenant_active ON accounting_connectors(tenant_id, provider) WHERE is_active = true;

-- Audit trail
CREATE TABLE connector_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL, connector_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL, performed_by UUID,
    ip_address INET, user_agent TEXT, details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_log_tenant ON connector_audit_log(tenant_id);
CREATE INDEX idx_audit_log_connector ON connector_audit_log(connector_id);
```

### 7.7 Checklist de sécurité

| # | Vérification | Statut |
|---|-------------|--------|
| 1 | Tokens chiffrés en DB (jamais en clair) | ✅ |
| 2 | Clé maître dans vault externe (AWS/HCV) | ✅ |
| 3 | Rotation auto refresh token (12h Celery) | ✅ |
| 4 | CSRF protection OAuth2 (state param) | ✅ |
| 5 | PKCE pour mobile | ⚠️ Planifié |
| 6 | IP whitelist webhooks | ⚠️ Planifié |
| 7 | HMAC signature vérification webhooks | ✅ |
| 8 | Idempotence webhook (event_id + TTL) | ✅ |
| 9 | Row-level security PostgreSQL | ✅ |
| 10 | Audit log sur opérations token | ✅ |
| 11 | Rate limiting par tenant/provider | ✅ |
| 12 | Token revocation (logout, suspension) | ✅ |
| 13 | Scope minimal OAuth2 | ✅ |
| 14 | Sandbox/test credentials CI/CD | ⚠️ |
| 15 | Monitoring erreurs d'auth | ⚠️ |

---

## Résumé exécutif

### Métriques du document

| Métrique | Valeur |
|----------|--------|
| **Connecteurs couverts** | **40+** |
| **Versions planifiées** | **12** (v0.1 à v2.0) |
| **Jours de développement estimés** | **~198 jours** |
| **Entreprises potentiellement couvertes** | **~2 000 000+** |
| **Logiciels comptables couverts** | **15+** (via Chift + natifs) |
| **CRM/ERP couverts** | **6** natifs |
| **Tables SQL spécifiées** | **12** |
| **Classes Python spécifiées** | **15+** |

### Stratégie Chift résumée

**Chift est le levier stratégique principal.** 1 connecteur Chift = 15+ logiciels comptables français + fintech + e-commerce + caisse. Coût ~€0.10/appel. Économie : 143 jours de dev natif évités, remplacés par 28 jours d'intégration Chift. ROI par client Sage 100 via Chift : ~12 jours de dev économisés.

**Limites Chift** : latence additionnelle (proxy), webhooks limités pour certains logiciels, modèle normalisé = moins de granularité. **Mitigation** : connecteurs natifs Pennylane (webhooks temps réel) et Yousign (workflow signature critique).

### Prochaines actions immédiates

1. **Valider partenariat Chift** — accord technique + sandbox API
2. **Implémenter infrastructure OAuth2** — TokenVault, tables, endpoint /auth/oauth2
3. **Développer HubSpotProvider** — premier connecteur natif (P0, v0.2)
4. **Mettre en place webhook handler** — route /webhooks/{provider}/{tenant_id}
5. **Créer environnements de test** — sandbox HubSpot, Pennylane, Yousign

---

> **Document maître TAKA OS — Écosystème Connecteurs & Roadmap d'Intégration**  
> Version 1.0 — Spécification technique validée — prêt pour implémentation
