import { FC, useState, useEffect } from "react";
import { useAuth } from "../components/AuthContext";

type Tab = "comments" | "workflows" | "notifications";

const CollaborationPage: FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>("comments");

  const tabs: { id: Tab; label: string }[] = [
    { id: "comments", label: "Commentaires" },
    { id: "workflows", label: "Approbations" },
    { id: "notifications", label: "Notifications" },
  ];

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Collaboration</h2>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", borderBottom: "2px solid #eee" }}>
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              padding: "0.5rem 1rem",
              borderBottom: activeTab === t.id ? "2px solid #e94560" : "2px solid transparent",
              fontWeight: activeTab === t.id ? "bold" : "normal",
              background: "none",
              border: "none",
              cursor: "pointer",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "comments" && <CommentsTab />}
      {activeTab === "workflows" && <WorkflowsTab />}
      {activeTab === "notifications" && <NotificationsTab />}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMMENTS TAB
// ═══════════════════════════════════════════════════════════════════════════════

const CommentsTab: FC = () => {
  const { token } = useAuth();
  const [aoId, setAoId] = useState("");
  const [comments, setComments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState("");
  const [replyTo, setReplyTo] = useState<string | null>(null);
  const [error, setError] = useState("");

  const loadComments = async () => {
    if (!aoId || !token) return;
    setError("");
    try {
      const res = await fetch(`/api/v1/comments/ao/${aoId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Erreur chargement commentaires");
      const json = await res.json();
      setComments(json.comments || []);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const postComment = async () => {
    if (!newComment.trim() || !aoId || !token) return;
    try {
      const res = await fetch(`/api/v1/comments/ao/${aoId}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: newComment, parent_id: replyTo }),
      });
      if (!res.ok) throw new Error("Erreur envoi commentaire");
      setNewComment("");
      setReplyTo(null);
      loadComments();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <input
          type="text"
          value={aoId}
          onChange={(e) => setAoId(e.target.value)}
          placeholder="ID de l'AO"
          style={{ flex: 1, padding: "0.5rem", border: "1px solid #ccc", borderRadius: "0.25rem" }}
        />
        <button
          onClick={loadComments}
          style={{ padding: "0.5rem 1rem", background: "#333", color: "#fff", border: "none", borderRadius: "0.25rem", cursor: "pointer" }}
        >
          Charger
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {comments.map((c: any) => (
          <CommentItem key={c.id} comment={c} onReply={setReplyTo} depth={0} />
        ))}
      </div>

      <div style={{ background: "#fff", padding: "1rem", borderRadius: "0.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        {replyTo && (
          <div style={{ fontSize: "0.875rem", color: "#e94560", marginBottom: "0.5rem" }}>
            Reponse a un commentaire
            <button onClick={() => setReplyTo(null)} style={{ marginLeft: "0.5rem", color: "#666", background: "none", border: "none", cursor: "pointer" }}>
              (annuler)
            </button>
          </div>
        )}
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Votre commentaire... Utilisez @nom pour mentionner"
          style={{ width: "100%", minHeight: "80px", padding: "0.5rem", border: "1px solid #ccc", borderRadius: "0.25rem", resize: "vertical" }}
        />
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "0.5rem" }}>
          <button
            onClick={postComment}
            style={{ padding: "0.5rem 1rem", background: "#0f3460", color: "#fff", border: "none", borderRadius: "0.25rem", cursor: "pointer" }}
          >
            Envoyer
          </button>
        </div>
      </div>
    </div>
  );
};

function CommentItem({ comment, onReply, depth }: { comment: any; onReply: (id: string) => void; depth: number }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div
      style={{
        background: "#fff",
        padding: "1rem",
        borderRadius: "0.5rem",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        marginLeft: depth > 0 ? "2rem" : 0,
        borderLeft: depth > 0 ? "3px solid #e94560" : "none",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <p style={{ whiteSpace: "pre-wrap", margin: 0 }}>{comment.content}</p>
          <div style={{ display: "flex", gap: "1rem", marginTop: "0.5rem", fontSize: "0.8rem", color: "#666" }}>
            <span>{comment.created_at ? new Date(comment.created_at).toLocaleString("fr-FR") : ""}</span>
            {comment.is_edited && <span>(modifie)</span>}
            <button
              onClick={() => onReply(comment.id)}
              style={{ color: "#0f3460", background: "none", border: "none", cursor: "pointer", fontSize: "0.8rem" }}
            >
              Repondre
            </button>
          </div>
        </div>
        {comment.status === "resolved" && (
          <span style={{ color: "#10b981", fontSize: "0.8rem", fontWeight: "bold" }}>Resolu</span>
        )}
      </div>

      {comment.replies?.length > 0 && (
        <div style={{ marginTop: "0.5rem" }}>
          <button
            onClick={() => setExpanded(!expanded)}
            style={{ fontSize: "0.8rem", color: "#666", background: "none", border: "none", cursor: "pointer" }}
          >
            {expanded ? "▼" : "▶"} {comment.replies.length} reponse(s)
          </button>
          {expanded && (
            <div style={{ marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {comment.replies.map((reply: any) => (
                <CommentItem key={reply.id} comment={reply} onReply={onReply} depth={depth + 1} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// WORKFLOWS TAB
// ═══════════════════════════════════════════════════════════════════════════════

const WorkflowsTab: FC = () => {
  const { token } = useAuth();
  const [requests, setRequests] = useState<any[]>([]);
  const [error, setError] = useState("");

  const loadRequests = async () => {
    if (!token) return;
    try {
      const res = await fetch("/api/v1/workflows/requests", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Erreur chargement workflows");
      const json = await res.json();
      setRequests(json.requests || []);
    } catch (e: any) {
      setError(e.message);
    }
  };

  useEffect(() => {
    loadRequests();
  }, [token]);

  const decide = async (requestId: string, decision: string) => {
    if (!token) return;
    try {
      const res = await fetch(`/api/v1/workflows/requests/${requestId}/decide`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ decision }),
      });
      if (!res.ok) throw new Error("Erreur decision");
      loadRequests();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <h3>Demandes d'approbation en cours</h3>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {requests.length === 0 ? (
        <p style={{ color: "#666", textAlign: "center", padding: "2rem" }}>Aucune demande en attente</p>
      ) : (
        requests.map((req: any) => (
          <div key={req.id} style={{ background: "#fff", padding: "1rem", borderRadius: "0.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p style={{ margin: 0, fontWeight: "bold" }}>Demande #{req.id.slice(0, 8)}</p>
                <p style={{ margin: 0, fontSize: "0.85rem", color: "#666" }}>
                  Etape {req.current_step} — {req.status}
                </p>
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button
                  onClick={() => decide(req.id, "approved")}
                  style={{ padding: "0.4rem 0.8rem", background: "#10b981", color: "#fff", border: "none", borderRadius: "0.25rem", cursor: "pointer", fontSize: "0.85rem" }}
                >
                  Approuver
                </button>
                <button
                  onClick={() => decide(req.id, "rejected")}
                  style={{ padding: "0.4rem 0.8rem", background: "#e94560", color: "#fff", border: "none", borderRadius: "0.25rem", cursor: "pointer", fontSize: "0.85rem" }}
                >
                  Rejeter
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// NOTIFICATIONS TAB
// ═══════════════════════════════════════════════════════════════════════════════

const NotificationsTab: FC = () => {
  const { token } = useAuth();
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [error, setError] = useState("");

  const loadNotifications = async () => {
    if (!token) return;
    try {
      const res = await fetch("/api/v1/notifications", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Erreur chargement notifications");
      const json = await res.json();
      setNotifications(json.items || []);
      setUnreadCount(json.unread_count || 0);
    } catch (e: any) {
      setError(e.message);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, [token]);

  const markRead = async (id: string) => {
    if (!token) return;
    try {
      await fetch(`/api/v1/notifications/${id}/read`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      loadNotifications();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const markAllRead = async () => {
    if (!token) return;
    try {
      await fetch("/api/v1/notifications/read-all", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      loadNotifications();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>
          Notifications
          {unreadCount > 0 && (
            <span
              style={{
                background: "#e94560",
                color: "#fff",
                fontSize: "0.75rem",
                padding: "0.2rem 0.5rem",
                borderRadius: "1rem",
                marginLeft: "0.5rem",
              }}
            >
              {unreadCount}
            </span>
          )}
        </h3>
        {unreadCount > 0 && (
          <button
            onClick={markAllRead}
            style={{ color: "#0f3460", background: "none", border: "none", cursor: "pointer", fontSize: "0.85rem" }}
          >
            Tout marquer comme lu
          </button>
        )}
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {notifications.length === 0 ? (
        <p style={{ color: "#666", textAlign: "center", padding: "2rem" }}>Aucune notification</p>
      ) : (
        notifications.map((n: any) => (
          <div
            key={n.id}
            onClick={() => !n.is_read && markRead(n.id)}
            style={{
              padding: "1rem",
              borderRadius: "0.5rem",
              cursor: n.is_read ? "default" : "pointer",
              background: n.is_read ? "#f5f5f5" : "#fff",
              boxShadow: n.is_read ? "none" : "0 1px 3px rgba(0,0,0,0.1)",
              borderLeft: n.is_read ? "none" : "4px solid #0f3460",
            }}
          >
            <div style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem" }}>
              <span style={{ fontSize: "1rem" }}>{n.is_read ? "🔕" : "🔔"}</span>
              <div style={{ flex: 1 }}>
                <p style={{ margin: 0, fontWeight: n.is_read ? "normal" : "bold", color: n.is_read ? "#666" : "#111" }}>
                  {n.title}
                </p>
                <p style={{ margin: 0, fontSize: "0.85rem", color: "#666" }}>{n.message}</p>
                <p style={{ margin: "0.25rem 0 0", fontSize: "0.75rem", color: "#999" }}>
                  {n.created_at ? new Date(n.created_at).toLocaleString("fr-FR") : ""}
                </p>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default CollaborationPage;
