import React, { useEffect, useState } from "react";
import { View, ScrollView, StyleSheet, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { colors, spacing, radius, elevation } from "@/design-system/theme";
import { TopBar } from "@components/app-shell/TopBar";
import { Text } from "@components/primitives/Text";
import { Pill } from "@components/primitives/Pill";
import { useCart } from "@hooks/useCart";
import { services } from "@/services";
import type { Article } from "@/types/domain";

export default function ScienceScreen() {
  const router = useRouter();
  const { itemCount } = useCart();
  const [articles, setArticles] = useState<Article[]>([]);

  useEffect(() => {
    services.analytics.screen("science");
    import("@/data/articles.json").then((mod) =>
      setArticles(mod.default as Article[]),
    );
  }, []);

  return (
    <View style={styles.wrap}>
      <TopBar cartCount={itemCount} />

      <ScrollView
        contentContainerStyle={{
          padding: spacing.md,
          paddingBottom: spacing.xxl,
        }}
      >
        <Text
          variant="bodyLarge"
          tone="secondary"
          style={{ marginBottom: spacing.md }}
        >
          The library — research-grade explainers for everything in your stack.
        </Text>

        {articles.map((article) => (
          <Pressable
            key={article.slug}
            onPress={() => router.push(`/science/${article.slug}`)}
            style={styles.card}
          >
            <View style={styles.cardHead}>
              <Pill label={article.category} tone="cream" />
              <Text variant="micro" tone="tertiary">
                {article.readTimeMin} min read
              </Text>
            </View>
            <Text
              variant="display3"
              weight="bold"
              style={{ marginTop: spacing.sm }}
              numberOfLines={2}
            >
              {article.title}
            </Text>
            <Text
              variant="bodySmall"
              tone="secondary"
              style={{ marginTop: spacing.xs }}
              numberOfLines={3}
            >
              {article.summary}
            </Text>
          </Pressable>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  card: {
    backgroundColor: colors.white,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...elevation.card,
  },
  cardHead: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
});
