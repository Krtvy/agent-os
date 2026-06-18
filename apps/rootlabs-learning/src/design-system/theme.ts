/**
 * Theme — composes tokens into a single object exported via `useTheme()`.
 * Future-proofs for dark mode: today only `light` is implemented; structure
 * supports adding `dark` without changing consumer components.
 */

import {
  colors,
  typography,
  spacing,
  radius,
  elevation,
  layout,
} from "./tokens";

export const lightTheme = {
  mode: "light" as const,
  colors,
  typography,
  spacing,
  radius,
  elevation,
  layout,
};

export type Theme = typeof lightTheme;

// Re-exports for convenience
export { colors, typography, spacing, radius, elevation, layout };
