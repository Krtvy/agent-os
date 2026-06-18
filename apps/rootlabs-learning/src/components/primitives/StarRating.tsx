import React from "react";
import { View, StyleSheet } from "react-native";
import { Star } from "lucide-react-native";
import { colors, spacing } from "@/design-system/theme";
import { Text } from "./Text";

interface StarRatingProps {
  rating: number; // 0..5
  count?: number;
  size?: number;
  showNumeric?: boolean;
}

export function StarRating({
  rating,
  count,
  size = 14,
  showNumeric = true,
}: StarRatingProps) {
  const filled = Math.round(rating);
  return (
    <View style={styles.row}>
      {Array.from({ length: 5 }).map((_, i) => (
        <Star
          key={i}
          size={size}
          color={i < filled ? colors.ratingStar : colors.border}
          fill={i < filled ? colors.ratingStar : "transparent"}
        />
      ))}
      {showNumeric ? (
        <Text
          variant="micro"
          tone="secondary"
          style={{ marginLeft: spacing.xs }}
        >
          {rating.toFixed(1)}
          {count !== undefined ? ` (${count})` : ""}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: 1,
  },
});
