import { useCallback, useEffect, useState } from "react";
import { apiRequest } from "../hooks/useApi";

type LogEntry = {
  id: number;
  level: string;
  source: string;
  message: string;
  context?: Record<string, unknown> | null;
  created_at: string;
};

type LogsResponse = {
  items: LogEntry[];
};

const levelBadgeClass = (level: string) => {
  switch (level.toUpperCase()) {
    case "ERROR":
      return "badge error";
    case "WARNING":
      return "badge warning";
    case "SUCCESS":
      return "badge success";
    default:
      return "badge info";
  }
};

const LogsPage = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiRequest<LogsResponse>("/api/logs");
      setLogs(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load logs");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchLogs();
    const interval = window.setInterval(() => {
      void fetchLogs();
    }, 8000);
    return () => window.clearInterval(interval);
  }, [fetchLogs]);

  if (loading) {
    return <div className="status-banner">Loading logs…</div>;
  }

  if (error) {
    return (
      <div className="empty-state">
        <p>{error}</p>
        <button className="secondary-button" type="button" onClick={() => fetchLogs()}>
          Retry
        </button>
      </div>
    );
  }

  if (logs.length === 0) {
    return <div className="empty-state">No log entries yet. Actions in the app will appear here.</div>;
  }

  return (
    <div className="log-list">
      {logs.map((log) => (
        <div key={log.id} className="log-item">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className={levelBadgeClass(log.level)}>{log.level}</span>
            <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>{new Date(log.created_at).toLocaleString()}</span>
          </div>
          <p style={{ margin: "0.5rem 0", color: "#1e293b" }}>{log.message}</p>
          <p style={{ margin: 0, fontSize: "0.75rem", color: "#475569" }}>Source: {log.source}</p>
          {log.context && (
            <pre style={{ marginTop: "0.5rem", background: "#0f172a", color: "#e2e8f0", padding: "0.5rem", borderRadius: "0.5rem", fontSize: "0.7rem" }}>
              {JSON.stringify(log.context, null, 2)}
            </pre>
          )}
        </div>
      ))}
    </div>
  );
};

export default LogsPage;
