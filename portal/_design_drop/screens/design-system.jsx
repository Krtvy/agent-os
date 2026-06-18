/* global React, RL, KpiTile, FilterBar, Sparkline, SparkButton, Modal, PageHead, IVideo, ILive, ICart, IRupee, IPercent, IInfo, IArrowRight */
/* ============================================================
   Design System — internal reference page
   ============================================================ */

function DesignSystemScreen() {
  const [filter, setFilter] = React.useState({ preset: "30d", products: [], compare: true, start: "", end: "" });
  const [modalOpen, setModalOpen] = React.useState(false);

  return (
    <div className="page" style={{ maxWidth: 1200 }}>
      <PageHead
        title="Design system"
        sub="Tokens + components that build the Rootlabs portal. Light-mode primary. Dark tokens defined below."
      />

      {/* TOC */}
      <div className="row" style={{ marginBottom: "var(--s-6)", gap: "var(--s-2)", flexWrap: "wrap" }}>
        {["color","type","spacing-radius","components","loading-states","rationale"].map(id => (
          <a key={id} href={"#sec-" + id}
             style={{ fontSize: "var(--t-12)", padding: "4px 10px", borderRadius: "var(--r-pill)", background: "var(--c-sunken)", color: "var(--c-ink-2)", textDecoration: "none" }}>
            {id.replace("-", " · ")}
          </a>
        ))}
      </div>

      {/* COLOR */}
      <Section id="color" title="Color tokens" sub="Warm-stone neutrals + a refined forest accent. Semantic colors stay quiet — chips and pill states, not big surfaces.">
        <SwatchGrid title="Neutrals" rows={[
          ["--c-bg",            "Page background"],
          ["--c-surface",       "Card surface"],
          ["--c-sunken",        "Table header / muted surface"],
          ["--c-sunken-2",      "Hovers / wells"],
          ["--c-border",        "Hairline border"],
          ["--c-border-strong", "Input border"],
          ["--c-ink",           "Primary text"],
          ["--c-ink-2",         "Secondary text"],
          ["--c-ink-3",         "Tertiary / labels"],
          ["--c-ink-4",         "Muted / placeholder"],
        ]} />

        <SwatchGrid title="Accent" rows={[
          ["--c-accent",        "Primary buttons, active nav, sparklines"],
          ["--c-accent-hover",  "Button hover"],
          ["--c-accent-press",  "Button active"],
          ["--c-accent-soft",   "Active nav background, chip"],
          ["--c-accent-soft-2", "Soft border / press"],
          ["--c-accent-ink",    "Text on soft accent"],
        ]} />

        <SwatchGrid title="Semantic" rows={[
          ["--c-success",      "Positive delta, success chip"],
          ["--c-success-soft", "Chip background"],
          ["--c-warn",         "Long-running query, paused"],
          ["--c-warn-soft",    "Loading pill bg"],
          ["--c-error",        "Negative delta, danger"],
          ["--c-error-soft",   "Soft error bg"],
          ["--c-info",         "Bundle tag"],
          ["--c-info-soft",    "Info chip bg"],
        ]} />

        <SwatchGrid title="Data viz (categorical, 5-step)" rows={[
          ["--c-data-1","Series 1 / accent"],
          ["--c-data-2","Series 2 / amber"],
          ["--c-data-3","Series 3 / indigo"],
          ["--c-data-4","Series 4 / violet"],
          ["--c-data-5","Series 5 / teal"],
        ]} />

        <div className="card" style={{ marginTop: "var(--s-4)" }}>
          <div className="card__head">
            <h3 className="card__title">Dark mode tokens</h3>
            <p className="card__sub">Defined under <code className="mono">[data-theme="dark"]</code> — not applied to screens yet. Apply at the &lt;html&gt; element for v2.</p>
          </div>
          <div className="card__body" data-theme="dark" style={{ background: "var(--c-bg)", color: "var(--c-ink)", borderRadius: "var(--r-4)" }}>
            <SwatchGrid title="" rows={[
              ["--c-bg","Page bg"], ["--c-surface","Card surface"], ["--c-sunken","Sunken"],
              ["--c-ink","Primary text"], ["--c-ink-3","Labels"],
              ["--c-accent","Accent"], ["--c-accent-soft","Soft accent"],
            ]} dark />
          </div>
        </div>
      </Section>

      {/* TYPE */}
      <Section id="type" title="Type" sub="Switzer for UI, JetBrains Mono for tabular data. Tabular numerals everywhere there's a number column.">
        <div className="card"><div className="card__body">
          <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: "var(--s-3) var(--s-5)", alignItems: "baseline" }}>
            {[
              ["t-36 / 600", { fontSize: 36, fontWeight: 600, letterSpacing: "-0.02em" }, "Display"],
              ["t-28 / 600", { fontSize: 28, fontWeight: 600, letterSpacing: "-0.02em" }, "KPI value"],
              ["t-22 / 600", { fontSize: 22, fontWeight: 600, letterSpacing: "-0.015em" }, "Page title"],
              ["t-18 / 500", { fontSize: 18, fontWeight: 500 }, "Section title"],
              ["t-16 / 400", { fontSize: 16, fontWeight: 400 }, "Lede / body lg"],
              ["t-14 / 400", { fontSize: 14, fontWeight: 400 }, "Body — default"],
              ["t-13 / 400", { fontSize: 13, fontWeight: 400 }, "Table cells, helper"],
              ["t-12 / 500", { fontSize: 12, fontWeight: 500 }, "Labels, chip text"],
              ["t-11 / 500", { fontSize: 11, fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.08em" }, "Caps overline"],
            ].map(([token, style, label]) => (
              <React.Fragment key={token}>
                <span className="mono muted" style={{ fontSize: "var(--t-12)" }}>{token}</span>
                <div style={style}>{label}</div>
              </React.Fragment>
            ))}
            <span className="mono muted" style={{ fontSize: "var(--t-12)" }}>JetBrains Mono</span>
            <div className="mono" style={{ fontVariantNumeric: "tabular-nums", fontSize: 16 }}>₹ 12,48,392.00 · 88,124 · 12.4%</div>
          </div>
        </div></div>
      </Section>

      {/* SPACING + RADIUS */}
      <Section id="spacing-radius" title="Spacing &amp; radius" sub="Spacing on a 4-px grid. Three radii: 4 (chips), 6 (controls/buttons), 8 (cards), 10 (modals).">
        <div className="card"><div className="card__body">
          <div style={{ display: "flex", gap: "var(--s-4)", flexWrap: "wrap" }}>
            {[
              ["s-1", 4], ["s-2", 8], ["s-3", 12], ["s-4", 16], ["s-5", 20], ["s-6", 24], ["s-7", 32], ["s-8", 40], ["s-9", 48], ["s-10", 64],
            ].map(([t, n]) => (
              <div key={t} style={{ textAlign: "center" }}>
                <div style={{ width: n, height: n, background: "var(--c-accent-soft)", borderRadius: 2, margin: "0 auto" }} />
                <div className="mono muted" style={{ fontSize: "var(--t-11)", marginTop: 4 }}>{t} · {n}</div>
              </div>
            ))}
          </div>
          <hr />
          <div style={{ display: "flex", gap: "var(--s-5)" }}>
            {[["r-2",4],["r-3",6],["r-4",8],["r-5",10],["r-6",12],["r-pill",999]].map(([t, n]) => (
              <div key={t} style={{ textAlign: "center" }}>
                <div style={{ width: 56, height: 56, background: "var(--c-sunken)", borderRadius: Math.min(n, 28), border: "1px solid var(--c-border)" }} />
                <div className="mono muted" style={{ fontSize: "var(--t-11)", marginTop: 4 }}>{t}</div>
              </div>
            ))}
          </div>
        </div></div>
      </Section>

      {/* COMPONENTS */}
      <Section id="components" title="Components" sub="The reusable bits that compose every screen.">

        <ComponentBlock name="KPI tile" desc="A label + big number + delta vs prior + a 200×28 area-fill sparkline. Compact, scannable, the unit of the dashboard.">
          <div className="kpi-grid">
            <KpiTile icon={<IVideo />} label="Videos posted" value="2,418" delta={{ dir: "up", v: 12.4 }} sparkData={[12,18,22,19,25,28,30,32,29,34]} priorLabel="prior 2,150" />
            <KpiTile icon={<IRupee />} label="GMV" value="₹ 14.2 L" delta={{ dir: "up", v: 8.1 }} sparkData={[40,55,42,60,68,70,75,82,90,96]} priorLabel="prior ₹ 13.1 L" />
            <KpiTile icon={<IPercent />} label="Commission" value="₹ 1.7 L" delta={{ dir: "down", v: 2.3 }} sparkData={[80,72,75,68,70,66,64,62,60,58]} sparkTone="error" priorLabel="prior ₹ 1.74 L" />
          </div>
        </ComponentBlock>

        <ComponentBlock name="Filter bar" desc="Range presets as a segmented control, products as a chip group, compare-toggle on the right. Custom date inputs collapse in until the Custom preset is selected.">
          <FilterBar value={filter} onChange={setFilter} />
        </ComponentBlock>

        <ComponentBlock name="Sparkline (120×24) + opens modal at 600×220" desc="Pure inline SVG, no chart lib. Same path-builder powers tile sparks, button sparks and big charts.">
          <div className="row">
            <SparkButton data={[10,14,12,18,22,21,26,30,28,32,38,42,48,52]} onOpen={() => setModalOpen(true)} />
            <span className="muted" style={{ fontSize: "var(--t-12)" }}>← click to open larger</span>
          </div>
          <Modal open={modalOpen} title="Sparkline at 600×220" onClose={() => setModalOpen(false)}>
            <Sparkline data={[10,14,12,18,22,21,26,30,28,32,38,42,48,52]} w={640} h={220} />
          </Modal>
        </ComponentBlock>

        <ComponentBlock name="Data table row" desc="Tabular-nums in number columns. Hover reveals row actions. Sticky thead, sortable headers.">
          <div className="card"><div className="card__body card__body--flush">
            <table className="tbl">
              <thead><tr><th>#</th><th>Handle</th><th className="num">Videos</th><th className="num">GMV</th><th>Trend</th><th /></tr></thead>
              <tbody>
                <tr>
                  <td><span className="rank rank--top">1</span></td>
                  <td><span className="handle"><span className="avatar avatar--sm">L</span><a>@luna.beauty</a></span></td>
                  <td className="num mono">142</td>
                  <td className="num mono">₹ 4.2 L</td>
                  <td><Sparkline data={[1,3,2,5,8,6,9,12,10,14]} /></td>
                  <td><button className="row-act">Open <IArrowRight size={12} /></button></td>
                </tr>
                <tr>
                  <td><span className="rank rank--top">2</span></td>
                  <td><span className="handle"><span className="avatar avatar--sm">K</span><a>@kabir.tries</a></span></td>
                  <td className="num mono">98</td>
                  <td className="num mono">₹ 2.8 L</td>
                  <td><Sparkline data={[8,12,10,11,14,12,16,18,20,22]} /></td>
                  <td><button className="row-act">Open <IArrowRight size={12} /></button></td>
                </tr>
              </tbody>
            </table>
          </div></div>
        </ComponentBlock>

        <ComponentBlock name="Buttons" desc="Default = quiet neutral. Primary = accent fill. Ghost = no chrome. Always 32px high (26 sm, 38 lg).">
          <div className="row" style={{ flexWrap: "wrap" }}>
            <button className="btn btn--primary">Primary</button>
            <button className="btn">Default</button>
            <button className="btn btn--ghost">Ghost</button>
            <button className="btn btn--danger">Danger</button>
            <button className="btn btn--sm">Small</button>
            <button className="btn btn--lg">Large</button>
            <button className="btn btn--primary"><IArrowRight /> With icon</button>
            <button className="btn" disabled>Disabled</button>
          </div>
        </ComponentBlock>

        <ComponentBlock name="Chips" desc="Inline status, filter pills, tags. Removable chips have an X-affordance.">
          <div className="row" style={{ flexWrap: "wrap" }}>
            <span className="chip">Default</span>
            <span className="chip chip--accent">Accent</span>
            <span className="chip chip--success">Success</span>
            <span className="chip chip--warn">Warn</span>
            <span className="chip chip--error">Error</span>
            <span className="chip chip--info">Info</span>
            <span className="chip">@luna.beauty <button className="chip__x"><IX size={10} /></button></span>
          </div>
        </ComponentBlock>

        <ComponentBlock name="Breadcrumb" desc="Top-bar nav for nested screens. Trailing item is bold, plain text.">
          <nav className="crumb">
            <a>Creators</a><span className="sep">/</span><strong>@luna.beauty</strong>
          </nav>
        </ComponentBlock>

        <ComponentBlock name="Modal" desc="Backdrop-blur is intentionally absent — page stays legible behind. ESC and scrim click both close.">
          <button className="btn" onClick={() => setModalOpen(true)}>Open modal demo</button>
        </ComponentBlock>

      </Section>

      {/* LOADING STATES */}
      <Section id="loading-states" title="Loading states" sub="Cold queries take 13–35 s. We need to make the wait survivable.">
        <div className="row" style={{ gap: "var(--s-5)", flexWrap: "wrap", alignItems: "flex-start" }}>
          <div style={{ flex: 1, minWidth: 320 }}>
            <div className="muted" style={{ fontSize: "var(--t-12)", marginBottom: 6 }}>Skeleton in tiles + rows</div>
            <div className="kpi-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
              <KpiTile loading label="Loading…" priorLabel="vs prior" />
              <KpiTile loading label="Loading…" priorLabel="vs prior" />
            </div>
          </div>
          <div style={{ flex: 1, minWidth: 320 }}>
            <div className="muted" style={{ fontSize: "var(--t-12)", marginBottom: 6 }}>Top-bar progress pill</div>
            <div className="stack">
              <span className="query-pill" style={{ alignSelf: "flex-start" }}><span className="query-pill__dot" /> Crunching 4.2M rows… 14s</span>
              <span className="query-pill query-pill--ok" style={{ alignSelf: "flex-start" }}><span className="query-pill__dot" /> Fresh · 17s</span>
            </div>
            <p className="muted" style={{ fontSize: "var(--t-12)", marginTop: "var(--s-3)" }}>
              The skeleton tells you <em>what</em> will load where. The pill tells you the query is alive and how long it's been working — important when results take 30 s+.
            </p>
          </div>
        </div>
      </Section>

      {/* RATIONALE */}
      <Section id="rationale" title="What I'd change and why" sub="The reasoning behind the visual choices.">
        <div className="card" style={{ padding: "var(--s-6)", lineHeight: 1.65, fontSize: "var(--t-14)" }}>
          <Rat title="Stop fighting the dashboard with stacked tables.">
            The current layout treats every chart and table as equally important; for a POC staring at this all day, only two things matter on landing: <em>did my GMV move?</em> and <em>who's driving it?</em>. The new dashboard puts those two front and centre — KPI strip with deltas, then a single big GMV chart and the top-5 creators next to it. The by-product table is demoted to below-the-fold and only renders when no product filter is active. The full creator roster moved to its own page.
          </Rat>

          <Rat title="Loading is a state, not a void.">
            Internal Server Error risk on a 30 s query is real. Two coordinated affordances: per-element shimmer skeletons so the layout never jumps, and a top-right "Crunching… 14s" pill that confirms the request is alive. Errors get the same slot but in red. Numbers feel honest when the wait is visible.
          </Rat>

          <Rat title="The act-as link gets promoted.">
            A tiny "act as →" link was easy to miss and slow to scan. The fix is two-part: the operator table row exposes <em>Act as ▸</em> as a real button (hidden until row-hover so the table stays calm), and once active, a persistent amber banner sits above the topbar with "You're viewing as Anika Raghav — Stop". Impersonation is now a mode you're <em>in</em>, not a link you clicked.
          </Rat>

          <Rat title="Filter bar = segmented control + chips, not three dropdowns.">
            Date presets (7d / 14d / 30d / 90d / Custom) collapse into a single segmented control. Products are a horizontal chip group with a clear All toggle — multi-select without a dropdown. The Custom-range date inputs only render when Custom is selected. Compare-to-prior moves to a checkbox on the right so it isn't competing with the primary filters.
          </Rat>

          <Rat title="Sparkline at any size from one primitive.">
            Same SVG path code at 120×24 inline and 600×220 in a modal. <code className="mono">preserveAspectRatio="none"</code> and a min/max-scaled path so a row of inline sparklines stays comparable. Click any sparkline → modal opens with the same series rendered larger plus axes and tooltips. No chart library — just inline SVG, as you asked.
          </Rat>

          <Rat title="Tabular numerals everywhere.">
            Every number column uses <code className="mono">font-variant-numeric: tabular-nums</code> on the cell, and JetBrains Mono for the cells themselves. The visual rhythm of stacked digits is what makes a dense table scannable. Switzer covers the rest of the UI.
          </Rat>

          <Rat title="Emoji KPI prefixes → monochrome icons (with an escape hatch).">
            📹 🔴 🛒 💰 💵 are fine but they shout, and they invert weirdly on hover. Same five concepts redrawn as 14 px monochrome icons sit better next to a label and tint with the accent color. The <strong>Tweaks</strong> panel includes a toggle to flip back to emoji — POCs who know the page by emoji shape don't have to re-learn it.
          </Rat>

          <Rat title="Density is a per-user setting, not a fight.">
            The base is 14 px body, 44 px rows — comfortable for a long workday. A density tweak compresses rows to 36 px for power users; everything else falls into place because every spacing is a token. No fixed pixel values were hand-typed in screen markup.
          </Rat>
        </div>
      </Section>
    </div>
  );
}

function Section({ id, title, sub, children }) {
  return (
    <section id={"sec-" + id} style={{ marginBottom: "var(--s-10)" }}>
      <h2 style={{ fontSize: "var(--t-18)", fontWeight: 600, margin: "0 0 4px", letterSpacing: "-0.01em" }}>{title}</h2>
      {sub && <p className="muted" style={{ fontSize: "var(--t-13)", margin: "0 0 var(--s-4)", maxWidth: 720 }}>{sub}</p>}
      {children}
    </section>
  );
}

function SwatchGrid({ title, rows, dark }) {
  return (
    <div style={{ marginBottom: "var(--s-4)" }}>
      {title && <h4 style={{ margin: "0 0 var(--s-2)", fontSize: "var(--t-12)", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--c-ink-3)" }}>{title}</h4>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "var(--s-2)" }}>
        {rows.map(([token, desc]) => (
          <div key={token} style={{ display: "flex", alignItems: "center", gap: 10, padding: "var(--s-2) var(--s-3)", border: "1px solid var(--c-border)", borderRadius: "var(--r-3)", background: "var(--c-surface)" }}>
            <span style={{ width: 24, height: 24, borderRadius: "var(--r-2)", background: `var(${token})`, border: "1px solid var(--c-border)" }} />
            <div style={{ minWidth: 0, flex: 1 }}>
              <div className="mono" style={{ fontSize: 11, color: "var(--c-ink)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{token}</div>
              <div className="muted" style={{ fontSize: 11 }}>{desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ComponentBlock({ name, desc, children }) {
  return (
    <div style={{ marginBottom: "var(--s-6)" }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: "var(--s-3)", marginBottom: "var(--s-2)" }}>
        <h3 style={{ margin: 0, fontSize: "var(--t-14)", fontWeight: 600 }}>{name}</h3>
        <span className="muted" style={{ fontSize: "var(--t-12)", maxWidth: 720 }}>{desc}</span>
      </div>
      <div style={{ padding: "var(--s-5)", background: "var(--c-sunken)", borderRadius: "var(--r-4)", border: "1px solid var(--c-border)" }}>
        {children}
      </div>
    </div>
  );
}

function Rat({ title, children }) {
  return (
    <div style={{ marginBottom: "var(--s-5)" }}>
      <div style={{ fontWeight: 600, color: "var(--c-ink)", marginBottom: 4 }}>{title}</div>
      <p className="muted" style={{ margin: 0, color: "var(--c-ink-2)" }}>{children}</p>
    </div>
  );
}

window.DesignSystemScreen = DesignSystemScreen;
