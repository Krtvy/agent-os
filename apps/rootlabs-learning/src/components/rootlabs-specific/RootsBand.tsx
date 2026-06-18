import React, { useEffect } from "react";
import {
  Dimensions,
  Pressable,
  ScrollView,
  StyleSheet,
  View,
} from "react-native";
import Animated, {
  Easing,
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withRepeat,
  withSequence,
  withTiming,
} from "react-native-reanimated";
import { colors, radius, spacing, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";

/**
 * Right from the Roots — pixel-faithful translation of Claude Design's
 * RightFromTheRoots component into React Native. Deep-green band, centered
 * serif headline + sub, horizontal-scroll pill switcher with yellow-orange
 * active state, focus card with serif-italic ingredient name + 2-line
 * description + pulsing accent dot.
 */

const SCREEN_W = Dimensions.get("window").width;

type Ingredient = {
  id: "shilajit" | "seamoss" | "turmeric" | "mushroom";
  name: string;
  italic: string;
  desc: string;
};

const INGREDIENTS: Ingredient[] = [
  {
    id: "shilajit",
    name: "Shilajit",
    italic: "Shilajit",
    desc: "Resin from the Himalayas, harvested at 14,000 ft. Used in Ayurveda for energy and endurance.",
  },
  {
    id: "seamoss",
    name: "Sea Moss",
    italic: "Sea Moss",
    desc: "Wild-harvested off the Irish coast. 92 of the 102 minerals your body needs.",
  },
  {
    id: "turmeric",
    name: "Turmeric",
    italic: "Turmeric",
    desc: "Curcumin-rich rhizomes from Tamil Nadu. Paired with black pepper for absorption.",
  },
  {
    id: "mushroom",
    name: "Mushroom",
    italic: "Mushroom",
    desc: "Reishi, lion’s mane, cordyceps. Functional fungi for clarity and immune balance.",
  },
];

interface RootsBandProps {
  onPressIngredient?: (id: Ingredient["id"]) => void;
}

export function RootsBand({ onPressIngredient }: RootsBandProps) {
  const [active, setActive] = React.useState<Ingredient["id"]>("shilajit");
  const cur: Ingredient =
    INGREDIENTS.find((i) => i.id === active) ?? INGREDIENTS[0]!;

  // Pulsing dot — opacity 0.25→1 + scale 0.7→1.6, 3.2s ease-in-out infinite
  const pulse = useSharedValue(0.25);
  useEffect(() => {
    pulse.value = withDelay(
      300,
      withRepeat(
        withSequence(
          withTiming(1, { duration: 1600, easing: Easing.inOut(Easing.sin) }),
          withTiming(0.25, {
            duration: 1600,
            easing: Easing.inOut(Easing.sin),
          }),
        ),
        -1,
        false,
      ),
    );
  }, []);
  const pulseStyle = useAnimatedStyle(() => ({
    opacity: pulse.value,
    transform: [{ scale: 0.7 + pulse.value * 0.9 }],
  }));

  return (
    <View style={styles.band}>
      <View style={styles.head}>
        <View style={{ marginBottom: 14 }}>
          <SectionKicker label="HANDPICKED IN NATURE" tone="onDark" />
        </View>
        <Text style={styles.headline}>
          Right from the <Text style={styles.headlineItalic}>Roots</Text>
        </Text>
        <Text style={styles.subhead}>
          Where the ingredient comes from is the ingredient. We don&apos;t
          substitute origin.
        </Text>
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.pillsRow}
      >
        {INGREDIENTS.map((i) => {
          const isActive = i.id === active;
          return (
            <Pressable
              key={i.id}
              onPress={() => {
                setActive(i.id);
                onPressIngredient?.(i.id);
              }}
              style={[styles.pill, isActive && styles.pillActive]}
            >
              <Text
                style={[styles.pillLabel, isActive && styles.pillLabelActive]}
              >
                {i.name}
              </Text>
            </Pressable>
          );
        })}
      </ScrollView>

      <View style={styles.focus}>
        <Animated.View style={[styles.dot, pulseStyle]} pointerEvents="none" />
        <View style={{ marginBottom: 12 }}>
          <SectionKicker
            label={`THE ROOTS · ${cur.name.toUpperCase()}`}
            tone="onDark"
          />
        </View>
        <Text style={styles.focusItalic}>{cur.italic}.</Text>
        <Text style={styles.focusDesc}>{cur.desc}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  band: {
    backgroundColor: colors.brandDark,
    paddingVertical: 56,
    width: SCREEN_W,
  },
  head: {
    paddingHorizontal: 24,
    alignItems: "center",
  },
  headline: {
    fontFamily: typography.serifNative,
    fontSize: 32,
    fontWeight: "700",
    color: colors.brandTextOnDark,
    textAlign: "center",
    letterSpacing: -0.5,
    lineHeight: 32 * 1.04,
    marginBottom: 12,
  },
  headlineItalic: {
    fontFamily: typography.serifItalic,
  },
  subhead: {
    fontFamily: typography.body,
    fontSize: 13.5,
    color: "rgba(254,248,243,0.78)",
    textAlign: "center",
    lineHeight: 13.5 * 1.55,
    maxWidth: 300,
  },
  pillsRow: {
    marginTop: 28,
    paddingHorizontal: 16,
    gap: 8,
  },
  pill: {
    height: 38,
    paddingHorizontal: 18,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.22)",
    alignItems: "center",
    justifyContent: "center",
  },
  pillActive: {
    backgroundColor: colors.accentBright,
    borderColor: colors.accentBright,
  },
  pillLabel: {
    color: "rgba(255,255,255,0.78)",
    fontFamily: typography.body,
    fontSize: 13,
    fontWeight: "600",
    letterSpacing: 0.3,
  },
  pillLabelActive: {
    color: colors.brandDark,
  },
  focus: {
    marginTop: 24,
    marginHorizontal: 24,
    backgroundColor: "rgba(255,255,255,0.04)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
    borderRadius: 18,
    paddingTop: 24,
    paddingHorizontal: 22,
    paddingBottom: 26,
    position: "relative",
  },
  dot: {
    position: "absolute",
    top: 16,
    right: 18,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.accentBright,
  },
  focusItalic: {
    fontFamily: typography.serifItalic,
    fontSize: 40,
    lineHeight: 40,
    color: colors.brandTextOnDark,
    marginBottom: 14,
  },
  focusDesc: {
    fontFamily: typography.body,
    fontSize: 13.5,
    color: "rgba(254,248,243,0.85)",
    lineHeight: 13.5 * 1.55,
  },
});
