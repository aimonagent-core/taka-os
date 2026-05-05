# TAKA OS — Analyse gRPC vs REST pour Connecteurs GRC/CRM/ERP
## Réponse CTO | Architecture interne vs APIs tierces | Mai 2026

---

## 1. Verdict en 10 secondes

| Usage | Protocole | Recommandation |
|-------|-----------|---------------|
| **APIs externes GRC** (HubSpot, Salesforce, Odoo, Sage) | REST/JSON (imposé par les APIs tierces) | REST — seul choix possible |
| **Communication interne TAKA** (Agent ↔ Agent, Agent ↔ Kernel) | REST/JSON actuel | REST suffisant en v0.x |
| **Streaming temps réel** (notifications, WebSocket) | WebSocket (Socket.io) | Pertinent pour v0.3+ |
| **Microservices TAKA** (v1.0+, scaling horizontal) | gRPC ou REST | gRPC envisageable alors |

**gRPC n'est PAS pertinent pour TAKA OS avant v1.0.**

---

## 2. Pourquoi gRPC n'est PAS pertinent maintenant

### 2.1 Les APIs GRC tierces sont toutes REST/JSON

| GRC/CRM/ERP | API Offerte | Protocole | gRPC Disponible ? |
|-------------|------------|-----------|-----------------|
| **HubSpot** | REST API v3 | HTTPS/JSON | ❌ Non |
| **Salesforce** | REST API + SOAP | HTTPS/JSON/XML | ❌ Non |
| **Odoo** | JSON-RPC + XML-RPC | HTTP/JSON | ❌ Non |
| **Pipedrive** | REST API | HTTPS/JSON | ❌ Non |
| **Sage Business Cloud** | REST partielle | HTTPS/JSON | ❌ Non |
| **Pennylane** | REST API | HTTPS/JSON | ❌ Non |
| **Zoho CRM** | REST API | HTTPS/JSON | ❌ Non |
| **QuickBooks** | REST API | HTTPS/JSON | ❌ Non |
| **SAP** | OData/REST | HTTPS/JSON | ❌ Non (rare) |
| **Chift** | REST API unifiée | HTTPS/JSON | ❌ Non |

**100% des APIs GRC/CRM/ERP sont REST/JSON.** Impossible de les appeler en gRPC.

### 2.2 gRPC complexifie sans bénéfice pour une équipe de 1-2 personnes

| Aspect | REST/JSON + FastAPI | gRPC + Protobuf |
|--------|--------------------|-----------------|
| **Setup** | `pip install fastapi httpx` — 2 min | `pip install grpcio protobuf` + protoc compiler — 30 min |
| **Debug** | cURL, browser, Swagger UI — instantané | grpcurl ou proxy — complexe |
| **Lecture** | JSON lisible humainement | Binaire protobuf — illisible |
| **Type safety** | Pydantic — validation auto | Protobuf — strict mais rigidifie |
| **Documentation** | Swagger auto-généré | Nécessite gRPC Gateway + OpenAPI proxy |
| **Frontend** | Natif avec fetch/axios | Requiert gRPC-Web + proxy (complexité) |
| **Formation** | FastAPI = standard Python | gRPC = courbe d'apprentissage |

### 2.3 Quand gRPC DEVIENT pertinent

| Condition | Notre situation v0.1-v0.5 | Seuil gRPC |
|-----------|----------------------|-----------|
| Microservices | Monolithe FastAPI | v1.0+ (si décomposition) |
| Haute performance interne | <100 req/s | >1000 req/s internes |
| Streaming bidirectionnel | Polling HTTP suffisant | WebSocket suffit pour notifications |
| Polyglotte (multi-langage) | Python uniquement | Si on ajoute Go/Rust |
| Network haute latence | VPS local | Multi-région |

**Conclusion :** Aucune condition gRPC n'est remplie avant v1.0.

---

## 3. Ce qui est pertinent à la place

### 3.1 REST/JSON natif — Pour TOUT

```python
# Client HTTP interne (httpx) — déjà dans notre stack
import httpx
from typing import Any

class TAKAClient:
    """Client HTTP interne pour tous les appels API.
    
    Que ce soit:
    - API interne TAKA (agent ↔ agent)
    - API tierce HubSpot/Salesforce/Odoo
    - API places de marché BOAMP/TED
    """
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            http2=True  # HTTP/2 activé pour performance
        )
    
    async def call(
        self,
        method: str,
        path: str,
        json: dict = None,
        headers: dict = None
    ) -> dict[str, Any]:
        """Appel API universel REST/JSON."""
        response = await self.client.request(
            method=method,
            url=path,
            json=json,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

# Usage: API interne
agent_client = TAKAClient("http://localhost:8000/api/v1")

# Usage: API externe HubSpot
hubspot_client = TAKAClient(
    "https://api.hubapi.com",
    headers={"Authorization": f"Bearer {token}"}
)

# Usage: API externe Odoo
odoo_client = TAKAClient(
    "https://mon-odoo.odoo.com/jsonrpc",
    headers={"Content-Type": "application/json"}
)
```

**Un seul client HTTP pour tout.** Pas de gRPC nécessaire.

### 3.2 WebSocket / Socket.io — Pour le temps réel (v0.3)

Quand on aura besoin de notifications temps réel (pas polling) :

| Usage | Technologie | Quand |
|-------|-----------|-------|
| Notifications in-app | WebSocket (FastAPI native) | v0.3 |
| Parsing progress (barre de progression) | Server-Sent Events (SSE) | v0.2 |
| Chat agent-human | WebSocket | v0.5 |
| Dashboard temps réel | Server-Sent Events | v0.3 |

```python
# FastAPI WebSocket natif — pas besoin de gRPC streaming
from fastapi import WebSocket

@app.websocket("/ws/notifications/{tenant_id}")
async def notifications(websocket: WebSocket, tenant_id: int):
    await websocket.accept()
    while True:
        event = await event_bus.wait_for(tenant_id)
        await websocket.send_json(event.to_dict())
```

### 3.3 HTTP/2 — Déjà activé avec httpx + Uvicorn

```python
# Uvicorn avec HTTP/2
# docker-compose.yml
# web (Nginx) → proxy HTTP/2 vers app (Uvicorn)
# httpx.AsyncClient(http2=True) côté client
```

**On a déjà 80% des bénéfices gRPC (multiplexage, compression headers) sans la complexité.**

---

## 4. Architecture REST proposée pour les connecteurs GRC

```
┌─────────────────────────────────────────────────────────────────┐
│  TAKA OS — Connecteurs GRC/CRM/ERP (Architecture REST/JSON)       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  TAKA API (FastAPI + Uvicorn + HTTP/2)                  │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐  │    │
│  │  │ Tenders │ │ Agents  │ │ Memory  │ │ GRC Bridge  │  │    │
│  │  │  REST   │ │  REST   │ │  REST   │ │   REST      │  │    │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └──────┬──────┘  │    │
│  │       │           │           │              │         │    │
│  │       └───────────┴───────────┴──────────────┘         │    │
│  │                      │                                 │    │
│  │               EventBus (asyncio / Redis v1.0)          │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                       │
│  ┌──────────────────────┼──────────────────────────────────┐     │
│  │  CONNECTEURS EXTERNES (tous REST/JSON via httpx)      │     │
│  │                                                        │     │
│  │  HubSpot API      ────►  https://api.hubapi.com        │     │
│  │  Salesforce API   ────►  https://{instance}.salesforce │     │
│  │  Odoo JSON-RPC    ────►  https://{instance}.odoo.com   │     │
│  │  Pipedrive API    ────►  https://{company}.pipedrive   │     │
│  │  Sage API         ────►  https://api.sage.com          │     │
│  │  Pennylane API    ────►  https://api.pennylane.com     │     │
│  │  Chift API        ────►  https://api.chift.eu          │     │
│  │  QuickBooks API   ────►  https://quickbooks.api.intuit │     │
│  │                                                        │     │
│  │  ┌─────────────┐                                       │     │
│  │  │ BOAMP/TED   │  (API places de marché — même stack)   │     │
│  │  └─────────────┘                                       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  OAUTH2 / JWT  (authentification universelle)            │   │
│  │  ├─ Authorization Code Flow (HubSpot, Salesforce...)     │   │
│  │  ├─ API Token (Pipedrive, Odoo...)                       │   │
│  │  └─ OAuth2 + Refresh Token (tous les SaaS modernes)      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  WEBHOOKS  (notifications temps réel des GRC)            │   │
│  │  ├─ HubSpot webhook → /webhooks/hubspot/{tenant_id}      │   │
│  │  ├─ Odoo webhook    → /webhooks/odoo/{tenant_id}         │   │
│  │  ├─ Pipedrive webhook → /webhooks/pipedrive/{tenant_id}  │   │
│  │  └─ Chift webhook → /webhooks/chift/{tenant_id}          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.1 GRC Bridge — L'abstraction interne

```python
# app/services/grc_bridge.py
from abc import ABC, abstractmethod
from typing import Any

class GRCProvider(ABC):
    """Interface abstraite pour TOUS les connecteurs GRC.
    
    Chaque provider implémente REST/JSON selon son API.
    TAKA parle "GRCProvider", pas "HubSpot" ou "Odoo".
    """
    
    @abstractmethod
    async def get_deals(self, status: str = "open") -> list[dict]:
        """Récupère les deals/projets actifs."""
        pass
    
    @abstractmethod
    async def get_contacts(self, region: str = None) -> list[dict]:
        """Récupère les contacts/clients."""
        pass
    
    @abstractmethod
    async def get_resources(self) -> dict:
        """Récupère les ressources (stock, employés, capacité)."""
        pass
    
    @abstractmethod
    async def create_deal(self, data: dict) -> dict:
        """Crée un deal/projet à partir d'un AO gagné."""
        pass
    
    @abstractmethod
    async def create_task(self, deal_id: str, title: str, due_date: str) -> dict:
        """Crée une tâche liée à un deal."""
        pass


class HubSpotProvider(GRCProvider):
    """Implémentation HubSpot via REST API."""
    
    BASE_URL = "https://api.hubapi.com"
    
    def __init__(self, access_token: str):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            http2=True,
            timeout=30.0
        )
    
    async def get_deals(self, status: str = "open") -> list[dict]:
        """GET /crm/v3/objects/deals?properties=dealname,amount,dealstage"""
        response = await self.client.get(
            "/crm/v3/objects/deals",
            params={
                "properties": "dealname,amount,dealstage,closedate",
                "limit": 100
            }
        )
        response.raise_for_status()
        data = response.json()
        # Filtrer par status
        deals = [
            {
                "id": deal["id"],
                "name": deal["properties"]["dealname"],
                "amount": float(deal["properties"].get("amount", 0)),
                "stage": deal["properties"].get("dealstage", ""),
            }
            for deal in data.get("results", [])
            if self._stage_matches(deal["properties"].get("dealstage", ""), status)
        ]
        return deals
    
    async def create_deal(self, data: dict) -> dict:
        """POST /crm/v3/objects/deals"""
        payload = {
            "properties": {
                "dealname": data["title"],
                "amount": str(data["amount"]),
                "dealstage": "appointmentscheduled",  # Premier stage
                "pipeline": data.get("pipeline", "default"),
                "closedate": data.get("deadline", ""),
            }
        }
        response = await self.client.post("/crm/v3/objects/deals", json=payload)
        response.raise_for_status()
        return response.json()


class OdooProvider(GRCProvider):
    """Implémentation Odoo via JSON-RPC."""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.client = httpx.AsyncClient(http2=True, timeout=30.0)
    
    async def _authenticate(self) -> int:
        """JSON-RPC authenticate."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self.db, self.username, self.password, {}]
            }
        }
        response = await self.client.post(f"{self.url}/jsonrpc", json=payload)
        data = response.json()
        self.uid = data["result"]
        return self.uid
    
    async def get_deals(self, status: str = "open") -> list[dict]:
        """project.project (projets Odoo)."""
        if not self.uid:
            await self._authenticate()
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self.db, self.uid, self.password,
                    "project.project", "search_read",
                    [[["stage_id", "!=", "Done"]]],  # Filtre status
                    {"fields": ["name", "partner_id", "date_start", "date_end"]}
                ]
            }
        }
        response = await self.client.post(f"{self.url}/jsonrpc", json=payload)
        data = response.json()
        return [
            {
                "id": proj["id"],
                "name": proj["name"],
                "client": proj.get("partner_id", [None, ""])[1],
                "start": proj.get("date_start"),
                "end": proj.get("date_end"),
            }
            for proj in data.get("result", [])
        ]
```

### 4.2 GRC Sync Service

```python
# app/services/grc/sync.py
class GRCSyncService:
    """Service de synchronisation GRC ↔ TAKA.
    
    Polling toutes les 60 min + webhooks temps réel.
    """
    
    SYNC_INTERVAL = 60  # minutes
    
    async def sync_tenant(self, tenant_id: int):
        """Synchronise tous les connecteurs GRC d'un tenant."""
        connectors = await self.get_active_connectors(tenant_id)
        
        for connector in connectors:
            try:
                provider = self._create_provider(connector)
                
                # 1. Récupérer données GRC
                deals = await provider.get_deals(status="open")
                contacts = await provider.get_contacts()
                resources = await provider.get_resources()
                
                # 2. Stocker dans cache TAKA
                await self._cache_data(tenant_id, connector.provider, {
                    "deals": deals,
                    "contacts": contacts,
                    "resources": resources,
                })
                
                # 3. Marquer comme synchronisé
                await self._mark_synced(connector.id, "success")
                
            except Exception as e:
                await self._mark_synced(connector.id, "error", str(e))
                logger.error(f"GRC sync failed for {connector.provider}: {e}")
    
    async def handle_webhook(self, provider: str, tenant_id: int, payload: dict):
        """Traite un webhook temps réel d'un GRC."""
        # HubSpot webhook: deal.updated
        # Odoo webhook: project.created
        # etc.
        
        event_type = payload.get("event_type")
        
        if event_type == "deal.updated":
            await self._update_cached_deal(tenant_id, payload["deal_id"])
        elif event_type == "contact.created":
            await self._update_cached_contacts(tenant_id)
        
        # Notifier les agents concernés via EventBus
        await event_bus.publish(
            TakaEvent(
                type=EventType.GRC_DATA_CHANGED,
                tenant_id=tenant_id,
                payload={"provider": provider, "event": event_type}
            )
        )
```

### 4.3 Scoring enrichi par GRC (REST interne)

```python
# app/services/qualification/grc_enrichment.py
class GRCEnrichmentService:
    """Enrichit le scoring avec données GRC synchronisées."""
    
    async def enrich_scoring(
        self,
        tender: Tender,
        tenant_id: int
    ) -> dict:
        """Retourne des facteurs d'enrichissement pour le scoring."""
        
        cache = await self._get_grc_cache(tenant_id)
        factors = []
        
        # 1. Capacité projet
        active_deals = cache.get("deals", [])
        active_count = len([d for d in active_deals if d["status"] == "open"])
        
        if active_count > 5:
            factors.append({
                "type": "capacity",
                "impact": -0.15,
                "reason": f"{active_count} projets en cours — capacité saturée"
            })
        elif active_count < 2:
            factors.append({
                "type": "capacity",
                "impact": +0.05,
                "reason": "Capacité disponible — ressources libres"
            })
        
        # 2. Client dans région
        contacts = cache.get("contacts", [])
        region_clients = [
            c for c in contacts
            if c.get("region") == tender.region_code
        ]
        if region_clients:
            factors.append({
                "type": "proximity",
                "impact": +0.10,
                "reason": f"{len(region_clients)} client(s) dans la région {tender.region_code}"
            })
        
        # 3. Historique CPV
        historical_deals = [
            d for d in active_deals
            if d.get("cpv_code") == tender.cpv_code
        ]
        won_count = len([d for d in historical_deals if d["status"] == "won"])
        total_count = len(historical_deals)
        
        if total_count > 0:
            win_rate = won_count / total_count
            if win_rate > 0.7:
                factors.append({
                    "type": "history",
                    "impact": +0.08,
                    "reason": f"Historique positif : {win_rate:.0%} de réussite sur CPV {tender.cpv_code}"
                })
            elif win_rate < 0.3:
                factors.append({
                    "type": "history",
                    "impact": -0.10,
                    "reason": f"Historique négatif : {win_rate:.0%} de réussite sur CPV {tender.cpv_code}"
                })
        
        return {
            "factors": factors,
            "total_impact": sum(f["impact"] for f in factors),
            "data_freshness": cache.get("synced_at")
        }
```

---

## 5. Quand gRPC DEVIENDRA pertinent (v1.0+)

| Condition | Situation v1.0+ | Architecture |
|-----------|----------------|-------------|
| **Microservices** | TAKA décomposé : API Gateway + Auth Service + Agent Service + Memory Service + GRC Service | gRPC entre services internes |
| **High throughput interne** | >1000 messages/sec EventBus | gRPC streaming |
| **Multi-langage** | Service en Go (performance) + Python (logique) | gRPC (polyglotte) |
| **Mobile natif** | App mobile TAKA (Flutter/React Native) | gRPC-Web via proxy |

**Architecture v1.0+ (si on y arrive) :**

```
┌────────────────────────────────────────────────────────────┐
│  API Gateway (FastAPI / Nginx)                              │
│  REST/JSON public + gRPC interne                            │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  gRPC  ┌─────────────┐  gRPC  ┌──────────┐│
│  │ Auth        │◄──────►│ Agent       │◄──────►│ Memory   ││
│  │ Service     │        │ Service     │        │ Service  ││
│  │ (Python)    │        │ (Python)    │        │ (Python) ││
│  └─────────────┘        └─────────────┘        └──────────┘│
│         │                      │                      │      │
│         └──────────────────────┴──────────────────────┘      │
│                           │                                  │
│                    gRPC / Redis EventBus                     │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  REST  ┌─────────────┐  REST  ┌──────────┐│
│  │ GRC Bridge  │◄──────►│ HubSpot API │◄──────►│ Odoo API ││
│  │ (Python)    │        │ (REST/JSON) │        │(JSON-RPC)││
│  └─────────────┘        └─────────────┘        └──────────┘│
│  (Les APIs tierces restent REST — imposé)                    │
└────────────────────────────────────────────────────────────┘
```

**Mais pour l'instant : REST/JSON partout. C'est simple, ça marche, c'est standard.**

---

## 6. Résumé — Pourquoi REST/JSON est le bon choix pour TAKA OS

| Critère | REST/JSON | gRPC | Verdict |
|---------|-----------|------|---------|
| **APIs tierces** | 100% support | 0% support | REST gagne |
| **Setup temps** | 2 minutes | 30 minutes | REST gagne |
| **Debug** | cURL, Swagger | grpcurl, proxy | REST gagne |
| **Lisibilité** | JSON humain | Binaire | REST gagne |
| **Frontend** | Natif | gRPC-Web requis | REST gagne |
| **Équipe** | 1 personne maîtrise | Formation nécessaire | REST gagne |
| **Performance** | Suffisant (<1000 req/s) | Meilleur >1000 req/s | REST suffisant |
| **Streaming** | WebSocket/SSE | Natif | WebSocket suffit |
| **Polyglotte** | Possible (REST est universel) | Excellente | Pas besoin |

**Score : REST/JSON = 9/10 pour TAKA OS. gRPC = 3/10 avant v1.0.**

---

## 7. Ce qu'on fait maintenant

| # | Action | Quand | Qui |
|---|--------|-------|-----|
| 1 | **Garder REST/JSON pour tout** | Dès maintenant | Décision verrouillée |
| 2 | **Ajouter `http2=True` à httpx** | Sprint 0 | Kimi Code |
| 3 | **Implémenter GRC Bridge abstrait** | v0.2 (Semaine 5-6) | Kimi Code |
| 4 | **Connecteur HubSpot REST** | v0.2 | Kimi Code |
| 5 | **Connecteur Pipedrive REST** | v0.2 | Kimi Code |
| 6 | **Connecteur Odoo JSON-RPC** | v0.3 | Kimi Code |
| 7 | **Connecteur Chift REST** | v0.4 | Kimi Code |
| 8 | **Reconsidérer gRPC** | v1.0+ | Si microservices |

---

## 8. Message au CEO

> **"Tu as raison de questionner gRPC. C'est une technologie excellente — mais pas pour nous maintenant."
>
> REST/JSON est le standard universel des APIs SaaS. 100% des GRC/CRM/ERP l'utilisent. Notre stack FastAPI + httpx + HTTP/2 donne déjà 80% des bénéfices de gRPC sans la complexité.
>
> **On garde REST. On ajoute HTTP/2. On implémente les connecteurs GRC via REST/JSON dès v0.2. Et on reconsidérera gRPC en v1.0 si on décompose en microservices.**"

---

*Analyse produite par le CTO TAKA OS | Basée sur benchmarks APIs GRC 2026, architecture FastAPI, et contraintes équipe réduite | Mai 2026*
