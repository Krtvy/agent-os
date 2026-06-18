import React from "react";
import { Image, Pressable, StyleSheet, View } from "react-native";
import { useRouter } from "expo-router";
import { Heart } from "lucide-react-native";
import { colors, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { getProductImage } from "@/data/product-images";
import type { Product } from "@/types/domain";

/**
 * Product card — pixel-faithful to Claude Design's ProductCard. Cream-alt
 * background, 18 radius. Peach image well (square aspect, 12 radius). Tone
 * kicker → serif name → pack size → price + ADD pill row. Optional badge.
 *
 * `chipLabel` (e.g. "−40%", "New", "Bestseller") shows in the top-left of
 * the image well. Negative-percent badges use the warm-orange accent.
 */

interface ProductCardProps {
  product: Product;
  onAdd?: (slug: string) => void;
  onHeart?: (slug: string) => void;
  saved?: boolean;
  chipLabel?: string;
  chipTone?: "cream" | "accent" | "brand";
}

function familyTone(product: Product): string {
  const fam = (product as any).family ?? "general";
  switch (fam) {
    case "alpha":
      return "VITALITY";
    case "ashwa":
      return "STRESS · SLEEP";
    case "immunity":
      return "IMMUNITY";
    case "shilajit":
      return "ENERGY · ENDURANCE";
    case "sea moss":
      return "THYROID · SKIN";
    case "turmeric":
      return "ANTI-INFLAMMATORY";
    default:
      return "WELLNESS";
  }
}

export function ProductCard({
  product,
  onAdd,
  onHeart,
  saved = false,
  chipLabel,
}: ProductCardProps) {
  const router = useRouter();
  const imgSource = getProductImage(product.slug);
  const tone = familyTone(product);

  // Derive a default chip when missing — show discount % if there's an MRP.
  const computedChip =
    chipLabel ??
    (() => {
      if (product.mrp && product.mrp > product.price) {
        const pct = Math.round((1 - product.price / product.mrp) * 100);
        return `−${pct}%`;
      }
      return undefined;
    })();
  const chipIsDiscount = computedChip?.startsWith("−");

  return (
    <Pressable
      onPress={() => router.push(`/product/${product.slug}`)}
      style={styles.card}
    >
      <View style={styles.imageWell}>
        {imgSource ? (
          <Image source={imgSource} style={styles.image} resizeMode="contain" />
        ) : (
          <View style={styles.image} />
        )}

        {computedChip ? (
          <View
            style={[
              styles.chip,
              {
                backgroundColor: chipIsDiscount ? colors.accent : colors.brand,
              },
            ]}
          >
            <Text style={styles.chipLabel}>{computedChip}</Text>
          </View>
        ) : null}

        <Pressable
          onPress={(e) => {
            e.stopPropagation?.();
            onHeart?.(product.slug);
          }}
          style={styles.heartButton}
          hitSlop={6}
        >
          <Heart
            size={16}
            color={saved ? colors.accent : colors.textPrimary}
            fill={saved ? colors.accent : "transparent"}
          />
        </Pressable>
      </View>

      <Text style={styles.tone}>{tone}</Text>
      <Text style={styles.name} numberOfLines={2}>
        {product.name}
      </Text>
      {product.pack ? <Text style={styles.pack}>{product.pack}</Text> : null}

      <View style={styles.bottomRow}>
        <View style={styles.priceRow}>
          <Text style={styles.price}>
            ${Math.round(product.price)}
            {product.price % 1
              ? (product.price - Math.floor(product.price)).toFixed(2).slice(1)
              : ""}
          </Text>
          {product.mrp ? <Text style={styles.mrp}>${product.mrp}</Text> : null}
        </View>
        <Pressable
          onPress={(e) => {
            e.stopPropagation?.();
            onAdd?.(product.slug);
          }}
          style={styles.addBtn}
        >
          <Text style={styles.addLabel}>ADD</Text>
        </Pressable>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    backgroundColor: colors.bgAlt,
    borderRadius: 18,
    padding: 12,
  },
  imageWell: {
    width: "100%",
    aspectRatio: 1,
    backgroundColor: colors.surfaceWarm,
    borderRadius: 12,
    marginBottom: 12,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
    position: "relative",
  },
  image: {
    width: "88%",
    height: "88%",
  },
  chip: {
    position: "absolute",
    top: 8,
    left: 8,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 99,
  },
  chipLabel: {
    color: colors.white,
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 10,
    letterSpacing: 0.6,
  },
  heartButton: {
    position: "absolute",
    top: 6,
    right: 6,
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: "rgba(254,248,243,0.85)",
    alignItems: "center",
    justifyContent: "center",
  },
  tone: {
    fontFamily: typography.body,
    fontSize: 10.5,
    fontWeight: "500",
    letterSpacing: 0.6,
    color: colors.textTertiary,
    marginBottom: 4,
  },
  name: {
    fontFamily: typography.serifNative,
    fontSize: 19,
    fontWeight: "600",
    color: colors.textPrimary,
    lineHeight: 19 * 1.1,
  },
  pack: {
    fontFamily: typography.body,
    fontSize: 11.5,
    color: colors.textTertiary,
    marginTop: 2,
  },
  bottomRow: {
    marginTop: 10,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 8,
  },
  priceRow: {
    flexDirection: "row",
    alignItems: "baseline",
    gap: 6,
  },
  price: {
    fontFamily: typography.body,
    fontWeight: "700",
    fontSize: 15,
    color: colors.textPrimary,
  },
  mrp: {
    fontFamily: typography.body,
    fontWeight: "500",
    fontSize: 11.5,
    color: colors.textTertiary,
    textDecorationLine: "line-through",
  },
  addBtn: {
    height: 30,
    paddingHorizontal: 14,
    borderRadius: 99,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  addLabel: {
    color: colors.white,
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 11.5,
    letterSpacing: 0.4,
  },
});
