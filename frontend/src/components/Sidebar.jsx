import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Image,
  History,
  Camera,
  Video,
  X,
} from "lucide-react";
import API from "../api/axiosInstance";

const links = [
  { name: "Dashboard",        path: "/",               icon: LayoutDashboard },
  { name: "Image Detection",  path: "/image-detection",icon: Image },
  { name: "Video Detection",  path: "/video-detection",icon: Video },
  { name: "Live Monitoring",  path: "/live-monitoring",icon: Camera },
  { name: "History",          path: "/history",        icon: History },
];

function NavLink({ link, active, onClick }) {
  const Icon = link.icon;
  return (
    <Link
      to={link.path}
      onClick={onClick}
      className={`vrs-nav-link ${active ? "active" : ""}`}
    >
      <Icon size={16} strokeWidth={active ? 2.5 : 1.8} />
      {link.name}
    </Link>
  );
}

function Sidebar() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        await API.get("/health");
        setBackendOnline(true);
      } catch (error) {
        setBackendOnline(false);
      }
    };

    checkBackendStatus();

    const interval = setInterval(checkBackendStatus, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* ── Desktop sidebar ────────────────────────────── */}
      <aside className="vrs-sidebar">
        <div className="vrs-sidebar__logo">
          <div className="vrs-sidebar__logo-title">
            AI<span>.</span>Security
          </div>
          <div className="vrs-sidebar__logo-sub">Vehicle Recognition System</div>
        </div>

        <nav className="vrs-sidebar__nav">
          {links.map((link) => (
            <NavLink
              key={link.path}
              link={link}
              active={location.pathname === link.path}
            />
          ))}
        </nav>

        <div className="vrs-sidebar__footer">
          <div
            className="vrs-sidebar__status"
            style={{
              color: backendOnline ? "#4ade80" : "#FF0000",
            }}
          >
            <span className={`vrs-status-dot ${backendOnline ? "" : "red"}`} />
            {backendOnline ? "System Online" : "System Offline"}
          </div>
        </div>
      </aside>

      {/* ── Mobile top navbar ──────────────────────────── */}
      <div className="vrs-mobile-nav">
        <div className="vrs-mobile-nav__bar">
          <div className="vrs-mobile-nav__title">
            AI<span>.</span>Vision
          </div>
          <button
            className="vrs-hamburger"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? (
              <X size={18} />
            ) : (
              <>
                <span />
                <span />
                <span />
              </>
            )}
          </button>
        </div>

        {mobileOpen && (
          <div className="vrs-mobile-menu">
            {links.map((link) => (
              <NavLink
                key={link.path}
                link={link}
                active={location.pathname === link.path}
                onClick={() => setMobileOpen(false)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Pushes content below fixed mobile nav */}
      <div className="vrs-mobile-spacer" />
    </>
  );
}

export default Sidebar;