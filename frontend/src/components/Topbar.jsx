import { LogoMark, MenuIcon, MoonIcon, SunIcon } from "./icons";

export default function Topbar({ isDarkMode, onToggleSidebar, onToggleTheme }) {
  return (
    <header className="topbar">
      <div className="topbar-brand">
        <button
          className="mobile-menu-button"
          type="button"
          aria-label="Open sidebar"
          onClick={onToggleSidebar}
        >
          <MenuIcon />
        </button>
        <LogoMark />
        <div className="topbar-copy">
          <h2>JUIT AI Assistant</h2>
          <p>Ask about admissions, academics, placements, campus life, and policies.</p>
        </div>
      </div>

      <div className="topbar-actions">
        <span className="status-pill">Online</span>
        <button
          className="icon-button"
          type="button"
          onClick={onToggleTheme}
          aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
          {isDarkMode ? <SunIcon /> : <MoonIcon />}
        </button>
      </div>
    </header>
  );
}
