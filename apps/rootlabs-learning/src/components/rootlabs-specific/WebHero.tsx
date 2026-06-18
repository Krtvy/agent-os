import React, { useEffect } from "react";
import { Image, Pressable, StyleSheet, View, Dimensions } from "react-native";
import Animated, {
  Easing,
  FadeIn,
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withTiming,
} from "react-native-reanimated";
import { colors, radius, spacing, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";
import { getWebImage, type WebImageKey } from "@/data/web-images";
import { getProductImage } from "@/data/product-images";

/**
 * Editorial hero with strict separation:
 *   ┌──────────────────────┐
 *   │   PHOTO (full bleed) │
 *   ├──────────────────────┤
 *   │  kicker              │
 *   │  Big serif headline. │
 *   │  Subhead             │
 *   │  [ pill CTA ]        │
 *   └──────────────────────┘
 * No text overlay on the image. The text band sits beneath the image on a
 * cream surface — matches the rootlabs.co editorial pattern after the
 * cinematic photo.
 */

const SCREEN_W = Dimensions.get("window").width;

type ImageRef =
  | { kind: "web"; key: WebImageKey }
  | { kind: "product"; slug: string };

interface WebHeroProps {
  image: ImageRef;
  kicker?: string;
  /** Plain text. To italicize a word, pass it in `italicWord`. */
  headline: string;
  italicWord?: string;
  subhead?: string;
  ctaLabel?: string;
  onPressCta?: () => void;
  /** Photo region height in px. Text band sizes itself. */
  imageHeight?: number;
}

function resolve(image: ImageRef) {
  if (image.kind === "web") return getWebImage(image.key);
  return getProductImage(image.slug);
}

export function WebHero({
  image,
  kicker,
  headline,
  italicWord,
  subhead,
  ctaLabel,
  onPressCta,
  imageHeight = 360,
}: WebHeroProps) {
  const slideY = useSharedValue(20);
  const opacity = useSharedValue(0);

  useEffect(() => {
    slideY.value = withDelay(
      150,
      withTiming(0, {
        duration: 650,
        easing: Easing.out(Easing.cubic),
      }),
    );
    opacity.value = withDelay(150, withTiming(1, { duration: 650 }));
  }, []);

  const animStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: slideY.value }],
    opacity: opacity.value,
  }));

  const renderHeadline = () => {
    if (!italicWord || !headline.includes(italicWord)) {
      return <Text style={styles.headline}>{headline}</Text>;
    }
    const [pre, post] = headline.split(italicWord);
    return (
      <Text style={styles.headline}>
        {pre}
        <Text style={[styles.headline, styles.italic]}>{italicWord}</Text>
        {post}
      </Text>
    );
  };

  return (
    <View style={styles.wrap}>
      <Animated.View
        entering={FadeIn.duration(500)}
        style={[styles.photoBox, { height: imageHeight }]}
      >
        <Image
          source={resolve(image)}
          style={StyleSheet.absoluteFill}
          resizeMode="cover"
        />
      </Animated.View>

      <Animated.View style={[styles.textBand, animStyle]}>
        {kicker ? (
          <View style={{ marginBottom: spacing.sm }}>
            <SectionKicker label={kicker} tone="brand" />
          </View>
        ) : null}
        {renderHeadline()}
        {subhead ? <Text style={styles.subhead}>{subhead}</Text> : null}
        {ctaLabel && onPressCta ? (
          <Pressable onPress={onPressCta} style={styles.cta}>
            <Text style={styles.ctaLabel}>{ctaLabel}</Text>
            <Text style={styles.ctaLabel}> →</Text>
          </Pressable>
        ) : null}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    width: SCREEN_W,
    backgroundColor: colors.bg,
  },
  photoBox: {
    width: "100%",
    backgroundColor: colors.surfaceWarm,
    overflow: "hidden",
  },
  textBand: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.xl,
    alignItems: "flex-start",
  },
  headline: {
    fontFamily: typography.serifNative,
    fontSize: typography.sizes.display0,
    lineHeight: typography.sizes.display0 * typography.lineHeights.tight,
    color: colors.textPrimary,
    fontWeight: "700",
    letterSpacing: -0.5,
  },
  italic: {
    fontFamily: typography.serifItalic,
    color: colors.brand,
  },
  subhead: {
    marginTop: spacing.md,
    fontFamily: typography.body,
    fontSize: typography.sizes.body,
    color: colors.textSecondary,
    lineHeight: typography.sizes.body * typography.lineHeights.relaxed,
    maxWidth: 320,
  },
  cta: {
    marginTop: spacing.lg,
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.brand,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: radius.pill,
  },
  ctaLabel: {
    fontFamily: typography.body,
    fontSize: typography.sizes.bodySmall,
    fontWeight: "600",
    color: colors.brandTextOnDark,
    letterSpacing: 0.3,
  },
});
