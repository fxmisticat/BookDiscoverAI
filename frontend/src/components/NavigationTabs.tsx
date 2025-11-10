import type { FC } from "react";

type Tab = {
  key: string;
  label: string;
};

type NavigationTabsProps = {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (key: string) => void;
};

const NavigationTabs: FC<NavigationTabsProps> = ({ tabs, activeTab, onTabChange }) => {
  return (
    <nav className="tab-bar" role="tablist" aria-label="Primary navigation">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          type="button"
          role="tab"
          aria-selected={activeTab === tab.key}
          className={`tab-button${activeTab === tab.key ? " active" : ""}`}
          onClick={() => onTabChange(tab.key)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
};

export default NavigationTabs;
