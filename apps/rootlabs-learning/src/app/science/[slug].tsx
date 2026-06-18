import React, { useEffect, useState } from "react";
import { View, ScrollView, StyleSheet, Pressable } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ArrowLeft } from "lucide-react-native";
import { colors, spacing, radius } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { Pill } from "@components/primitives/Pill";
import { Button } from "@components/primitives/Button";
import type { Article, Product } from "@/types/domain";
import { services } from "@/services";
import { useCart } from "@hooks/useCart";

export default function ArticleScreen() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { addItem } = useCart();
  const [article, setArticle] = useState<Article | null>(null);
  const [linkedProducts, setLinkedProducts] = useState<Product[]>([]);

  useEffect(() => {
    if (!slug) return;
    services.analytics.screen("article", { slug });
    (async () => {
      const articles = (await import("@/data/articles.json"))
        .default as Article[];
      const a = articles.find((x) => x.slug === slug) ?? null;
      setArticle(a);
      if (a?.linkedProducts?.length) {
        const products = await Promise.all(
          a.linkedProducts.map((s) => services.products.getBySlug(s)),
        );
        setLinkedProducts(products.filter((p): p is Product => p !== null));
      }
    })();
  }, [slug]);

  if (!article) {
    return (
      <View style={[styles.wrap, styles.centered]}>
        <Text tone="tertiary">Loading…</Text>
      </View>
    );
  }

  return (
    <View style={styles.wrap}>
      <View style={[styles.header, { paddingTop: insets.top }]}>
        <Pressable onPress={() => router.back()} hitSlop={8}>
          <ArrowLeft size={24} color={colors.textPrimary} />
        </Pressable>
        <Text variant="bodySmall" weight="semibold">
          Science
        </Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView
        contentContainerStyle={{
          padding: spacing.md,
          paddingBottom: spacing.xxl,
        }}
      >
        <Pill label={article.category} tone="cream" />
        <Text
          variant="display1"
          weight="bold"
          style={{ marginTop: spacing.md }}
        >
          {article.title}
        </Text>
        <Text
          variant="bodySmall"
          tone="tertiary"
          style={{ marginTop: spacing.xs }}
        >
          {article.readTimeMin} min read · From the Root Labs library
        </Text>

        <Text
          variant="bodyLarge"
          tone="secondary"
          style={{ marginTop: spacing.lg, lineHeight: 26 }}
        >
          {article.summary}
        </Text>

        <View style={styles.bodyBlock}>
          {article.body.split("\n\n").map((para, i) => (
            <Text
              key={i}
              variant="body"
              tone="secondary"
              style={{ marginBottom: spacing.md, lineHeight: 24 }}
            >
              {para}
            </Text>
          ))}
        </View>

        {linkedProducts.length > 0 ? (
          <View style={styles.linked}>
            <Text
              variant="display3"
              weight="bold"
              style={{ marginBottom: spacing.md }}
            >
              Related products
            </Text>
            {linkedProducts.map((p) => (
              <View key={p.slug} style={styles.linkedRow}>
                <View style={{ flex: 1 }}>
                  <Text variant="body" weight="semibold">
                    {p.name}
                  </Text>
                  <Text variant="bodySmall" tone="tertiary">
                    {p.pack} · ${p.price.toFixed(2)}
                  </Text>
                </View>
                <Button
                  label="View"
                  variant="outlined"
                  size="sm"
                  onPress={() => router.push(`/product/${p.slug}`)}
                />
              </View>
            ))}
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  centered: { alignItems: "center", justifyContent: "center" },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  bodyBlock: {
    marginTop: spacing.xl,
  },
  linked: {
    marginTop: spacing.xxl,
    paddingTop: spacing.lg,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  linkedRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.sm,
    gap: spacing.md,
  },
});
