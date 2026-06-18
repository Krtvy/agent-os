/* global React, RL, PageHead, IPlus, IUpload, IX, IDownload, IUsers, ICheck */
/* ============================================================
   Roster management
   ============================================================ */

function RosterScreen({ pocId, navigate }) {
  const poc = RL.POC_DATA[pocId];
  const [roster, setRoster] = React.useState(poc.roster.map(r => r.handle));
  const [draft, setDraft] = React.useState("");
  const [bulk, setBulk] = React.useState(false);
  const [bulkText, setBulkText] = React.useState("");

  function addOne() {
    const h = draft.trim().startsWith("@") ? draft.trim() : "@" + draft.trim();
    if (!h.match(/^@[\w.]+$/) || roster.includes(h)) return;
    setRoster([h, ...roster]);
    setDraft("");
  }

  function removeOne(h) {
    setRoster(roster.filter(x => x !== h));
  }

  function importBulk() {
    const handles = bulkText.split(/[\n,\s]+/).map(s => s.trim()).filter(Boolean)
      .map(s => s.startsWith("@") ? s : "@" + s)
      .filter(s => s.match(/^@[\w.]+$/));
    const fresh = handles.filter(h => !roster.includes(h));
    setRoster([...fresh, ...roster]);
    setBulkText(""); setBulk(false);
  }

  return (
    <div className="page">
      <PageHead
        title="Roster"
        sub={<>{roster.length} creator handles on your roster · changes apply within 5 minutes</>}
        right={[
          <button key="dl" className="btn"><IDownload /> Download CSV</button>,
          <button key="bk" className="btn" onClick={() => setBulk(true)}><IUpload /> Bulk upload</button>,
        ]}
      />

      {/* Add row */}
      <div className="card" style={{ marginBottom: "var(--s-4)" }}>
        <div className="card__body" style={{ display: "flex", gap: "var(--s-3)" }}>
          <span className="filterbar__icon-label" style={{ paddingLeft: 0 }}><IPlus /></span>
          <input className="input" placeholder="@handle (paste TikTok username)" value={draft}
            onChange={e => setDraft(e.target.value)}
            onKeyDown={e => e.key === "Enter" && addOne()}
            style={{ flex: 1, maxWidth: 360 }} />
          <button className="btn btn--primary" disabled={!draft.trim()} onClick={addOne}>Add to roster</button>
          <span className="muted" style={{ fontSize: "var(--t-12)", alignSelf: "center" }}>
            We'll backfill the last 60 days of data on add.
          </span>
        </div>
      </div>

      {/* Roster list (chip grid) */}
      <div className="card">
        <div className="card__head">
          <h3 className="card__title">Your roster</h3>
          <p className="card__sub">{roster.length} handles</p>
        </div>
        <div className="card__body">
          {roster.length === 0
            ? <div className="empty">
                <div className="empty__icon"><IUsers /></div>
                <p className="empty__title">No creators on your roster</p>
                <p className="empty__sub">Add handles above or use Bulk upload to paste a list.</p>
              </div>
            : <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {roster.map(h => (
                  <span key={h} className="chip" style={{ padding: "4px 4px 4px 10px", fontFamily: "var(--f-mono)" }}>
                    {h}
                    <button className="chip__x" onClick={() => removeOne(h)} aria-label={"Remove " + h}><IX size={10} /></button>
                  </span>
                ))}
              </div>
          }
        </div>
      </div>

      {/* Bulk upload modal */}
      {bulk && (
        <div className="modal-scrim" onClick={() => setBulk(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal__head">
              <h3 className="modal__title">Bulk upload handles</h3>
              <div style={{ flex: 1 }} />
              <button className="btn btn--ghost btn--icon" onClick={() => setBulk(false)}><IX /></button>
            </div>
            <div className="modal__body">
              <p className="muted" style={{ fontSize: "var(--t-13)", marginTop: 0 }}>
                Paste handles separated by commas, spaces, or newlines. The <code style={{ fontFamily: "var(--f-mono)" }}>@</code> is optional.
              </p>
              <textarea
                className="input"
                style={{ height: 180, padding: "var(--s-3)", fontFamily: "var(--f-mono)", fontSize: "var(--t-13)", resize: "vertical" }}
                placeholder={"@luna.beauty\n@kabir.tries\nrohan.studio\n…"}
                value={bulkText} onChange={e => setBulkText(e.target.value)}
              />
              <p style={{ fontSize: "var(--t-12)", color: "var(--c-ink-3)", marginTop: 8 }}>
                {bulkText.split(/[\n,\s]+/).filter(Boolean).length} handles detected
              </p>
            </div>
            <div className="modal__foot">
              <button className="btn" onClick={() => setBulk(false)}>Cancel</button>
              <button className="btn btn--primary" onClick={importBulk} disabled={!bulkText.trim()}>
                <ICheck /> Add to roster
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

window.RosterScreen = RosterScreen;
