/**
 * Onboarding — Goal picker (Step 2 of 3).
 * Pixel-faithful port of design_handoff/source/screens/onboarding.jsx.
 *
 *  Status spacer 54 → progress row (3 segments) + Skip → Wordmark centered
 *  → kicker "Step 2 · Your roots" → 32 serif headline with italic accent
 *  → body → 2×2 goal grid (creamAlt cards, 18 radius, glyph in 40px white
 *  rounded square, serif title 22, sub 12.5) → Continue pill (disabled
 *  until selection) → "Already have an account? Sign in" line.
 */

import React, { useState } from "react";
import { Pressable, ScrollView, StyleSheet, View } from "react-native";
import Svg, { Path } from "react-native-svg";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { colors, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";
import { Wordmark } from "@components/primitives/Wordmark";
import {
  BoltGlyph,
  HeartThinGlyph,
  LeafGlyph,
  ShieldGlyph,
} from "@components/primitives/Glyphs";
import { useUser } from "@hooks/useUser";

type GoalId = "energy" | "immunity" | "vitality" | "general";
const GOALS: {
  id: GoalId;
  label: string;
  desc: string;
  Glyph: typeof BoltGlyph;
}[] = [
  {
    id: "energy",
    label: "Energy",
    desc: "Stamina, focus, AM lift.",
    Glyph: BoltGlyph,
  },
  {
    id: "immunity",
    label: "Immunity",
    desc: "Year-round defense.",
    Glyph: ShieldGlyph,
  },
  {
    id: "vitality",
    label: "Vitality",
    desc: "Recovery, sleep, mood.",
    Glyph: HeartThinGlyph,
  },
  {
    id: "general",
    label: "General",
    desc: "A daily multi-adaptogen.",
    Glyph: LeafGlyph,
  },
];

export default function GoalPicker() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { updateGoal, signInAnonymous } = useUser();
  const [selected, setSelected] = useState<GoalId | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleContinue() {
    if (!selected || busy) return;
    setBusy(true);
    await signInAnonymous();
    await updateGoal(selected);
    router.replace("/(tabs)/for-you");
  }

  function handleSkip() {
    router.replace("/(tabs)/for-you");
  }

  return (
    <ScrollView
      style={styles.wrap}
      contentContainerStyle={{ flexGrow: 1, paddingTop: insets.top }}
    >
      {/* Progress row + Skip */}
      <View style={styles.progressRow}>
        <View style={styles.progressBar}>
          {[1, 2, 3].map((i) => (
            <View
              key={i}
              style={[
                styles.progressSeg,
                i <= 2 ? styles.progressFill : styles.progressEmpty,
              ]}
            />
          ))}
        </View>
        <Pressable onPress={handleSkip} hitSlop={8}>
          <Text style={styles.skipLabel}>Skip</Text>
        </Pressable>
      </View>

      {/* Wordmark centered */}
      <View style={styles.wordmarkWrap}>
        <Wordmark size={11} color={colors.brand} />
      </View>

      {/* Title block */}
      <View style={styles.title}>
        <View style={{ alignItems: "center", marginBottom: 14 }}>
          <SectionKicker label="STEP 2 · YOUR ROOTS" tone="muted" />
        </View>
        <Text style={styles.headline}>
          What brings you to{" "}
          <Text style={styles.headlineItalic}>Root Labs</Text>?
        </Text>
        <Text style={styles.body}>
          Pick one. We&rsquo;ll tune the lineup around it — you can change it
          later.
        </Text>
      </View>

      {/* Goal grid */}
      <View style={styles.grid}>
        {GOALS.map((g) => {
          const active = selected === g.id;
          const Glyph = g.Glyph;
          return (
            <Pressable
              key={g.id}
              onPress={() => setSelected(g.id)}
              style={[styles.card, active && styles.cardActive]}
            >
              {active ? (
                <View style={styles.checkBadge}>
                  <Svg width={12} height={12} viewBox="0 0 16 16" fill="none">
                    <Path
                      d="M3 8.5l3 3 7-8"
                      stroke="#fff"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </Svg>
                </View>
              ) : null}
              <View style={styles.glyphPlate}>
                <Glyph size={22} />
              </View>
              <Text style={styles.cardTitle}>{g.label}</Text>
              <Text style={styles.cardDesc}>{g.desc}</Text>
            </Pressable>
          );
        })}
      </View>

      <View style={{ flex: 1 }} />

      {/* Bottom CTA */}
      <View style={[styles.ctaWrap, { paddingBottom: 44 + insets.bottom }]}>
        <Pressable
          onPress={handleContinue}
          disabled={!selected || busy}
          style={[styles.continueBtn, !selected && styles.continueBtnDisabled]}
        >
          <Text style={styles.continueLabel}>Continue</Text>
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
        <Text style={styles.signIn}>
          Already have an account?{" "}
          <Text style={styles.signInLink}>Sign in</Text>
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  progressRow: {
    paddingHorizontal: 24,
    paddingTop: 14,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  progressBar: { flex: 1, flexDirection: "row", gap: 4 },
  progressSeg: { flex: 1, height: 3, borderRadius: 99 },
  progressFill: { backgroundColor: colors.brand },
  progressEmpty: { backgroundColor: "rgba(30,30,30,0.12)" },
  skipLabel: {
    fontFamily: typography.body,
    fontSize: 13,
    color: colors.textTertiary,
    fontWeight: "500",
  },
  wordmarkWrap: { paddingTop: 36, paddingBottom: 4, alignItems: "center" },
  title: {
    paddingHorizontal: 30,
    paddingTop: 20,
    paddingBottom: 8,
    alignItems: "center",
  },
  headline: {
    fontFamily: typography.serifNative,
    fontWeight: "700",
    fontSize: 32,
    lineHeight: 32 * 1.04,
    color: colors.textPrimary,
    textAlign: "center",
    letterSpacing: -0.5,
    marginBottom: 14,
  },
  headlineItalic: {
    fontFamily: typography.serifItalic,
  },
  body: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 14 * 1.5,
    color: colors.textSecondary,
    textAlign: "center",
    maxWidth: 280,
  },
  grid: {
    paddingTop: 32,
    paddingHorizontal: 20,
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  card: {
    flexBasis: "47%",
    flexGrow: 1,
    backgroundColor: colors.bgAlt,
    borderRadius: 18,
    paddingTop: 20,
    paddingHorizontal: 16,
    paddingBottom: 18,
    minHeight: 158,
    borderWidth: 2,
    borderColor: "transparent",
    position: "relative",
  },
  cardActive: {
    borderColor: colors.brand,
  },
  checkBadge: {
    position: "absolute",
    top: 12,
    right: 12,
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  glyphPlate: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: colors.white,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 14,
  },
  cardTitle: {
    fontFamily: typography.serifNative,
    fontWeight: "600",
    fontSize: 22,
    lineHeight: 22 * 1.05,
    color: colors.textPrimary,
  },
  cardDesc: {
    marginTop: 4,
    fontFamily: typography.body,
    fontSize: 12.5,
    color: colors.textTertiary,
  },
  ctaWrap: {
    paddingHorizontal: 16,
    paddingTop: 24,
  },
  continueBtn: {
    width: "100%",
    height: 52,
    borderRadius: 99,
    backgroundColor: colors.brand,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  continueBtnDisabled: { backgroundColor: "rgba(19,82,59,0.22)" },
  continueLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 15,
    letterSpacing: 0.3,
    color: colors.white,
  },
  signIn: {
    marginTop: 14,
    fontFamily: typography.body,
    fontSize: 12,
    color: colors.textTertiary,
    textAlign: "center",
  },
  signInLink: {
    color: colors.brand,
    fontWeight: "500",
  },
});
