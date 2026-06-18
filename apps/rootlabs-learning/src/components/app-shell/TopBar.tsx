import React from "react";
import { Pressable, StyleSheet, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ShoppingCart } from "lucide-react-native";
import { useRouter } from "expo-router";
import { colors, layout, spacing, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { Wordmark } from "@components/primitives/Wordmark";

interface TopBarProps {
  cartCount?: number;
  /** Cream sections (light) or deep-green sections (dark) */
  tone?: "light" | "dark";
}

export function TopBar({ cartCount = 0, tone = "light" }: TopBarProps) {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const isDark = tone === "dark";
  const bg = isDark ? colors.brandDark : colors.bg;
  const iconColor = isDark ? colors.brandTextOnDark : colors.textPrimary;

  return (
    <View
      style={[
        styles.bar,
        {
          backgroundColor: bg,
          paddingTop: insets.top,
          borderBottomColor: isDark
            ? "rgba(255,255,255,0.14)"
            : "rgba(30,30,30,0.08)",
        },
      ]}
    >
      <View style={styles.row}>
        <View style={styles.spacer} />
        <View style={styles.center}>
          <Wordmark color={iconColor} />
        </View>
        <Pressable
          onPress={() => router.push("/cart")}
          hitSlop={8}
          style={styles.right}
        >
          <View>
            <ShoppingCart size={22} color={iconColor} />
            {cartCount > 0 ? (
              <View style={styles.badge}>
                <Text style={styles.badgeLabel}>{cartCount}</Text>
              </View>
            ) : null}
          </View>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  row: {
    height: layout.topBarHeight - 8,
    paddingHorizontal: spacing.md,
    flexDirection: "row",
    alignItems: "center",
  },
  spacer: { width: 40 },
  center: { flex: 1, alignItems: "center" },
  right: { width: 40, alignItems: "flex-end" },
  badge: {
    position: "absolute",
    top: -3,
    right: -4,
    minWidth: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.accent,
    paddingHorizontal: 4,
    alignItems: "center",
    justifyContent: "center",
  },
  badgeLabel: {
    color: colors.white,
    fontFamily: typography.body,
    fontSize: 10,
    fontWeight: "700",
  },
});
