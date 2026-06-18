import React, { useEffect } from "react";
import { View, StyleSheet, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ArrowLeft } from "lucide-react-native";
import { colors, spacing } from "@/design-system/theme";
import { PitchCard } from "@components/rootlabs-specific/PitchCard";
import { services } from "@/services";

export default function SearchScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  useEffect(() => {
    services.analytics.screen("search");
  }, []);

  return (
    <View style={styles.wrap}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.sm }]}>
        <Pressable onPress={() => router.back()} hitSlop={8}>
          <ArrowLeft size={24} color={colors.textPrimary} />
        </Pressable>
      </View>
      <PitchCard
        headlinePrefix="Search is"
        headlineItalic="coming soon"
        body={
          <>
            Full-text search across products, ingredients, and lab panels will
            run on the Shopify Storefront API. The rotating placeholders on the
            For You feed preview the query intents the live index will cover.
          </>
        }
        code={[
          {
            comment: "// today",
            line: "await services.products.search(query) // local filter",
          },
          {
            comment: "// flip to live",
            line: "await shopifyStorefront.search({ query, types: [PRODUCT] })",
          },
        ]}
        secondaryLabel="Back"
        onSecondary={() => router.back()}
        primaryLabel="Browse the lineup"
        onPrimary={() => router.replace("/(tabs)/for-you")}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.sm,
    backgroundColor: colors.bg,
  },
});
