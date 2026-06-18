import React from "react";
import {
  Text as RNText,
  TextProps as RNTextProps,
  StyleSheet,
} from "react-native";
import { colors, typography } from "@/design-system/theme";

type Variant =
  | "display1"
  | "display2"
  | "display3"
  | "bodyLarge"
  | "body"
  | "bodySmall"
  | "micro"
  | "tiny";
type Weight = "regular" | "medium" | "semibold" | "bold";
type Tone =
  | "primary"
  | "secondary"
  | "tertiary"
  | "brand"
  | "accent"
  | "success"
  | "error"
  | "white";

interface TextProps extends RNTextProps {
  variant?: Variant;
  weight?: Weight;
  tone?: Tone;
  italic?: boolean;
  center?: boolean;
}

const toneToColor: Record<Tone, string> = {
  primary: colors.textPrimary,
  secondary: colors.textSecondary,
  tertiary: colors.textTertiary,
  brand: colors.brand,
  accent: colors.accent,
  success: colors.success,
  error: colors.error,
  white: colors.white,
};

export function Text({
  variant = "body",
  weight = "regular",
  tone = "primary",
  italic,
  center,
  style,
  children,
  ...rest
}: TextProps) {
  return (
    <RNText
      {...rest}
      style={[
        styles.base,
        {
          fontSize: typography.sizes[variant],
          fontWeight: typography.weights[
            weight
          ] as RNTextProps["style"] extends infer S ? any : never,
          color: toneToColor[tone],
          fontStyle: italic ? "italic" : "normal",
          textAlign: center ? "center" : undefined,
        },
        style,
      ]}
    >
      {children}
    </RNText>
  );
}

const styles = StyleSheet.create({
  base: {
    fontFamily: typography.body,
  },
});
