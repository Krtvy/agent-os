import React from "react";
import { Image, Pressable, StyleSheet, View, Dimensions } from "react-native";
import { colors, radius, spacing, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";
import { getWebImage, type WebImageKey } from "@/data/web-images";

/**
 * A reusable image+serif-headline band — matches the rootlabs.co editorial
 * pattern where each big section has a kicker, serif headline, supporting
 * body, optional CTA, and a featured image.
 *
 * Layout: 1) kicker + headline + body stacked on left, image on right (when
 * the parent is wide enough) or 2) image on top, text below (always stacked
 * on phone).
 */

const SCREEN_W = Dimensions.get("window").width;

interface EditorialBandProps {
  imageKey: WebImageKey;
  kicker: string;
  headline: string;
  body?: string;
  ctaLabel?: string;
  onPressCta?: () => void;
  /** "cream" (default — cream bg) or "green" (dark immersive). */
  tone?: "cream" | "green";
  /** Image position relative to text. */
  imagePosition?: "top" | "bottom";
}

export function EditorialBand({
  imageKey,
  kicker,
  headline,
  body,
  ctaLabel,
  onPressCta,
  tone = "cream",
  imagePosition = "top",
}: EditorialBandProps) {
  const isDark = tone === "green";

  const Image_ = (
    <Image
      source={getWebImage(imageKey)}
      style={styles.image}
      resizeMode="cover"
    />
  );

  const Text_ = (
    <View style={styles.textWrap}>
      <SectionKicker label={kicker} tone={isDark ? "onDark" : "muted"} />
      <Text
        style={[
          styles.headline,
          { color: isDark ? colors.brandTextOnDark : colors.textPrimary },
        ]}
        accessibilityRole="header"
      >
        {headline}
      </Text>
      {body ? (
        <Text
          style={[
            styles.body,
            {
              color: isDark ? "rgba(254,248,243,0.85)" : colors.textSecondary,
            },
          ]}
        >
          {body}
        </Text>
      ) : null}
      {ctaLabel && onPressCta ? (
        <Pressable
          onPress={onPressCta}
          style={[styles.cta, isDark ? styles.ctaOnDark : styles.ctaOnCream]}
        >
          <Text
            style={[
              styles.ctaLabel,
              isDark ? styles.ctaLabelOnDark : styles.ctaLabelOnCream,
            ]}
          >
            {ctaLabel}
          </Text>
          <Text
            style={[
              styles.ctaLabel,
              isDark ? styles.ctaLabelOnDark : styles.ctaLabelOnCream,
              { marginLeft: 4 },
            ]}
          >
            →
          </Text>
        </Pressable>
      ) : null}
    </View>
  );

  return (
    <View
      style={[
        styles.band,
        { backgroundColor: isDark ? colors.brandDark : colors.bg },
      ]}
    >
      {imagePosition === "top" ? Image_ : null}
      {Text_}
      {imagePosition === "bottom" ? Image_ : null}
    </View>
  );
}

const styles = StyleSheet.create({
  band: {
    width: SCREEN_W,
    paddingBottom: spacing.xl,
  },
  image: {
    width: "100%",
    height: 240,
    marginBottom: spacing.lg,
  },
  textWrap: {
    paddingHorizontal: spacing.lg,
  },
  headline: {
    fontFamily: typography.serifNative,
    fontSize: typography.sizes.display1,
    fontWeight: "700",
    lineHeight: typography.sizes.display1 * typography.lineHeights.tight,
    marginTop: spacing.sm,
    letterSpacing: -0.3,
  },
  body: {
    marginTop: spacing.sm,
    fontFamily: typography.body,
    fontSize: typography.sizes.body,
    lineHeight: typography.sizes.body * typography.lineHeights.relaxed,
  },
  cta: {
    marginTop: spacing.md,
    alignSelf: "flex-start",
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    borderWidth: 1,
  },
  ctaOnCream: {
    borderColor: colors.brand,
    backgroundColor: "transparent",
  },
  ctaOnDark: {
    borderColor: colors.brandTextOnDark,
    backgroundColor: "transparent",
  },
  ctaLabel: {
    fontFamily: typography.body,
    fontSize: typography.sizes.bodySmall,
    fontWeight: "600",
    letterSpacing: 0.3,
  },
  ctaLabelOnCream: { color: colors.brand },
  ctaLabelOnDark: { color: colors.brandTextOnDark },
});
