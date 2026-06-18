/* global React, RL, IUp, IDown, ICalendar, IFilter, IX, IChevronDown, Sparkline */
/* ============================================================
   Rootlabs Portal — KPI tile, Filter bar, Modal, Skeletons
   ============================================================ */

function fmtDelta(v) {
  const n = Math.abs(v);
  return (v >= 0 ? "+" : "−") + (n < 10 ? n.toFixed(1) : Math.round(n)) + "%";
}

function Delta({ pct, size = "sm" }) {
  if (!pct || pct.dir === "flat") {
    return <span className="kpi__delta kpi__delta--flat">±0%</span>;
  }
  const cls = pct.dir === "up" ? "kpi__delta--up" : "kpi__delta--down";
  const I = pct.dir === "up" ? IUp : IDown;
  return <span className={"kpi__delta " + cls}><I size={10} />{fmtDelta(pct.v)}</span>;
}

// ---- KPI tile ----
function KpiTile({ icon, label, value, delta, sparkData, sparkTone = "accent", priorLabel, loading, useEmoji, emoji }) {
  return (
    <div className="kpi">
      <div className="kpi__head">
        {useEmoji
          ? <span style={{ fontSize: 14, lineHeight: 1 }}>{emoji}</span>
          : icon}
        <span className="kpi__label">{label}</span>
      </div>
      {loading
        ? <span className="sk sk--num" />
        : <div className="kpi__value">{value}</div>
      }
      <div className="kpi__row">
        {loading
          ? <span className="sk" style={{ width: 60, height: 14 }} />
          : <>
              <Delta pct={delta} />
              <span className="kpi__foot">{priorLabel}</span>
            </>
        }
      </div>
      {loading
        ? <span className="sk sk--spark" />
        : <Sparkline data={sparkData} w={200} h={28} tone={sparkTone} area />
      }
    </div>
  );
}

// ---- Filter bar ----
// Date pickers + segmented period + product chips. Active filters render as removable chips below.
const PRESETS = [
  { id: "7d",   label: "7d",   days: 7 },
  { id: "14d",  label: "14d",  days: 14 },
  { id: "30d",  label: "30d",  days: 30 },
  { id: "90d",  label: "90d",  days: 90 },
  { id: "custom", label: "Custom", days: null },
];

function FilterBar({ value, onChange }) {
  const { preset, start, end, products, compare } = value;
  function set(k, v) { onChange({ ...value, [k]: v }); }

  function toggleProduct(id) {
    const has = products.includes(id);
    set("products", has ? products.filter(p => p !== id) : [...products, id]);
  }

  return (
    <div className="filterbar">
      <span className="filterbar__icon-label"><ICalendar /> Range</span>

      <div className="seg">
        {PRESETS.map(p => (
          <button key={p.id} className={"seg__opt " + (preset === p.id ? "is-active" : "")}
                  onClick={() => set("preset", p.id)}>{p.label}</button>
        ))}
      </div>

      <div className="filterbar__group" style={{ display: preset === "custom" ? "flex" : "none" }}>
        <input className="input" type="date" value={start} onChange={e => set("start", e.target.value)} />
        <input className="input" type="date" value={end} onChange={e => set("end", e.target.value)} />
      </div>

      <div style={{ width: 1, height: 22, background: "var(--c-border)", margin: "0 4px" }} />

      <span className="filterbar__icon-label"><IFilter /> Products</span>
      <div className="seg" style={{ background: "var(--c-surface)" }}>
        <button className={"seg__opt " + (products.length === 0 ? "is-active" : "")}
                onClick={() => set("products", [])}>All</button>
        {RL.PRODUCTS.map(p => (
          <button key={p.id} className={"seg__opt " + (products.includes(p.id) ? "is-active" : "")}
                  onClick={() => toggleProduct(p.id)}>
            <span style={{ width: 6, height: 6, borderRadius: 2, background: p.color, display: "inline-block", marginRight: 6, verticalAlign: "middle" }} />
            {p.name}
          </button>
        ))}
      </div>

      <div style={{ flex: 1 }} />

      <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "var(--t-12)", color: "var(--c-ink-3)", whiteSpace: "nowrap" }}>
        <input type="checkbox" checked={compare} onChange={e => set("compare", e.target.checked)} />
        Compare to prior
      </label>
    </div>
  );
}

// ---- Modal ----
function Modal({ open, title, onClose, children, footer, width }) {
  React.useEffect(() => {
    if (!open) return;
    function onKey(e) { if (e.key === "Escape") onClose && onClose(); }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="modal-scrim" onClick={onClose}>
      <div className="modal" style={width ? { width } : null} onClick={e => e.stopPropagation()}>
        <div className="modal__head">
          <h3 className="modal__title">{title}</h3>
          <div style={{ flex: 1 }} />
          <button className="btn btn--ghost btn--icon" onClick={onClose} aria-label="Close"><IX /></button>
        </div>
        <div className="modal__body">{children}</div>
        {footer && <div className="modal__foot">{footer}</div>}
      </div>
    </div>
  );
}

// ---- Skeleton helpers ----
function SkRow({ widths = [60, 40, 40, 60, 40] }) {
  return (
    <tr>
      {widths.map((w, i) => (
        <td key={i}><span className="sk sk--row" style={{ width: w + "%" }} /></td>
      ))}
    </tr>
  );
}

function SkKpiGrid({ n = 5 }) {
  return (
    <div className="kpi-grid">
      {Array.from({ length: n }).map((_, i) => (
        <KpiTile key={i} loading label="Loading…" priorLabel="vs prior" />
      ))}
    </div>
  );
}

Object.assign(window, { KpiTile, Delta, FilterBar, Modal, SkRow, SkKpiGrid, fmtDelta });
