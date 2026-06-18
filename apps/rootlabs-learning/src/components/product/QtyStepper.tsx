import React from "react";
import { View, StyleSheet, Pressable } from "react-native";
import { Minus, Plus } from "lucide-react-native";
import { colors, spacing, radius } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";

interface QtyStepperProps {
  qty: number;
  onChange: (newQty: number) => void;
  min?: number;
  max?: number;
}

export function QtyStepper({
  qty,
  onChange,
  min = 0,
  max = 99,
}: QtyStepperProps) {
  return (
    <View style={styles.wrap}>
      <Pressable
        onPress={() => onChange(Math.max(min, qty - 1))}
        disabled={qty <= min}
        style={styles.btn}
        hitSlop={6}
      >
        <Minus
          size={14}
          color={qty <= min ? colors.textTertiary : colors.brand}
        />
      </Pressable>
      <Text variant="body" weight="semibold" style={styles.qty}>
        {qty}
      </Text>
      <Pressable
        onPress={() => onChange(Math.min(max, qty + 1))}
        disabled={qty >= max}
        style={styles.btn}
        hitSlop={6}
      >
        <Plus
          size={14}
          color={qty >= max ? colors.textTertiary : colors.brand}
        />
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    backgroundColor: colors.white,
  },
  btn: {
    width: 32,
    height: 32,
    alignItems: "center",
    justifyContent: "center",
  },
  qty: {
    minWidth: 24,
    textAlign: "center",
  },
});
