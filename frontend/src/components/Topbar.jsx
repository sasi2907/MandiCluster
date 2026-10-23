function Topbar() {
  return (
    <header className="topbar">
      <div>
        <div className="breadcrumb">Workspace / Dashboard</div>
        <h1>Market intelligence</h1>
      </div>

      <div className="topbar-right">
        <span className="api-status">
          <span className="status-dot" />
          API connected
        </span>

        <div className="avatar">MC</div>
      </div>
    </header>
  );
}

export default Topbar;
