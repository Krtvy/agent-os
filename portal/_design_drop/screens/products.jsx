/* global React, RL, PageHead, IPackage */
/* ============================================================
   Products catalog — read-only
   ============================================================ */

function ProductsScreen() {
  const tagColor = { hero: "chip--accent", bundle: "chip--info", extra: "chip" };
  const [filter, setFilter] = React.useState("all");
  const groups = ["all", "hero", "bundle", "extra"];

  return (
    <div className="page">
      <PageHead
        title="Products"
        sub={<>{RL.CATALOG.length} SKUs across {RL.PRODUCTS.length} product families · read-only</>}
      />

      <div className="row" style={{ marginBottom: "var(--s-3)" }}>
        <div className="seg">
          {groups.map(g => (
            <button key={g} className={"seg__opt " + (filter === g ? "is-active" : "")} onClick={() => setFilter(g)}>
              {g[0].toUpperCase() + g.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Product family overview cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "var(--s-3)", marginBottom: "var(--s-5)" }}>
        {RL.PRODUCTS.map(p => {
          const skus = RL.CATALOG.filter(s => s.product === p.id);
          return (
            <div key={p.id} className="card" style={{ padding: "var(--s-4)" }}>
              <span style={{ display: "inline-block", width: 28, height: 4, borderRadius: 2, background: p.color, marginBottom: "var(--s-2)" }} />
              <div style={{ fontWeight: 600, fontSize: "var(--t-15)" }}>{p.name}</div>
              <div className="muted" style={{ fontSize: "var(--t-12)", marginBottom: "var(--s-3)" }}>{p.full}</div>
              <div className="row" style={{ gap: 4 }}>
                <span className="chip">{skus.length} SKUs</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="card">
        <div className="card__head">
          <h3 className="card__title">Catalog</h3>
          <p className="card__sub">All SKUs across product families</p>
        </div>
        <div className="card__body card__body--flush">
          <table className="tbl">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Name</th>
                <th>Family</th>
                <th>Tag</th>
                <th className="num">MRP</th>
              </tr>
            </thead>
            <tbody>
              {RL.CATALOG.filter(s => filter === "all" || s.tag === filter).map(s => {
                const p = RL.PRODUCTS.find(p => p.id === s.product);
                return (
                  <tr key={s.sku}>
                    <td className="mono muted" style={{ fontSize: "var(--t-12)" }}>{s.sku}</td>
                    <td><strong style={{ fontWeight: 500 }}>{s.name}</strong></td>
                    <td>
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                        <span style={{ width: 8, height: 8, borderRadius: 2, background: p.color }} />
                        {p.name}
                      </span>
                    </td>
                    <td><span className={"chip " + tagColor[s.tag]}>{s.tag}</span></td>
                    <td className="num mono">{RL.inr(s.price)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

window.ProductsScreen = ProductsScreen;
