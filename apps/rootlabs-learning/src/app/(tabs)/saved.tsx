/**
 * Saved — pixel-faithful port of design_handoff/source/screens/saved.jsx.
 *
 * Empty state: TopBar → "Your Library" / Saved for *later* / build a
 * shortlist body → 200×200 editorial sprout SVG → "Save what *speaks* to
 * you." headline + body + Browse-the-lineup CTA → Suggested-for-you
 * horizontal carousel of 140px cards.
 *
 * Filled state: TopBar → same title block (subtitle becomes "N products
 * saved") → 2-col grid of ProductCard with `saved` prop.
 */

import React from "react";
import { Image, Pressable, ScrollView, StyleSheet, View } from "react-native";
import Svg, { Path } from "react-native-svg";
import { useRouter } from "expo-router";
import { colors, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";
import { TopBar } from "@components/app-shell/TopBar";
import { ProductCard } from "@components/product/ProductCard";
import { services } from "@/services";
import { useUser } from "@hooks/useUser";
import { useCart } from "@hooks/useCart";
import { getProductImage } from "@/data/product-images";
import type { Product } from "@/types/domain";

const SUGGESTED_SLUGS = [
  "alpha-gummies-60s",
  "shilajit-gummies-60s",
  "sea-moss-gummies-60s",
];

export default function SavedScreen() {
  const router = useRouter();
  const { user, toggleSaved } = useUser();
  const { itemCount, addItem } = useCart();
  const [products, setProducts] = React.useState<Product[]>([]);
  const [suggested, setSuggested] = React.useState<Product[]>([]);

  React.useEffect(() => {
    services.analytics.screen("saved");
    let active = true;
    (async () => {
      const slugs = user?.savedProductSlugs ?? [];
      const fetched = await Promise.all(
        slugs.map((s) => services.products.getBySlug(s)),
      );
      if (!active) return;
      setProducts(fetched.filter((p): p is Product => !!p));

      const all = await services.products.list({});
      if (!active) return;
      setSuggested(
        SUGGESTED_SLUGS.map((s) => all.find((p) => p.slug === s)).filter(
          (p): p is Product => !!p,
        ),
      );
    })();
    return () => {
      active = false;
    };
  }, [user?.savedProductSlugs]);

  return (
    <View style={styles.wrap}>
      <TopBar cartCount={itemCount} />

      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.titleBlock}>
          <View style={{ marginBottom: 10 }}>
            <SectionKicker label="YOUR LIBRARY" tone="muted" />
          </View>
          <Text style={styles.title}>
            Saved for <Text style={styles.titleItalic}>later</Text>.
          </Text>
          <Text style={styles.titleSub}>
            {products.length > 0
              ? `${products.length} ${products.length === 1 ? "product" : "products"} saved`
              : "Build a shortlist as you browse."}
          </Text>
        </View>

        {products.length === 0 ? (
          <EmptyState
            suggested={suggested}
            onShop={() => router.push("/(tabs)/shop")}
          />
        ) : (
          <View style={styles.grid}>
            {products.map((p) => (
              <View key={p.slug} style={styles.gridSlot}>
                <ProductCard
                  product={p}
                  onAdd={addItem}
                  onHeart={(s) => toggleSaved(s)}
                  saved
                />
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
}

function EmptyState({
  suggested,
  onShop,
}: {
  suggested: Product[];
  onShop: () => void;
}) {
  return (
    <View style={styles.emptyWrap}>
      {/* Editorial sprout illustration */}
      <View style={styles.sprout}>
        <Svg width={200} height={200} viewBox="0 0 200 200" fill="none">
          {/* soil line */}
          <Path
            d="M14 154 Q70 148 100 152 Q130 156 186 150"
            stroke={colors.textTertiary}
            strokeWidth={0.8}
            strokeLinecap="round"
            opacity={0.5}
          />
          <Path
            d="M14 162 Q70 156 100 160 Q130 164 186 158"
            stroke={colors.textTertiary}
            strokeWidth={0.6}
            strokeLinecap="round"
            opacity={0.35}
          />
          {/* roots */}
          <Path
            d="M100 152 Q97 168 88 178"
            stroke={colors.brand}
            strokeWidth={1}
            strokeLinecap="round"
          />
          <Path
            d="M100 152 Q104 170 116 180"
            stroke={colors.brand}
            strokeWidth={1}
            strokeLinecap="round"
          />
          <Path
            d="M100 152 Q100 174 100 188"
            stroke={colors.brand}
            strokeWidth={1}
            strokeLinecap="round"
            opacity={0.7}
          />
          {/* stem */}
          <Path
            d="M100 152 Q100 110 100 64"
            stroke={colors.brand}
            strokeWidth={1.4}
            strokeLinecap="round"
          />
          {/* leaf left */}
          <Path
            d="M100 112 Q70 100 56 78 Q82 76 100 100 Z"
            stroke={colors.brand}
            strokeWidth={1.2}
            strokeLinejoin="round"
          />
          <Path
            d="M62 84 Q82 92 99 108"
            stroke={colors.brand}
            strokeWidth={0.6}
            opacity={0.5}
          />
          {/* leaf right */}
          <Path
            d="M100 92 Q132 80 146 58 Q120 56 100 80 Z"
            stroke={colors.brand}
            strokeWidth={1.2}
            strokeLinejoin="round"
          />
          <Path
            d="M140 64 Q120 74 101 90"
            stroke={colors.brand}
            strokeWidth={0.6}
            opacity={0.5}
          />
          {/* sprout top heart */}
          <Path
            d="M100 64 Q92 56 92 50 A4.5 4.5 0 0 1 100 47 A4.5 4.5 0 0 1 108 50 Q108 56 100 64 Z"
            fill={colors.accent}
            stroke={colors.accent}
            strokeWidth={1}
            strokeLinejoin="round"
          />
          {/* sparkles */}
          <Path
            d="M150 30 L150 38 M146 34 L154 34"
            stroke={colors.accent}
            strokeWidth={1.2}
            strokeLinecap="round"
          />
          <Path
            d="M44 110 L44 116 M41 113 L47 113"
            stroke={colors.accent}
            strokeWidth={1}
            strokeLinecap="round"
            opacity={0.8}
          />
        </Svg>
      </View>

      <Text style={styles.emptyHeadline}>
        Save what <Text style={styles.emptyItalic}>speaks</Text> to you.
      </Text>
      <Text style={styles.emptyBody}>
        Tap the heart on any product. Your shortlist lives here, lab reports and
        all.
      </Text>

      <Pressable onPress={onShop} style={styles.browseBtn}>
        <Text style={styles.browseLabel}>Browse the lineup</Text>
        <Svg width={14} height={14} viewBox="0 0 16 16" fill="none">
          <Path
            d="M3 8h10M9 4l4 4-4 4"
            stroke="#fff"
            strokeWidth={1.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </Svg>
      </Pressable>

      {/* Suggested for you */}
      <View style={styles.suggestedWrap}>
        <View style={styles.suggestedHead}>
          <View style={styles.hairline} />
          <SectionKicker label="SUGGESTED FOR YOU" tone="muted" />
          <View style={styles.hairline} />
        </View>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{ paddingHorizontal: 24, gap: 10 }}
        >
          {suggested.map((p) => {
            const img = getProductImage(p.slug);
            return (
              <View key={p.slug} style={styles.suggCard}>
                <View style={styles.suggThumb}>
                  {img ? (
                    <Image
                      source={img}
                      style={styles.suggImg}
                      resizeMode="contain"
                    />
                  ) : null}
                </View>
                <Text style={styles.suggName}>{p.name}</Text>
                <Text style={styles.suggPrice}>${Math.round(p.price)}</Text>
              </View>
            );
          })}
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },

  titleBlock: {
    paddingTop: 20,
    paddingHorizontal: 22,
    paddingBottom: 4,
  },
  title: {
    fontFamily: typography.serifNative,
    fontWeight: "700",
    fontSize: 32,
    lineHeight: 32 * 1.04,
    color: colors.textPrimary,
    letterSpacing: -0.5,
  },
  titleItalic: {
    fontFamily: typography.serifItalic,
  },
  titleSub: {
    marginTop: 10,
    fontFamily: typography.body,
    fontSize: 13.5,
    color: colors.textSecondary,
    lineHeight: 13.5 * 1.5,
  },

  emptyWrap: {
    paddingTop: 40,
    paddingHorizontal: 24,
    paddingBottom: 32,
    alignItems: "center",
  },
  sprout: { width: 200, height: 200, marginBottom: 28 },
  emptyHeadline: {
    fontFamily: typography.serifNative,
    fontWeight: "700",
    fontSize: 24,
    lineHeight: 24 * 1.04,
    color: colors.textPrimary,
    textAlign: "center",
    maxWidth: 280,
    marginBottom: 12,
    letterSpacing: -0.3,
  },
  emptyItalic: {
    fontFamily: typography.serifItalic,
  },
  emptyBody: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 14 * 1.5,
    color: colors.textSecondary,
    textAlign: "center",
    maxWidth: 260,
    marginBottom: 24,
  },
  browseBtn: {
    height: 44,
    paddingHorizontal: 22,
    borderRadius: 22,
    backgroundColor: colors.brand,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  browseLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 14,
    letterSpacing: 0.2,
    color: colors.white,
  },

  suggestedWrap: {
    width: "100%",
    marginTop: 44,
  },
  suggestedHead: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 14,
    paddingHorizontal: 24,
  },
  hairline: { flex: 1, height: 1, backgroundColor: "rgba(30,30,30,0.08)" },
  suggCard: {
    width: 140,
    backgroundColor: colors.bgAlt,
    borderRadius: 14,
    padding: 10,
  },
  suggThumb: {
    height: 100,
    backgroundColor: colors.surfaceWarm,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 8,
    overflow: "hidden",
  },
  suggImg: { width: "78%", height: "78%" },
  suggName: {
    fontFamily: typography.serifNative,
    fontWeight: "600",
    fontSize: 14.5,
    color: colors.textPrimary,
    lineHeight: 14.5 * 1.1,
  },
  suggPrice: {
    fontFamily: typography.body,
    fontSize: 11,
    color: colors.textTertiary,
    marginTop: 2,
  },

  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    paddingHorizontal: 16,
    paddingTop: 24,
    gap: 12,
  },
  gridSlot: {
    flexBasis: "47.5%",
    flexGrow: 1,
  },
});
