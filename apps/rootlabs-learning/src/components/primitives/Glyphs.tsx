import React from "react";
import Svg, { Circle, Path } from "react-native-svg";
import { colors } from "@/design-system/theme";

/**
 * SVG glyphs translated verbatim from Claude Design's shared.jsx + home.jsx.
 * Stroke widths, viewBox, and path data are unchanged so the rendered shape
 * matches the design exactly.
 */

interface GlyphProps {
  size?: number;
  color?: string;
  filled?: boolean;
}

// ─── Three-pillars glyphs (home.jsx) ──────────────────────────────────────

export function GlyphCraft({ size = 34, color = colors.brand }: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <Path
        d="M20 6c0 6-4 8-8 8 0 8 4 14 8 18 4-4 8-10 8-18-4 0-8-2-8-8z"
        stroke={color}
        strokeWidth={1.3}
        strokeLinejoin="round"
      />
      <Path
        d="M20 14v18M20 20l-3 3M20 24l3 3"
        stroke={color}
        strokeWidth={1.1}
        strokeLinecap="round"
      />
    </Svg>
  );
}

export function GlyphAbsorb({ size = 34, color = colors.brand }: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <Circle cx={20} cy={20} r={10} stroke={color} strokeWidth={1.3} />
      <Circle cx={20} cy={20} r={4.5} stroke={color} strokeWidth={1.1} />
      <Path
        d="M20 4v6M20 30v6M4 20h6M30 20h6M8 8l4 4M28 28l4 4M32 8l-4 4M12 28l-4 4"
        stroke={color}
        strokeWidth={1.1}
        strokeLinecap="round"
      />
    </Svg>
  );
}

export function GlyphScience({ size = 34, color = colors.brand }: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <Path
        d="M14 6h12M16 6v9L9 30a3 3 0 0 0 2.6 4.5h16.8A3 3 0 0 0 31 30L24 15V6"
        stroke={color}
        strokeWidth={1.3}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <Circle cx={17} cy={26} r={1.2} fill={color} />
      <Circle cx={22} cy={29} r={1} fill={color} />
    </Svg>
  );
}

// ─── Tab-bar glyphs (shared.jsx) ─────────────────────────────────────────

export function TabSparkle({
  size = 22,
  color = colors.textTertiary,
  filled = false,
}: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M12 3.5c.3 3.7 1.6 5 5.3 5.3-3.7.3-5 1.6-5.3 5.3-.3-3.7-1.6-5-5.3-5.3 3.7-.3 5-1.6 5.3-5.3z"
        fill={filled ? color : "none"}
        stroke={color}
        strokeWidth={1.4}
        strokeLinejoin="round"
      />
      <Path
        d="M18.5 14.5c.2 2 .9 2.7 2.8 2.9-1.9.2-2.6.9-2.8 2.9-.2-2-.9-2.7-2.8-2.9 1.9-.2 2.6-.9 2.8-2.9z"
        fill={filled ? color : "none"}
        stroke={color}
        strokeWidth={1.3}
        strokeLinejoin="round"
      />
    </Svg>
  );
}

export function TabBag({
  size = 22,
  color = colors.textTertiary,
  filled = false,
}: GlyphProps) {
  return (
    <Svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={filled ? color : "none"}
      stroke={color}
      strokeWidth={1.5}
    >
      <Path d="M5 8h14l-1 12H6L5 8z" strokeLinejoin="round" />
      <Path
        d="M9 8V6a3 3 0 0 1 6 0v2"
        fill="none"
        stroke={color}
        strokeWidth={1.5}
      />
    </Svg>
  );
}

export function TabFlask({
  size = 22,
  color = colors.textTertiary,
  filled = false,
}: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M10 3h4M11 3v6L6 19a2 2 0 0 0 1.7 3h8.6A2 2 0 0 0 18 19l-5-10V3"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        fill={filled ? color : "none"}
        fillOpacity={filled ? 0.18 : 1}
      />
      <Circle cx={10.5} cy={16} r={0.8} fill={color} />
      <Circle cx={13.5} cy={18} r={0.6} fill={color} />
    </Svg>
  );
}

export function TabHeart({
  size = 22,
  color = colors.textTertiary,
  filled = false,
}: GlyphProps) {
  return (
    <Svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={filled ? color : "none"}
      stroke={color}
      strokeWidth={1.6}
    >
      <Path
        d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.5a4.3 4.3 0 0 1 7.5 2.8C19.5 15.9 12 20.5 12 20.5z"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

// ─── Onboarding goal glyphs (onboarding.jsx) ─────────────────────────────

export function BoltGlyph({ size = 22, color = colors.brand }: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M13 3L5 13h6l-1 8 8-10h-6l1-8z"
        stroke={color}
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </Svg>
  );
}

export function ShieldGlyph({ size = 22, color = colors.brand }: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6l8-3z"
        stroke={color}
        strokeWidth={1.5}
        strokeLinejoin="round"
      />
      <Path
        d="M8.5 12l2.5 2.5L15.5 10"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

export function HeartThinGlyph({
  size = 22,
  color = colors.brand,
}: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M12 20s-7-4.4-7-9.6A4 4 0 0 1 12 7.5a4 4 0 0 1 7 2.9c0 5.2-7 9.6-7 9.6z"
        stroke={color}
        strokeWidth={1.5}
        strokeLinejoin="round"
      />
    </Svg>
  );
}

export function LeafGlyph({ size = 22, color = colors.brand }: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M20 4c0 9-5 14-14 14 0-9 5-14 14-14z"
        stroke={color}
        strokeWidth={1.5}
        strokeLinejoin="round"
      />
      <Path
        d="M6 18l8-8"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
      />
    </Svg>
  );
}

// ─── Verified mark (shared.jsx) ───────────────────────────────────────────

export function VerifiedBadge({ size = 14, color = colors.brand }: GlyphProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 16 16" fill="none">
      <Path
        d="M8 1l1.7 1.1 2 .1.7 1.9 1.5 1.4-.5 2 .5 2-1.5 1.4-.7 1.9-2 .1L8 14l-1.7-1.1-2-.1-.7-1.9L2.1 9.5l.5-2-.5-2 1.5-1.4.7-1.9 2-.1L8 1z"
        fill={color}
      />
      <Path
        d="M5.5 8l1.7 1.7L10.6 6.3"
        stroke="#fff"
        strokeWidth={1.6}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}
