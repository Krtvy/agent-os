import React from "react";
import { View, StyleSheet, ViewStyle } from "react-native";
import { colors, radius, spacing } from "@/design-system/theme";
import { Text } from "./Text";

type PillTone =
  | "brand"
  | "accent"
  | "success"
  | "warning"
  | "neutral"
  | "cream";

interface PillProps {
  label: string;
  tone?: PillTone;
  icon?: React.ReactNode;
  style?: ViewStyle;
}

const TONE_STYLES: Record<PillTone, { bg: string; fg: string }> = {
  brand: { bg: colors.brand, fg: colors.white },
  accent: { bg: colors.accent, fg: colors.white },
  success: { bg: colors.successBg, fg: colors.success },
  warning: { bg: colors.warning, fg: colors.textPrimary },
  neutral: { bg: colors.bgAlt, fg: colors.textSecondary },
  cream: { bg: colors.surfaceWarm, fg: colors.textPrimary },
};

export function Pill({ label, tone = "neutral", icon, style }: PillProps) {
  const tones = TONE_STYLES[tone];
  return (
    <View style={[styles.pill, { backgroundColor: tones.bg }, style]}>
      {icon}
      <Text variant="micro" weight="semibold" style={{ color: tones.fg }}>
        {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    alignSelf: "flex-start",
  },
});
