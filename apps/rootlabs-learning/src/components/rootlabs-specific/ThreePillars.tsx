import React from "react";
import { View, StyleSheet } from "react-native";
import { colors, spacing, radius } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { brand } from "@/design-system/brand";

export function ThreePillars() {
  return (
    <View style={styles.wrap}>
      {brand.pillars.map((pillar) => (
        <View key={pillar.title} style={styles.pillar}>
          <Text variant="display3">{pillar.icon}</Text>
          <Text
            variant="bodySmall"
            weight="bold"
            center
            style={{ marginTop: spacing.xs }}
          >
            {pillar.title}
          </Text>
          <Text variant="micro" tone="tertiary" center style={{ marginTop: 2 }}>
            {pillar.body}
          </Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: "row",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.lg,
    backgroundColor: colors.bg,
    gap: spacing.sm,
  },
  pillar: {
    flex: 1,
    alignItems: "center",
    paddingHorizontal: spacing.xs,
  },
});
