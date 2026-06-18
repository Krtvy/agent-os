/* global React, RL, FilterBar, Sparkline, SparkButton, Modal, PageHead, LineChart, labelForPreset, IUpload, ISearch, IPlus, IArrowRight */
/* ============================================================
   Creators List — full roster for the current POC
   ============================================================ */

function CreatorsListScreen({ pocId, navigate, filter, setFilter, loadingTrigger }) {
  const poc = RL.POC_DATA[pocId];
  const [loading, setLoading] = React.useState(false);
  const [query, setQuery] = React.useState("");
  const [sortKey, setSortKey] = React.useState("gmv");
  const [sortDir, setSortDir] = React.useState("desc");
  const [statusFilter, setStatusFilter] = React.useState("all");
  const [openCreator, setOpenCreator] = React.useState(null);

  React.useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => setLoading(false), 1400);
    return () => clearTimeout(t);
  }, [filter, pocId, loadingTrigger]);

  const filtered = poc.roster.filter(c => {
    if (query && !c.handle.toLowerCase().includes(query.toLowerCase())) return false;
    if (statusFilter !== "all" && c.status !== statusFilter) return false;
    return true;
  });
  const sorted = [...filtered].sort((a, b) => {
    const av = a[sortKey], bv = b[sortKey];
    if (typeof av === "string") return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
    return sortDir === "asc" ? av - bv : bv - av;
  });

  function th(key, label, num) {
    const active = sortKey === key;
    return (
      <th className={num ? "num" : ""} style={{ cursor: "pointer", userSelect: "none" }}
          onClick={() => { if (active) setSortDir(d => d === "asc" ? "desc" : "asc"); else { setSortKey(key); setSortDir("desc"); } }}>
        {label}{active && <span style={{ color: "var(--c-accent)", marginLeft: 4 }}>{sortDir === "asc" ? "↑" : "↓"}</span>}
      </th>
    );
  }

  const totals = sorted.reduce((acc, c) => {
    acc.videos += c.videos; acc.lives += c.lives; acc.orders += c.orders; acc.gmv += c.gmv; acc.commission += c.commission;
    return acc;
  }, { videos: 0, lives: 0, orders: 0, gmv: 0, commission: 0 });

  return (
    <div className="page">
      <PageHead
        title="Creators"
        sub={<>{poc.rosterSize} creators · {labelForPreset(filter.preset)}</>}
        right={[
          <button key="ex" className="btn"><IUpload /> Export</button>,
          <button key="add" className="btn btn--primary" onClick={() => navigate("roster")}><IPlus /> Manage roster</button>,
        ]}
      />

      <FilterBar value={filter} onChange={setFilter} />

      {/* Quick filter row */}
      <div className="row" style={{ marginBottom: "var(--s-3)", gap: "var(--s-3)" }}>
        <div className="topbar__search" style={{ width: 320, background: "var(--c-surface)" }}>
          <ISearch size={14} />
          <input placeholder="Search by handle…" value={query} onChange={e => setQuery(e.target.value)} />
        </div>
        <div className="seg">
          {[["all","All"],["active","Active"],["paused","Paused"]].map(([id, lbl]) => (
            <button key={id} className={"seg__opt " + (statusFilter === id ? "is-active" : "")} onClick={() => setStatusFilter(id)}>{lbl}</button>
          ))}
        </div>
        <span className="muted" style={{ fontSize: "var(--t-12)", marginLeft: "auto", whiteSpace: "nowrap" }}>
          Showing <strong style={{ color: "var(--c-ink-2)" }}>{sorted.length}</strong> of {poc.rosterSize}
        </span>
      </div>

      <div className="card">
        <div className="card__body card__body--flush">
          <div className="tbl-wrap">
            <table className="tbl">
              <thead>
                <tr>
                  <th style={{ width: 40 }}>#</th>
                  <th>Handle</th>
                  {th("videos", "Videos", true)}
                  {th("lives", "Lives", true)}
                  {th("orders", "Orders", true)}
                  {th("gmv", "GMV", true)}
                  {th("commission", "Commission", true)}
                  <th>Cumulative videos</th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: 8 }).map((_, i) =>
                      <tr key={i}>
                        <td><span className="sk" style={{ width: 22, height: 12 }} /></td>
                        <td><span className="sk" style={{ width: 140, height: 12 }} /></td>
                        <td><span className="sk" style={{ width: 40, height: 12 }} /></td>
                        <td><span className="sk" style={{ width: 40, height: 12 }} /></td>
                        <td><span className="sk" style={{ width: 40, height: 12 }} /></td>
                        <td><span className="sk" style={{ width: 70, height: 12 }} /></td>
                        <td><span className="sk" style={{ width: 70, height: 12 }} /></td>
                        <td><span className="sk" style={{ width: 120, height: 22 }} /></td>
                      </tr>
                    )
                  : sorted.map((c, i) => (
                    <tr key={c.handle} className={c.status === "paused" ? "is-disabled" : ""}>
                      <td><span className={"rank " + (i < 3 ? "rank--top" : "")}>{i + 1}</span></td>
                      <td>
                        <span className="handle">
                          <span className="avatar avatar--sm" style={{ background: c.avatarColor + "1a", color: c.avatarColor, borderColor: c.avatarColor + "33" }}>{c.handle[1].toUpperCase()}</span>
                          <a href={"#/creator/" + c.handle.slice(1)}
                             onClick={(e) => { e.preventDefault(); navigate("creator-detail", { handle: c.handle }); }}>
                            {c.handle}
                          </a>
                          {c.status === "paused" && <span className="chip" style={{ fontSize: 10, padding: "1px 6px" }}>paused</span>}
                        </span>
                      </td>
                      <td className="num mono">{RL.n(c.videos)}</td>
                      <td className="num mono">{c.lives || "—"}</td>
                      <td className="num mono">{RL.n(c.orders)}</td>
                      <td className="num mono">{RL.inr(c.gmv)}</td>
                      <td className="num mono">{RL.inr(c.commission)}</td>
                      <td>
                        <SparkButton data={c.cumVideos} w={120} h={24}
                          onOpen={() => setOpenCreator(c)} />
                      </td>
                    </tr>
                  ))
                }
              </tbody>
              {!loading && sorted.length > 0 && (
                <tfoot>
                  <tr style={{ background: "var(--c-sunken)", borderTop: "1px solid var(--c-border)" }}>
                    <td colSpan={2} style={{ color: "var(--c-ink-3)", fontSize: "var(--t-12)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Totals (filtered)</td>
                    <td className="num mono"><strong style={{ fontWeight: 500 }}>{RL.n(totals.videos)}</strong></td>
                    <td className="num mono"><strong style={{ fontWeight: 500 }}>{RL.n(totals.lives)}</strong></td>
                    <td className="num mono"><strong style={{ fontWeight: 500 }}>{RL.n(totals.orders)}</strong></td>
                    <td className="num mono"><strong style={{ fontWeight: 500 }}>{RL.inr(totals.gmv)}</strong></td>
                    <td className="num mono"><strong style={{ fontWeight: 500 }}>{RL.inr(totals.commission)}</strong></td>
                    <td></td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        </div>
      </div>

      <Modal
        open={!!openCreator}
        title={openCreator ? "Cumulative videos · " + openCreator.handle : ""}
        onClose={() => setOpenCreator(null)}
        footer={
          <>
            <button className="btn" onClick={() => setOpenCreator(null)}>Close</button>
            <button className="btn btn--primary" onClick={() => { const c = openCreator; setOpenCreator(null); navigate("creator-detail", { handle: c.handle }); }}>
              Open profile <IArrowRight />
            </button>
          </>
        }
      >
        {openCreator && (
          <>
            <div className="row" style={{ marginBottom: "var(--s-3)" }}>
              <span className="chip">{RL.n(openCreator.videos)} videos</span>
              <span className="chip">{RL.n(openCreator.orders)} orders</span>
              <span className="chip chip--accent">{RL.inr(openCreator.gmv)} GMV</span>
              <span className="chip chip--success">{RL.inr(openCreator.commission)} commission</span>
            </div>
            <LineChart
              series={{
                current: openCreator.cumVideos,
                labels: openCreator.cumVideos.map((_, i) => RL.dateLabel(openCreator.cumVideos.length - 1 - i)),
              }}
              format={(v) => Math.round(v)}
              h={240}
              w={640}
            />
            <p className="muted" style={{ fontSize: "var(--t-12)", marginTop: "var(--s-3)" }}>
              Cumulative videos posted over the selected period. Same SVG primitive as the 120×24 inline sparkline — just scaled up.
            </p>
          </>
        )}
      </Modal>
    </div>
  );
}

window.CreatorsListScreen = CreatorsListScreen;
