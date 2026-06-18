import React, { useEffect, useState } from "react";
import { View, ScrollView, StyleSheet, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { colors, spacing } from "@/design-system/theme";
import { TopBar } from "@components/app-shell/TopBar";
import { SearchBar } from "@components/app-shell/SearchBar";
import { ProductCard } from "@components/product/ProductCard";
import { Pill } from "@components/primitives/Pill";
import { services } from "@/services";
import { useCart } from "@hooks/useCart";
import { WELLNESS_GOALS } from "@/types/domain";
import type { Product, WellnessGoal } from "@/types/domain";

export default function ShopScreen() {
  const router = useRouter();
  const { itemCount, addItem } = useCart();
  const [filter, setFilter] = useState<WellnessGoal | null>(null);
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    services.analytics.screen("shop", { filter });
    services.products
      .list(filter ? { goal: filter } : undefined)
      .then(setProducts);
  }, [filter]);

  return (
    <View style={styles.wrap}>
      <TopBar cartCount={itemCount} />
      <View style={{ paddingHorizontal: spacing.md, paddingTop: spacing.md }}>
        <SearchBar
          asLink
          onPressNonInteractive={() => router.push("/search")}
        />
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.filters}
      >
        <Pill
          label="All"
          tone={filter === null ? "brand" : "neutral"}
          style={{ paddingHorizontal: spacing.md, paddingVertical: spacing.sm }}
        />
        {WELLNESS_GOALS.map((g) => (
          <Pill
            key={g.id}
            label={`${g.icon} ${g.label}`}
            tone={filter === g.id ? "brand" : "neutral"}
            style={{
              paddingHorizontal: spacing.md,
              paddingVertical: spacing.sm,
            }}
          />
        ))}
      </ScrollView>

      <ScrollView contentContainerStyle={{ paddingBottom: spacing.xxl }}>
        <View style={styles.grid}>
          {products.map((p) => (
            <View key={p.slug} style={styles.slot}>
              <ProductCard product={p} onAdd={addItem} />
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  filters: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    gap: spacing.sm,
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    paddingHorizontal: spacing.md - spacing.sm / 2,
  },
  slot: {
    width: "50%",
    padding: spacing.sm / 2,
  },
});
