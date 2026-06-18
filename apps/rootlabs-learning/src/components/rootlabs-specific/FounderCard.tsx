import React from "react";
import { Image, StyleSheet, View } from "react-native";
import { colors, radius, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";
import { getWebImage } from "@/data/web-images";

/**
 * The Roots — founder card. Pixel-faithful to Claude Design's FounderCard:
 *  - deep-green card, 24 radius, 36/28 padding
 *  - centered circular portrait, 120×120, 3px translucent border
 *  - serif italic quote
 *  - 24×1 hairline rule
 *  - sans semibold name + tracked sub
 */

export function FounderCard() {
  return (
    <View style={styles.card}>
      <View style={{ marginBottom: 14 }}>
        <SectionKicker label="THE ROOTS" tone="onDark" />
      </View>

      <View style={styles.portraitFrame}>
        <Image
          source={getWebImage("founder-mayank")}
          style={styles.portrait}
          resizeMode="cover"
        />
      </View>

      <Text style={styles.quote}>
        &ldquo;I started Root Labs because I was tired of buying supplements I
        had no way to verify. Anything we say on a label, we&apos;ll prove on a
        lab report. Every batch. Publicly.&rdquo;
      </Text>

      <View style={styles.rule} />

      <Text style={styles.name}>Mayank Kumar</Text>
      <Text style={styles.role}>Founder, Root Labs</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.brandDark,
    borderRadius: 24,
    marginHorizontal: 16,
    paddingTop: 36,
    paddingHorizontal: 28,
    paddingBottom: 32,
    alignItems: "center",
    overflow: "hidden",
  },
  portraitFrame: {
    width: 120,
    height: 120,
    borderRadius: 60,
    overflow: "hidden",
    marginBottom: 22,
    borderWidth: 3,
    borderColor: "rgba(255,255,255,0.16)",
  },
  portrait: { width: "100%", height: "100%" },
  quote: {
    fontFamily: typography.serifItalic,
    fontSize: 22,
    lineHeight: 22 * 1.3,
    color: colors.brandTextOnDark,
    textAlign: "center",
    marginBottom: 22,
  },
  rule: {
    width: 24,
    height: 1,
    backgroundColor: "rgba(255,255,255,0.30)",
    marginBottom: 14,
  },
  name: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 13,
    color: colors.brandTextOnDark,
    letterSpacing: 0.3,
  },
  role: {
    fontFamily: typography.body,
    fontSize: 11.5,
    color: "rgba(255,255,255,0.65)",
    marginTop: 4,
    letterSpacing: 0.3,
  },
});
