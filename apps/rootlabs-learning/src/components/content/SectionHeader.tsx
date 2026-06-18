import React from "react";
import { Pressable, StyleSheet, View } from "react-native";
import { ChevronRight } from "lucide-react-native";
import { colors, spacing, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";

interface SectionHeaderProps {
  /** Tiny ALL-CAPS kicker above title — Rootlabs editorial convention. */
  kicker?: string;
  title: string;
  subtitle?: string;
  actionLabel?: string;
  onAction?: () => void;
  /** Cream sections vs. green immersive sections. */
  tone?: "muted" | "onDark";
  /** Center-align title (used for full-bleed editorial blocks). */
  align?: "left" | "center";
}

export function SectionHeader({
  kicker,
  title,
  subtitle,
  actionLabel,
  onAction,
  tone = "muted",
  align = "left",
}: SectionHeaderProps) {
  const isDark = tone === "onDark";
  return (
    <View
      style={[
        styles.wrap,
        { justifyContent: align === "center" ? "center" : "space-between" },
      ]}
    >
      <View
        style={{
          flex: align === "center" ? undefined : 1,
          alignItems: align === "center" ? "center" : "flex-start",
        }}
      >
        {kicker ? (
          <View style={{ marginBottom: spacing.xs }}>
            <SectionKicker label={kicker} tone={isDark ? "onDark" : "muted"} />
          </View>
        ) : null}
        <Text
          style={[
            styles.title,
            {
              color: isDark ? colors.brandTextOnDark : colors.textPrimary,
              textAlign: align === "center" ? "center" : "left",
            },
          ]}
          accessibilityRole="header"
        >
          {title}
        </Text>
        {subtitle ? (
          <Text
            variant="bodySmall"
            tone={isDark ? "white" : "tertiary"}
            style={{ marginTop: 2 }}
          >
            {subtitle}
          </Text>
        ) : null}
      </View>
      {actionLabel && align !== "center" ? (
        <Pressable onPress={onAction} style={styles.action} hitSlop={6}>
          <Text variant="bodySmall" weight="semibold" tone="brand">
            {actionLabel}
          </Text>
          <ChevronRight size={14} color={colors.brand} />
        </Pressable>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: "row",
    alignItems: "flex-end",
    paddingHorizontal: spacing.md,
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  title: {
    fontFamily: typography.serifNative,
    fontSize: typography.sizes.display2,
    fontWeight: "700",
    letterSpacing: -0.2,
    lineHeight: typography.sizes.display2 * typography.lineHeights.tight,
  },
  action: {
    flexDirection: "row",
    alignItems: "center",
    gap: 2,
  },
});
