import React from "react";
import { View, StyleSheet } from "react-native";
import { colors, spacing, radius, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { Button } from "@components/primitives/Button";

interface HeroBannerProps {
  headline: string;
  highlightWord?: string; // italicized accent within the headline
  subhead?: string;
  ctaLabel?: string;
  onPressCta?: () => void;
  tone?: "cream" | "warm" | "clinical";
}

export function HeroBanner({
  headline,
  highlightWord,
  subhead,
  ctaLabel,
  onPressCta,
  tone = "cream",
}: HeroBannerProps) {
  const bg =
    tone === "warm"
      ? colors.surfaceWarm
      : tone === "clinical"
        ? colors.bgClinical
        : colors.bgAlt;

  // Split headline around highlightWord for italic-script accent (matches Rootlabs voice)
  const parts =
    highlightWord && headline.includes(highlightWord)
      ? headline.split(highlightWord)
      : null;

  return (
    <View style={[styles.wrap, { backgroundColor: bg }]}>
      <View style={styles.content}>
        {parts ? (
          <Text
            variant="display1"
            weight="bold"
            style={{ fontFamily: typography.display }}
          >
            {parts[0]}
            <Text variant="display1" weight="bold" italic tone="brand">
              {highlightWord}
            </Text>
            {parts[1]}
          </Text>
        ) : (
          <Text
            variant="display1"
            weight="bold"
            style={{ fontFamily: typography.display }}
          >
            {headline}
          </Text>
        )}
        {subhead ? (
          <Text
            variant="body"
            tone="secondary"
            style={{ marginTop: spacing.sm }}
          >
            {subhead}
          </Text>
        ) : null}
        {ctaLabel ? (
          <View style={{ marginTop: spacing.md, alignSelf: "flex-start" }}>
            <Button label={ctaLabel} onPress={onPressCta} variant="filled" />
          </View>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    borderRadius: radius.lg,
    marginHorizontal: spacing.md,
    marginTop: spacing.md,
    overflow: "hidden",
  },
  content: {
    padding: spacing.lg,
  },
});
