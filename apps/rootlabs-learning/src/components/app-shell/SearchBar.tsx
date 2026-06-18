import React, { useEffect, useState } from "react";
import { View, StyleSheet, TextInput, Pressable } from "react-native";
import { Search } from "lucide-react-native";
import {
  colors,
  radius,
  spacing,
  layout,
  typography,
} from "@/design-system/theme";

const ROTATING_PLACEHOLDERS = [
  "Shilajit Gummies",
  "Ashwagandha",
  "Immunity Combo",
  "Sea Moss",
  "Energy support",
];

interface SearchBarProps {
  value?: string;
  onChangeText?: (v: string) => void;
  onPressNonInteractive?: () => void;
  /** If true, render as a tappable button that navigates to search rather than an active input */
  asLink?: boolean;
}

export function SearchBar({
  value,
  onChangeText,
  onPressNonInteractive,
  asLink,
}: SearchBarProps) {
  const [placeholderIdx, setPlaceholderIdx] = useState(0);

  useEffect(() => {
    if (!asLink) return;
    const interval = setInterval(() => {
      setPlaceholderIdx((i) => (i + 1) % ROTATING_PLACEHOLDERS.length);
    }, 2400);
    return () => clearInterval(interval);
  }, [asLink]);

  const placeholder = `Search for "${ROTATING_PLACEHOLDERS[placeholderIdx]}"`;

  if (asLink) {
    return (
      <Pressable onPress={onPressNonInteractive} style={styles.wrap}>
        <Search size={18} color={colors.textTertiary} />
        <View style={{ flex: 1 }}>
          <View style={styles.fakeInput}>
            <View>{/* placeholder shown via Text below */}</View>
          </View>
        </View>
      </Pressable>
    );
  }

  return (
    <View style={styles.wrap}>
      <Search size={18} color={colors.textTertiary} />
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.textTertiary}
        style={styles.input}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    height: layout.inputHeight,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
  },
  input: {
    flex: 1,
    fontSize: typography.sizes.body,
    fontFamily: typography.body,
    color: colors.textPrimary,
  },
  fakeInput: {
    height: layout.inputHeight,
    justifyContent: "center",
  },
});
