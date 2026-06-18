import React from "react";
import { View, StyleSheet } from "react-native";
import { colors, spacing } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";

interface PriceRowProps {
  price: number;
  mrp?: number;
  currency?: "USD";
  size?: "sm" | "md" | "lg";
}

export function PriceRow({
  price,
  mrp,
  currency = "USD",
  size = "md",
}: PriceRowProps) {
  const sym = currency === "USD" ? "$" : "";
  const priceVariant =
    size === "lg" ? "display3" : size === "sm" ? "bodySmall" : "body";
  const mrpVariant = size === "lg" ? "body" : "micro";
  const pct =
    mrp && mrp > price ? Math.round(((mrp - price) / mrp) * 100) : null;

  return (
    <View style={styles.row}>
      <Text variant={priceVariant} weight="bold">
        {sym}
        {price.toFixed(2)}
      </Text>
      {mrp && mrp > price ? (
        <Text
          variant={mrpVariant}
          tone="tertiary"
          style={{ textDecorationLine: "line-through", marginLeft: spacing.xs }}
        >
          {sym}
          {mrp.toFixed(2)}
        </Text>
      ) : null}
      {pct ? (
        <View style={styles.pctPill}>
          <Text variant="tiny" weight="bold" style={{ color: colors.success }}>
            {pct}% off
          </Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "baseline",
    gap: spacing.xs,
  },
  pctPill: {
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    backgroundColor: colors.successBg,
    borderRadius: 4,
    marginLeft: spacing.xs,
  },
});
