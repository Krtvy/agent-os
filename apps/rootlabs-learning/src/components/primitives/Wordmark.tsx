import React from "react";
import { StyleSheet, View } from "react-native";
import { Text } from "./Text";
import { colors, typography } from "@/design-system/theme";

/**
 * The Root Labs editorial wordmark: tracked-out sans caps split by a small
 * italic serif dot. Matches the rootlabs.co treatment.
 */

interface WordmarkProps {
  size?: number;
  color?: string;
}

export function Wordmark({
  size = 13,
  color = colors.textPrimary,
}: WordmarkProps) {
  return (
    <View style={styles.row}>
      <Text style={[styles.cap, { fontSize: size, color }]}>ROOT</Text>
      <Text
        style={[styles.dot, { fontSize: size + 4, color, marginHorizontal: 5 }]}
      >
        ·
      </Text>
      <Text style={[styles.cap, { fontSize: size, color }]}>LABS</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
  },
  cap: {
    fontFamily: typography.body,
    fontWeight: "700",
    letterSpacing: 3.4,
  },
  dot: {
    fontFamily: typography.serifItalic,
    marginTop: -2,
  },
});
