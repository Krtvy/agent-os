/* global React, IGrid, IUsers, IPackage, ITable, IUser, ILogout, ISearch, IChevron */
/* ============================================================
   Rootlabs Portal — App shell (sidebar + topbar + impersonation banner)
   ============================================================ */

function Sidebar({ route, navigate, impersonating, currentPoc }) {
  const items = [
    { id: "dashboard", label: "Dashboard", icon: <IGrid />, route: impersonating ? "poc-dashboard" : (currentPoc?.role === "operator" ? "operator-dashboard" : "poc-dashboard") },
    { id: "creators", label: "Creators", icon: <IUsers />, route: "creators", count: currentPoc?.rosterSize },
    { id: "roster",   label: "Roster",   icon: <IList />,  route: "roster" },
    { id: "products", label: "Products", icon: <IPackage />, route: "products" },
    { id: "browse",   label: "Browse data", icon: <ITable />,  route: "wizard" },
  ];
  const opItems = currentPoc?.role === "operator" && !impersonating
    ? [{ id: "team", label: "Team overview", icon: <IUsers />, route: "operator-dashboard" }]
    : [];

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__brand-mark">R</span>
        <span>Rootlabs</span>
      </div>

      <div className="sidebar__section">Workspace</div>
      {items.map(it => (
        <a
          key={it.id} href={"#/" + it.route}
          onClick={(e) => { e.preventDefault(); navigate(it.route); }}
          className={"nav-item " + (route === it.route ? "is-active" : "")}
        >
          {it.icon}<span>{it.label}</span>
          {it.count != null && <span className="nav-item__count">{it.count}</span>}
        </a>
      ))}

      {opItems.length > 0 && (<>
        <div className="sidebar__section">Operator</div>
        {opItems.map(it => (
          <a key={it.id} href={"#/" + it.route}
             onClick={(e) => { e.preventDefault(); navigate(it.route); }}
             className={"nav-item " + (route === it.route ? "is-active" : "")}>
            {it.icon}<span>{it.label}</span>
          </a>
        ))}
      </>)}

      <div className="sidebar__footer">
        <span className="avatar avatar--accent">{currentPoc?.initials || "OP"}</span>
        <div style={{ minWidth: 0 }}>
          <div style={{ color: "var(--c-ink)", fontSize: "var(--t-13)", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{currentPoc?.name || "Operator"}</div>
          <div style={{ fontSize: "var(--t-11)" }}>{currentPoc?.role === "operator" ? "Operator" : "POC"}</div>
        </div>
        <button className="btn btn--ghost btn--icon" title="Sign out" onClick={() => navigate("login")} style={{ marginLeft: "auto" }}><ILogout /></button>
      </div>
    </aside>
  );
}

function Topbar({ crumbs, right, queryState }) {
  return (
    <div className="topbar">
      <nav className="crumb">
        {crumbs.map((c, i) => (
          <React.Fragment key={i}>
            {i > 0 && <span className="sep">/</span>}
            {c.href ? <a href={c.href} onClick={c.onClick}>{c.label}</a> : <strong>{c.label}</strong>}
          </React.Fragment>
        ))}
      </nav>

      <div className="topbar__spacer" />

      {queryState && (
        queryState.state === "loading"
          ? <span className="query-pill"><span className="query-pill__dot" /> Crunching {queryState.rows ? `${queryState.rows} rows` : "data"}… {queryState.elapsed}s</span>
          : <span className="query-pill query-pill--ok"><span className="query-pill__dot" /> Fresh · {queryState.elapsed}s</span>
      )}

      <div className="topbar__search">
        <ISearch size={14} />
        <input placeholder="Jump to creator, POC, product…" />
        <span className="kbd">⌘K</span>
      </div>

      {right}
    </div>
  );
}

function ImpersonationBanner({ poc, onStop }) {
  return (
    <div className="banner-impersonate">
      <span className="avatar avatar--sm" style={{ background: "#f6e0b0", color: "#6b4a07", borderColor: "#eccc7a" }}>{poc.initials}</span>
      <span>You're viewing as <strong>{poc.name}</strong>. Anything you do is logged under your operator account.</span>
      <span className="banner-impersonate__spacer" />
      <button className="btn btn--sm" onClick={onStop}>Stop acting as {poc.name.split(" ")[0]}</button>
    </div>
  );
}

function PageHead({ title, sub, right }) {
  return (
    <div className="page__head">
      <div>
        <h1 className="page__title">{title}</h1>
        {sub && <p className="page__sub">{sub}</p>}
      </div>
      {right && <div className="row">{right}</div>}
    </div>
  );
}

Object.assign(window, { Sidebar, Topbar, ImpersonationBanner, PageHead });
