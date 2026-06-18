/* global React, RL, PageHead, ITable, IArrowRight, ICheck, IDownload, IClock, IPlus, IX, IBolt */
/* ============================================================
   Browse data wizard — 3-step ad-hoc data export
   ============================================================ */

const TABLES = [
  { id: "videos",    label: "Videos",     desc: "One row per posted video",        rows: "4.2M",  cols: 22 },
  { id: "orders",    label: "Orders",     desc: "Order line items, attributed",    rows: "812K",  cols: 18 },
  { id: "lives",     label: "Live sessions", desc: "One row per live broadcast",   rows: "31K",   cols: 14 },
  { id: "creators",  label: "Creators",   desc: "Roster snapshots, daily",         rows: "284K",  cols: 16 },
  { id: "products",  label: "Products",   desc: "SKU dimension table",             rows: "15",    cols: 11 },
];

const FIELDS = {
  videos: ["video_id","handle","posted_at","duration_s","product","views","orders","gmv","commission","platform"],
  orders: ["order_id","creator_handle","sku","product","price","quantity","gmv","commission","placed_at","state"],
  lives:  ["live_id","handle","started_at","duration_min","peak_viewers","orders","gmv","product"],
  creators: ["handle","poc","joined_at","status","follower_count","tier","last_post_at"],
  products: ["sku","name","family","tag","price","launched_at"],
};

function WizardScreen() {
  const [step, setStep] = React.useState(1);
  const [table, setTable] = React.useState(null);
  const [rows, setRows] = React.useState([]);
  const [cols, setCols] = React.useState([]);
  const [filters, setFilters] = React.useState([]);
  const [running, setRunning] = React.useState(null);

  function startRun() {
    const taskId = "tsk_" + Math.random().toString(36).slice(2, 10);
    setRunning({ id: taskId, state: "queued", elapsed: 0 });
    setStep(3);
    setTimeout(() => setRunning(r => ({ ...r, state: "running" })), 600);
    let t = 0;
    const tick = setInterval(() => {
      t += 1;
      setRunning(r => r ? { ...r, elapsed: t } : r);
      if (t >= 18) {
        clearInterval(tick);
        setRunning(r => ({ ...r, state: "done", elapsed: t, downloadUrl: "#" }));
      }
    }, 280);
  }

  function reset() {
    setStep(1); setTable(null); setRows([]); setCols([]); setFilters([]); setRunning(null);
  }

  return (
    <div className="page">
      <PageHead
        title="Browse data"
        sub="Build a one-off export in three steps. Heavy queries run async — download when ready."
        right={[<button key="hist" className="btn"><IClock /> History</button>]}
      />

      <div className="wiz-steps">
        <div className={"wiz-step " + (step === 1 ? "is-active" : step > 1 ? "is-done" : "")}>
          <span className="wiz-step__num">{step > 1 ? "✓" : "1"}</span> Pick a table
        </div>
        <span className="wiz-step__bar" />
        <div className={"wiz-step " + (step === 2 ? "is-active" : step > 2 ? "is-done" : "")}>
          <span className="wiz-step__num">{step > 2 ? "✓" : "2"}</span> Choose rows, columns &amp; filters
        </div>
        <span className="wiz-step__bar" />
        <div className={"wiz-step " + (step === 3 ? "is-active" : "")}>
          <span className="wiz-step__num">3</span> Run &amp; download
        </div>
      </div>

      {step === 1 && (
        <div className="card">
          <div className="card__head"><h3 className="card__title">Pick a table</h3></div>
          <div className="card__body" style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "var(--s-3)" }}>
            {TABLES.map(t => (
              <button key={t.id}
                onClick={() => { setTable(t); setStep(2); }}
                style={{
                  textAlign: "left", padding: "var(--s-4)",
                  border: "1px solid " + (table?.id === t.id ? "var(--c-accent)" : "var(--c-border)"),
                  borderRadius: "var(--r-4)", background: "var(--c-surface)", cursor: "pointer",
                  display: "flex", gap: "var(--s-3)", alignItems: "flex-start",
                }}>
                <span style={{ width: 36, height: 36, borderRadius: "var(--r-3)", background: "var(--c-accent-soft)", color: "var(--c-accent)", display: "grid", placeItems: "center" }}>
                  <ITable />
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600 }}>{t.label}</div>
                  <div className="muted" style={{ fontSize: "var(--t-12)" }}>{t.desc}</div>
                  <div className="row" style={{ marginTop: 8, gap: 6 }}>
                    <span className="chip">{t.rows} rows</span>
                    <span className="chip">{t.cols} columns</span>
                  </div>
                </div>
                <IArrowRight />
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 2 && table && (
        <>
          <div className="card" style={{ marginBottom: "var(--s-4)" }}>
            <div className="card__head">
              <div>
                <h3 className="card__title">{table.label}</h3>
                <p className="card__sub">{table.rows} rows · drag fields into Rows, Columns or Filters</p>
              </div>
              <div className="card__spacer" />
              <button className="btn btn--sm" onClick={() => setStep(1)}>← Change table</button>
            </div>
            <div className="card__body">
              <p className="muted" style={{ fontSize: "var(--t-12)", margin: "0 0 8px" }}>Available fields</p>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {FIELDS[table.id].map(f => (
                  <span key={f} className="chip mono" style={{ cursor: "grab" }}
                        onClick={() => setCols(c => c.includes(f) ? c : [...c, f])}>
                    + {f}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="pivot">
            <div className="pivot-col">
              <h4>Rows</h4>
              {rows.map(f => <PivotField key={f} field={f} onRemove={() => setRows(rows.filter(r => r !== f))} />)}
              <DropHint onAdd={(f) => setRows([...new Set([...rows, f])])} fields={FIELDS[table.id].filter(f => !rows.includes(f))} />
            </div>
            <div className="pivot-col">
              <h4>Columns</h4>
              {cols.map(f => <PivotField key={f} field={f} accent onRemove={() => setCols(cols.filter(c => c !== f))} />)}
              <DropHint onAdd={(f) => setCols([...new Set([...cols, f])])} fields={FIELDS[table.id].filter(f => !cols.includes(f))} />
            </div>
            <div className="pivot-col">
              <h4>Filters</h4>
              {filters.map((f, i) => (
                <div key={i} className="pivot-field">
                  <span className="mono" style={{ fontWeight: 500 }}>{f.field}</span>
                  <span className="muted">=</span>
                  <span className="mono">{f.value}</span>
                  <button className="chip__x" onClick={() => setFilters(filters.filter((_, j) => j !== i))} style={{ marginLeft: "auto" }}><IX size={10} /></button>
                </div>
              ))}
              <button className="btn btn--sm" style={{ marginTop: 4 }}
                onClick={() => setFilters([...filters, { field: FIELDS[table.id][0], value: "…" }])}>
                <IPlus /> Add filter
              </button>
            </div>
          </div>

          <div className="row" style={{ justifyContent: "flex-end", marginTop: "var(--s-4)", gap: "var(--s-2)" }}>
            <span className="muted" style={{ fontSize: "var(--t-12)", marginRight: "auto" }}>
              {rows.length + cols.length === 0 ? "Pick at least one row or column to enable Run" : `${rows.length + cols.length} fields selected, ${filters.length} filters`}
            </span>
            <button className="btn" onClick={() => setStep(1)}>Back</button>
            <button className="btn btn--primary" disabled={rows.length + cols.length === 0} onClick={startRun}>
              <IBolt /> Run query
            </button>
          </div>
        </>
      )}

      {step === 3 && running && (
        <div className="card">
          <div className="card__body" style={{ display: "flex", gap: "var(--s-5)", alignItems: "center" }}>
            <div style={{
              width: 56, height: 56, borderRadius: "50%",
              background: running.state === "done" ? "var(--c-success-soft)" : "var(--c-warn-soft)",
              color: running.state === "done" ? "var(--c-success)" : "var(--c-warn)",
              display: "grid", placeItems: "center", flex: "none"
            }}>
              {running.state === "done" ? <ICheck size={24} /> : <IClock size={24} />}
            </div>
            <div style={{ flex: 1 }}>
              <div className="row" style={{ gap: 8 }}>
                <span className="mono" style={{ fontSize: "var(--t-12)", color: "var(--c-ink-3)" }}>{running.id}</span>
                <span className={"chip " + (running.state === "done" ? "chip--success" : "chip--warn")}>{running.state}</span>
              </div>
              <h2 style={{ margin: "4px 0", fontSize: "var(--t-18)", fontWeight: 600 }}>
                {running.state === "done"
                  ? "Done. Your CSV is ready."
                  : running.state === "queued" ? "Queued…" : `Crunching ${table.rows} rows · ${running.elapsed}s elapsed`}
              </h2>
              {running.state !== "done" && (
                <div style={{ height: 6, background: "var(--c-sunken)", borderRadius: 3, overflow: "hidden", marginTop: "var(--s-3)" }}>
                  <div style={{
                    height: "100%", width: Math.min(95, (running.elapsed / 18) * 100) + "%",
                    background: "var(--c-accent)", transition: "width .3s var(--ease)",
                    animation: "shimmer 2s infinite",
                    backgroundImage: "linear-gradient(90deg, var(--c-accent), #2a8a5e, var(--c-accent))",
                    backgroundSize: "200px 100%",
                  }} />
                </div>
              )}
              <p className="muted" style={{ fontSize: "var(--t-12)", marginTop: 8 }}>
                You can leave this page — we'll keep a record under <strong>History</strong> and ping #ops-data when it's done.
              </p>
            </div>
            <div className="stack" style={{ gap: 8 }}>
              {running.state === "done"
                ? <button className="btn btn--primary"><IDownload /> Download CSV</button>
                : <button className="btn" disabled>Waiting…</button>}
              <button className="btn" onClick={reset}>New query</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function PivotField({ field, accent, onRemove }) {
  return (
    <div className={"pivot-field " + (accent ? "pivot-field--accent" : "")}>
      <span className="mono" style={{ fontWeight: 500 }}>{field}</span>
      <button className="chip__x" style={{ marginLeft: "auto" }} onClick={onRemove}><IX size={10} /></button>
    </div>
  );
}

function DropHint({ onAdd, fields }) {
  const [open, setOpen] = React.useState(false);
  return (
    <div style={{ marginTop: 6, position: "relative" }}>
      <button className="btn btn--sm" onClick={() => setOpen(o => !o)} style={{ width: "100%", justifyContent: "flex-start", borderStyle: "dashed", color: "var(--c-ink-3)" }}>
        <IPlus /> Drop or add field
      </button>
      {open && (
        <div style={{
          position: "absolute", top: "calc(100% + 4px)", left: 0, right: 0, zIndex: 5,
          background: "var(--c-surface)", border: "1px solid var(--c-border)", borderRadius: "var(--r-3)",
          boxShadow: "var(--sh-pop)", padding: 4, maxHeight: 200, overflow: "auto",
        }}>
          {fields.map(f => (
            <button key={f} className="nav-item mono"
              style={{ width: "100%", padding: "4px 8px", fontSize: "var(--t-12)" }}
              onClick={() => { onAdd(f); setOpen(false); }}>
              + {f}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

window.WizardScreen = WizardScreen;
