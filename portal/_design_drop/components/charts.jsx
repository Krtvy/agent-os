/* global React */
/* ============================================================
   Rootlabs Portal — Sparkline + Chart primitives
   Pure inline SVG. Two sizes share the same data + path math.
   ============================================================ */

// ---- Sparkline: tiny inline chart ----
// data: number[]; w, h: dimensions; tone: "accent" | "ink" | "success" | "error" | "warn"
function Sparkline({ data, w = 120, h = 24, tone = "accent", area = true, dot = false }) {
  if (!data || data.length === 0) return <svg width={w} height={h} />;
  const pad = 1;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const stepX = (w - pad * 2) / Math.max(1, data.length - 1);
  const yFor = (v) => pad + (1 - (v - min) / range) * (h - pad * 2);
  const pts = data.map((v, i) => [pad + i * stepX, yFor(v)]);
  const line = pts.map((p, i) => (i === 0 ? "M" : "L") + p[0].toFixed(2) + " " + p[1].toFixed(2)).join(" ");
  const areaPath = line + ` L ${(pad + (data.length - 1) * stepX).toFixed(2)} ${h - pad} L ${pad} ${h - pad} Z`;

  const stroke = {
    accent: "var(--c-accent)",
    ink:    "var(--c-ink-2)",
    success: "var(--c-success)",
    error:  "var(--c-error)",
    warn:   "var(--c-warn)",
    muted:  "var(--c-ink-4)",
  }[tone] || tone;

  const fill = {
    accent: "rgba(31,111,74,0.10)",
    ink:    "rgba(28,25,23,0.08)",
    success: "rgba(22,121,77,0.10)",
    error:  "rgba(180,35,24,0.10)",
    warn:   "rgba(180,83,9,0.10)",
    muted:  "rgba(120,113,108,0.10)",
  }[tone] || "rgba(31,111,74,0.10)";

  const last = pts[pts.length - 1];

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" aria-hidden="true">
      {area && <path d={areaPath} fill={fill} />}
      <path d={line} fill="none" stroke={stroke} strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
      {dot && last && <circle cx={last[0]} cy={last[1]} r="2.25" fill={stroke} />}
    </svg>
  );
}

// ---- SparkButton: clickable sparkline that opens a modal ----
function SparkButton({ data, onOpen, w = 120, h = 24, tone = "accent" }) {
  return (
    <button className="spark-btn" onClick={onOpen} aria-label="Open larger chart">
      <Sparkline data={data} w={w} h={h} tone={tone} area={true} dot={true} />
    </button>
  );
}

// ---- LineChart: larger inline SVG line chart with current + prior overlay ----
// series: { current: number[], prior?: number[], labels?: string[] }
function LineChart({ series, w = 720, h = 240, padding = { t: 16, r: 16, b: 28, l: 48 }, format = (v) => v, tone = "accent" }) {
  const { current, prior, labels } = series;
  const [hover, setHover] = React.useState(null);
  const ref = React.useRef(null);

  const all = [...(current || []), ...(prior || [])].filter(v => typeof v === "number");
  const min = 0;
  const max = Math.max(...all) * 1.1 || 1;
  const innerW = w - padding.l - padding.r;
  const innerH = h - padding.t - padding.b;
  const n = current.length;
  const stepX = innerW / Math.max(1, n - 1);
  const xFor = (i) => padding.l + i * stepX;
  const yFor = (v) => padding.t + (1 - (v - min) / (max - min)) * innerH;

  const path = (arr) => arr.map((v, i) => (i === 0 ? "M" : "L") + xFor(i).toFixed(1) + " " + yFor(v).toFixed(1)).join(" ");

  const stroke = "var(--c-accent)";
  const fill = "rgba(31,111,74,0.08)";
  const areaPath = path(current) + ` L ${xFor(n - 1).toFixed(1)} ${padding.t + innerH} L ${xFor(0).toFixed(1)} ${padding.t + innerH} Z`;

  // y-axis ticks (4)
  const ticks = [0, 0.25, 0.5, 0.75, 1].map(t => min + (max - min) * t);

  function handleMove(e) {
    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const i = Math.round((x - padding.l) / stepX);
    if (i < 0 || i >= n) { setHover(null); return; }
    setHover({ i, x: xFor(i), yC: yFor(current[i]), yP: prior ? yFor(prior[i]) : null });
  }
  function handleLeave() { setHover(null); }

  return (
    <div style={{ position: "relative" }}>
      <svg
        ref={ref}
        width="100%" height={h} viewBox={`0 0 ${w} ${h}`}
        onMouseMove={handleMove} onMouseLeave={handleLeave}
        style={{ display: "block", cursor: "crosshair" }}
      >
        {/* y gridlines + labels */}
        {ticks.map((t, i) => {
          const y = yFor(t);
          return (
            <g key={i}>
              <line x1={padding.l} x2={w - padding.r} y1={y} y2={y} stroke="var(--c-divider)" strokeWidth="1" />
              <text x={padding.l - 8} y={y + 3} textAnchor="end" fontSize="10" fontFamily="var(--f-mono)" fill="var(--c-ink-3)">{format(t)}</text>
            </g>
          );
        })}
        {/* x-axis labels (first, middle, last) */}
        {labels && [0, Math.floor(n / 2), n - 1].map(i => (
          <text key={i} x={xFor(i)} y={h - 8} textAnchor="middle" fontSize="10" fontFamily="var(--f-mono)" fill="var(--c-ink-3)">{labels[i]}</text>
        ))}

        {/* prior period (dashed) */}
        {prior && (
          <path d={path(prior)} fill="none" stroke="var(--c-ink-3)" strokeDasharray="3 4" strokeWidth="1.5" opacity="0.7" />
        )}
        {/* current period area + line */}
        <path d={areaPath} fill={fill} />
        <path d={path(current)} fill="none" stroke={stroke} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />

        {/* hover guideline + dots */}
        {hover && (
          <g>
            <line x1={hover.x} x2={hover.x} y1={padding.t} y2={h - padding.b} stroke="var(--c-ink)" strokeWidth="1" opacity="0.25" strokeDasharray="2 3" />
            {prior && hover.yP != null && <circle cx={hover.x} cy={hover.yP} r="4" fill="var(--c-surface)" stroke="var(--c-ink-3)" strokeWidth="1.5" />}
            <circle cx={hover.x} cy={hover.yC} r="5" fill="var(--c-surface)" stroke={stroke} strokeWidth="2" />
          </g>
        )}
      </svg>
      {hover && (
        <div className="chart-tip" style={{ left: `calc(${(hover.x / w) * 100}% + 0px)`, top: `${hover.yC + 8}px` }}>
          <div className="chart-tip__row"><span className="chart-tip__sw" style={{ background: stroke }} /><span>{labels ? labels[hover.i] : "Day " + (hover.i + 1)}</span></div>
          <div><strong>{format(current[hover.i])}</strong> <span className="muted">current</span></div>
          {prior && <div><strong>{format(prior[hover.i])}</strong> <span className="muted">prior</span></div>}
        </div>
      )}
    </div>
  );
}

// ---- BarsMini: tiny inline horizontal bars (used in creator detail / product mix) ----
function BarsMini({ items, max, format = (v) => v, w = 240 }) {
  const mx = max || Math.max(...items.map(i => i.value));
  return (
    <div style={{ display: "grid", gap: 6, width: w }}>
      {items.map((it, i) => (
        <div key={i} style={{ display: "grid", gridTemplateColumns: "70px 1fr 60px", alignItems: "center", gap: 8, fontSize: "var(--t-12)" }}>
          <span className="muted">{it.label}</span>
          <span style={{ height: 6, borderRadius: 3, background: "var(--c-sunken)", overflow: "hidden" }}>
            <span style={{ display: "block", height: "100%", width: `${(it.value / mx) * 100}%`, background: it.color || "var(--c-accent)" }} />
          </span>
          <span className="num mono" style={{ textAlign: "right" }}>{format(it.value)}</span>
        </div>
      ))}
    </div>
  );
}

Object.assign(window, { Sparkline, SparkButton, LineChart, BarsMini });
