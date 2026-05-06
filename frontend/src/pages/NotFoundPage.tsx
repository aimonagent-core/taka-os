import { FC } from "react";
import { Link } from "react-router-dom";

const NotFoundPage: FC = () => {
  return (
    <div
      style={{
        minHeight: "80vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
      }}
    >
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>🔍</div>
        <h1 style={{ fontSize: "4rem", margin: 0, color: "#1a1a2e" }}>404</h1>
        <p style={{ fontSize: "1.25rem", color: "#666", margin: "0.5rem 0" }}>Page non trouvee</p>
        <p style={{ color: "#999", marginBottom: "2rem" }}>
          La page que vous recherchez n'existe pas ou a ete deplacee.
        </p>
        <Link
          to="/"
          style={{
            display: "inline-block",
            padding: "0.75rem 1.5rem",
            background: "#0f3460",
            color: "#fff",
            textDecoration: "none",
            borderRadius: "0.5rem",
          }}
        >
          🏠 Retour a l'accueil
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;
