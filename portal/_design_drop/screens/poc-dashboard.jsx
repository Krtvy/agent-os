/* global React, RL, KpiTile, FilterBar, LineChart, Sparkline, IVideo, ILive, ICart, IRupee, IPercent, IArrowRight, SkKpiGrid, SkRow, BarsMini, ISparkles */
/* ============================================================
   POC Dashboard
   ============================================================ */

function PocDashboardScreen({ pocId, navigate, filter, setFilter, useEmoji, loadingTrigger }) {
  const poc = RL.POC_DATA[pocId];
  const [loading, setLoading] = React.useState(false);
  const [elapsed, setElapsed] = React.useState(0);

  // Fake "cold query" experience — every filter change kicks a 1.6s-ish skeleton
  React.useEffect(() => {
    setLoading(true);
    setElapsed(1);
    const start = Date.now();
    const tick = setInterval(() => setElapsed(Math.max(1, Math.round((Date.now() - start) / 1000))), 250);
    const done = setTimeout(() => { setLoading(false); clearInterval(tick); }, 1800);
    return () => { clearInterval(tick); clearTimeout(done); };
  }, [filter, pocId, loadingTrigger]);

  const greetingName = poc.name.split(" ")[0];
  const greeting = getGreeting() + ", " + greetingName;

  const periodLabel = labelForPreset(filter.preset, filter.start, filter.end);
  const compareLabel = filter.compare ? "vs prior period" : "no comparison";

  // KPI deltas
  const k = {
    videos:    RL.pct(poc.videos, poc.prior.videos),
    lives:     RL.pct(poc.lives, poc.prior.lives),
    orders:    RL.pct(poc.orders, poc.prior.orders),
    gmv:       RL.pct(poc.gmv, poc.prior.gmv),
    commission:RL.pct(poc.commission, poc.prior.commission),
  };

  const labels = poc.dailyGmv.map((_, i) => RL.dateLabel(poc.dailyGmv.length - 1 - i));

  // Top 5 creators
  const top = poc.roster.slice(0, 5);

  // By-product table only shown when no product filter
  const showByProduct = filter.products.length === 0;

  return (
    <div className="page">
      <PageHead
        title={greeting}
        sub={<>
          Tracking <strong style={{ color: "var(--c-ink)" }}>{poc.rosterSize} creators</strong> · {periodLabel}
          <span className="muted" style={{ marginLeft: 10 }}> · {compareLabel}</span>
        </>}
        right={[
          <button key="add" className="btn"><IUpload /> Export CSV</button>,
          <button key="new" className="btn btn--primary" onClick={() => navigate("roster")}><IPlus /> Add creator</button>,
        ]}
      />

      <FilterBar value={filter} onChange={setFilter} />

      {loading
        ? <SkKpiGrid />
        : <div className="kpi-grid">
            <KpiTile useEmoji={useEmoji} emoji="📹" icon={<IVideo />} label="Videos posted"
                     value={RL.n(poc.videos)} delta={k.videos} sparkData={poc.dailyOrders}
                     priorLabel={"prior " + RL.n(poc.prior.videos)} />
            <KpiTile useEmoji={useEmoji} emoji="🔴" icon={<ILive />} label="Lives done"
                     value={RL.n(poc.lives)} delta={k.lives} sparkData={poc.dailyOrders.map(v => v * 0.4)}
                     sparkTone="error" priorLabel={"prior " + RL.n(poc.prior.lives)} />
            <KpiTile useEmoji={useEmoji} emoji="🛒" icon={<ICart />} label="Orders"
                     value={RL.n(poc.orders)} delta={k.orders} sparkData={poc.dailyOrders}
                     sparkTone="ink" priorLabel={"prior " + RL.n(poc.prior.orders)} />
            <KpiTile useEmoji={useEmoji} emoji="💰" icon={<IRupee />} label="GMV"
                     value={RL.inr(poc.gmv)} delta={k.gmv} sparkData={poc.dailyGmv}
                     priorLabel={"prior " + RL.inr(poc.prior.gmv)} />
            <KpiTile useEmoji={useEmoji} emoji="💵" icon={<IPercent />} label="Est. commission"
                     value={RL.inr(poc.commission)} delta={k.commission} sparkData={poc.dailyGmv.map(v => v * 0.12)}
                     sparkTone="success" priorLabel={"prior " + RL.inr(poc.prior.commission)} />
          </div>
      }

      {/* Main chart + side card */}
      <div className="grid-2col" style={{ marginTop: "var(--s-5)" }}>
        <div className="card">
          <div className="card__head">
            <div>
              <h3 className="card__title">Daily GMV</h3>
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
              : <LineChart
                  series={{
                    current: poc.dailyGmv,
                    prior: filter.compare ? poc.prior.dailyGmv : null,
                    labels,
                  }}
                  format={(v) => RL.inr(v).replace("₹","₹")}
                  h={260}
                />
            }
          </div>
        </div>

        {/* Side: top creators */}
        <div className="card">
          <div className="card__head">
            <div>
              <h3 className="card__title">Top creators</h3>
              <p className="card__sub">By GMV · {periodLabel}</p>
            </div>
            <div className="card__spacer" />
            <a href="#/creators" onClick={(e) => { e.preventDefault(); navigate("creators"); }} className="muted" style={{ fontSize: "var(--t-12)" }}>
              View all <IArrowRight size={12} style={{ verticalAlign: "middle" }} />
            </a>
          </div>
          <div className="card__body card__body--flush">
            {loading
              ? <div style={{ padding: "var(--s-5)" }}>
                  {[0,1,2,3,4].map(i => <div key={i} style={{ display: "flex", gap: 12, marginBottom: 14 }}>
                    <span className="sk" style={{ width: 22, height: 22, borderRadius: 4 }} />
                    <span className="sk" style={{ flex: 1, height: 12 }} />
                    <span className="sk" style={{ width: 50, height: 12 }} />
                  </div>)}
                </div>
              : <table className="tbl">
                  <tbody>
                    {top.map((c, i) => (
                      <tr key={c.handle} onClick={() => navigate("creator-detail", { handle: c.handle })} style={{ cursor: "pointer" }}>
                        <td style={{ width: 32 }}><span className={"rank " + (i < 3 ? "rank--top" : "")}>{i+1}</span></td>
                        <td><span className="handle"><span className="avatar avatar--sm" style={{ background: c.avatarColor + "1a", color: c.avatarColor, borderColor: c.avatarColor + "33" }}>{c.handle[1].toUpperCase()}</span><a>{c.handle}</a></span></td>
                        <td className="num mono">{RL.inr(c.gmv)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
            }
          </div>
        </div>
      </div>

      {/* By product (only when no product filter) */}
      {showByProduct && (
        <div className="card" style={{ marginTop: "var(--s-5)" }}>
          <div className="card__head">
            <div>
              <h3 className="card__title">Videos &amp; GMV by product</h3>
              <p className="card__sub">{periodLabel} · click a row to filter the dashboard</p>
            </div>
          </div>
          <div className="card__body card__body--flush">
            {loading
              ? <table className="tbl"><thead><tr><th>Product</th><th>Videos</th><th>GMV</th><th>Share</th></tr></thead><tbody>{[0,1,2,3,4].map(i => <SkRow key={i} widths={[40,30,30,80]} />)}</tbody></table>
              : <table className="tbl">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th className="num">Videos</th>
                      <th className="num">GMV</th>
                      <th>Share of GMV</th>
                    </tr>
                  </thead>
                  <tbody>
                    {poc.byProduct.map(row => {
                      const prod = RL.PRODUCTS.find(p => p.id === row.product);
                      const share = (row.gmv / poc.gmv) * 100;
                      return (
                        <tr key={row.product}
                            onClick={() => setFilter({ ...filter, products: [row.product] })}
                            style={{ cursor: "pointer" }}>
                          <td>
                            <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                              <span style={{ width: 10, height: 10, borderRadius: 3, background: prod.color }} />
                              <strong style={{ fontWeight: 500 }}>{prod.name}</strong>
                              <span className="muted" style={{ fontSize: "var(--t-12)" }}>{prod.full}</span>
                            </span>
                          </td>
                          <td className="num mono">{RL.n(row.videos)}</td>
                          <td className="num mono">{RL.inr(row.gmv)}</td>
                          <td>
                            <div style={{ display: "flex", alignItems: "center", gap: 10, maxWidth: 360 }}>
                              <span style={{ flex: 1, height: 6, borderRadius: 3, background: "var(--c-sunken)", overflow: "hidden" }}>
                                <span style={{ display: "block", height: "100%", width: share + "%", background: prod.color }} />
                              </span>
                              <span className="mono" style={{ fontSize: "var(--t-12)", color: "var(--c-ink-3)", minWidth: 36, textAlign: "right" }}>{share.toFixed(1)}%</span>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
            }
          </div>
        </div>
      )}
    </div>
  );
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

function labelForPreset(p, start, end) {
  switch (p) {
    case "7d":  return "Last 7 days";
    case "14d": return "Last 14 days";
    case "30d": return "Last 30 days";
    case "90d": return "Last 90 days";
    case "custom": return (start || "—") + " → " + (end || "—");
    default: return "Last 30 days";
  }
}

Object.assign(window, { PocDashboardScreen, labelForPreset });
