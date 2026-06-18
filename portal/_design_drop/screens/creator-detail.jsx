/* global React, RL, PageHead, LineChart, Sparkline, BarsMini, IExternal, IArrowRight, KpiTile, IVideo, ICart, IRupee, IPercent */
/* ============================================================
   Creator Detail
   ============================================================ */

function CreatorDetailScreen({ pocId, handle, navigate }) {
  const poc = RL.POC_DATA[pocId];
  const c = poc.roster.find(r => r.handle === handle) || poc.roster[0];
  const labels = c.dailyOrders.map((_, i) => RL.dateLabel(c.dailyOrders.length - 1 - i));
  const recent = RL.makeRecentVideos(c.handle.length * 31);

  // Product mix bars from c.productMix (normalize)
  const mixTotal = RL.PRODUCTS.reduce((s, p) => s + c.productMix[p.id], 0) || 1;
  const mixItems = RL.PRODUCTS.map(p => ({ label: p.name, value: c.productMix[p.id], color: p.color })).sort((a, b) => b.value - a.value);

  return (
    <div className="page">
      <nav className="crumb" style={{ marginBottom: "var(--s-4)" }}>
        <a href="#/creators" onClick={(e) => { e.preventDefault(); navigate("creators"); }}>Creators</a>
        <span className="sep">/</span>
        <strong>{c.handle}</strong>
      </nav>

      <PageHead
        title={<span style={{ display: "inline-flex", alignItems: "center", gap: "var(--s-3)" }}>
          <span className="avatar avatar--lg" style={{ background: c.avatarColor + "1a", color: c.avatarColor, borderColor: c.avatarColor + "33", fontSize: "var(--t-15)" }}>{c.handle[1].toUpperCase()}</span>
          {c.handle}
          {c.status === "paused" && <span className="chip chip--warn">paused</span>}
        </span>}
        sub={<>Joined {c.joinedDays} days ago · AOV {RL.inr(c.aov)} · top product <strong style={{ color: "var(--c-ink)" }}>{mixItems[0].label}</strong></>}
        right={[
          <button key="ext" className="btn"><IExternal /> Open TikTok</button>,
          <button key="msg" className="btn btn--primary">Message</button>,
        ]}
      />

      {/* KPI mini-strip */}
      <div className="kpi-grid">
        <KpiTile icon={<IVideo />} label="Videos" value={RL.n(c.videos)} sparkData={c.cumVideos.map((v,i,a) => i>0?v-a[i-1]:v)} priorLabel="period" delta={{ dir: "up", v: 12.3 }} />
        <KpiTile icon={<ICart />} label="Orders" value={RL.n(c.orders)} sparkData={c.dailyOrders} sparkTone="ink" priorLabel="period" delta={{ dir: "up", v: 8.9 }} />
        <KpiTile icon={<IRupee />} label="GMV" value={RL.inr(c.gmv)} sparkData={c.dailyGmv} priorLabel="period" delta={{ dir: "up", v: 18.4 }} />
        <KpiTile icon={<IPercent />} label="Commission" value={RL.inr(c.commission)} sparkData={c.dailyGmv.map(v => v*0.12)} sparkTone="success" priorLabel="period" delta={{ dir: "up", v: 18.4 }} />
        <div className="kpi">
          <div className="kpi__head"><span className="kpi__label">AOV · Status · Lives</span></div>
          <div style={{ display: "flex", gap: "var(--s-3)", marginTop: 4, flexWrap: "wrap" }}>
            <span className="chip chip--accent">AOV {RL.inr(c.aov)}</span>
            <span className={"chip " + (c.status === "paused" ? "chip--warn" : "chip--success")}>{c.status}</span>
            <span className="chip">{c.lives} lives</span>
          </div>
          <div className="kpi__foot" style={{ marginTop: "auto" }}>Last live 4 days ago</div>
        </div>
      </div>

      {/* Charts row */}
      <div className="grid-2col" style={{ marginTop: "var(--s-5)" }}>
        <div className="card">
          <div className="card__head">
            <div>
              <h3 className="card__title">Daily videos</h3>
              <p className="card__sub">Last 30 days</p>
            </div>
          </div>
          <div className="chart-wrap">
            <LineChart
              series={{ current: c.cumVideos.map((v,i,a) => i>0?v-a[i-1]:v), labels }}
              format={(v) => Math.round(v)}
              h={220}
            />
          </div>
        </div>

        <div className="card">
          <div className="card__head">
            <div>
              <h3 className="card__title">Daily orders</h3>
              <p className="card__sub">Last 30 days</p>
            </div>
          </div>
          <div className="chart-wrap">
            <LineChart
              series={{ current: c.dailyOrders, labels }}
              format={(v) => Math.round(v)}
              tone="ink"
              h={220}
            />
          </div>
        </div>
      </div>

      <div className="grid-2col" style={{ marginTop: "var(--s-5)" }}>
        <div className="card">
          <div className="card__head">
            <div>
              <h3 className="card__title">Top products they push</h3>
              <p className="card__sub">Share of mentions across recent videos</p>
            </div>
          </div>
          <div className="card__body">
            <BarsMini
              items={mixItems.map(m => ({ ...m, value: m.value }))}
              max={Math.max(...mixItems.map(m => m.value))}
              format={(v) => v + "%"}
              w={"100%"}
            />
          </div>
        </div>

        <div className="card">
          <div className="card__head">
            <div>
              <h3 className="card__title">Recent videos</h3>
              <p className="card__sub">Last 6 posts</p>
            </div>
          </div>
          <div className="card__body card__body--flush">
            <table className="tbl">
              <thead>
                <tr>
                  <th>Caption</th>
                  <th>Product</th>
                  <th className="num">Views</th>
                  <th className="num">Orders</th>
                  <th className="num">GMV</th>
                  <th className="num">When</th>
                </tr>
              </thead>
              <tbody>
                {recent.map(v => {
                  const p = RL.PRODUCTS.find(p => p.id === v.product);
                  return (
                    <tr key={v.id}>
                      <td style={{ maxWidth: 280, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{v.caption}</td>
                      <td><span className="chip" style={{ background: p.color + "1a", color: p.color, borderColor: p.color + "33" }}>{p.name}</span></td>
                      <td className="num mono">{RL.nshort(v.views)}</td>
                      <td className="num mono">{v.orders}</td>
                      <td className="num mono">{RL.inr(v.gmv)}</td>
                      <td className="num mono muted">{v.daysAgo}d ago</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

window.CreatorDetailScreen = CreatorDetailScreen;
