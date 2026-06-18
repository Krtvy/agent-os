/* ============================================================
   Rootlabs Portal — Mock data
   Seeded deterministic pseudo-random so charts are stable.
   ============================================================ */

(function () {
  function mulberry32(seed) {
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      let t = seed;
      t = Math.imul(t ^ t >>> 15, t | 1);
      t ^= t + Math.imul(t ^ t >>> 7, t | 61);
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  const PRODUCTS = [
    { id: "HGR",      name: "HGR",      full: "Hair Growth Routine",      tag: "hero",   color: "#1f6f4a" },
    { id: "Alpha",    name: "Alpha",    full: "Alpha Testosterone Stack", tag: "hero",   color: "#b45309" },
    { id: "MagAshwa", name: "MagAshwa", full: "Mag + Ashwagandha",        tag: "bundle", color: "#1d4ed8" },
    { id: "BB",       name: "BB",       full: "Beard Booster",            tag: "extra",  color: "#7c3aed" },
    { id: "PPP",      name: "PPP",      full: "Performance Power Plus",   tag: "extra",  color: "#0e7490" },
  ];

  const POCS = [
    { id: "anika",   name: "Anika Raghav",    initials: "AR", color: "#1f6f4a" },
    { id: "bharath", name: "Bharath Kotyada", initials: "BK", color: "#b45309" },
    { id: "cyrus",   name: "Cyrus Mehta",     initials: "CM", color: "#1d4ed8" },
    { id: "devika",  name: "Devika Pant",     initials: "DP", color: "#7c3aed" },
    { id: "eshaan",  name: "Eshaan Tandon",   initials: "ET", color: "#0e7490" },
    { id: "farah",   name: "Farah Qureshi",   initials: "FQ", color: "#be185d" },
    { id: "gaurav",  name: "Gaurav Vyas",     initials: "GV", color: "#0f766e" },
    { id: "hiba",    name: "Hiba Nasreen",    initials: "HN", color: "#9333ea" },
  ];

  // Handle pool — generic enough
  const HANDLE_FIRST = ["luna","kabir","sana","arjun","mira","rohan","priya","kiran","aditi","viraj","nisha","tanvi","ishaan","zoya","aaryan","myra","reyansh","kavya","veer","aanya","vivaan","saanvi","ayaan","ira","abeer","navya"];
  const HANDLE_SUFFIX = ["beauty","wellness","fit","reels","official","tries","daily","life","talks","studio","glow","real","clips","co","fam","story","unfiltered","speaks","irl",""];

  function makeRoster(seedBase, n) {
    const r = mulberry32(seedBase);
    const out = [];
    const used = new Set();
    for (let i = 0; i < n; i++) {
      let handle = "";
      while (!handle || used.has(handle)) {
        const first = HANDLE_FIRST[Math.floor(r() * HANDLE_FIRST.length)];
        const suf = HANDLE_SUFFIX[Math.floor(r() * HANDLE_SUFFIX.length)];
        handle = "@" + first + (suf ? "." + suf : "") + (r() < 0.18 ? Math.floor(r() * 99) : "");
      }
      used.add(handle);
      const baseScale = Math.pow(r(), 1.6); // heavy tail
      const videos = Math.max(0, Math.round(8 + baseScale * 110 + r() * 12));
      const lives = Math.max(0, Math.round(baseScale * 18 + r() * 4));
      const orders = Math.max(0, Math.round(videos * (1.2 + r() * 4) + lives * (12 + r() * 25)));
      const aov = 720 + Math.round(r() * 380);
      const gmv = orders * aov;
      const commission = Math.round(gmv * (0.10 + r() * 0.05));
      const productMix = {};
      PRODUCTS.forEach(p => { productMix[p.id] = Math.round(r() * 100); });
      // normalize roughly
      out.push({
        handle, videos, lives, orders, gmv, commission, aov,
        cumVideos: makeCumSeries(seedBase + i * 7, 30, videos),
        dailyOrders: makeSeries(seedBase + i * 11, 30, orders / 30, 0.5),
        dailyGmv: makeSeries(seedBase + i * 13, 30, gmv / 30, 0.45),
        productMix,
        joinedDays: Math.round(r() * 220 + 14),
        status: r() < 0.07 ? "paused" : "active",
        avatarColor: PRODUCTS[Math.floor(r() * PRODUCTS.length)].color,
      });
    }
    return out.sort((a, b) => b.gmv - a.gmv);
  }

  function makeSeries(seed, n, mean, vol) {
    const r = mulberry32(seed);
    const out = [];
    for (let i = 0; i < n; i++) {
      const noise = (r() - 0.5) * 2 * vol;
      const trend = (i / n) * 0.4;
      out.push(Math.max(0, Math.round(mean * (1 + noise + trend))));
    }
    return out;
  }
  function makeCumSeries(seed, n, total) {
    const series = makeSeries(seed, n, total / n, 0.5);
    let s = 0;
    return series.map(v => (s += v));
  }
  function sum(a) { return a.reduce((x, y) => x + y, 0); }

  // Build all POC rosters and aggregates
  const POC_DATA = {};
  POCS.forEach((p, idx) => {
    const roster = makeRoster(1000 + idx * 100, 18 + (idx % 4) * 3);
    const videos = sum(roster.map(r => r.videos));
    const lives = sum(roster.map(r => r.lives));
    const orders = sum(roster.map(r => r.orders));
    const gmv = sum(roster.map(r => r.gmv));
    const commission = sum(roster.map(r => r.commission));
    // daily aggregated
    const dailyGmv = new Array(30).fill(0);
    const dailyOrders = new Array(30).fill(0);
    roster.forEach(c => {
      c.dailyGmv.forEach((v, i) => dailyGmv[i] += v);
      c.dailyOrders.forEach((v, i) => dailyOrders[i] += v);
    });
    const prior = {
      videos: Math.round(videos * (0.85 + (idx % 3) * 0.08)),
      lives:  Math.round(lives  * (0.92 + (idx % 4) * 0.04)),
      orders: Math.round(orders * (0.78 + (idx % 5) * 0.06)),
      gmv:    Math.round(gmv    * (0.81 + (idx % 4) * 0.07)),
      commission: Math.round(commission * (0.82 + (idx % 3) * 0.06)),
      dailyGmv: dailyGmv.map((v, i) => Math.round(v * (0.78 + 0.3 * Math.sin((i + idx) * 0.4)))),
    };
    POC_DATA[p.id] = {
      ...p,
      rosterSize: roster.length,
      roster,
      videos, lives, orders, gmv, commission,
      dailyGmv, dailyOrders, prior,
      byProduct: PRODUCTS.map(prod => {
        const r = mulberry32(idx * 31 + prod.id.length);
        const v = Math.round(videos * (0.1 + r() * 0.4));
        const g = Math.round(gmv * (0.05 + r() * 0.35));
        return { product: prod.id, videos: v, gmv: g };
      }),
    };
  });

  // Operator-level aggregate
  const OPERATOR = (function () {
    const agg = { videos: 0, lives: 0, orders: 0, gmv: 0, commission: 0 };
    const prior = { videos: 0, lives: 0, orders: 0, gmv: 0, commission: 0, dailyGmv: new Array(30).fill(0) };
    const dailyGmv = new Array(30).fill(0);
    POCS.forEach(p => {
      const d = POC_DATA[p.id];
      ["videos","lives","orders","gmv","commission"].forEach(k => { agg[k] += d[k]; prior[k] += d.prior[k]; });
      d.dailyGmv.forEach((v, i) => dailyGmv[i] += v);
      d.prior.dailyGmv.forEach((v, i) => prior.dailyGmv[i] += v);
    });
    return { ...agg, prior, dailyGmv, rosterSize: POCS.reduce((s, p) => s + POC_DATA[p.id].rosterSize, 0) };
  })();

  // Recent videos for creator-detail
  function makeRecentVideos(seed) {
    const r = mulberry32(seed);
    const captions = [
      "POV: when your hairline starts winning again",
      "3-month update, before/after",
      "okay this stuff actually works",
      "rating wellness brands I've tried",
      "GRWM + my morning stack",
      "what's in my supplement drawer",
      "honest review after 8 weeks",
      "tag your boyfriend who needs this",
      "this saved my routine",
      "did NOT expect these results",
    ];
    const out = [];
    for (let i = 0; i < 6; i++) {
      out.push({
        id: i,
        caption: captions[Math.floor(r() * captions.length)],
        product: PRODUCTS[Math.floor(r() * PRODUCTS.length)].id,
        views: Math.round(2000 + r() * 480000),
        orders: Math.round(2 + r() * 140),
        gmv: Math.round((500 + r() * 80000)),
        daysAgo: Math.round(r() * 22),
      });
    }
    return out;
  }

  // Catalog
  const CATALOG = [
    { sku: "HGR-01", name: "HGR Daily Tonic", product: "HGR", tag: "hero", price: 1499 },
    { sku: "HGR-02", name: "HGR Scalp Serum", product: "HGR", tag: "hero", price: 899 },
    { sku: "HGR-03", name: "HGR Starter Kit", product: "HGR", tag: "bundle", price: 2199 },
    { sku: "ALP-01", name: "Alpha Daily Caps", product: "Alpha", tag: "hero", price: 1799 },
    { sku: "ALP-02", name: "Alpha Boost Shot", product: "Alpha", tag: "extra", price: 449 },
    { sku: "ALP-03", name: "Alpha + Mag Stack", product: "Alpha", tag: "bundle", price: 2599 },
    { sku: "MAG-01", name: "MagAshwa Sleep",  product: "MagAshwa", tag: "hero", price: 1199 },
    { sku: "MAG-02", name: "MagAshwa Calm AM",product: "MagAshwa", tag: "extra", price: 1099 },
    { sku: "MAG-03", name: "Calm Bundle",     product: "MagAshwa", tag: "bundle", price: 1999 },
    { sku: "BB-01",  name: "Beard Booster Oil",product: "BB", tag: "hero", price: 699 },
    { sku: "BB-02",  name: "Beard Roller",    product: "BB", tag: "extra", price: 599 },
    { sku: "BB-03",  name: "Beard Grow Kit",  product: "BB", tag: "bundle", price: 1399 },
    { sku: "PPP-01", name: "Performance Caps",product: "PPP", tag: "hero", price: 1299 },
    { sku: "PPP-02", name: "Power Pre-Workout",product: "PPP", tag: "extra", price: 999 },
    { sku: "PPP-03", name: "PPP Performance Stack", product: "PPP", tag: "bundle", price: 2299 },
  ];

  // Format helpers
  function inr(n) {
    if (n >= 10_000_000) return "₹" + (n / 10_000_000).toFixed(2) + " Cr";
    if (n >= 100_000)    return "₹" + (n / 100_000).toFixed(2) + " L";
    if (n >= 1000)       return "₹" + (n / 1000).toFixed(1) + "K";
    return "₹" + n.toLocaleString("en-IN");
  }
  function nshort(n) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
    if (n >= 1_000)     return (n / 1_000).toFixed(1) + "K";
    return String(n);
  }
  function n(n) { return n.toLocaleString("en-IN"); }
  function pct(curr, prior) {
    if (!prior) return { v: 0, dir: "flat" };
    const d = (curr - prior) / prior * 100;
    return { v: d, dir: d > 0.5 ? "up" : d < -0.5 ? "down" : "flat" };
  }
  function dateLabel(daysAgo) {
    const d = new Date();
    d.setDate(d.getDate() - daysAgo);
    return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short" });
  }

  window.RL = {
    PRODUCTS, POCS, POC_DATA, OPERATOR, CATALOG,
    makeRecentVideos,
    inr, nshort, n, pct, dateLabel,
  };
})();
