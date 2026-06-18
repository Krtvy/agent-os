/**
 * Mock AI coach — hand-written canned responses keyed by wellness goal.
 *
 * ⚠ PLUG IN HERE: replace with `ai-coach.claude.ts` when the company
 * provides Anthropic API access (route via a server proxy — never embed
 * a raw API key in the mobile bundle).
 */

import type { ProductRecommendation, WellnessGoal } from "@/types/domain";
import type { AICoachService } from "./ai-coach.interface";

const FAKE_LATENCY_MS = 400; // a touch slower to feel "AI"
const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

const GOAL_RECOMMENDATIONS: Record<WellnessGoal, ProductRecommendation[]> = {
  energy: [
    {
      productSlug: "alpha-gummies-60s",
      rationale:
        "Shilajit + Ashwagandha hits clean energy without caffeine crashes. Start with 60s pack.",
      confidence: 0.92,
    },
    {
      productSlug: "sea-moss-gummies",
      rationale:
        "Trace minerals fill the gaps most diets miss — supports cellular energy production.",
      confidence: 0.78,
    },
  ],
  immunity: [
    {
      productSlug: "immunity-combo",
      rationale:
        "Shilajit + Sea Moss + Turmeric stack — covers mineral, antioxidant, and inflammation angles.",
      confidence: 0.94,
    },
    {
      productSlug: "turmeric-gummies",
      rationale:
        "Curcumin bioavailability via piperine — daily anti-inflammatory baseline.",
      confidence: 0.81,
    },
  ],
  vitality: [
    {
      productSlug: "alpha-gummies-120s",
      rationale:
        "The deeper protocol — 4 months at full dose lets adaptogens reach steady state.",
      confidence: 0.9,
    },
    {
      productSlug: "sea-moss-gummies",
      rationale: "Mineral floor for everything else to build on.",
      confidence: 0.72,
    },
  ],
  general: [
    {
      productSlug: "alpha-gummies-60s",
      rationale:
        "Start here — single formulation covers energy, vitality, and absorption at a sensible price.",
      confidence: 0.85,
    },
    {
      productSlug: "turmeric-gummies",
      rationale: "Add if you want anti-inflammatory support alongside.",
      confidence: 0.7,
    },
  ],
};

const INGREDIENT_EXPLAINERS: Record<string, string> = {
  shilajit:
    "Shilajit is a resin that seeps from Himalayan rocks at 16,000+ feet. " +
    "It carries 84+ trace minerals and fulvic acid, which acts like a transport molecule — " +
    "helping your cells actually absorb what you eat. Think of it as a delivery system " +
    "for everything else in your supplement stack.",
  ashwagandha:
    "Ashwagandha (Withania somnifera) is an adaptogen — it doesn't push your body in one " +
    "direction, it helps regulate. KSM-66 is the full-spectrum root extract; it has the " +
    "strongest research backing for cortisol regulation and stress resilience. Best taken " +
    "in the evening when your cortisol curve should be falling anyway.",
  "sea-moss":
    "Sea moss (Irish moss) is a red algae carrying iodine, magnesium, potassium, and 90+ " +
    "trace minerals in their bioavailable form. It's not a magic bullet — it's the floor " +
    "that lets everything else work. If you've been mineral-deficient (most people are), " +
    "you'll notice it within 2–3 weeks.",
  turmeric:
    "Turmeric's active compound is curcumin. The catch: curcumin alone has very poor " +
    "bioavailability — your body excretes most of it. We pair it with piperine (from black " +
    "pepper) which boosts absorption 20×. Daily anti-inflammatory baseline.",
};

export const mockAICoach: AICoachService = {
  async recommendProducts(goal, _context) {
    await wait(FAKE_LATENCY_MS);
    return GOAL_RECOMMENDATIONS[goal] ?? GOAL_RECOMMENDATIONS.general;
  },

  async explainIngredient(slug) {
    await wait(FAKE_LATENCY_MS);
    return (
      INGREDIENT_EXPLAINERS[slug] ??
      "This ingredient hasn't been profiled yet in the demo. When Claude is wired in, this " +
        "response will be generated from the ingredient research database."
    );
  },

  async answerWellnessQuestion(question) {
    await wait(FAKE_LATENCY_MS);
    return (
      `(Demo mode) You asked: "${question}"\n\n` +
      "When Claude is wired in, this returns a grounded, source-cited answer drawing from " +
      "the rootlabs.co Science library and ingredient research. For now, the question is " +
      "logged so you can see the flow."
    );
  },
};
