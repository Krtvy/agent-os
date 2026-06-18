/* global React, RL, IArrowRight */
/* ============================================================
   Login — single email field, SSO-shaped.
   ============================================================ */

function LoginScreen({ navigate }) {
  const [email, setEmail] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const valid = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);

  function submit(e) {
    e.preventDefault();
    if (!valid) return;
    setSubmitting(true);
    setTimeout(() => {
      // Decide route by domain: "operator@" gets operator view, else POC
      const isOperator = email.toLowerCase().startsWith("operator") || email.toLowerCase().startsWith("admin");
      if (isOperator) navigate("operator-dashboard", { user: { role: "operator", name: "Ops Operator", initials: "OP" } });
      else navigate("poc-dashboard", { user: { role: "poc", pocId: "anika" } });
    }, 480);
  }

  return (
    <div className="login">
      <section className="login__brand-pane">
        <div className="login__brand">
          <span className="login__brand-mark">R</span>
          <span className="login__brand-name">Rootlabs Portal</span>
        </div>

        <div>
          <p style={{ fontSize: "var(--t-12)", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--c-ink-3)", marginBottom: "var(--s-4)" }}>
            For Mosaic Wellness creator ops
          </p>
          <h2 className="login__hero">
            One place to track your TikTok roster — <span>videos, lives, orders, GMV, commission. Daily.</span>
          </h2>

          <div style={{ display: "flex", gap: "var(--s-6)", marginTop: "var(--s-7)", fontSize: "var(--t-12)", color: "var(--c-ink-3)" }}>
            <span><strong style={{ color: "var(--c-ink)", fontFamily: "var(--f-mono)", fontSize: "var(--t-14)" }}>8</strong><br/>POCs</span>
            <span><strong style={{ color: "var(--c-ink)", fontFamily: "var(--f-mono)", fontSize: "var(--t-14)" }}>164</strong><br/>creators tracked</span>
            <span><strong style={{ color: "var(--c-ink)", fontFamily: "var(--f-mono)", fontSize: "var(--t-14)" }}>15</strong><br/>SKUs</span>
          </div>
        </div>

        <p style={{ fontSize: "var(--t-12)", color: "var(--c-ink-4)" }}>
          Internal tool · Mosaic Wellness Pvt. Ltd. · v2.0
        </p>
      </section>

      <section className="login__form-pane">
        <form className="login__form" onSubmit={submit}>
          <h1>Sign in</h1>
          <p className="sub">Use your @mosaicwellness.com email. SSO arrives next sprint.</p>

          <label className="label" htmlFor="email">Work email</label>
          <input
            id="email"
            className="input input--lg"
            type="email"
            placeholder="you@mosaicwellness.com"
            value={email}
            onChange={e => setEmail(e.target.value)}
            autoFocus
          />

          <button
            type="submit"
            className="btn btn--primary btn--lg"
            disabled={!valid || submitting}
            style={{ width: "100%", marginTop: "var(--s-4)" }}
          >
            {submitting ? "Sending magic link…" : "Continue"} <IArrowRight />
          </button>

          <p className="login__hint">
            Tip: <code style={{ fontFamily: "var(--f-mono)", background: "var(--c-sunken)", padding: "1px 5px", borderRadius: 3 }}>operator@…</code> signs in as the operator view; anything else is a POC.
          </p>
        </form>
      </section>
    </div>
  );
}

window.LoginScreen = LoginScreen;
