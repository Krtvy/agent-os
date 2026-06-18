import React from "react";
import { StyleSheet, View } from "react-native";
import { Text } from "./Text";
import { colors, spacing, typography } from "@/design-system/theme";

/**
 * Tiny ALL-CAPS section label, optionally with a hairline on either side.
 * Used above every section headline per the rootlabs.co convention
 * ("OUR SCIENCE", "OUR PRODUCTS", "PERFECTED IN SCIENCE", etc.).
 */

interface SectionKickerProps {
  label: string;
  /** "left" (default) puts a short hairline on the right; "center" rules on both sides. */
  align?: "left" | "center";
  /** Brand (cream-on-green sections) or muted (cream sections). */
  tone?: "brand" | "muted" | "onDark";
}

export function SectionKicker({
  label,
  align = "left",
  tone = "muted",
}: SectionKickerProps) {
  const color =
    tone === "brand"
      ? colors.brand
      : tone === "onDark"
        ? colors.brandTextOnDark
        : colors.textTertiary;

  if (align === "center") {
    return (
      <View style={styles.centerWrap}>
        <View style={[styles.rule, { backgroundColor: color, opacity: 0.5 }]} />
        <Text style={[styles.label, { color }]} accessibilityRole="header">
          {label}
        </Text>
        <View style={[styles.rule, { backgroundColor: color, opacity: 0.5 }]} />
      </View>
    );
  }
  return (
    <Text style={[styles.label, { color }]} accessibilityRole="header">
      {label}
    </Text>
  );
}

const styles = StyleSheet.create({
  label: {
    fontSize: typography.sizes.kicker,
    fontWeight: typography.weights.semibold,
    letterSpacing: 1.4,
    textTransform: "uppercase",
    fontFamily: typography.body,
  },
  centerWrap: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  rule: {
    flex: 1,
    height: StyleSheet.hairlineWidth,
  },
});
