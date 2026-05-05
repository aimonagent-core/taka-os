# Section 4 — Frontend & DevOps

## Blueprint TAKA OS : OS Agentic Open Source pour Appels d'Offres

---

## 1. Architecture Frontend

### 1.a. Stack Technique Detaillee

| Couche | Technologie | Version | Justification |
|--------|-------------|---------|---------------|
| Framework | React | 18+ | Concurrent features, Suspense, performance |
| Langage | TypeScript | 5.3+ | Typage strict, DX, maintainabilite |
| Bundler | Vite | 5+ | HMR ultra-rapide, build optimisee, ESM natif |
| Styling | Tailwind CSS | 3.4+ | Utility-first, consistency design system, zero CSS mort |
| Composants | shadcn/ui | latest | Base Radix UI + theming Tailwind, accessible, copiables |
| State Global | Zustand | 4.5+ | Minimal, pas de boilerplate, TypeScript-first |
| Data Fetching | TanStack Query (React Query) | 5+ | Cache intelligent, invalidation, dedup, background refetch |
| Routing | React Router | v6 | Declaratif, lazy loading, protected routes |
| Formulaires | React Hook Form + Zod | 7+ / 3+ | Validation performante, typesafe, schema-driven |
| HTTP Client | Axios | 1.6+ | Intercepteurs JWT, retry logic, cancel tokens |
| Dates | date-fns | 3+ | Tree-shakeable, immutabilite, i18n ready |
| DnD | @dnd-kit/core | 6+ | Accessible, moderne, flexible (pipeline Kanban) |

**Contraintes de la stack :**
- Pas de Redux : Zustand suffit pour la complexite du state TAKA OS
- Pas de CSS Modules : Tailwind uniquement, pas de conflit de specificity
- Pas de MUI/Chakra : shadcn/ui pour le controle total du design system
- Pas de Next.js : SPA Vite suffisant, pas besoin de SSR pour un SaaS interne

### 1.b. Structure du Projet

```
frontend/
├── src/
│   ├── main.tsx                    # Point d'entree, providers
│   ├── App.tsx                     # Router, layouts, guards
│   ├── index.css                   # Tailwind directives + variables CSS
│   │
│   ├── components/                 # COMPOSANTS REUTILISABLES
│   │   ├── ui/                     # shadcn/ui (Button, Card, Dialog, etc.)
│   │   ├── layout/
│   │   │   ├── Layout.tsx          # Sidebar + Header + Content
│   │   │   ├── Sidebar.tsx         # Navigation verticale
│   │   │   ├── Header.tsx          # Top bar (titre, actions, profil)
│   │   │   └── MobileNav.tsx       # Navigation mobile (bottom bar)
│   │   ├── tenders/
│   │   │   ├── TenderCard.tsx      # Carte Kanban + liste
│   │   │   ├── TenderForm.tsx      # Formulaire creation/edition
│   │   │   ├── TenderTable.tsx     # Tableau AO (sortable, paginable)
│   │   │   └── TenderFilters.tsx   # Barre de filtres avances
│   │   ├── pipeline/
│   │   │   ├── PipelineBoard.tsx   # Plateau Kanban complet
│   │   │   ├── PipelineColumn.tsx  # Colonne (stage)
│   │   │   └── SortableTenderCard.tsx # Carte draggable
│   │   ├── qualification/
│   │   │   ├── QualificationBadge.tsx   # GO/NO-GO/MAYBE
│   │   │   ├── QualificationResult.tsx  # Barres de score detaille
│   │   │   └── QualificationTrigger.tsx # Bouton lancer agent
│   │   ├── shared/
│   │   │   ├── KPICard.tsx         # Carte KPI (dashboard)
│   │   │   ├── DeadlineBadge.tsx   # Badge deadline colore
│   │   │   ├── FileUploadZone.tsx  # Zone drag & drop
│   │   │   ├── SearchBar.tsx       # Recherche + filtres
│   │   │   ├── DataTable.tsx       # Table generique (tanstack-table)
│   │   │   ├── StatusBadge.tsx     # Badge generique (stage, statut)
│   │   │   ├── ConfirmDialog.tsx   # Dialog de confirmation
│   │   │   ├── EmptyState.tsx      # Etat vide illustre
│   │   │   └── LoadingSkeleton.tsx # Skeleton screens
│   │   └── memory/
│   │       ├── MemorySearch.tsx    # Input recherche semantique
│   │       └── MemoryResultCard.tsx # Card resultat memoire
│   │
│   ├── pages/                      # PAGES (1 page = 1 route)
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── TendersPage.tsx
│   │   ├── TenderDetailPage.tsx
│   │   ├── PipelinePage.tsx
│   │   ├── UploadPage.tsx
│   │   ├── MemoryPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── AuditLogsPage.tsx
│   │
│   ├── hooks/                      # CUSTOM HOOKS
│   │   ├── useAuth.ts              # Auth + guards
│   │   ├── useTenders.ts           # CRUD tenders + cache
│   │   ├── useTender.ts            # Single tender + mutations
│   │   ├── usePipeline.ts          # Kanban DnD + reorder
│   │   ├── useQualification.ts     # Lancer + suivre qualification
│   │   ├── useUpload.ts            # Upload DCE + progression
│   │   ├── useMemory.ts            # Recherche vectorielle
│   │   ├── useAuditLogs.ts         # Logs admin
│   │   ├── useStages.ts            # Stages pipeline (settings)
│   │   ├── useDebounce.ts          # Debounce generique
│   │   └── useMediaQuery.ts        # Breakpoints responsive
│   │
│   ├── stores/                     # ZUSTAND STORES
│   │   ├── authStore.ts
│   │   ├── tenderStore.ts
│   │   ├── pipelineStore.ts
│   │   └── uiStore.ts
│   │
│   ├── services/                   # API CALLS
│   │   ├── api.ts                  # Instance Axios configuree
│   │   ├── auth.service.ts         # Login, refresh, logout
│   │   ├── tender.service.ts       # CRUD tenders
│   │   ├── pipeline.service.ts     # Stages + mouvements
│   │   ├── upload.service.ts       # Upload + parsing DCE
│   │   ├── memory.service.ts       # Recherche memoire
│   │   ├── settings.service.ts     # Parametres tenant
│   │   └── audit.service.ts        # Logs audit
│   │
│   ├── types/                      # TYPES TYPESCRIPT
│   │   ├── auth.ts                 # User, Role, TokenPayload
│   │   ├── tender.ts               # Tender, Stage, Qualification
│   │   ├── pipeline.ts             # PipelineColumn, TenderCard
│   │   ├── upload.ts               # UploadProgress, ParsedDCE
│   │   ├── memory.ts               # MemoryChunk, SearchResult
│   │   ├── settings.ts             # TenantSettings, QualRule
│   │   └── api.ts                  # ApiResponse, PaginatedResult
│   │
│   └── lib/                        # UTILITAIRES
│       ├── utils.ts                # cn() (clsx + tailwind-merge)
│       ├── constants.ts            # Routes, stages par defaut, limits
│       ├── date-utils.ts           # Formatage dates, comparaisons
│       ├── formatters.ts           # Montants, pourcentages, texte
│       └── validators.ts           # Schemas Zod partages
│
├── public/                         # Assets statiques
│   ├── logo.svg
│   └── favicon.ico
│
├── index.html
├── package.json
├── tailwind.config.js              # Theme TAKA OS (colors, fonts)
├── tsconfig.json                   # Strict mode, path aliases
├── vite.config.ts                  # Proxy dev, path aliases
├── components.json                 # Config shadcn/ui
└── .env.example                    # Variables d'environnement
```

### 1.c. Configuration Tailwind (Theme TAKA OS)

```javascript
// tailwind.config.js
import { fontFamily } from "tailwindcss/defaultTheme";

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      colors: {
        // Palette TAKA OS
        taka: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
          950: "#082f49",
        },
        // Semantic colors (qualification)
        qual: {
          go: "#22c55e",      // Vert
          "go-light": "#dcfce7",
          maybe: "#f59e0b",   // Orange
          "maybe-light": "#fef3c7",
          nogo: "#ef4444",    // Rouge
          "nogo-light": "#fee2e2",
        },
        // Deadline colors
        deadline: {
          safe: "#22c55e",     // >14j
          warning: "#f59e0b",  // 7-14j
          danger: "#ef4444",   // <7j
          expired: "#6b7280",  // Passée
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", ...fontFamily.sans],
        mono: ["JetBrains Mono", ...fontFamily.mono],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "slide-in": {
          from: { transform: "translateX(-100%)", opacity: "0" },
          to: { transform: "translateX(0)", opacity: "1" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "slide-in": "slide-in 0.3s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
```

### 1.d. Configuration Vite

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@pages": path.resolve(__dirname, "./src/pages"),
      "@hooks": path.resolve(__dirname, "./src/hooks"),
      "@stores": path.resolve(__dirname, "./src/stores"),
      "@services": path.resolve(__dirname, "./src/services"),
      "@types": path.resolve(__dirname, "./src/types"),
      "@lib": path.resolve(__dirname, "./src/lib"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          router: ["react-router-dom"],
          query: ["@tanstack/react-query"],
          forms: ["react-hook-form", "@hookform/resolvers", "zod"],
          dnd: ["@dnd-kit/core", "@dnd-kit/sortable", "@dnd-kit/utilities"],
          charts: ["recharts"],
        },
      },
    },
  },
});
```

### 1.e. Point d'Entree (main.tsx)

```tsx
// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { RouterProvider } from "react-router-dom";
import { router } from "./App";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,     // 5 min
      gcTime: 1000 * 60 * 30,       // 30 min (cacheTime renomme)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>
);
```

---

## 2. Pages et Composants Detailles

### 2.a. Login (/login)

**Route :** `/login` — Publique, redirect si deja authentifie

**Layout :** Centré, fond gradient subtil, sans sidebar

**Composants :**
- `LoginForm` (formulaire email + password)
- `DevLoginButton` (visible uniquement en `import.meta.env.DEV`)

**États :**
- Zustand : `authStore.login(credentials)`, `authStore.isLoading`
- React Query : `useLoginMutation`

**Actions utilisateur :**
1. Saisir email + password
2. Soumettre → appel `/api/auth/login`
3. Stockage token (httpOnly cookie + memoire Zustand)
4. Redirection vers `/dashboard`
5. Mode dev : bouton "Dev Login" → login automatique avec creds de test

```tsx
// src/pages/LoginPage.tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@stores/authStore";
import { Button } from "@components/ui/button";
import { Input } from "@components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@components/ui/form";

const loginSchema = z.object({
  email: z.string().email("Email invalide"),
  password: z.string().min(1, "Mot de passe requis"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (data: LoginFormData) => {
    await login(data);
    navigate("/dashboard");
  };

  const handleDevLogin = async () => {
    await login({ email: "dev@taka.os", password: "dev" });
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-taka-50 to-taka-100">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center">
          <img src="/logo.svg" alt="TAKA OS" className="h-12 mx-auto mb-4" />
          <CardTitle className="text-2xl">Connexion</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="vous@entreprise.fr" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Mot de passe</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Connexion..." : "Se connecter"}
              </Button>
            </form>
          </Form>

          {import.meta.env.DEV && (
            <Button variant="outline" className="w-full" onClick={handleDevLogin}>
              Dev Login (rapide)
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Card centree, largeur max 448px
- Mobile : Card pleine largeur avec padding 16px

---

### 2.b. Dashboard (/dashboard)

**Route :** `/dashboard` — Protégée (tous les rôles)

**Layout :** Standard (sidebar + header + content)

**Composants :**
- `KPICard` x4 (AO actifs, deadlines 7j, taux GO, total en cours)
- `PipelineChart` (Recharts — bar chart des tenders par stage)
- `RecentTendersTable` (5 derniers AO avec statut)

**États :**
- React Query : `useDashboardStats`, `useRecentTenders`
- Zustand : `uiStore.sidebarOpen`

**Actions utilisateur :**
1. Visualiser KPIs (auto-refresh toutes les 5 min)
2. Cliquer sur un KPI → redirection vers `/tenders` avec filtre pre-rempli
3. Cliquer sur un AO recent → fiche detail
4. Hover sur graphique → tooltip detaille

```tsx
// src/pages/DashboardPage.tsx — extrait structure
import { KPICard } from "@components/shared/KPICard";
import { PipelineChart } from "@components/dashboard/PipelineChart";
import { RecentTendersTable } from "@components/dashboard/RecentTendersTable";

export default function DashboardPage() {
  const { data: stats } = useDashboardStats();
  const { data: recentTenders } = useRecentTenders(5);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Tableau de bord</h1>
        <p className="text-muted-foreground">Vue d'ensemble de vos appels d'offres</p>
      </div>

      {/* KPI Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="AO Actifs"
          value={stats?.activeTenders ?? 0}
          icon="FileText"
          trend={+12}
          href="/tenders?filter=active"
        />
        <KPICard
          title="Deadlines < 7j"
          value={stats?.urgentDeadlines ?? 0}
          icon="AlertTriangle"
          variant="warning"
          href="/tenders?filter=urgent"
        />
        <KPICard
          title="Taux Qualification GO"
          value={`${stats?.goRate ?? 0}%`}
          icon="CheckCircle"
          variant="success"
        />
        <KPICard
          title="Montant Total"
          value={formatCurrency(stats?.totalValue ?? 0)}
          icon="Euro"
        />
      </div>

      {/* Chart + Table */}
      <div className="grid gap-6 lg:grid-cols-7">
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <PipelineChart data={stats?.pipelineDistribution} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>AO Recents</CardTitle>
          </CardHeader>
          <CardContent>
            <RecentTendersTable data={recentTenders} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Grid 2x2 KPIs, chart 7 cols + table 3 cols
- Tablette : KPIs 2x2, chart + table empilés
- Mobile : KPIs empilés, graphique avec hauteur 250px, table scrollable horizontalement

---

### 2.c. Liste des AO (/tenders)

**Route :** `/tenders` — Protégée (viewer+, manager+ pour création)

**Layout :** Standard

**Composants :**
- `SearchBar` (recherche texte libre)
- `TenderFilters` (stage, qualification, deadline range)
- `DataTable` (tableau paginé, triable)
- `NewTenderDialog` (modal création manuelle)
- `UploadDCEDialog` (modal upload PDF)

**Colonnes DataTable :**
| Colonne | Triable | Filtrable | Note |
|---------|---------|-----------|------|
| Reference | Oui | Non | Lien vers fiche |
| Titre | Oui | Search | Tronqué a 60 chars |
| Acheteur | Oui | Select | |
| Deadline | Oui | Date range | DeadlineBadge |
| Stage | Oui | Select | StatusBadge |
| Qualification | Oui | Select | QualificationBadge |
| Actions | Non | Non | Voir / Editer / Supprimer |

**États :**
- Zustand : `tenderStore.filters`, `tenderStore.pagination`
- React Query : `useTenders({ filters, pagination })`, `useDeleteTenderMutation`

```tsx
// src/pages/TendersPage.tsx — extrait
export default function TendersPage() {
  const { filters, setFilters, pagination, setPagination } = useTenderStore();
  const { data, isLoading } = useTenders({ filters, pagination });
  const deleteMutation = useDeleteTenderMutation();

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Appels d'Offres</h1>
          <p className="text-muted-foreground">{data?.total} AO trouves</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setUploadOpen(true)}>
            <Upload className="mr-2 h-4 w-4" /> Upload DCE
          </Button>
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" /> Nouvel AO
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-4 lg:flex-row">
        <SearchBar
          value={filters.search}
          onChange={(v) => setFilters({ ...filters, search: v })}
          placeholder="Rechercher par titre, reference, acheteur..."
        />
        <TenderFilters filters={filters} onChange={setFilters} />
      </div>

      <DataTable
        columns={tenderColumns}
        data={data?.items ?? []}
        isLoading={isLoading}
        pagination={pagination}
        onPaginationChange={setPagination}
        totalCount={data?.total ?? 0}
      />
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Filtres en ligne, table pleine largeur, pagination en bas
- Mobile : Filtres dans un drawer, table scrollable horizontalement, cards empilées en alternative

---

### 2.d. Fiche AO (/tenders/:id)

**Route :** `/tenders/:id` — Protégée (tous les rôles, edit manager+)

**Layout :** Standard, pleine largeur

**Onglets (Tabs shadcn/ui) :**

#### Onglet 1 : Details
- Formulaire avec tous les champs du tender
- Champs : reference, titre, description, acheteur, deadline, montant estime, CPV, lieu, type de marche, procedure
- Mode lecture (viewer) / edition (manager)
- Bouton Sauvegarder (mutation React Query avec invalidation cache)

#### Onglet 2 : Documents
- Liste des documents (DCE, RC, DPGF, etc.)
- Upload de nouveaux documents
- Statut de parsing pour chaque document (pending / processing / done / error)
- Preview PDF inline (iframe)

#### Onglet 3 : Qualification
- Resultat GO/NO-GO/MAYBE avec badge colore
- Barres de score par critere (eligibilite, technique, financier, calendrier, risques)
- Justification textuelle de l'agent
- Bouton "Relancer la qualification" (manager+)
- Historique des qualifications precedentes

#### Onglet 4 : Historique
- Timeline verticale des evenements (audit trail)
- Types : creation, modification, qualification, changement stage, upload document
- Auteur + date pour chaque evenement

```tsx
// src/pages/TenderDetailPage.tsx — structure onglets
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@components/ui/tabs";

export default function TenderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: tender } = useTender(id!);

  return (
    <div className="space-y-6">
      {/* Header de la fiche */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">{tender?.title}</h1>
            <QualificationBadge result={tender?.qualification} />
          </div>
          <p className="text-muted-foreground">Ref: {tender?.reference}</p>
        </div>
        <div className="flex gap-2">
          <DeadlineBadge date={tender?.deadline} />
          <Button onClick={() => triggerQualification(id!)}>
            <Sparkles className="mr-2 h-4 w-4" /> Qualifier
          </Button>
        </div>
      </div>

      <Tabs defaultValue="details" className="w-full">
        <TabsList className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="qualification">Qualification</TabsTrigger>
          <TabsTrigger value="history">Historique</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <TenderForm tender={tender} readOnly={!canEdit} />
        </TabsContent>

        <TabsContent value="documents">
          <DocumentsTab tenderId={id!} documents={tender?.documents} />
        </TabsContent>

        <TabsContent value="qualification">
          <QualificationTab tenderId={id!} qualification={tender?.qualification_result} />
        </TabsContent>

        <TabsContent value="history">
          <HistoryTimeline tenderId={id!} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Tabs horizontales, formulaire 2 colonnes, timeline pleine largeur
- Mobile : Tabs scrollables horizontalement, formulaire 1 colonne, timeline compactee

---

### 2.e. Kanban Pipeline (/pipeline)

**Route :** `/pipeline` — Protégée (tous les rôles, DnD manager+)

**Layout :** Standard, pleine largeur sans padding lateral

**Composants :**
- `PipelineBoard` — conteneur DnD (@dnd-kit)
- `PipelineColumn` — colonne (stage) avec compteur
- `SortableTenderCard` — carte draggable
- `QualificationFilter` — filtre GO/NO-GO/MAYBE/TOUS

**Fonctionnalites DnD :**
- Drag & drop horizontal entre colonnes
- Reordonnancement vertical dans une colonne
- Animation fluide (CSS transitions)
- Confetti visuel lors d'un drop dans "Gagne" (option UX)

```tsx
// src/pages/PipelinePage.tsx — structure DnD
import { DndContext, DragOverlay, closestCorners } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { PipelineColumn } from "@components/pipeline/PipelineColumn";
import { SortableTenderCard } from "@components/pipeline/SortableTenderCard";
import { TenderCard } from "@components/tenders/TenderCard";

export default function PipelinePage() {
  const { stages, tendersByStage, moveTender, reorderTender } = usePipeline();
  const [activeId, setActiveId] = useState<string | null>(null);
  const [qualFilter, setQualFilter] = useState<Qualification | "ALL">("ALL");

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeTender = findTender(active.id as string);
    const overStage = over.data.current?.stageId;

    if (overStage && activeTender.stage_id !== overStage) {
      moveTender({ tenderId: active.id as string, targetStage: overStage });
    }
    setActiveId(null);
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header avec filtres */}
      <div className="flex items-center justify-between px-6 py-4">
        <div>
          <h1 className="text-3xl font-bold">Pipeline</h1>
          <p className="text-muted-foreground">Glissez-deposez pour avancer vos AO</p>
        </div>
        <QualificationFilter value={qualFilter} onChange={setQualFilter} />
      </div>

      {/* Board DnD */}
      <DndContext
        collisionDetection={closestCorners}
        onDragStart={({ active }) => setActiveId(active.id as string)}
        onDragEnd={handleDragEnd}
      >
        <div className="flex-1 flex gap-4 overflow-x-auto px-6 pb-4">
          {stages.map((stage) => (
            <PipelineColumn
              key={stage.id}
              stage={stage}
              tenders={(tendersByStage[stage.id] ?? []).filter(
                (t) => qualFilter === "ALL" || t.qualification === qualFilter
              )}
            />
          ))}
        </div>

        <DragOverlay>
          {activeId ? <TenderCard tender={findTender(activeId)} isDragging /> : null}
        </DragOverlay>
      </DndContext>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Colonnes fixes, scroll horizontal, cards larges (280px min)
- Mobile : Vue liste alternative (cards empilees par stage), DnD desactive

---

### 2.f. Upload DCE (/upload)

**Route :** `/upload` — Protégée (manager+)

**Layout :** Standard, centré

**Composants :**
- `FileUploadZone` — zone drag & drop
- `UploadProgress` — barre de progression
- `ParsedTenderPreview` — prévisualisation champs extraits
- `TenderCorrectionForm` — correction des champs avant validation

**Flux utilisateur :**
1. Drop fichier PDF ou clic pour selection
2. Upload avec barre de progression (Axios onUploadProgress)
3. Parsing côté backend (retour SSE ou polling)
4. Affichage des champs extraits (titre, reference, deadline, montant, acheteur, CPV)
5. Utilisateur corrige si besoin
6. Validation → création du tender + redirection fiche

```tsx
// src/pages/UploadPage.tsx — flux complet
export default function UploadPage() {
  const [step, setStep] = useState<"upload" | "parsing" | "preview" | "success">("upload");
  const [progress, setProgress] = useState(0);
  const [parsedData, setParsedData] = useState<ParsedTender | null>(null);
  const uploadMutation = useUploadDCE();

  const handleDrop = async (files: File[]) => {
    const file = files[0];
    if (!file || file.type !== "application/pdf") {
      toast.error("Veuillez deposer un fichier PDF");
      return;
    }

    setStep("upload");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const result = await uploadMutation.mutateAsync(
        { file, onProgress: setProgress },
        {
          onSuccess: (data) => {
            setParsedData(data);
            setStep("preview");
          },
        }
      );
    } catch (error) {
      setStep("upload");
      toast.error("Erreur lors de l'upload");
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Upload de DCE</h1>
        <p className="text-muted-foreground">
          Deposez un DCE PDF pour extraction automatique des informations
        </p>
      </div>

      {step === "upload" && (
        <FileUploadZone onDrop={handleDrop} accept=".pdf" maxSize={50 * 1024 * 1024} />
      )}

      {step === "parsing" && (
        <Card className="p-8">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-taka-600" />
            <p>Analyse du document en cours...</p>
            <Progress value={progress} className="w-full" />
          </div>
        </Card>
      )}

      {step === "preview" && parsedData && (
        <ParsedTenderPreview
          data={parsedData}
          onConfirm={(corrected) => createTender(corrected)}
          onBack={() => setStep("upload")}
        />
      )}
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Zone drop grande (400px hauteur), formulaire correction 2 colonnes
- Mobile : Zone drop pleine largeur, formulaire 1 colonne, steps en vertical

---

### 2.g. Memoire (/memory)

**Route :** `/memory` — Protégée (tous les rôles)

**Layout :** Standard

**Composants :**
- `MemorySearch` — input recherche avec similarité
- `MemoryResultCard` — card resultat (contenu + % similarité)
- `TagFilter` — filtres par tags/categories

**Fonctionnement :**
- Recherche textuelle envoyée à `/api/memory/search?q=...`
- Retour : chunks vectoriels avec score de similarité
- Affichage : cards avec extrait, similarité en badge, tags cliquables
- Highlight des termes recherchés dans les résultats

```tsx
// src/pages/MemoryPage.tsx
export default function MemoryPage() {
  const [query, setQuery] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const { data: results, isLoading } = useMemorySearch(query, selectedTags);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Memoire</h1>
        <p className="text-muted-foreground">
          Recherche semantique dans la base de connaissances
        </p>
      </div>

      <MemorySearch
        value={query}
        onChange={setQuery}
        placeholder="Rechercher par contenu semantique..."
      />

      <TagFilter
        tags={availableTags}
        selected={selectedTags}
        onChange={setSelectedTags}
      />

      {isLoading ? (
        <LoadingSkeleton count={6} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {results?.map((result) => (
            <MemoryResultCard
              key={result.id}
              content={result.content}
              similarity={result.similarity}
              tags={result.tags}
              source={result.source}
              onTagClick={(tag) => setSelectedTags((prev) => [...prev, tag])}
            />
          ))}
        </div>
      )}

      {results?.length === 0 && query && (
        <EmptyState
          icon="Search"
          title="Aucun resultat"
          description="Essayez avec d'autres termes"
        />
      )}
    </div>
  );
}
```

---

### 2.h. Parametres (/settings)

**Route :** `/settings` — Protégée (admin pour users, tous pour profil)

**Onglets :**

#### Profil
- Photo, nom, email, changement password

#### Regles de Qualification (admin)
- CPV whitelist/blacklist (textarea avec tags)
- Fourchette montants (min/max)
- Types de marche autorises (checkboxes)
- Seuil de score GO/MAYBE/NO-GO

#### Stages Pipeline (admin)
- Liste des stages (drag & drop pour reorder)
- Ajouter / Renommer / Supprimer un stage
- Couleur par stage

#### Utilisateurs (admin)
- Table des utilisateurs (nom, email, rôle, derniere connexion)
- Ajouter un utilisateur (invitation par email)
- Modifier rôle, Désactiver, Supprimer

```tsx
// src/pages/SettingsPage.tsx
export default function SettingsPage() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === "admin";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Parametres</h1>
        <p className="text-muted-foreground">Configuration de votre espace TAKA OS</p>
      </div>

      <Tabs defaultValue="profile" orientation="vertical" className="flex gap-6">
        <TabsList className="flex-col h-fit w-48">
          <TabsTrigger value="profile">Profil</TabsTrigger>
          {isAdmin && (
            <>
              <TabsTrigger value="qualification">Regles de Qualification</TabsTrigger>
              <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
              <TabsTrigger value="users">Utilisateurs</TabsTrigger>
            </>
          )}
        </TabsList>

        <div className="flex-1">
          <TabsContent value="profile"><ProfileSettings /></TabsContent>
          {isAdmin && (
            <>
              <TabsContent value="qualification"><QualificationRules /></TabsContent>
              <TabsContent value="pipeline"><PipelineSettings /></TabsContent>
              <TabsContent value="users"><UsersManagement /></TabsContent>
            </>
          )}
        </div>
      </Tabs>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Tabs verticales a gauche (sidebar 192px), contenu a droite
- Mobile : Tabs horizontales scrollables, contenu pleine largeur

---

### 2.i. Audit Logs (/admin/audit)

**Route :** `/admin/audit` — Admin uniquement (route guard)

**Layout :** Standard

**Composants :**
- `AuditFilters` — date range, user, action type
- `AuditTable` — table paginée
- `ExportButton` — export CSV/PDF

**Colonnes :** Date | Utilisateur | Action | Entite | Details | IP

```tsx
// src/pages/AuditLogsPage.tsx
export default function AuditLogsPage() {
  const { filters, setFilters, pagination, setPagination } = useAuditStore();
  const { data: logs, isLoading } = useAuditLogs({ filters, pagination });

  const handleExport = async (format: "csv" | "pdf") => {
    const blob = await exportAuditLogs(format, filters);
    downloadFile(blob, `audit-logs.${format}`);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Logs d'Audit</h1>
          <p className="text-muted-foreground">Historique complet des actions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => handleExport("csv")}>
            <Download className="mr-2 h-4 w-4" /> CSV
          </Button>
          <Button variant="outline" onClick={() => handleExport("pdf")}>
            <Download className="mr-2 h-4 w-4" /> PDF
          </Button>
        </div>
      </div>

      <AuditFilters filters={filters} onChange={setFilters} />
      <AuditTable logs={logs?.items} isLoading={isLoading} pagination={pagination} />
    </div>
  );
}
```

---

### 2.j. Composants Reutilisables — Specifications Detailles

#### Layout (Sidebar + Header + Content)

```tsx
// src/components/layout/Layout.tsx
export function Layout() {
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar Desktop */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen transition-all duration-300 bg-card border-r",
          sidebarOpen ? "w-64" : "w-16"
        )}
      >
        <Sidebar collapsed={!sidebarOpen} />
      </aside>

      {/* Main Content */}
      <div
        className={cn(
          "transition-all duration-300 min-h-screen flex flex-col",
          sidebarOpen ? "ml-64" : "ml-16"
        )}
      >
        <Header onMenuClick={toggleSidebar} />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>

      {/* Mobile Bottom Nav */}
      <MobileNav className="lg:hidden" />
    </div>
  );
}
```

#### Sidebar

- Logo TAKA OS (réduit quand collapsed)
- Navigation items avec icons (Dashboard, AO, Pipeline, Upload, Memoire, Parametres)
- Section admin (Audit) conditionnelle
- Tenant name + user avatar en bas
- Tooltip quand collapsed

```tsx
const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
  { label: "Appels d'Offres", icon: FileText, href: "/tenders" },
  { label: "Pipeline", icon: Kanban, href: "/pipeline" },
  { label: "Upload DCE", icon: Upload, href: "/upload" },
  { label: "Memoire", icon: Brain, href: "/memory" },
  { label: "Parametres", icon: Settings, href: "/settings" },
];
```

#### TenderCard (Kanban)

```tsx
// src/components/tenders/TenderCard.tsx
interface TenderCardProps {
  tender: Tender;
  isDragging?: boolean;
  onClick?: () => void;
}

export function TenderCard({ tender, isDragging, onClick }: TenderCardProps) {
  return (
    <Card
      className={cn(
        "cursor-pointer hover:shadow-md transition-shadow",
        isDragging && "opacity-50 rotate-2 shadow-xl"
      )}
      onClick={onClick}
    >
      <CardContent className="p-3 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-medium text-sm line-clamp-2">{tender.title}</h3>
          <QualificationBadge result={tender.qualification} size="sm" />
        </div>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <DeadlineBadge date={tender.deadline} size="sm" />
          {tender.estimated_value && (
            <span>{formatCurrency(tender.estimated_value)}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

#### QualificationBadge

```tsx
// src/components/qualification/QualificationBadge.tsx
const qualConfig = {
  GO:      { label: "GO",      color: "bg-green-500",      light: "bg-green-100 text-green-800" },
  MAYBE:   { label: "MAYBE",   color: "bg-amber-500",      light: "bg-amber-100 text-amber-800" },
  "NO-GO": { label: "NO-GO",   color: "bg-red-500",        light: "bg-red-100 text-red-800" },
  PENDING: { label: "En attente", color: "bg-gray-400",     light: "bg-gray-100 text-gray-600" },
};

interface QualificationBadgeProps {
  result?: keyof typeof qualConfig;
  size?: "sm" | "md" | "lg";
}

export function QualificationBadge({ result = "PENDING", size = "md" }: QualificationBadgeProps) {
  const config = qualConfig[result];
  const sizeClasses = {
    sm: "text-[10px] px-1.5 py-0.5",
    md: "text-xs px-2.5 py-0.5",
    lg: "text-sm px-3 py-1",
  };

  return (
    <Badge className={cn(config.light, sizeClasses[size], "font-semibold")}>
      {config.label}
    </Badge>
  );
}
```

#### DeadlineBadge

```tsx
// src/components/shared/DeadlineBadge.tsx
export function DeadlineBadge({ date, size = "md" }: DeadlineBadgeProps) {
  if (!date) return null;

  const days = differenceInDays(parseISO(date), new Date());
  const config =
    days < 0 ? { label: "Expire", color: "bg-gray-500" }
    : days < 7 ? { label: `${days}j`, color: "bg-red-500" }
    : days < 14 ? { label: `${days}j`, color: "bg-amber-500" }
    : { label: `${days}j`, color: "bg-green-500" };

  return (
    <div className="flex items-center gap-1">
      <Clock className={cn("text-muted-foreground", size === "sm" ? "h-3 w-3" : "h-4 w-4")} />
      <span className={cn("font-medium", days < 7 && "text-red-600")}>
        {config.label}
      </span>
    </div>
  );
}
```

#### FileUploadZone

```tsx
// src/components/shared/FileUploadZone.tsx
export function FileUploadZone({ onDrop, accept = ".pdf", maxSize = 50 * 1024 * 1024 }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxSize,
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors",
        isDragActive
          ? "border-taka-500 bg-taka-50"
          : "border-border hover:border-taka-300 hover:bg-accent"
      )}
    >
      <input {...getInputProps()} />
      <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
      <p className="text-lg font-medium">
        {isDragActive ? "Deposez le fichier ici" : "Glissez un PDF ici, ou cliquez pour selectionner"}
      </p>
      <p className="text-sm text-muted-foreground mt-2">
        PDF uniquement, max {Math.round(maxSize / 1024 / 1024)} MB
      </p>
    </div>
  );
}
```

#### KPICard

```tsx
// src/components/shared/KPICard.tsx
export function KPICard({ title, value, icon, trend, variant, href }: KPICardProps) {
  const Icon = ICONS[icon];
  return (
    <Card className={cn("hover:shadow-md transition-shadow", href && "cursor-pointer")}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold">{value}</p>
            {trend !== undefined && (
              <div className={cn("flex items-center text-sm", trend >= 0 ? "text-green-600" : "text-red-600")}>
                {trend >= 0 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
                {Math.abs(trend)}%
              </div>
            )}
          </div>
          <div className={cn("p-3 rounded-full", VARIANTS[variant ?? "default"])}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

#### SearchBar avec Filtres

```tsx
// src/components/shared/SearchBar.tsx
export function SearchBar({ value, onChange, placeholder }: SearchBarProps) {
  return (
    <div className="relative flex-1">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="pl-10"
      />
      {value && (
        <button onClick={() => onChange("")} className="absolute right-3 top-1/2 -translate-y-1/2">
          <X className="h-4 w-4 text-muted-foreground" />
        </button>
      )}
    </div>
  );
}
```

#### DataTable (TanStack Table)

```tsx
// src/components/shared/DataTable.tsx
export function DataTable<TData>({ columns, data, isLoading, pagination, onPaginationChange, totalCount }: DataTableProps<TData>) {
  const table = useReactTable({
    data,
    columns,
    pageCount: Math.ceil(totalCount / pagination.pageSize),
    state: { pagination },
    onPaginationChange,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    manualPagination: true,
  });

  return (
    <div className="space-y-4">
      <div className="rounded-md border overflow-x-auto">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((hg) => (
              <TableRow key={hg.id}>
                {hg.headers.map((header) => (
                  <TableHead key={header.id}>
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={columns.length}>
                  <LoadingSkeleton count={5} />
                </TableCell>
              </TableRow>
            ) : table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="text-center py-8">
                  Aucun resultat
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {pagination.pageIndex * pagination.pageSize + 1} -{" "}
          {Math.min((pagination.pageIndex + 1) * pagination.pageSize, totalCount)} sur {totalCount}
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>
            Precedent
          </Button>
          <Button variant="outline" size="sm" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
            Suivant
          </Button>
        </div>
      </div>
    </div>
  );
}
```



---

## 3. State Management (Zustand)

### 3.a. Philosophie

Zustand est utilise pour le state **client-only** (UI, auth, filtres). TanStack Query gère le state **serveur** (tenders, users, logs). Pas de duplication — Zustand ne stocke pas de données qui viennent du serveur.

### 3.b. authStore

```typescript
// src/stores/authStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";

interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "manager" | "viewer";
  tenant_id: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  login: (credentials: { email: string; password: string }) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  immer(
    persist(
      (set, get) => ({
        user: null,
        token: null,
        isLoading: false,
        isAuthenticated: false,

        login: async (credentials) => {
          set({ isLoading: true });
          try {
            const response = await authService.login(credentials);
            set({
              user: response.user,
              token: response.access_token,
              isAuthenticated: true,
              isLoading: false,
            });
          } catch (error) {
            set({ isLoading: false });
            throw error;
          }
        },

        logout: () => {
          authService.logout();
          set({ user: null, token: null, isAuthenticated: false });
          // Reset other stores
          useTenderStore.getState().reset();
          useUIStore.getState().reset();
        },

        setUser: (user) => set({ user }),

        refreshToken: async () => {
          try {
            const response = await authService.refresh();
            set({ token: response.access_token });
          } catch {
            get().logout();
          }
        },
      }),
      {
        name: "taka-auth",
        partialize: (state) => ({ token: state.token }),
      }
    )
  )
);

// Selector derive
export const useIsAdmin = () => useAuthStore((s) => s.user?.role === "admin");
export const useCanEdit = () => useAuthStore((s) => ["admin", "manager"].includes(s.user?.role ?? ""));
```

### 3.c. tenderStore

```typescript
// src/stores/tenderStore.ts
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

interface TenderFilters {
  search: string;
  stage: string | null;
  qualification: string | null;
  deadlineFrom: string | null;
  deadlineTo: string | null;
}

interface Pagination {
  pageIndex: number;
  pageSize: number;
}

interface TenderState {
  // Filtres
  filters: TenderFilters;
  setFilters: (filters: Partial<TenderFilters>) => void;
  resetFilters: () => void;

  // Pagination
  pagination: Pagination;
  setPagination: (pagination: Partial<Pagination>) => void;

  // Selection
  selectedTenderId: string | null;
  setSelectedTenderId: (id: string | null) => void;

  // UI
  isCreateOpen: boolean;
  setCreateOpen: (open: boolean) => void;
  isUploadOpen: boolean;
  setUploadOpen: (open: boolean) => void;

  // Reset
  reset: () => void;
}

const defaultFilters: TenderFilters = {
  search: "",
  stage: null,
  qualification: null,
  deadlineFrom: null,
  deadlineTo: null,
};

const defaultPagination: Pagination = {
  pageIndex: 0,
  pageSize: 25,
};

export const useTenderStore = create<TenderState>()(
  immer((set) => ({
    filters: { ...defaultFilters },
    pagination: { ...defaultPagination },
    selectedTenderId: null,
    isCreateOpen: false,
    isUploadOpen: false,

    setFilters: (filters) =>
      set((state) => {
        Object.assign(state.filters, filters);
        state.pagination.pageIndex = 0; // Reset page on filter change
      }),

    resetFilters: () => set({ filters: { ...defaultFilters }, pagination: { ...defaultPagination, pageSize: get().pagination.pageSize } }),

    setPagination: (pagination) =>
      set((state) => {
        Object.assign(state.pagination, pagination);
      }),

    setSelectedTenderId: (id) => set({ selectedTenderId: id }),
    setCreateOpen: (open) => set({ isCreateOpen: open }),
    setUploadOpen: (open) => set({ isUploadOpen: open }),

    reset: () =>
      set({
        filters: { ...defaultFilters },
        pagination: { ...defaultPagination },
        selectedTenderId: null,
        isCreateOpen: false,
        isUploadOpen: false,
      }),
  }))
);
```

### 3.d. pipelineStore

```typescript
// src/stores/pipelineStore.ts
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

interface PipelineState {
  stages: Stage[];
  setStages: (stages: Stage[]) => void;

  // Optimistic update DnD
  moveTenderOptimistic: (tenderId: string, targetStageId: string) => void;
  revertMove: (tenderId: string, originalStageId: string) => void;

  // Filters
  qualFilter: Qualification | "ALL";
  setQualFilter: (filter: Qualification | "ALL") => void;
}

export const usePipelineStore = create<PipelineState>()(
  immer((set) => ({
    stages: [],
    qualFilter: "ALL",

    setStages: (stages) => set({ stages }),

    moveTenderOptimistic: (tenderId, targetStageId) =>
      set((state) => {
        // Update tender stage in local state
        for (const stage of state.stages) {
          const idx = stage.tenders.findIndex((t) => t.id === tenderId);
          if (idx !== -1) {
            const [tender] = stage.tenders.splice(idx, 1);
            tender.stage_id = targetStageId;
            const targetStage = state.stages.find((s) => s.id === targetStageId);
            targetStage?.tenders.push(tender);
            break;
          }
        }
      }),

    setQualFilter: (filter) => set({ qualFilter: filter }),
  }))
);
```

### 3.e. uiStore

```typescript
// src/stores/uiStore.ts
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { persist } from "zustand/middleware";

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant: "default" | "destructive" | "success";
}

interface UIState {
  // Sidebar
  sidebarOpen: boolean;
  toggleSidebar: () => void;

  // Modals
  activeModal: string | null;
  modalData: Record<string, unknown> | null;
  openModal: (modal: string, data?: Record<string, unknown>) => void;
  closeModal: () => void;

  // Toasts
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void;
  removeToast: (id: string) => void;

  // Theme
  theme: "light" | "dark" | "system";
  setTheme: (theme: "light" | "dark" | "system") => void;

  reset: () => void;
}

export const useUIStore = create<UIState>()(
  immer(
    persist(
      (set) => ({
        sidebarOpen: true,
        theme: "system",
        activeModal: null,
        modalData: null,
        toasts: [],

        toggleSidebar: () => set((state) => { state.sidebarOpen = !state.sidebarOpen; }),
        setTheme: (theme) => set({ theme }),

        openModal: (modal, data) => set({ activeModal: modal, modalData: data ?? null }),
        closeModal: () => set({ activeModal: null, modalData: null }),

        addToast: (toast) =>
          set((state) => {
            state.toasts.push({ ...toast, id: crypto.randomUUID() });
          }),

        removeToast: (id) =>
          set((state) => {
            state.toasts = state.toasts.filter((t) => t.id !== id);
          }),

        reset: () => set({ activeModal: null, modalData: null, toasts: [] }),
      }),
      {
        name: "taka-ui",
        partialize: (state) => ({ sidebarOpen: state.sidebarOpen, theme: state.theme }),
      }
    )
  )
);
```

### 3.f. API Service (Axios)

```typescript
// src/services/api.ts
import axios from "axios";
import { useAuthStore } from "@stores/authStore";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Request interceptor — injecte le token JWT
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — gestion 401 + refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        await useAuthStore.getState().refreshToken();
        const newToken = useAuthStore.getState().token;
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch {
        useAuthStore.getState().logout();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    // Erreurs 500 — toast notification
    if (error.response?.status >= 500) {
      useUIStore.getState().addToast({
        title: "Erreur serveur",
        description: "Une erreur est survenue. Reessayez plus tard.",
        variant: "destructive",
      });
    }

    return Promise.reject(error);
  }
);
```

### 3.g. Hooks React Query

```typescript
// src/hooks/useTenders.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tenderService } from "@services/tender.service";

export function useTenders(params: TenderListParams) {
  return useQuery({
    queryKey: ["tenders", params],
    queryFn: () => tenderService.list(params),
    placeholderData: (previousData) => previousData, // keepPreviousData
  });
}

export function useTender(id: string) {
  return useQuery({
    queryKey: ["tender", id],
    queryFn: () => tenderService.getById(id),
    enabled: !!id,
  });
}

export function useCreateTenderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: tenderService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenders"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateTenderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TenderUpdate }) =>
      tenderService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tender", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["tenders"] });
    },
  });
}

export function useDeleteTenderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: tenderService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenders"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useQualifyTenderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (tenderId: string) => tenderService.qualify(tenderId),
    onSuccess: (_, tenderId) => {
      queryClient.invalidateQueries({ queryKey: ["tender", tenderId] });
      queryClient.invalidateQueries({ queryKey: ["tenders"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
```

```typescript
// src/hooks/useUpload.ts
import { useMutation } from "@tanstack/react-query";
import { uploadService } from "@services/upload.service";

export function useUploadDCE() {
  return useMutation({
    mutationFn: ({
      file,
      onProgress,
    }: {
      file: File;
      onProgress: (progress: number) => void;
    }) => uploadService.upload(file, onProgress),
  });
}
```

### 3.h. Router avec Guards

```tsx
// src/App.tsx
import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { Layout } from "@components/layout/Layout";
import { useAuthStore } from "@stores/authStore";
import { Suspense, lazy } from "react";
import { LoadingSkeleton } from "@components/shared/LoadingSkeleton";

// Lazy loading des pages
const LoginPage = lazy(() => import("@pages/LoginPage"));
const DashboardPage = lazy(() => import("@pages/DashboardPage"));
const TendersPage = lazy(() => import("@pages/TendersPage"));
const TenderDetailPage = lazy(() => import("@pages/TenderDetailPage"));
const PipelinePage = lazy(() => import("@pages/PipelinePage"));
const UploadPage = lazy(() => import("@pages/UploadPage"));
const MemoryPage = lazy(() => import("@pages/MemoryPage"));
const SettingsPage = lazy(() => import("@pages/SettingsPage"));
const AuditLogsPage = lazy(() => import("@pages/AuditLogsPage"));

// Route guard — authentification
function AuthGuard({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

// Route guard — admin uniquement
function AdminGuard({ children }: { children: React.ReactNode }) {
  const isAdmin = useAuthStore((s) => s.user?.role === "admin");
  return isAdmin ? <>{children}</> : <Navigate to="/dashboard" replace />;
}

// Route guard — manager+
function ManagerGuard({ children }: { children: React.ReactNode }) {
  const role = useAuthStore((s) => s.user?.role);
  const canEdit = role === "admin" || role === "manager";
  return canEdit ? <>{children}</> : <Navigate to="/dashboard" replace />;
}

// Layout wrapper avec suspense
function PageWrapper({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<LoadingSkeleton className="h-screen" />}>{children}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: "/login",
    element: (
      <PageWrapper>
        <LoginPage />
      </PageWrapper>
    ),
  },
  {
    path: "/",
    element: (
      <AuthGuard>
        <Layout />
      </AuthGuard>
    ),
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      {
        path: "dashboard",
        element: (
          <PageWrapper>
            <DashboardPage />
          </PageWrapper>
        ),
      },
      {
        path: "tenders",
        element: (
          <PageWrapper>
            <TendersPage />
          </PageWrapper>
        ),
      },
      {
        path: "tenders/:id",
        element: (
          <PageWrapper>
            <TenderDetailPage />
          </PageWrapper>
        ),
      },
      {
        path: "pipeline",
        element: (
          <PageWrapper>
            <PipelinePage />
          </PageWrapper>
        ),
      },
      {
        path: "upload",
        element: (
          <ManagerGuard>
            <PageWrapper>
              <UploadPage />
            </PageWrapper>
          </ManagerGuard>
        ),
      },
      {
        path: "memory",
        element: (
          <PageWrapper>
            <MemoryPage />
          </PageWrapper>
        ),
      },
      {
        path: "settings",
        element: (
          <PageWrapper>
            <SettingsPage />
          </PageWrapper>
        ),
      },
      {
        path: "admin/audit",
        element: (
          <AdminGuard>
            <PageWrapper>
              <AuditLogsPage />
            </PageWrapper>
          </AdminGuard>
        ),
      },
    ],
  },
]);
```

---

## 4. DevOps & Deploiement

### 4.a. Architecture Docker Compose (Production)

```yaml
# docker-compose.yml — Production
version: "3.8"

services:
  db:
    image: ankane/pgvector:pg15
    container_name: taka-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-takaos}
      POSTGRES_USER: ${POSTGRES_USER:-taka}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-taka} -d ${POSTGRES_DB:-takaos}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - taka-network
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 256M

  api:
    image: ghcr.io/${GITHUB_OWNER}/taka-os-api:${TAG:-latest}
    container_name: taka-api
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-taka}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB:-takaos}
      SECRET_KEY: ${SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ENVIRONMENT: production
      LOG_LEVEL: INFO
      CORS_ORIGINS: ${CORS_ORIGINS:-https://${DOMAIN}}
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s
    networks:
      - taka-network
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 256M

  web:
    image: ghcr.io/${GITHUB_OWNER}/taka-os-web:${TAG:-latest}
    container_name: taka-web
    restart: unless-stopped
    depends_on:
      - api
    networks:
      - taka-network
    deploy:
      resources:
        limits:
          memory: 128M

  nginx:
    image: nginx:1.25-alpine
    container_name: taka-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - certbot-data:/etc/letsencrypt
      - certbot-www:/var/www/certbot
    depends_on:
      - api
      - web
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 15s
      timeout: 5s
      retries: 3
    networks:
      - taka-network

  certbot:
    image: certbot/certbot:latest
    container_name: taka-certbot
    volumes:
      - certbot-data:/etc/letsencrypt
      - certbot-www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    networks:
      - taka-network

volumes:
  pgdata:
    driver: local
  uploads:
    driver: local
  certbot-data:
    driver: local
  certbot-www:
    driver: local

networks:
  taka-network:
    driver: bridge
```

### 4.b. Dockerfile Frontend (Multi-stage)

```dockerfile
# frontend/Dockerfile — Multi-stage build
# ---- Stage 1: Build ----
FROM node:20-alpine AS builder

WORKDIR /app

# Dependencies
COPY package*.json ./
RUN npm ci --only=production=false

# Source + build
COPY . .
RUN npm run build

# ---- Stage 2: Serve (Nginx) ----
FROM nginx:1.25-alpine

# Copy build
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Security headers + SPA fallback
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
        add_header Content-Type text/plain; \
    } \
    \
    gzip on; \
    gzip_types text/plain text/css application/json application/javascript text/xml; \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
```

### 4.c. Dockerfile Backend

```dockerfile
# backend/Dockerfile — Python 3.12 slim
FROM python:3.12-slim AS builder

WORKDIR /app

# Build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Runtime ----
FROM python:3.12-slim

WORKDIR /app

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Application
COPY . .

# Create uploads dir
RUN mkdir -p /app/uploads

# Migrations + start
CMD alembic upgrade head && \
    gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### 4.d. Configuration Nginx (Production)

```nginx
# nginx/conf.d/takaos.conf
upstream api_backend {
    server api:8000;
    keepalive 32;
}

upstream web_frontend {
    server web:80;
    keepalive 32;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    # SSL
    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # API proxy
    location /api/ {
        proxy_pass http://api_backend/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
    }

    # WebSocket (SSE pour parsing progress)
    location /api/v1/stream/ {
        proxy_pass http://api_backend/v1/stream/;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_buffering off;
    }

    # Frontend SPA
    location / {
        proxy_pass http://web_frontend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://web_frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

### 4.e. Variables d'Environnement (.env)

```bash
# === TAKA OS — Configuration Production ===

# Domaine
DOMAIN=takaos.votre-domaine.fr

# Base de donnees
POSTGRES_DB=takaos
POSTGRES_USER=taka
POSTGRES_PASSWORD=<GENERER_MDP_FORT_32_CHARS>

# Securite
SECRET_KEY=<GENERER_CLE_ALEATOIRE_64_CHARS>

# OpenAI (qualification agentic)
OPENAI_API_KEY=sk-...

# GitHub Container Registry
GITHUB_OWNER=votre-org
GITHUB_TOKEN=ghp_...

# VPS
VPS_HOST=<IP_VPS>
VPS_USER=deploy
VPS_SSH_KEY=~/.ssh/id_ed25519_deploy

# CORS (production)
CORS_ORIGINS=https://takaos.votre-domaine.fr

# Backup (optionnel)
S3_ENDPOINT=s3.eu-central-1.amazonaws.com
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=takaos-backups
```

### 4.f. CI/CD GitHub Actions

#### Workflow 1 — Tests (Pull Request)

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: ankane/pgvector:pg15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: takaos_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint (ruff)
        working-directory: ./backend
        run: ruff check .

      - name: Type check (mypy)
        working-directory: ./backend
        run: mypy .

      - name: Run tests
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:test@localhost:5432/takaos_test
        run: pytest -xvs --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: ./frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Lint (ESLint)
        working-directory: ./frontend
        run: npm run lint

      - name: Type check (tsc)
        working-directory: ./frontend
        run: npx tsc --noEmit

      - name: Build
        working-directory: ./frontend
        run: npm run build
```

#### Workflow 2 — Build & Push Images

```yaml
# .github/workflows/build.yml
name: Build & Push

on:
  push:
    branches: [main, develop]
    tags: ["v*"]

env:
  REGISTRY: ghcr.io
  IMAGE_API: ghcr.io/${{ github.repository_owner }}/taka-os-api
  IMAGE_WEB: ghcr.io/${{ github.repository_owner }}/taka-os-web

jobs:
  build-api:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_API }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & push
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  build-web:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_WEB }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & push
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          build-args: |
            VITE_API_URL=/api
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

#### Workflow 3 — Deploy VPS

```yaml
# .github/workflows/deploy.yml
name: Deploy to VPS

on:
  workflow_run:
    workflows: ["Build & Push"]
    branches: [main]
    types: [completed]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
      - uses: actions/checkout@v4

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/takaos

            # Pull latest compose + env
            git pull origin main

            # Login GHCR
            echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin

            # Pull new images
            TAG=main docker compose pull

            # Database backup avant migration
            docker compose exec -T db pg_dump -U taka takaos | gzip > backups/pre-deploy-$(date +%Y%m%d-%H%M%S).sql.gz

            # Zero-downtime deploy
            docker compose up -d --no-deps --scale api=2 api
            sleep 10
            docker compose up -d --no-deps --scale api=1 api

            # Frontend + nginx
            docker compose up -d --no-deps web nginx

            # Cleanup
            docker system prune -f
            docker volume prune -f

            # Health check
            sleep 5
            curl -f http://localhost:8000/health || exit 1
```

### 4.g. Health Endpoint (Backend)

```python
# backend/app/api/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
import psutil
import shutil

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    checks = {}

    # DB check
    try:
        await db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        raise HTTPException(status_code=503, detail=checks)

    # Disk check
    disk = shutil.disk_usage("/")
    disk_free_pct = disk.free / disk.total * 100
    checks["disk"] = {
        "status": "ok" if disk_free_pct > 10 else "warning",
        "free_percent": round(disk_free_pct, 1),
    }

    # Memory check
    memory = psutil.virtual_memory()
    checks["memory"] = {
        "status": "ok" if memory.percent < 90 else "warning",
        "used_percent": memory.percent,
    }

    return {
        "status": "healthy",
        "checks": checks,
        "version": "1.0.0",
    }
```

### 4.h. Logging Structure (Backend)

```python
# backend/app/core/logging.py
import structlog
import logging
import sys

# Configuration structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("takaos")

# Middleware FastAPI pour log des requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2),
        user=request.state.user.id if hasattr(request.state, "user") else None,
    )

    return response
```

### 4.i. Backup Automatique

```bash
#!/bin/bash
# scripts/backup.sh — Backup quotidien PostgreSQL + Uploads

set -euo pipefail

BACKUP_DIR="/opt/takaos/backups"
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=7
S3_BUCKET="${S3_BUCKET:-}"

# PostgreSQL backup
echo "[+] Backup PostgreSQL..."
docker compose exec -T db pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip > "${BACKUP_DIR}/db-${DATE}.sql.gz"

# Uploads backup
echo "[+] Backup Uploads..."
tar czf "${BACKUP_DIR}/uploads-${DATE}.tar.gz" -C /opt/takaos uploads/

# Cleanup local (retention 7 jours)
echo "[+] Cleanup local backups (> ${RETENTION_DAYS} jours)..."
find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
find "${BACKUP_DIR}" -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete

# Upload S3 (si configure)
if [ -n "$S3_BUCKET" ]; then
    echo "[+] Upload vers S3..."
    aws s3 cp "${BACKUP_DIR}/db-${DATE}.sql.gz" "s3://${S3_BUCKET}/db/"
    aws s3 cp "${BACKUP_DIR}/uploads-${DATE}.tar.gz" "s3://${S3_BUCKET}/uploads/"

    # Cleanup S3 (retention 30 jours)
    aws s3 ls "s3://${S3_BUCKET}/db/" | awk '$1 < "'$(date -d '30 days ago' +%Y-%m-%d)'" {print $4}' | xargs -I {} aws s3 rm "s3://${S3_BUCKET}/db/{}"
fi

echo "[+] Backup termine: ${DATE}"
```

```cron
# Crontab — Backup quotidien a 3h du matin
0 3 * * * /opt/takaos/scripts/backup.sh >> /var/log/takaos-backup.log 2>&1
```

### 4.j. Mise a Jour Zero-Downtime

**Strategie :** Blue-green via Docker Compose

```bash
#!/bin/bash
# scripts/deploy.sh — Zero-downtime deployment

set -e

echo "=== Deploiement TAKA OS ==="

# 1. Backup DB
docker compose exec -T db pg_dump -U taka takaos | gzip > "backups/pre-deploy-$(date +%s).sql.gz"

# 2. Pull images
docker compose pull

# 3. Start new containers (blue)
TAG=$TAG docker compose up -d --no-deps --scale api=2 --no-recreate api

# 4. Health check nouveau container
sleep 10
NEW_CONTAINER=$(docker compose ps -q api | tail -1)
docker exec "$NEW_CONTAINER" curl -f http://localhost:8000/health || {
    echo "[!] Health check failed — rollback"
    docker compose up -d --no-deps --scale api=1 api
    exit 1
}

# 5. Stop ancien container (green)
OLD_CONTAINER=$(docker compose ps -q api | head -1)
docker stop "$OLD_CONTAINER"
docker rm "$OLD_CONTAINER"

# 6. Scale back to 1
docker compose up -d --no-deps --scale api=1 api

# 7. Frontend + nginx
docker compose up -d --no-deps web nginx

# 8. Cleanup
docker system prune -f

echo "=== Deploiement OK ==="
```

### 4.k. Rollback

```bash
#!/bin/bash
# scripts/rollback.sh — Rollback vers version precedente

set -e

PREVIOUS_TAG=${1:-"$(git rev-parse HEAD~1)"}

echo "=== Rollback vers ${PREVIOUS_TAG} ==="

# Tag images precedentes
export TAG=${PREVIOUS_TAG}

# Redeploy
docker compose pull
docker compose up -d

echo "=== Rollback OK ==="
```

---

## 5. Securite Frontend

### 5.a. CSP Headers (via Nginx)

```nginx
# Ajouter dans le server block Nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self' /api; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
```

### 5.b. Validation des Inputs (Zod)

```typescript
// src/lib/validators.ts
import { z } from "zod";

export const tenderSchema = z.object({
  reference: z.string().min(1, "Reference requise").max(100),
  title: z.string().min(1, "Titre requis").max(500),
  description: z.string().max(5000).optional(),
  buyer: z.string().min(1, "Acheteur requis").max(200),
  deadline: z.string().datetime("Date invalide"),
  estimated_value: z.number().min(0).optional(),
  cpv_code: z.string().regex(/^\d{8}-\d$/, "Code CPV invalide (format: 12345678-9)").optional(),
  location: z.string().max(200).optional(),
  procedure_type: z.enum(["open", "restricted", "negotiated", "dialogue"]).optional(),
});

export const loginSchema = z.object({
  email: z.string().email("Email invalide").max(255),
  password: z.string().min(8, "Min. 8 caracteres").max(128),
});

export const userInviteSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(["admin", "manager", "viewer"]),
});
```

### 5.c. Variables d'Environnement Vite

```bash
# .env.development
VITE_API_URL=http://localhost:8000

# .env.production
VITE_API_URL=/api
```

**Regles :**
- Toutes les variables Vite doivent commencer par `VITE_`
- Jamais de secrets (clés API, tokens) dans les variables Vite publics
- Les secrets backend restent côté backend uniquement
- `import.meta.env` pour accéder aux variables

### 5.d. Gestion des Tokens

```typescript
// src/services/auth.service.ts
class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/login", credentials);

    // Stockage securise
    this.setToken(response.data.access_token);

    return response.data;
  }

  private setToken(token: string): void {
    // En production : httpOnly cookie gere par le backend
    // En dev : stockage memoire Zustand uniquement
    if (import.meta.env.PROD) {
      // Le backend set un httpOnly cookie
      return;
    }
    useAuthStore.getState().token = token;
  }

  async refresh(): Promise<{ access_token: string }> {
    const response = await api.post("/auth/refresh");
    return response.data;
  }

  logout(): void {
    // Appel au backend pour invalider le token
    api.post("/auth/logout").catch(() => {});
  }
}

export const authService = new AuthService();
```

### 5.e. Sécurité Routing

```tsx
// Route guards deja definis dans App.tsx
// Protection supplementaire : hook usePermission

export function usePermission(permission: Permission): boolean {
  const { user } = useAuthStore();
  const rolePermissions: Record<Role, Permission[]> = {
    admin: ["read", "write", "delete", "manage_users", "manage_settings", "view_audit"],
    manager: ["read", "write", "delete", "manage_settings"],
    viewer: ["read"],
  };
  return user ? rolePermissions[user.role].includes(permission) : false;
}
```

### 5.f. Checklist Sécurite Frontend

| # | Controle | Statut | Implementation |
|---|----------|--------|----------------|
| 1 | HTTPS only | Obligatoire | Nginx redirect 80→443 + HSTS |
| 2 | CSP headers | Obligatoire | Nginx add_header CSP |
| 3 | X-Frame-Options | Obligatoire | Nginx SAMEORIGIN |
| 4 | X-Content-Type-Options | Obligatoire | Nginx nosniff |
| 5 | Input validation | Obligatoire | Zod schemas tous formulaires |
| 6 | Output encoding | Obligatoire | React JSX auto-escape |
| 7 | No secrets in code | Obligatoire | .env + variables d'environnement |
| 8 | JWT httpOnly cookie | Recommande | Backend set cookie, pas localStorage |
| 9 | Token refresh auto | Obligatoire | Axios interceptor 401 → refresh |
| 10 | Rate limiting | Obligatoire | Nginx limit_req 10r/s |
| 11 | Session timeout | Recommande | JWT expiry 15min, refresh 7j |
| 12 | Audit logging | Obligatoire | Toutes les actions CRUD loggees |
| 13 | Dependency scanning | Recommande | Dependabot + npm audit |

---

## 6. Annexes

### 6.a. package.json Frontend

```json
{
  "name": "takaos-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@dnd-kit/core": "^6.1.0",
    "@dnd-kit/sortable": "^8.0.0",
    "@dnd-kit/utilities": "^3.2.2",
    "@hookform/resolvers": "^3.3.4",
    "@radix-ui/react-accordion": "^1.1.2",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-popover": "^1.0.7",
    "@radix-ui/react-progress": "^1.0.3",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-separator": "^1.0.3",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-switch": "^1.0.3",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-tooltip": "^1.0.7",
    "@tanstack/react-query": "^5.17.0",
    "@tanstack/react-table": "^8.11.0",
    "axios": "^1.6.5",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "date-fns": "^3.0.6",
    "lucide-react": "^0.303.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-dropzone": "^14.2.3",
    "react-hook-form": "^7.49.2",
    "react-router-dom": "^6.21.1",
    "recharts": "^2.10.3",
    "tailwind-merge": "^2.2.0",
    "tailwindcss-animate": "^1.0.7",
    "zod": "^3.22.4",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.46",
    "@types/react-dom": "^18.2.18",
    "@typescript-eslint/eslint-plugin": "^6.16.0",
    "@typescript-eslint/parser": "^6.16.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.56.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.3",
    "vite": "^5.0.10"
  }
}
```

### 6.b. Structure des Types TypeScript

```typescript
// src/types/auth.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "manager" | "viewer";
  tenant_id: string;
  created_at: string;
  last_login: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// src/types/tender.ts
export type Stage = "draft" | "identified" | "qualified" | "preparing" | "submitted" | "awarded" | "lost" | "cancelled";

export type Qualification = "GO" | "MAYBE" | "NO-GO" | "PENDING";

export interface Tender {
  id: string;
  reference: string;
  title: string;
  description: string | null;
  buyer: string;
  deadline: string;
  estimated_value: number | null;
  cpv_code: string | null;
  location: string | null;
  procedure_type: string | null;
  stage: Stage;
  qualification: Qualification;
  qualification_result: QualificationResult | null;
  documents: Document[];
  created_at: string;
  updated_at: string;
  created_by: string;
  tenant_id: string;
}

export interface QualificationResult {
  id: string;
  tender_id: string;
  verdict: Qualification;
  overall_score: number;
  criteria_scores: Record<string, number>;
  justification: string;
  created_at: string;
}

// src/types/api.ts
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

### 6.c. Commandes Utiles

```bash
# === DEVELOPPEMENT ===
# Lancer le frontend
cd frontend && npm run dev        # http://localhost:3000

# Lancer le backend
cd backend && uvicorn app.main:app --reload --port 8000

# === DOCKER LOCAL ===
docker compose up -d              # Tout demarrer
docker compose logs -f api        # Logs API
docker compose exec db psql -U taka -d takaos  # Shell PostgreSQL

# === PRODUCTION ===
# Deploy
cd /opt/takaos && git pull && ./scripts/deploy.sh

# Backup manuel
cd /opt/takaos && ./scripts/backup.sh

# Logs production
docker compose logs -f --tail 100

# Stats ressources
docker stats
```

### 6.d. Matrice des Permissions

| Fonctionnalite | Admin | Manager | Viewer |
|----------------|-------|---------|--------|
| Dashboard | ✅ | ✅ | ✅ |
| Liste AO | ✅ | ✅ | ✅ |
| Fiche AO (lecture) | ✅ | ✅ | ✅ |
| Fiche AO (edition) | ✅ | ✅ | ❌ |
| Creer AO | ✅ | ✅ | ❌ |
| Supprimer AO | ✅ | ✅ | ❌ |
| Qualifier AO | ✅ | ✅ | ❌ |
| Pipeline Kanban (DnD) | ✅ | ✅ | ❌ |
| Pipeline Kanban (vue) | ✅ | ✅ | ✅ |
| Upload DCE | ✅ | ✅ | ❌ |
| Memoire (recherche) | ✅ | ✅ | ✅ |
| Parametres profil | ✅ | ✅ | ✅ |
| Parametres tenant | ✅ | ❌ | ❌ |
| Gestion utilisateurs | ✅ | ❌ | ❌ |
| Audit Logs | ✅ | ❌ | ❌ |

---

**Fin de la Section 4 — Frontend & DevOps**

*Ce document specifie l'integralite de l'architecture frontend et de l'infrastructure DevOps pour TAKA OS. Toutes les technologies, composants, stores, pipelines CI/CD et procedures de deploiement sont detailles avec des exemples de code fonctionnels.*
