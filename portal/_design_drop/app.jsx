/* global React, ReactDOM, RL, LoginScreen, PocDashboardScreen, OperatorDashboardScreen, CreatorsListScreen, CreatorDetailScreen, RosterScreen, ProductsScreen, WizardScreen, DesignSystemScreen, Sidebar, Topbar, ImpersonationBanner, useTweaks, TweaksPanel, TweakSection, TweakRadio, TweakColor, TweakToggle, TweakSelect, IInfo */
/* ============================================================
   Rootlabs Portal — App router + session
   ============================================================ */

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#1f6f4a",
  "density": "regular",
  "useEmoji": false,
  "showImpersonationByDefault": false,
  "startScreen": "POC dashboard",
  "fontPair": "Switzer + JetBrains Mono"
}/*EDITMODE-END*/;

function readInitialRoute() {
  const h = window.location.hash.replace(/^#\/?/, "");
  return h || "login";
}

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  // Apply accent + density to <html> via CSS vars
  React.useEffect(() => {
    document.documentElement.style.setProperty("--c-accent", t.accent);
    // Tint variants from accent so the whole palette updates coherently
    document.documentElement.style.setProperty("--c-accent-hover", shade(t.accent, -10));
    document.documentElement.style.setProperty("--c-accent-press", shade(t.accent, -22));
    document.documentElement.style.setProperty("--c-accent-soft",  tint(t.accent, 0.88));
    document.documentElement.style.setProperty("--c-accent-soft-2",tint(t.accent, 0.75));
    document.documentElement.style.setProperty("--c-accent-ink",   shade(t.accent, -25));
  }, [t.accent]);

  React.useEffect(() => {
    document.documentElement.setAttribute("data-density", t.density);
  }, [t.density]);

  React.useEffect(() => {
    if (t.fontPair === "IBM Plex Sans + IBM Plex Mono") {
      document.documentElement.style.setProperty("--f-sans", `"IBM Plex Sans", ui-sans-serif, system-ui, sans-serif`);
      document.documentElement.style.setProperty("--f-mono", `"IBM Plex Mono", ui-monospace, monospace`);
    } else if (t.fontPair === "System default") {
      document.documentElement.style.setProperty("--f-sans", `ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif`);
      document.documentElement.style.setProperty("--f-mono", `ui-monospace, "SF Mono", Menlo, Consolas, monospace`);
    } else {
      document.documentElement.style.setProperty("--f-sans", `"Switzer", ui-sans-serif, system-ui, sans-serif`);
      document.documentElement.style.setProperty("--f-mono", `"JetBrains Mono", ui-monospace, Menlo, Consolas, monospace`);
    }
  }, [t.fontPair]);

  const [route, setRoute] = React.useState(readInitialRoute());
  const [routeParams, setRouteParams] = React.useState({});

  // Session — operator may impersonate a POC; when impersonating, currentPoc is the target.
  const [session, setSession] = React.useState({
    user: null,
    activeAs: null, // null | { pocId }
  });

  // Sync hash on navigate
  React.useEffect(() => {
    const slug = routeParams.handle ? `${route}/${routeParams.handle}` : route;
    if (window.location.hash !== "#/" + slug) {
      window.history.replaceState(null, "", "#/" + slug);
    }
  }, [route, routeParams]);

  // Listen for hash changes (browser nav)
  React.useEffect(() => {
    const fn = () => {
      const parts = window.location.hash.replace(/^#\/?/, "").split("/");
      setRoute(parts[0] || "login");
      if (parts[0] === "creator-detail" && parts[1]) setRouteParams({ handle: "@" + parts[1] });
      else setRouteParams({});
    };
    window.addEventListener("hashchange", fn);
    return () => window.removeEventListener("hashchange", fn);
  }, []);

  // Auto-bootstrap a session when leaving login (handle deep-link refresh)
  React.useEffect(() => {
    if (!session.user && route !== "login" && route !== "design-system") {
      // Pick starting screen based on tweak choice
      const isOperator = route === "operator-dashboard";
      setSession({
        user: isOperator
          ? { role: "operator", name: "Ops Operator", initials: "OP" }
          : { role: "poc", pocId: "anika" },
        activeAs: null,
      });
    }
  }, [route]);

  // Filter state (shared across dashboard, creators)
  const [filter, setFilter] = React.useState({
    preset: "30d", products: [], compare: true, start: "", end: "",
  });

  // Loading-trigger to nudge skeletons on impersonation switch etc.
  const [loadingTick, setLoadingTick] = React.useState(0);

  function navigate(r, params = {}) {
    if (r === "login") {
      setSession({ user: null, activeAs: null });
    }
    if (params.user) {
      setSession({ user: params.user, activeAs: null });
    }
    setRoute(r);
    setRouteParams(params);
    window.scrollTo({ top: 0 });
  }

  function actAs(pocId) {
    setSession(s => ({ ...s, activeAs: { pocId } }));
    setLoadingTick(n => n + 1);
    navigate("poc-dashboard");
  }
  function stopActAs() {
    setSession(s => ({ ...s, activeAs: null }));
    setLoadingTick(n => n + 1);
    navigate("operator-dashboard");
  }

  // Compute effective POC for screens that need one
  const effectivePocId = session.activeAs
    ? session.activeAs.pocId
    : (session.user?.role === "poc" ? session.user.pocId : "anika");

  const currentPoc = session.user?.role === "operator" && !session.activeAs
    ? { ...session.user, rosterSize: undefined, role: "operator" }
    : { ...RL.POC_DATA[effectivePocId], role: "poc" };

  const impersonating = !!session.activeAs;
  const showShell = route !== "login";

  return (
    <>
      {/* Login */}
      {route === "login" && (
        <LoginScreen navigate={navigate} />
      )}

      {/* App shell */}
      {showShell && (
        <div className="app">
          <Sidebar
            route={route}
            navigate={navigate}
            impersonating={impersonating}
            currentPoc={currentPoc}
          />
          <div>
            {impersonating && session.activeAs && (
              <ImpersonationBanner
                poc={RL.POC_DATA[session.activeAs.pocId]}
                onStop={stopActAs}
              />
            )}
            <Topbar
              crumbs={crumbsFor(route, routeParams, currentPoc)}
              queryState={null /* per-page loading pill is more accurate */}
              right={null}
            />

            {route === "poc-dashboard" && (
              <PocDashboardScreen pocId={effectivePocId} filter={filter} setFilter={setFilter} useEmoji={t.useEmoji} loadingTrigger={loadingTick} navigate={navigate} />
            )}

            {route === "operator-dashboard" && session.user?.role === "operator" && !impersonating && (
              <OperatorDashboardScreen filter={filter} setFilter={setFilter} navigate={navigate} useEmoji={t.useEmoji} actAs={actAs} loadingTrigger={loadingTick} />
            )}

            {route === "operator-dashboard" && (session.user?.role !== "operator" || impersonating) && (
              <PermissionStub navigate={navigate} role={session.user?.role} />
            )}

            {route === "creators" && (
              <CreatorsListScreen pocId={effectivePocId} navigate={navigate} filter={filter} setFilter={setFilter} loadingTrigger={loadingTick} />
            )}

            {route === "creator-detail" && (
              <CreatorDetailScreen pocId={effectivePocId} handle={routeParams.handle} navigate={navigate} />
            )}

            {route === "roster" && (
              <RosterScreen pocId={effectivePocId} navigate={navigate} />
            )}

            {route === "products" && (
              <ProductsScreen />
            )}

            {route === "wizard" && (
              <WizardScreen />
            )}

            {route === "design-system" && (
              <DesignSystemScreen />
            )}
          </div>
        </div>
      )}

      {/* Floating jump-to (top right of every screen) — quick demo nav */}
      {showShell && <JumpBar navigate={navigate} session={session} setSession={setSession} />}

      {/* Tweaks panel */}
      <TweaksPanel title="Tweaks">
        <TweakSection label="Look" />
        <TweakColor label="Accent" value={t.accent}
          options={["#1f6f4a","#2d6a4f","#0f766e","#15803d","#0e7490","#1d4ed8","#7c3aed","#b45309"]}
          onChange={(v) => setTweak("accent", v)} />
        <TweakRadio label="Density" value={t.density}
          options={["tight","regular","loose"]}
          onChange={(v) => setTweak("density", v)} />
        <TweakSelect label="Type" value={t.fontPair}
          options={["Switzer + JetBrains Mono","IBM Plex Sans + IBM Plex Mono","System default"]}
          onChange={(v) => setTweak("fontPair", v)} />
        <TweakSection label="KPIs" />
        <TweakToggle label="Use emoji prefixes (📹 🔴 🛒 💰 💵)"
          value={t.useEmoji}
          onChange={(v) => setTweak("useEmoji", v)} />
      </TweaksPanel>
    </>
  );
}

function PermissionStub({ navigate }) {
  return (
    <div className="page">
      <div className="empty">
        <div className="empty__icon"><IInfo /></div>
        <p className="empty__title">Operator view requires the operator role</p>
        <p className="empty__sub">Sign in as <code className="mono">operator@…</code> from the login screen to see the team dashboard.</p>
        <button className="btn btn--primary" onClick={() => navigate("login")}>Back to sign-in</button>
      </div>
    </div>
  );
}

function JumpBar({ navigate, session, setSession }) {
  // Tiny dev/demo helper — surfaces all the screens since this is a portfolio mock.
  const [open, setOpen] = React.useState(false);
  const screens = [
    ["poc-dashboard",      "POC dashboard"],
    ["operator-dashboard", "Operator dashboard"],
    ["creators",           "Creators"],
    ["creator-detail",     "Creator detail"],
    ["roster",             "Roster"],
    ["products",           "Products"],
    ["wizard",             "Browse data"],
    ["design-system",      "Design system"],
    ["login",              "Login"],
  ];
  return (
    <div style={{
      position: "fixed", left: "calc(var(--sidebar-w) + 16px)", bottom: 16, zIndex: 40,
      display: "flex", pointerEvents: "auto",
    }}>
      <div style={{
        background: "var(--c-surface)",
        border: "1px solid var(--c-border)",
        borderRadius: "var(--r-pill)",
        boxShadow: "var(--sh-pop)",
        padding: 4,
        display: "flex",
        alignItems: "center",
        gap: 2,
      }}>
        <span className="mono" style={{ fontSize: 10, color: "var(--c-ink-3)", padding: "0 10px", textTransform: "uppercase", letterSpacing: "0.08em" }}>
          Demo · jump to
        </span>
        {!open && <button className="btn btn--sm" onClick={() => setOpen(true)} style={{ borderColor: "transparent", borderRadius: "var(--r-pill)" }}>All screens →</button>}
        {open && screens.map(([id, label]) => (
          <button key={id} className="btn btn--sm" onClick={() => {
            // simulate operator vs POC permission
            if (id === "operator-dashboard" && session.user?.role !== "operator") {
              setSession({ user: { role: "operator", name: "Ops Operator", initials: "OP" }, activeAs: null });
            }
            navigate(id);
          }} style={{ borderColor: "transparent", borderRadius: "var(--r-pill)" }}>
            {label}
          </button>
        ))}
        {open && <button className="btn btn--sm btn--icon" onClick={() => setOpen(false)} style={{ borderColor: "transparent", borderRadius: "var(--r-pill)" }}>×</button>}
      </div>
    </div>
  );
}

function crumbsFor(route, params, poc) {
  const home = { label: "Rootlabs", href: "#/poc-dashboard" };
  switch (route) {
    case "poc-dashboard":      return [home, { label: poc?.name ? poc.name + "'s dashboard" : "Dashboard" }];
    case "operator-dashboard": return [home, { label: "Team overview" }];
    case "creators":           return [home, { label: "Creators" }];
    case "creator-detail":     return [home, { label: "Creators", href: "#/creators" }, { label: params.handle || "" }];
    case "roster":             return [home, { label: "Roster" }];
    case "products":           return [home, { label: "Products" }];
    case "wizard":             return [home, { label: "Browse data" }];
    case "design-system":      return [home, { label: "Design system" }];
    default:                   return [home];
  }
}

/* Color helpers — adjust lightness in HSL to derive accent variants */
function hexToHSL(hex) {
  let r = parseInt(hex.slice(1,3),16)/255;
  let g = parseInt(hex.slice(3,5),16)/255;
  let b = parseInt(hex.slice(5,7),16)/255;
  const max = Math.max(r,g,b), min = Math.min(r,g,b);
  let h=0,s=0,l=(max+min)/2;
  if (max!==min) {
    const d = max-min;
    s = l > 0.5 ? d/(2-max-min) : d/(max+min);
    switch(max){
      case r: h=(g-b)/d+(g<b?6:0); break;
      case g: h=(b-r)/d+2; break;
      case b: h=(r-g)/d+4; break;
    }
    h/=6;
  }
  return [h*360, s*100, l*100];
}
function hslToHex(h,s,l){
  s/=100; l/=100;
  const a = s*Math.min(l,1-l);
  const f = (n,k=(n+h/30)%12) => l - a*Math.max(-1,Math.min(k-3,9-k,1));
  const toHex = v => Math.round(v*255).toString(16).padStart(2,"0");
  return "#"+toHex(f(0))+toHex(f(8))+toHex(f(4));
}
function shade(hex, dl){ const [h,s,l] = hexToHSL(hex); return hslToHex(h,s,Math.max(0,Math.min(100,l+dl))); }
function tint(hex, towardWhite){
  const [h,s,l] = hexToHSL(hex);
  const newL = l + (100-l)*towardWhite;
  const newS = s * (1 - towardWhite*0.5);
  return hslToHex(h, newS, newL);
}

const root = document.getElementById("root");
ReactDOM.createRoot(root).render(<App />);
