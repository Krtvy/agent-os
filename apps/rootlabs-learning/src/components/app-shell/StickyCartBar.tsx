import React from "react";
import { View, StyleSheet, Pressable } from "react-native";
import { X } from "lucide-react-native";
import { useRouter } from "expo-router";
import { colors, spacing, radius, elevation } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { Button } from "@components/primitives/Button";

interface StickyCartBarProps {
  itemCount: number;
  onDismiss?: () => void;
}

export function StickyCartBar({ itemCount, onDismiss }: StickyCartBarProps) {
  const router = useRouter();
  if (itemCount === 0) return null;
  return (
    <View style={styles.wrap}>
      <View style={styles.left}>
        <Text variant="bodySmall" weight="semibold">
          You have items in cart
        </Text>
        <Text variant="micro" tone="tertiary">
          {itemCount} {itemCount === 1 ? "item" : "items"}
        </Text>
      </View>
      <View style={styles.right}>
        <Button
          label="View Cart"
          size="sm"
          onPress={() => router.push("/cart")}
        />
        {onDismiss ? (
          <Pressable onPress={onDismiss} hitSlop={8}>
            <X size={20} color={colors.textTertiary} />
          </Pressable>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.white,
    borderRadius: radius.md,
    marginHorizontal: spacing.md,
    marginBottom: spacing.sm,
    ...elevation.card,
  },
  left: {
    flex: 1,
  },
  right: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
});
