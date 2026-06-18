import React from "react";
import { View, StyleSheet, Pressable } from "react-native";
import { ChevronRight } from "lucide-react-native";
import { colors, spacing } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";

interface MenuRowProps {
  icon?: React.ReactNode;
  title: string;
  subtitle?: string;
  onPress?: () => void;
  showChevron?: boolean;
}

export function MenuRow({
  icon,
  title,
  subtitle,
  onPress,
  showChevron = true,
}: MenuRowProps) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.row, pressed && styles.pressed]}
    >
      {icon ? <View style={styles.icon}>{icon}</View> : null}
      <View style={{ flex: 1 }}>
        <Text variant="body" weight="medium">
          {title}
        </Text>
        {subtitle ? (
          <Text variant="bodySmall" tone="tertiary" style={{ marginTop: 2 }}>
            {subtitle}
          </Text>
        ) : null}
      </View>
      {showChevron ? (
        <ChevronRight size={20} color={colors.textTertiary} />
      ) : null}
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
  icon: {
    width: 32,
    alignItems: "center",
  },
});
