/**
 * PitchCard — full-screen "Pitch Moment · Eng Demo" card used by the
 * Shop / Science / Search tabs. Visually mirrors the Cart pitch sheet
 * (sparkle icon → kicker → italic-accent serif headline → body → code
 * swap block → outline + solid CTAs) but renders inline, not as a modal.
 *
 * Communicates the same demo-vs-real story: "this tab will be wired
 * to <provider> via a single import swap in src/services/index.ts".
 */

import React from "react";
import { Pressable, ScrollView, StyleSheet, View } from "react-native";
import Svg, { Circle, Path } from "react-native-svg";
import { colors, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";

export type PitchCardProps = {
  /** Pre-headline copy (e.g. "Shop"). Rendered upright in serif. */
  headlinePrefix: string;
  /** Italic accent words (e.g. "coming soon"). Rendered serif italic. */
  headlineItalic: string;
  /** Optional trailing punctuation after the italic, default ".". */
  headlineTail?: string;
  /** Paragraph body explaining the demo state. */
  body: React.ReactNode;
  /** Optional code-block snippet showing the import swap. */
  code?: { comment: string; line: string }[];
  /** Primary action label (right-side filled pill). */
  primaryLabel?: string;
  /** Primary action handler. */
  onPrimary?: () => void;
  /** Secondary action label (left-side outline pill). */
  secondaryLabel?: string;
  /** Secondary action handler. */
  onSecondary?: () => void;
};

export function PitchCard({
  headlinePrefix,
  headlineItalic,
  headlineTail = ".",
  body,
  code,
  primaryLabel,
  onPrimary,
  secondaryLabel,
  onSecondary,
}: PitchCardProps) {
  return (
    <ScrollView
      contentContainerStyle={styles.scroll}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.card}>
        <SparkleIcon />
        <View style={{ marginBottom: 10 }}>
          <SectionKicker label="PITCH MOMENT · ENG DEMO" />
        </View>
        <Text style={styles.headline}>
          {headlinePrefix} <Text style={styles.italic}>{headlineItalic}</Text>
          {headlineTail}
        </Text>
        <Text style={styles.body}>{body}</Text>
        {code && code.length > 0 ? (
          <View style={styles.codeBlock}>
            {code.map((row, i) => (
              <View key={i} style={i > 0 ? { marginTop: 6 } : null}>
                <Text style={styles.codeComment}>{row.comment}</Text>
                <Text style={styles.codeLine}>{row.line}</Text>
              </View>
            ))}
          </View>
        ) : null}
        {primaryLabel || secondaryLabel ? (
          <View style={styles.buttons}>
            {secondaryLabel ? (
              <Pressable onPress={onSecondary} style={styles.outlineBtn}>
                <Text style={styles.outlineLabel}>{secondaryLabel}</Text>
              </Pressable>
            ) : null}
            {primaryLabel ? (
              <Pressable onPress={onPrimary} style={styles.solidBtn}>
                <Text style={styles.solidLabel}>{primaryLabel}</Text>
                <ArrowSvg />
              </Pressable>
            ) : null}
          </View>
        ) : null}
      </View>
    </ScrollView>
  );
}

function SparkleIcon() {
  return (
    <View style={styles.iconTile}>
      <Svg width={26} height={26} viewBox="0 0 24 24" fill="none">
        <Path
          d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"
          stroke={colors.accentBright}
          strokeWidth={1.6}
          strokeLinecap="round"
        />
        <Circle
          cx={12}
          cy={12}
          r={3.5}
          stroke={colors.accentBright}
          strokeWidth={1.6}
        />
      </Svg>
    </View>
  );
}

function ArrowSvg() {
  return (
    <Svg width={14} height={14} viewBox="0 0 16 16" fill="none">
      <Path
        d="M3 8h10M9 4l4 4-4 4"
        stroke="#fff"
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

const styles = StyleSheet.create({
  scroll: {
    flexGrow: 1,
    paddingHorizontal: 16,
    paddingTop: 24,
    paddingBottom: 48,
    justifyContent: "center",
  },
  card: {
    backgroundColor: colors.bg,
    borderRadius: 24,
    paddingHorizontal: 22,
    paddingTop: 24,
    paddingBottom: 26,
    borderWidth: 1,
    borderColor: "rgba(30,30,30,0.08)",
  },
  iconTile: {
    width: 56,
    height: 56,
    borderRadius: 16,
    backgroundColor: colors.brandDark,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 18,
  },
  headline: {
    fontFamily: typography.serifBold,
    fontSize: 26,
    lineHeight: 26 * 1.05,
    color: colors.textPrimary,
    marginBottom: 14,
    letterSpacing: -0.3,
  },
  italic: {
    fontFamily: typography.serifItalic,
  },
  body: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 14 * 1.5,
    color: colors.textSecondary,
    marginBottom: 18,
  },
  codeBlock: {
    backgroundColor: colors.bgAlt,
    borderRadius: 14,
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginBottom: 22,
  },
  codeLine: {
    fontFamily: typography.body,
    fontSize: 12,
    color: colors.textSecondary,
    lineHeight: 12 * 1.55,
  },
  codeComment: {
    fontFamily: typography.body,
    fontSize: 12,
    color: colors.textTertiary,
    lineHeight: 12 * 1.55,
  },
  buttons: { flexDirection: "row", gap: 10 },
  outlineBtn: {
    flex: 1,
    height: 46,
    borderRadius: 23,
    borderWidth: 1,
    borderColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "transparent",
  },
  outlineLabel: {
    fontFamily: typography.bodySemi,
    fontSize: 13.5,
    color: colors.brand,
  },
  solidBtn: {
    flex: 1.4,
    height: 46,
    borderRadius: 23,
    backgroundColor: colors.brand,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  solidLabel: {
    fontFamily: typography.bodySemi,
    fontSize: 13.5,
    color: colors.white,
  },
});
