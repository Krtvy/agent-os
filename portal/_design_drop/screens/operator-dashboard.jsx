/* global React, RL, KpiTile, FilterBar, LineChart, Sparkline, PageHead, IVideo, ILive, ICart, IRupee, IPercent, IArrowRight, IUsers, SkKpiGrid, ISwitch, IBolt, labelForPreset, IUpload */
/* ============================================================
   Operator Dashboard — totals across all 8 POCs + per-POC table
   ============================================================ */

function OperatorDashboardScreen({ filter, setFilter, navigate, useEmoji, actAs, loadingTrigger }) {
  const op = RL.OPERATOR;
  const [loading, setLoading] = React.useState(false);
  React.useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => setLoading(false), 1600);
    return () => clearTimeout(t);
  }, [filter, loadingTrigger]);

  const periodLabel = labelForPreset(filter.preset, filter.start, filter.end);
  const k = {
    videos: RL.pct(op.videos, op.prior.videos),
    lives:  RL.pct(op.lives, op.prior.lives),
    orders: RL.pct(op.orders, op.prior.orders),
    gmv:    RL.pct(op.gmv, op.prior.gmv),
    commission: RL.pct(op.commission, op.prior.commission),
  };
  const labels = op.dailyGmv.map((_, i) => RL.dateLabel(op.dailyGmv.length - 1 - i));

  // POC rows w/ deltas & sort
  const [sortKey, setSortKey] = React.useState("gmv");
  const pocs = [...RL.POCS].map(p => {
    const d = RL.POC_DATA[p.id];
    return {
      ...p,
      rosterSize: d.rosterSize,
      videos: d.videos, lives: d.lives, orders: d.orders, gmv: d.gmv, commission: d.commission,
      gmvDelta: RL.pct(d.gmv, d.prior.gmv),
      dailyGmv: d.dailyGmv,
    };
  }).sort((a, b) => (b[sortKey] || 0) - (a[sortKey] || 0));

  function thSort(key, label, num) {
    return (
      <th className={num ? "num" : ""} style={{ cursor: "pointer", userSelect: "none" }} onClick={() => setSortKey(key)}>
        {label} {sortKey === key && <span style={{ color: "var(--c-accent)" }}>↓</span>}
      </th>
    );
  }

  return (
    <div className="page">
      <PageHead
        title="Team overview"
        sub={<>Aggregate across <strong style={{ color: "var(--c-ink)" }}>{RL.POCS.length} POCs</strong> · {op.rosterSize} creators · {periodLabel}</>}
        right={[
          <button key="ex" className="btn"><IUpload /> Export team CSV</button>,
        ]}
      />

      <FilterBar value={filter} onChange={setFilter} />

      {loading
        ? <SkKpiGrid />
        : <div className="kpi-grid">
            <KpiTile useEmoji={useEmoji} emoji="📹" icon={<IVideo />} label="Videos posted"
                     value={RL.n(op.videos)} delta={k.videos}
                     sparkData={op.dailyGmv.map(v => v / 6000)} priorLabel={"prior " + RL.n(op.prior.videos)} />
            <KpiTile useEmoji={useEmoji} emoji="🔴" icon={<ILive />} label="Lives done"
                     value={RL.n(op.lives)} delta={k.lives}
                     sparkData={op.dailyGmv.map(v => v / 18000)} sparkTone="error"
                     priorLabel={"prior " + RL.n(op.prior.lives)} />
            <KpiTile useEmoji={useEmoji} emoji="🛒" icon={<ICart />} label="Orders"
                     value={RL.n(op.orders)} delta={k.orders}
                     sparkData={op.dailyGmv.map(v => v / 800)} sparkTone="ink"
                     priorLabel={"prior " + RL.n(op.prior.orders)} />
            <KpiTile useEmoji={useEmoji} emoji="💰" icon={<IRupee />} label="GMV"
                     value={RL.inr(op.gmv)} delta={k.gmv}
                     sparkData={op.dailyGmv} priorLabel={"prior " + RL.inr(op.prior.gmv)} />
            <KpiTile useEmoji={useEmoji} emoji="💵" icon={<IPercent />} label="Est. commission"
                     value={RL.inr(op.commission)} delta={k.commission}
                     sparkData={op.dailyGmv.map(v => v * 0.12)} sparkTone="success"
                     priorLabel={"prior " + RL.inr(op.prior.commission)} />
          </div>
      }

      {/* Main GMV chart */}
      <div className="card" style={{ marginTop: "var(--s-5)" }}>
        <div className="card__head">
          <div>
            <h3 className="card__title">Total GMV across team</h3>
            <p className="card__sub">{periodLabel} · current vs prior period</p>
          </div>
          <div className="card__spacer" />
          <div className="chart-legend">
            <span><span className="chart-legend__sw" style={{ background: "var(--c-accent)" }} />Current</span>
            {filter.compare && <span><span className="chart-legend__sw chart-legend__sw--dashed" />Prior</span>}
          </div>
        </div>
        <div className="chart-wrap">
          {loading
            ? <div style={{ height: 240, display: "grid", placeItems: "center" }}><span className="sk" style={{ width: "100%", height: 200 }} /></div>
            : <LineChart series={{ current: op.dailyGmv, prior: filter.compare ? op.prior.dailyGmv : null, labels }} format={(v) => RL.inr(v)} h={260} />
          }
        </div>
      </div>

      {/* POC leaderboard table */}
      <div className="card" style={{ marginTop: "var(--s-5)" }}>
        <div className="card__head">
          <div>
            <h3 className="card__title">POC leaderboard</h3>
            <p className="card__sub">One row per POC · click <em>Act as</em> to view their dashboard</p>
          </div>
          <div className="card__spacer" />
          <span className="chip"><IUsers size={12} /> {RL.POCS.length} POCs</span>
        </div>
        <div className="card__body card__body--flush">
          <div className="tbl-wrap">
            <table className="tbl">
              <thead>
                <tr>
                  <th>POC</th>
                  <th className="num">Roster</th>
                  {thSort("videos", "Videos", true)}
                  {thSort("lives", "Lives", true)}
                  {thSort("orders", "Orders", true)}
                  {thSort("gmv", "GMV", true)}
                  <th className="num">Δ vs prior</th>
                  <th>GMV trend</th>
                  <th style={{ width: 120 }}></th>
                </tr>
              </thead>
              <tbody>
                {pocs.map((p, i) => (
                  <tr key={p.id}>
                    <td>
                      <span className="handle">
                        <span className="avatar avatar--sm" style={{ background: p.color + "1a", color: p.color, borderColor: p.color + "33" }}>{p.initials}</span>
                        <span>
                          <strong style={{ fontWeight: 500 }}>{p.name}</strong>
                        </span>
                      </span>
                    </td>
                    <td className="num mono">{p.rosterSize}</td>
                    <td className="num mono">{RL.n(p.videos)}</td>
                    <td className="num mono">{RL.n(p.lives)}</td>
                    <td className="num mono">{RL.n(p.orders)}</td>
                    <td className="num mono"><strong style={{ fontWeight: 500 }}>{RL.inr(p.gmv)}</strong></td>
                    <td className="num">
                      <span className={"kpi__delta " + (p.gmvDelta.dir === "up" ? "kpi__delta--up" : p.gmvDelta.dir === "down" ? "kpi__delta--down" : "kpi__delta--flat")}>
                        {p.gmvDelta.dir === "up" ? "▲" : p.gmvDelta.dir === "down" ? "▼" : "—"} {Math.abs(p.gmvDelta.v).toFixed(1)}%
                      </span>
                    </td>
                    <td><Sparkline data={p.dailyGmv} w={120} h={24} tone="accent" /></td>
                    <td>
                      <button className="row-act" onClick={() => actAs(p.id)}>
                        Act as <IArrowRight size={12} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

window.OperatorDashboardScreen = OperatorDashboardScreen;
