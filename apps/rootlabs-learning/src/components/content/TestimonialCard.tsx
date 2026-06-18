import React from "react";
import { StyleSheet, View } from "react-native";
import { BadgeCheck } from "lucide-react-native";
import { colors, radius, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { StarRating } from "@components/primitives/StarRating";
import type { Review } from "@/types/domain";

/**
 * Testimonial card — pixel-faithful to Claude Design's TestimonialCarousel
 * item. Cream-alt card, 20 radius, 250px wide. Star row → serif italic
 * quote → initial avatar + name + verified.
 */

interface TestimonialCardProps {
  review: Review;
}

export function TestimonialCard({ review }: TestimonialCardProps) {
  const initial = review.authorName.charAt(0).toUpperCase();
  return (
    <View style={styles.card}>
      <StarRating rating={review.rating} size={13} showNumeric={false} />
      <Text style={styles.quote} numberOfLines={6}>
        &ldquo;{review.body}&rdquo;
      </Text>
      <View style={styles.byline}>
        <View style={styles.avatar}>
          <Text style={styles.avatarLetter}>{initial}</Text>
        </View>
        <Text style={styles.name}>{review.authorName}</Text>
        <View style={styles.verifiedRow}>
          <BadgeCheck size={11} color={colors.textTertiary} />
          <Text style={styles.verifiedLabel}>Verified</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.bgAlt,
    borderRadius: 20,
    width: 250,
    paddingTop: 20,
    paddingHorizontal: 18,
    paddingBottom: 18,
    flexDirection: "column",
    gap: 12,
  },
  quote: {
    fontFamily: typography.serifItalic,
    fontSize: 17.5,
    lineHeight: 17.5 * 1.3,
    color: colors.textPrimary,
  },
  byline: {
    marginTop: "auto",
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarLetter: {
    color: colors.white,
    fontFamily: typography.serifNative,
    fontWeight: "600",
    fontSize: 15,
  },
  name: {
    fontFamily: typography.body,
    fontSize: 12.5,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  verifiedRow: {
    marginLeft: "auto",
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  verifiedLabel: {
    fontFamily: typography.body,
    fontSize: 10.5,
    color: colors.textTertiary,
  },
});
