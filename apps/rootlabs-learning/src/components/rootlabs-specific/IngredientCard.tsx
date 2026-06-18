import React from "react";
import { View, StyleSheet, Pressable } from "react-native";
import { ChevronRight } from "lucide-react-native";
import { colors, spacing, radius, elevation } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import type { Ingredient } from "@/types/domain";

interface IngredientCardProps {
  ingredient: Ingredient;
  onPress?: () => void;
}

export function IngredientCard({ ingredient, onPress }: IngredientCardProps) {
  return (
    <Pressable onPress={onPress} style={styles.card}>
      <View style={{ flex: 1 }}>
        <Text variant="bodyLarge" weight="bold">
          🌿 {ingredient.name}
        </Text>
        <Text variant="bodySmall" italic tone="brand" style={{ marginTop: 2 }}>
          {ingredient.tagline}
        </Text>
        {ingredient.origin ? (
          <Text
            variant="micro"
            tone="tertiary"
            style={{ marginTop: spacing.xs }}
          >
            {ingredient.origin}
          </Text>
        ) : null}
        <Text
          variant="bodySmall"
          tone="secondary"
          style={{ marginTop: spacing.sm }}
          numberOfLines={3}
        >
          {ingredient.shortDescription}
        </Text>
        {onPress ? (
          <View style={styles.action}>
            <Text variant="bodySmall" weight="semibold" tone="brand">
              Read more
            </Text>
            <ChevronRight size={14} color={colors.brand} />
          </View>
        ) : null}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.white,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    ...elevation.card,
  },
  action: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: spacing.sm,
    gap: 2,
  },
});
