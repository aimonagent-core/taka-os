// File: frontend/src/components/ErrorBoundary.tsx
// Purpose: React Error Boundary with Sentry error reporting
// Dependencies: @sentry/react, react

import { Component, type ReactNode, type ErrorInfo } from "react";
import * as Sentry from "@sentry/react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    Sentry.captureException(error, {
      extra: { componentStack: errorInfo.componentStack },
    });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div
          style={{
            minHeight: "80vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "2rem",
            background: "#f5f5f5",
          }}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: "0.5rem",
              boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
              padding: "2rem",
              maxWidth: "480px",
              width: "100%",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>⚠️</div>
            <h1 style={{ fontSize: "1.5rem", margin: "0 0 0.5rem", color: "#1a1a2e" }}>
              Une erreur est survenue
            </h1>
            <p style={{ color: "#666", marginBottom: "1rem" }}>
              Nous sommes desoles, une erreur inattendue s'est produite.
              L'equipe TAKA a ete notifiee.
            </p>
            {import.meta.env.DEV && this.state.error && (
              <pre
                style={{
                  background: "#f5f5f5",
                  borderRadius: "0.25rem",
                  padding: "0.75rem",
                  fontSize: "0.75rem",
                  textAlign: "left",
                  color: "#666",
                  overflow: "auto",
                  maxHeight: "120px",
                  marginBottom: "1rem",
                }}
              >
                {this.state.error.message}
              </pre>
            )}
            <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center" }}>
              <button
                onClick={() => window.location.reload()}
                style={{
                  padding: "0.5rem 1rem",
                  background: "#0f3460",
                  color: "#fff",
                  border: "none",
                  borderRadius: "0.25rem",
                  cursor: "pointer",
                }}
              >
                🔄 Rafraichir
              </button>
              <a
                href="/"
                style={{
                  padding: "0.5rem 1rem",
                  background: "#e3e3e3",
                  color: "#333",
                  textDecoration: "none",
                  borderRadius: "0.25rem",
                }}
              >
                🏠 Accueil
              </a>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
