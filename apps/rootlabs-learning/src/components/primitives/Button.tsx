import React from "react";
import {
  Pressable,
  StyleSheet,
  View,
  ActivityIndicator,
  ViewStyle,
} from "react-native";
import { colors, radius, layout, typography } from "@/design-system/theme";
import { Text } from "./Text";

type Variant = "filled" | "outlined" | "link" | "destructive";
type Size = "md" | "sm";

interface ButtonProps {
  label: string;
  onPress?: () => void;
  variant?: Variant;
  size?: Size;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  subtext?: string;
  style?: ViewStyle;
}

export function Button({
  label,
  onPress,
  variant = "filled",
  size = "md",
  disabled,
  loading,
  fullWidth,
  subtext,
  style,
}: ButtonProps) {
  const height = size === "sm" ? layout.buttonHeightSm : layout.buttonHeight;
  const variantStyle = VARIANT_STYLES[variant];

  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.base,
        { height, opacity: disabled ? 0.5 : pressed ? 0.85 : 1 },
        variantStyle.container,
        fullWidth && styles.fullWidth,
        style,
      ]}
      accessibilityRole="button"
      accessibilityLabel={label}
    >
      {loading ? (
        <ActivityIndicator color={variantStyle.label} />
      ) : (
        <View style={styles.content}>
          <Text
            variant={size === "sm" ? "bodySmall" : "body"}
            weight="semibold"
            style={{ color: variantStyle.label }}
          >
            {label}
          </Text>
          {subtext ? (
            <Text
              variant="micro"
              style={{ color: variantStyle.label, opacity: 0.7 }}
            >
              {subtext}
            </Text>
          ) : null}
        </View>
      )}
    </Pressable>
  );
}

const VARIANT_STYLES = {
  filled: {
    container: { backgroundColor: colors.brand, borderWidth: 0 },
    label: colors.white,
  },
  outlined: {
    container: {
      backgroundColor: colors.transparent,
      borderWidth: 1,
      borderColor: colors.brand,
    },
    label: colors.brand,
  },
  link: {
    container: { backgroundColor: colors.transparent, borderWidth: 0 },
    label: colors.brand,
  },
  destructive: {
    container: { backgroundColor: colors.errorBg, borderWidth: 0 },
    label: colors.error,
  },
} as const;

const styles = StyleSheet.create({
  base: {
    borderRadius: radius.pill,
    paddingHorizontal: 24,
    alignItems: "center",
    justifyContent: "center",
  },
  content: {
    alignItems: "center",
  },
  fullWidth: {
    width: "100%",
  },
});
