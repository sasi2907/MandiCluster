import {
  LayoutDashboard,
  Sprout,
  Layers3,
  Store,
  Leaf,
} from "lucide-react";

function Sidebar() {
  return (
    <aside className="sidebar">
      <a className="brand" href="#dashboard">
        <span className="brand-icon">
          <Sprout size={25} />
        </span>

        <span>
          <strong>MandiCluster</strong>
          <small>Market intelligence</small>
        </span>
      </a>

      <div className="sidebar-label">WORKSPACE</div>

      <nav className="nav-menu">
        <a className="nav-item active" href="#dashboard">
          <LayoutDashboard size={18} />
          Dashboard
        </a>

        <a className="nav-item" href="#clusters">
          <Layers3 size={18} />
          Market clusters
        </a>

        <a className="nav-item" href="#markets">
          <Store size={18} />
          Explore markets
        </a>
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-leaf">
          <Leaf size={22} />
        </div>

        <strong>Data-driven decisions</strong>

        <p>
          Explore market-price similarities across agricultural markets.
        </p>

        <span className="status-pill">
          <span className="status-dot" />
          ML results loaded from API
        </span>
      </div>

      <div className="sidebar-footer">
        MANDICLUSTER · ML PROJECT
      </div>
    </aside>
  );
}

export default Sidebar;
