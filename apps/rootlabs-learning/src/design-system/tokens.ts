/**
 * Design Tokens — single source of truth for visual values.
 *
 * Color palette is extracted directly from rootlabs.co's Shopify theme JSON
 * (see _audit/2026-05-14_rootlabs-design-extraction.md). Do NOT change these
 * without updating that doc — they're the actual brand values, not guesses.
 *
 * Mosaic mobile patterns (button shape, spacing scale, etc.) are inherited
 * from the Be Bodywise + Man Matters extraction (see _audit/2026-05-14_mosaic-design-system-extraction.md).
 */

export const colors = {
  // ─── Brand (Rootlabs-specific) ─────────────────────────────────
  brand: "#13523B", // Primary forest green — the Rootlabs colour
  brandDark: "#0C3D2B", // Deeper green for the immersive Roots section
  brandHover: "#01563E", // Hover/pressed darker shade
  brandTeal: "#108474", // Social proof / verified badges
  accent: "#E5732E", // Warm orange — discount / urgency
  accentBright: "#F2A93B", // Yellow-orange — active pill / curve highlight
  ratingStar: "#FBCD0A", // Yellow stars

  // ─── Surfaces (cream-based, NOT pure white) ────────────────────
  bg: "#FEF8F3", // Primary background — warm cream
  bgAlt: "#F2F0E8", // Alternating section bg
  bgClinical: "#F9FAFB", // For science/clinical sections
  surfaceWarm: "#E8DDD3", // Peach accent surface
  brandTextOnDark: "#FEF8F3", // Cream-colored text on green sections

  // ─── Text ──────────────────────────────────────────────────────
  textPrimary: "#1E1E1E", // Near-black (gentler than #000)
  textSecondary: "#343434",
  textTertiary: "#808191", // Strike-through MRP, micro-copy
  white: "#FFFFFF",

  // ─── System (Mosaic-inherited) ─────────────────────────────────
  success: "#22A06B",
  successBg: "#E7F4EC",
  warning: "#FEF3C7",
  error: "#EF4444",
  errorBg: "#FEE2E2",
  border: "#E5E7EB",

  // ─── Transparent helpers ───────────────────────────────────────
  transparent: "transparent",
  overlay: "rgba(30, 30, 30, 0.5)",
} as const;

export const typography = {
  // Cormorant Garamond (heavy serif, editorial headlines + italic accents)
  // + Inter (humanist sans, all body/UI). Loaded via @expo-google-fonts
  // in app/_layout.tsx. Named-variant fonts: each family string maps to
  // one specific weight+style file — RN's fontWeight/fontStyle props are
  // ignored on these, so use the variant family directly.
  display: "Inter_400Regular",
  body: "Inter_400Regular",
  bodyMedium: "Inter_500Medium",
  bodySemi: "Inter_600SemiBold",
  bodyBold: "Inter_700Bold",
  serif: '"CormorantGaramond_700Bold", Georgia, "Times New Roman", serif',
  serifNative: "CormorantGaramond_700Bold", // headlines (alias of serifBold)
  serifBold: "CormorantGaramond_700Bold",
  serifSemi: "CormorantGaramond_600SemiBold", // card titles
  serifItalic: "CormorantGaramond_500Medium_Italic", // italic accent words

  sizes: {
    display0: 40, // Hero serif headline
    display1: 32,
    display2: 24,
    display3: 20,
    bodyLarge: 18,
    body: 16,
    bodySmall: 14,
    micro: 12,
    tiny: 11,
    kicker: 11, // Tiny ALL-CAPS section labels
  },

  weights: {
    regular: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
  },

  lineHeights: {
    tight: 1.2,
    normal: 1.4,
    relaxed: 1.6,
  },
} as const;

export const spacing = {
  // 4-point grid — matches Mosaic spacing in BB + MM extraction
  none: 0,
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
} as const;

export const radius = {
  none: 0,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  pill: 9999,
} as const;

export const elevation = {
  none: {
    shadowColor: "transparent",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0,
  },
  card: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  sticky: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  modal: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 24,
    elevation: 12,
  },
} as const;

export const layout = {
  screenPadding: spacing.md,
  cardGap: spacing.sm,
  sectionGap: spacing.xl,
  topBarHeight: 56,
  bottomTabHeight: 64,
  stickyCartHeight: 56,
  inputHeight: 48,
  buttonHeight: 48,
  buttonHeightSm: 36,
} as const;

export type Colors = typeof colors;
export type Typography = typeof typography;
export type Spacing = typeof spacing;
export type Radius = typeof radius;
