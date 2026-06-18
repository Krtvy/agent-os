import React, { useEffect } from "react";
import { View, StyleSheet, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { colors, spacing, typography } from "@/design-system/theme";
import { brand } from "@/design-system/brand";
import { Text } from "@components/primitives/Text";
import { useUser } from "@hooks/useUser";

/**
 * Entry point — decides whether to route to onboarding (first launch)
 * or directly to the (tabs) home (returning user).
 */
export default function Index() {
  const router = useRouter();
  const { user, loading } = useUser();

  useEffect(() => {
    if (loading) return;
    const t = setTimeout(() => {
      if (user?.goal) {
        router.replace("/(tabs)/for-you");
      } else {
        router.replace("/onboarding/goal-picker");
      }
    }, 600);
    return () => clearTimeout(t);
  }, [loading, user, router]);

  return (
    <View style={styles.wrap}>
      <Text style={styles.wordmark}>{brand.displayName}</Text>
      <Text
        variant="bodySmall"
        italic
        tone="brand"
        style={{ marginTop: spacing.sm }}
      >
        {brand.taglineShort}
      </Text>
      <ActivityIndicator
        style={{ marginTop: spacing.xl }}
        color={colors.brand}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flex: 1,
    backgroundColor: colors.bg,
    alignItems: "center",
    justifyContent: "center",
  },
  wordmark: {
    fontFamily: typography.display,
    fontSize: 36,
    fontWeight: typography.weights.bold,
    color: colors.brand,
    letterSpacing: -0.5,
  },
});
