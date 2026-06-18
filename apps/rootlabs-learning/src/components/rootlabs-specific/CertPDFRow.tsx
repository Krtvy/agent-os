import React from "react";
import { View, StyleSheet, Pressable } from "react-native";
import { Shield, ChevronRight } from "lucide-react-native";
import { colors, spacing } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import type { CertPanel } from "@/types/domain";

interface CertPDFRowProps {
  panel: CertPanel;
  onPress?: () => void;
}

export function CertPDFRow({ panel, onPress }: CertPDFRowProps) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.row, pressed && styles.pressed]}
    >
      <Shield size={20} color={colors.brand} />
      <View style={{ flex: 1 }}>
        <Text variant="body" weight="semibold">
          {panel.name}
        </Text>
        <Text variant="micro" tone="tertiary" style={{ marginTop: 2 }}>
          {panel.verdict}
        </Text>
        {panel.summary ? (
          <Text variant="tiny" tone="tertiary" style={{ marginTop: 2 }}>
            {panel.summary}
          </Text>
        ) : null}
      </View>
      <ChevronRight size={18} color={colors.textTertiary} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    gap: spacing.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
    backgroundColor: colors.white,
  },
  pressed: {
    backgroundColor: colors.bgAlt,
  },
});
