// File: frontend/src/main.tsx
// Purpose: React application entry point with Sentry initialization
// Dependencies: @sentry/react, react-router-dom

import { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from "@sentry/react";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;
const APP_VERSION = import.meta.env.VITE_APP_VERSION || "0.2.0";
const ENVIRONMENT = import.meta.env.VITE_ENVIRONMENT || "development";

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    release: APP_VERSION,
    environment: ENVIRONMENT,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: false,
        blockAllMedia: false,
      }),
    ],
    tracesSampleRate: ENVIRONMENT === "production" ? 0.1 : 1.0,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  });
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
