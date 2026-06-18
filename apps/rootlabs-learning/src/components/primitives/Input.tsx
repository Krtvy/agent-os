import React from "react";
import { TextInput, TextInputProps, StyleSheet, View } from "react-native";
import {
  colors,
  radius,
  spacing,
  layout,
  typography,
} from "@/design-system/theme";
import { Text } from "./Text";

interface InputProps extends TextInputProps {
  label?: string;
  helper?: string;
  error?: string;
}

export function Input({ label, helper, error, style, ...rest }: InputProps) {
  return (
    <View style={styles.wrap}>
      {label ? (
        <Text
          variant="bodySmall"
          weight="semibold"
          style={{ marginBottom: spacing.xs }}
        >
          {label}
        </Text>
      ) : null}
      <TextInput
        {...rest}
        placeholderTextColor={colors.textTertiary}
        style={[styles.input, error ? styles.inputError : null, style]}
      />
      {error ? (
        <Text variant="micro" tone="error" style={{ marginTop: spacing.xs }}>
          {error}
        </Text>
      ) : helper ? (
        <Text variant="micro" tone="tertiary" style={{ marginTop: spacing.xs }}>
          {helper}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    width: "100%",
  },
  input: {
    height: layout.inputHeight,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    fontSize: typography.sizes.body,
    fontFamily: typography.body,
    color: colors.textPrimary,
    backgroundColor: colors.white,
  },
  inputError: {
    borderColor: colors.error,
  },
});
