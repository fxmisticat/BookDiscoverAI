import { FormEvent, useCallback, useEffect, useState } from "react";
import { apiRequest } from "../hooks/useApi";

type Settings = {
  abs_url?: string;
  google_books_api_key?: string;
  open_library_enabled: boolean;
  embedding_provider: string;
  embedding_model: string;
  llm_provider: string;
  llm_model: string;
  demo_mode: boolean;
};

type SyncStatus = {
  id: number;
  job_type: string;
  status: string;
  message?: string;
  started_at: string;
  finished_at?: string;
} | null;

type TropeExtractionResponse = {
  status: string;
  scheduled: boolean;
  processed: number;
  message: string;
};

const SettingsPage = () => {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>(null);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [tropeProcessing, setTropeProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadSettings = useCallback(async () => {
    try {
      const response = await apiRequest<Settings>("/api/settings");
      setSettings(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load settings");
    }
  }, []);

  const loadSyncStatus = useCallback(async () => {
    try {
      const response = await apiRequest<SyncStatus>("/api/abs/status");
      setSyncStatus(response);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    void loadSettings();
    void loadSyncStatus();
  }, [loadSettings, loadSyncStatus]);

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      if (!settings) return;
      setSaving(true);
      setError(null);
      setSuccess(null);
      try {
        const formData = new FormData(event.currentTarget);
        const payload = {
          abs_url: formData.get("abs_url")?.toString() || undefined,
          abs_token: formData.get("abs_token")?.toString() || undefined,
          google_books_api_key: formData.get("google_books_api_key")?.toString() || undefined,
          open_library_enabled: formData.get("open_library_enabled") === "on",
          embedding_provider: formData.get("embedding_provider")?.toString() || "openai",
          embedding_model: formData.get("embedding_model")?.toString() || "text-embedding-3-small",
          llm_provider: formData.get("llm_provider")?.toString() || "openai",
          llm_model: formData.get("llm_model")?.toString() || "gpt-4o-mini",
          demo_mode: formData.get("demo_mode") === "on"
        };
        const response = await apiRequest<Settings>("/api/settings", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        setSettings(response);
        setSuccess("Settings updated");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to save settings");
      } finally {
        setSaving(false);
      }
    },
    [settings]
  );

  const triggerSync = useCallback(async () => {
    setSyncing(true);
    setError(null);
    try {
      const response = await apiRequest<SyncStatus>("/api/abs/sync", {
        method: "POST"
      });
      setSyncStatus(response);
      setSuccess("Sync started");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start sync");
    } finally {
      setSyncing(false);
      void loadSyncStatus();
    }
  }, [loadSyncStatus]);

  const triggerTropeJob = useCallback(
    async (force: boolean) => {
      setTropeProcessing(true);
      setError(null);
      setSuccess(null);
      try {
        const endpoint = force ? "/api/tropes/refresh" : "/api/tropes/extract";
        const response = await apiRequest<TropeExtractionResponse>(endpoint, { method: "POST" });
        setSuccess(response.message || "Trope discovery job queued");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to queue trope extraction");
      } finally {
        setTropeProcessing(false);
      }
    },
    []
  );

  if (!settings) {
    return <div className="status-banner">Loading settings…</div>;
  }

  return (
    <div>
      {error && <div className="empty-state">{error}</div>}
      {success && <div className="status-banner">{success}</div>}
      <form className="settings-form" onSubmit={handleSubmit}>
        <div className="settings-field">
          <label htmlFor="abs_url">Audiobookshelf URL</label>
          <input id="abs_url" name="abs_url" placeholder="https://abs.local" defaultValue={settings.abs_url || ""} />
        </div>
        <div className="settings-field">
          <label htmlFor="abs_token">Audiobookshelf API Token</label>
          <input id="abs_token" name="abs_token" type="password" placeholder="Paste token" />
        </div>
        <div className="settings-field">
          <label htmlFor="google_books_api_key">Google Books API Key</label>
          <input
            id="google_books_api_key"
            name="google_books_api_key"
            placeholder="Optional"
            defaultValue={settings.google_books_api_key || ""}
          />
        </div>
        <div className="settings-field">
          <label htmlFor="embedding_provider">Embedding Provider</label>
          <select id="embedding_provider" name="embedding_provider" defaultValue={settings.embedding_provider}>
            <option value="openai">OpenAI</option>
            <option value="huggingface">HuggingFace</option>
          </select>
        </div>
        <div className="settings-field">
          <label htmlFor="embedding_model">Embedding Model</label>
          <input id="embedding_model" name="embedding_model" defaultValue={settings.embedding_model} />
        </div>
        <div className="settings-field">
          <label htmlFor="llm_provider">LLM Provider</label>
          <select id="llm_provider" name="llm_provider" defaultValue={settings.llm_provider}>
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
          </select>
        </div>
        <div className="settings-field">
          <label htmlFor="llm_model">LLM Model</label>
          <input id="llm_model" name="llm_model" defaultValue={settings.llm_model} />
        </div>
        <div className="settings-field">
          <label>
            <input type="checkbox" name="open_library_enabled" defaultChecked={settings.open_library_enabled} /> Enable Open
            Library fallback
          </label>
        </div>
        <div className="settings-field">
          <label>
            <input type="checkbox" name="demo_mode" defaultChecked={settings.demo_mode} /> Demo mode (use seed data)
          </label>
        </div>
        <div className="settings-actions">
          <button type="submit" className="primary-button" disabled={saving}>
            {saving ? "Saving…" : "Save"}
          </button>
          <button type="button" className="secondary-button" onClick={() => triggerSync()} disabled={syncing}>
            {syncing ? "Syncing…" : "Run sync"}
          </button>
        </div>
      </form>
      {syncStatus && (
        <div style={{ marginTop: "1.5rem", fontSize: "0.85rem", color: "#475569" }}>
          <p style={{ margin: "0 0 0.25rem" }}>
            Last job status: <strong>{syncStatus.status}</strong>
          </p>
          {syncStatus.message && <p style={{ margin: 0 }}>{syncStatus.message}</p>}
        </div>
      )}
      <section style={{ marginTop: "2rem" }}>
        <h3 style={{ margin: "0 0 0.5rem", fontSize: "1rem", color: "#1e293b" }}>Trope Discovery Engine</h3>
        <p style={{ margin: "0 0 1rem", fontSize: "0.85rem", color: "#475569" }}>
          Tag your library with romantasy tropes and generate trope-matched recommendations.
        </p>
        <div className="settings-actions">
          <button
            type="button"
            className="primary-button"
            onClick={() => triggerTropeJob(false)}
            disabled={tropeProcessing}
          >
            {tropeProcessing ? "Queuing…" : "Extract tropes"}
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={() => triggerTropeJob(true)}
            disabled={tropeProcessing}
          >
            Refresh tags
          </button>
        </div>
      </section>
    </div>
  );
};

export default SettingsPage;
