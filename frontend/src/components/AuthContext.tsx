// File: frontend/src/components/AuthContext.tsx
// Purpose: Authentication context provider with auto-hydration from /me

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { useAuthStore } from "../store/useAuthStore";

interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  tenant_id: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [initialized, setInitialized] = useState(false);
  const { setAuth, clearAuth } = useAuthStore();

  const login = useCallback((newToken: string, newUser: User) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setUser(newUser);
    setAuth(
      {
        id: Number(newUser.id),
        email: newUser.email,
        first_name: newUser.full_name?.split(" ")[0] || null,
        last_name: newUser.full_name?.split(" ").slice(1).join(" ") || null,
        role: newUser.role,
      },
      newToken
    );
  }, [setAuth]);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    clearAuth();
    // Appel optionnel au backend pour tracer le logout
    fetch("/api/v1/auth/logout", {
      method: "POST",
      headers: { Authorization: `Bearer ${localStorage.getItem("token") || ""}` },
    }).catch(() => {
      // silencieux
    });
  }, [clearAuth]);

  // Hydratation initiale : si un token existe, on récupère /me
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (!storedToken) {
      setInitialized(true);
      return;
    }

    let cancelled = false;
    fetch("/api/v1/auth/me", {
      headers: { Authorization: `Bearer ${storedToken}` },
    })
      .then(async (res) => {
        if (!res.ok) {
          // Token invalide, on nettoie
          localStorage.removeItem("token");
          clearAuth();
          return;
        }
        const json = await res.json();
        const meUser = json.data;
        if (!meUser || cancelled) return;

        const userObj: User = {
          id: String(meUser.id),
          email: meUser.email,
          full_name: meUser.full_name || null,
          role: meUser.role,
          tenant_id: String(meUser.tenant_id),
        };
        setToken(storedToken);
        setUser(userObj);
        setAuth(
          {
            id: Number(userObj.id),
            email: userObj.email,
            first_name: userObj.full_name?.split(" ")[0] || null,
            last_name: userObj.full_name?.split(" ").slice(1).join(" ") || null,
            role: userObj.role,
          },
          storedToken
        );
      })
      .catch(() => {
        // Réseau indisponible, on garde le token en local pour retry plus tard
      })
      .finally(() => {
        if (!cancelled) setInitialized(true);
      });

    return () => { cancelled = true; };
  }, [clearAuth, setAuth]);

  if (!initialized) {
    // Petit loader pour éviter le flash de connexion/déconnexion
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
