import { useMemo, useState } from "react";
import FeedPage from "./pages/FeedPage";
import LogsPage from "./pages/LogsPage";
import SettingsPage from "./pages/SettingsPage";
import NavigationTabs from "./components/NavigationTabs";

type TabKey = "feed" | "settings" | "logs";

const App = () => {
  const [activeTab, setActiveTab] = useState<TabKey>("feed");

  const renderContent = useMemo(() => {
    switch (activeTab) {
      case "feed":
        return <FeedPage />;
      case "settings":
        return <SettingsPage />;
      case "logs":
        return <LogsPage />;
      default:
        return null;
    }
  }, [activeTab]);

  return (
    <div className="app-container">
      <NavigationTabs
        activeTab={activeTab}
        onTabChange={setActiveTab}
        tabs={[
          { key: "feed", label: "Discover" },
          { key: "settings", label: "Settings" },
          { key: "logs", label: "Logs" }
        ]}
      />
      {renderContent}
      <footer style={{ marginTop: "2rem", textAlign: "center", fontSize: "0.75rem", color: "#94a3b8" }}>
        BookDiscoverAI · v{__APP_VERSION__}
      </footer>
    </div>
  );
};

export default App;
