# Plan : Validation Concept TAKA OS — Approche Vertical + Modèle Organisationnel

## Objectif
Valider le concept complet de TAKA OS — Vertical Appels d'Offres uniquement — avant tout développement.

## Livrables

### 1. Analyse Critique Approche Vertical Séparé
- TAKA OS - AO (soumissionnaire + acheteur) : version 1
- TAKA OS - Fiducial (expert-comptable) : version 2, dérivée de la v1
- Avantages et inconvénients détaillés

### 2. Modèle Organisationnel Complet (5 rôles)
- Éditeur (Super Admin)
- Client Soumissionnaire (Admin + Collaborateur)
- Client Acheteur Public (Admin + Collaborateur)
- Matrice de permissions détaillée

### 3. Flows Onboarding & Paramétrage
- Flow création instance (Éditeur)
- Flow onboarding soumissionnaire
- Flow onboarding acheteur public
- Flow paramétrage métier (règles, scoring, pipeline)
- Flow invitation collaborateurs

### 4. Interfaces par Rôle
- Dashboard Éditeur
- Dashboard Admin Soumissionnaire
- Dashboard Collaborateur Soumissionnaire
- Dashboard Admin Acheteur
- Dashboard Collaborateur Acheteur
- Parcours utilisateur détaillé

### 5. Architecture de Ségrégation
- Séparation données soumissionnaire vs acheteur
- Modèle multi-tenant avec 2 types de tenants
- Sécurité et isolation
