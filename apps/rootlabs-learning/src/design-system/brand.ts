/**
 * Brand identity strings — change here to swap the entire app's brand.
 *
 * Phase 0 Decision 4: "Rootlabs" for code identifiers, "Root Labs" for display copy.
 * Both forms appear on the live rootlabs.co — neither is wrong.
 */

export const brand = {
  // Identifiers (code-side)
  slug: "rootlabs",

  // Display (user-facing)
  displayName: "Root Labs",
  displayNameShort: "Root Labs",
  tagline: "Handpicked in nature. Perfected in science.",
  taglineShort: "Handpicked in nature.",
  copyright: "© Root Labs 2026. All rights reserved",

  // Brand pillars (3-up section)
  pillars: [
    {
      icon: "🌿",
      title: "Carefully crafted",
      body: "Each ingredient hand-selected at its source.",
    },
    {
      icon: "🧬",
      title: "Maximum absorption",
      body: "Bioavailability-first formulation.",
    },
    {
      icon: "📚",
      title: "Science-backed",
      body: "Every claim tied to peer-reviewed research.",
    },
  ],

  // Voice phrases (verbatim from rootlabs.co — use these in headers / hero copy)
  voicePhrases: {
    expandYourRoots: "Expand Your Roots",
    rightFromTheRoots: "Right from the Roots",
    bornFromDesire: "Born of the desire to return to our roots",
    influencingOurVoice: "Influencing Our Voice",
    fromExpertsWeTrust: "From Experts We Trust",
    ourCustomersSpeak: "Our Customers Speak",
    bioavailabilityMadeAvailable: "Bioavailability Made Available",
    noSugarcoating: "No sugarcoating. We mean it",
    knowYourBody: "Know Your Body",
    findYourIngredients: "Find Your Ingredients",
    harnessingAncientRemedies: "Harnessing the Power of Ancient Remedies",
    perfectedInScience: "Perfected in Science",
    handpickedInNature: "Handpicked in Nature",
  },

  // Section kickers — tiny ALL-CAPS labels above headlines (verbatim from site)
  kickers: {
    ourScience: "OUR SCIENCE",
    ourProducts: "OUR PRODUCTS",
    ourStory: "OUR STORY",
    ourVoice: "OUR VOICE",
    ourInfluencers: "OUR INFLUENCERS",
    perfectedInScience: "PERFECTED IN SCIENCE",
    handpickedInNature: "HANDPICKED IN NATURE",
    ingredients: "INGREDIENTS",
  },

  // Founder (from /pages/our-story)
  founder: {
    name: "Mayank Kumar",
    role: "Founder",
    headline: "Influencing Our Voice",
  },

  // Social handles (rootlabs.co footer)
  social: {
    instagram: "rootlabsofficial",
    tiktok: "rootlabsofficial",
  },
} as const;
