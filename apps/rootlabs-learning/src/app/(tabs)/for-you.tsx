/**
 * For You / Home screen — pixel-faithful translation of the Claude Design
 * output at _private/rl_design/screens/home.jsx. Every section, every
 * spacing value, every kicker/headline pairing matches that source.
 *
 * Section order:
 *  1. TopBar (centered wordmark, cart count)
 *  2. Search field
 *  3. Cinematic hero — full-bleed 16:9 photo + serif headline below on cream
 *  4. OUR PRODUCTS · Expand Your Roots (2×2 grid)
 *  5. HANDPICKED IN NATURE · Right from the Roots (deep-green immersive band)
 *  6. Three pillars
 *  7. OUR STORY · Born of the desire to return to our roots
 *  8. PERFECTED IN SCIENCE · From Experts We Trust (doctor carousel)
 *  9. OUR CRAFT · Crafting organic gummies with rigorous testing
 * 10. INGREDIENTS · Find Your Ingredients (with origin chips)
 * 11. OUR CUSTOMERS · Our Customers Speak (testimonial carousel)
 * 12. OUR VOICE · Influencing Our Voice
 * 13. MADE FOR EVERY DAY · One a day. The rest takes care of itself.
 * 14. THE ROOTS founder card
 */

import React, { useEffect, useState } from "react";
import {
  FlatList,
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  View,
} from "react-native";
import Animated, {
  Easing,
  FadeInDown,
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withTiming,
} from "react-native-reanimated";
import { useRouter } from "expo-router";
import { Search } from "lucide-react-native";
import { colors, radius, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";
import { TopBar } from "@components/app-shell/TopBar";
import { ProductCard } from "@components/product/ProductCard";
import { TestimonialCard } from "@components/content/TestimonialCard";
import { DoctorEndorsementCard } from "@components/rootlabs-specific/DoctorEndorsementCard";
import { FounderCard } from "@components/rootlabs-specific/FounderCard";
import { RootsBand } from "@components/rootlabs-specific/RootsBand";
import { services } from "@/services";
import { useUser } from "@hooks/useUser";
import { useCart } from "@hooks/useCart";
import { getWebImage } from "@/data/web-images";
import {
  GlyphAbsorb,
  GlyphCraft,
  GlyphScience,
} from "@components/primitives/Glyphs";
import type { Doctor, Product, Review } from "@/types/domain";

const SEARCH_TERMS = [
  "Shilajit Gummies",
  "Ashwagandha",
  "Sea Moss",
  "Turmeric",
  "Lab reports",
];

const FEATURED_SLUGS = [
  "ashwa-mag",
  "shilajit-gummies-60s",
  "sea-moss-gummies-60s",
  "turmeric-gummies-60s",
];

export default function ForYouScreen() {
  const router = useRouter();
  const { user } = useUser();
  const { itemCount, addItem } = useCart();
  const [products, setProducts] = useState<Product[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [searchIdx, setSearchIdx] = useState(0);

  useEffect(() => {
    services.analytics.screen("for-you");
    let active = true;
    (async () => {
      const all = await services.products.list({});
      if (!active) return;
      const featured = FEATURED_SLUGS.map((s) =>
        all.find((p) => p.slug === s),
      ).filter((p): p is Product => !!p);
      setProducts(featured);

      const doctorsData = (await import("@/data/doctors.json"))
        .default as Doctor[];
      const reviewsData = (await import("@/data/reviews.json"))
        .default as Review[];
      if (active) {
        setDoctors(doctorsData);
        setReviews(reviewsData.slice(0, 4));
      }
    })();
    return () => {
      active = false;
    };
  }, [user?.goal]);

  // Rotating search placeholder
  useEffect(() => {
    const t = setInterval(
      () => setSearchIdx((i) => (i + 1) % SEARCH_TERMS.length),
      2600,
    );
    return () => clearInterval(t);
  }, []);

  return (
    <View style={styles.wrap}>
      <TopBar cartCount={itemCount} />
      <Animated.ScrollView
        contentContainerStyle={{ paddingBottom: 64 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Search field */}
        <View style={styles.searchWrap}>
          <Pressable
            style={styles.searchField}
            onPress={() => router.push("/search")}
          >
            <Search size={16} color={colors.textTertiary} />
            <Text style={styles.searchHint}>
              Search for &lsquo;
              <Text style={styles.searchTerm}>{SEARCH_TERMS[searchIdx]}</Text>
              &rsquo;
            </Text>
          </Pressable>
        </View>

        {/* 1. Cinematic hero */}
        <CinematicHero onShop={() => router.push("/(tabs)/shop")} />

        {/* 2. OUR PRODUCTS — Expand Your Roots */}
        <View style={styles.productSection}>
          <SectionHead
            kicker="OUR PRODUCTS"
            headline="Expand Your "
            italic="Roots"
            size={30}
            onViewAll={() => router.push("/(tabs)/shop")}
          />
          <View style={styles.productGrid}>
            {products.slice(0, 4).map((p, i) => (
              <Animated.View
                key={p.slug}
                entering={FadeInDown.delay(100 + i * 90).duration(520)}
                style={styles.gridSlot}
              >
                <ProductCard
                  product={p}
                  onAdd={(slug) => {
                    addItem(slug);
                  }}
                />
              </Animated.View>
            ))}
          </View>
        </View>

        {/* 3. HANDPICKED IN NATURE — Right from the Roots */}
        <RootsBand />

        {/* 4. Three pillars */}
        <ThreePillarsList />

        {/* 5. OUR STORY */}
        <OurStoryBand onRead={() => router.push("/account/honest-reports")} />

        {/* 6. PERFECTED IN SCIENCE — Doctors */}
        <View style={{ paddingBottom: 56 }}>
          <View style={styles.headPad}>
            <SectionHead
              kicker="PERFECTED IN SCIENCE"
              headline="From Experts We "
              italic="Trust"
              size={28}
            />
          </View>
          <FlatList
            horizontal
            data={doctors}
            keyExtractor={(d) => d.slug}
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{ paddingHorizontal: 16, gap: 12 }}
            renderItem={({ item }) => <DoctorEndorsementCard doctor={item} />}
          />
        </View>

        {/* 7. OUR CRAFT */}
        <OurCraftBand
          onReports={() => router.push("/account/honest-reports")}
        />

        {/* 8. INGREDIENTS — origin chips */}
        <IngredientsBand />

        {/* 9. OUR CUSTOMERS — Speak */}
        <View style={{ paddingBottom: 56 }}>
          <View style={styles.headPad}>
            <SectionHead
              kicker="OUR CUSTOMERS"
              headline="Our Customers "
              italic="Speak"
              size={28}
            />
          </View>
          <FlatList
            horizontal
            data={reviews}
            keyExtractor={(r) => r.id}
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{ paddingHorizontal: 16, gap: 12 }}
            renderItem={({ item }) => <TestimonialCard review={item} />}
          />
        </View>

        {/* 10. OUR VOICE */}
        <OurVoiceBand />

        {/* 11. MADE FOR EVERY DAY */}
        <EveryDayBand onShop={() => router.push("/(tabs)/shop")} />

        {/* 12. THE ROOTS founder card */}
        <View style={{ paddingHorizontal: 16, paddingBottom: 64 }}>
          <FounderCard />
        </View>
      </Animated.ScrollView>
    </View>
  );
}

// ─── Sub-components ──────────────────────────────────────────────────────

function SectionHead({
  kicker,
  headline,
  italic,
  size = 28,
  onViewAll,
}: {
  kicker: string;
  headline: string;
  italic?: string;
  size?: number;
  onViewAll?: () => void;
}) {
  return (
    <View style={styles.sectionHead}>
      <View style={{ flex: 1 }}>
        <View style={{ marginBottom: 10 }}>
          <SectionKicker label={kicker} />
        </View>
        <Text
          style={[
            styles.headline,
            {
              fontSize: size,
              lineHeight: size * 1.04,
            },
          ]}
        >
          {headline}
          {italic ? <Text style={styles.headlineItalic}>{italic}</Text> : null}
          {italic ? "." : ""}
        </Text>
      </View>
      {onViewAll ? (
        <Pressable onPress={onViewAll} style={styles.viewAll}>
          <Text style={styles.viewAllLabel}>View all →</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

function CinematicHero({ onShop }: { onShop: () => void }) {
  const opacity = useSharedValue(0);
  const translateY = useSharedValue(8);
  useEffect(() => {
    opacity.value = withDelay(150, withTiming(1, { duration: 500 }));
    translateY.value = withDelay(
      150,
      withTiming(0, {
        duration: 500,
        easing: Easing.bezier(0.2, 0.7, 0.3, 1),
      }),
    );
  }, []);
  const animStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateY: translateY.value }],
  }));

  return (
    <View style={styles.heroSection}>
      <View style={styles.heroPhoto}>
        <Image
          source={getWebImage("hero-lifestyle")}
          style={StyleSheet.absoluteFill}
          resizeMode="cover"
        />
        <View style={styles.heroVignette} />
      </View>
      <Animated.View style={[styles.heroText, animStyle]}>
        <View style={{ marginBottom: 12 }}>
          <SectionKicker label="HANDPICKED IN NATURE" />
        </View>
        <Text style={styles.heroHeadline}>
          Handpicked in nature.{"\n"}Perfected in{" "}
          <Text style={styles.headlineItalic}>science</Text>.
        </Text>
        <Text style={styles.heroBody}>
          Single-ingredient adaptogens, third-party lab reports for every batch.
        </Text>
        <Pressable style={styles.heroCta} onPress={onShop}>
          <Text style={styles.heroCtaLabel}>Shop Your Product</Text>
          <Text style={styles.heroCtaLabel}> →</Text>
        </Pressable>
      </Animated.View>
    </View>
  );
}

function ThreePillarsList() {
  const pillars = [
    {
      kicker: "PILLAR 01",
      title: "Carefully crafted",
      desc: "Single-ingredient gummies. No fillers, no compromises.",
      Glyph: GlyphCraft,
    },
    {
      kicker: "PILLAR 02",
      title: "Maximum absorption",
      desc: "Bioavailable forms. Pairings that your body actually uses.",
      Glyph: GlyphAbsorb,
    },
    {
      kicker: "PILLAR 03",
      title: "Science-backed",
      desc: "Third-party batch testing. Reports published publicly.",
      Glyph: GlyphScience,
    },
  ];
  return (
    <View style={{ paddingHorizontal: 16, paddingBottom: 56 }}>
      <View style={{ gap: 12 }}>
        {pillars.map((p) => {
          const Glyph = p.Glyph;
          return (
            <View key={p.kicker} style={styles.pillarRow}>
              <View style={styles.pillarGlyph}>
                <Glyph size={34} />
              </View>
              <View style={{ flex: 1, minWidth: 0 }}>
                <SectionKicker label={p.kicker} />
                <Text style={styles.pillarTitle}>{p.title}</Text>
                <Text style={styles.pillarDesc}>{p.desc}</Text>
              </View>
            </View>
          );
        })}
      </View>
    </View>
  );
}

function OurStoryBand({ onRead }: { onRead: () => void }) {
  return (
    <View style={{ paddingBottom: 56 }}>
      <View style={{ paddingHorizontal: 16 }}>
        <Image
          source={getWebImage("story-family")}
          style={styles.editorialImage}
          resizeMode="cover"
        />
      </View>
      <View style={styles.editorialText}>
        <View style={{ marginBottom: 12 }}>
          <SectionKicker label="OUR STORY" />
        </View>
        <Text
          style={[styles.headline, { fontSize: 30, lineHeight: 30 * 1.04 }]}
        >
          Born of the desire to return{"\n"}to our{" "}
          <Text style={styles.headlineItalic}>roots</Text>.
        </Text>
        <View style={{ marginTop: 18, gap: 10 }}>
          {[
            "Founded after our CEO couldn’t verify a single supplement claim on his shelf.",
            "Recipes drawn from Ayurveda, validated by US-credentialed scientists.",
            "A public lab report for every batch — searchable by the code on the bottle.",
          ].map((line, i) => (
            <View key={i} style={styles.bulletRow}>
              <View style={styles.bullet} />
              <Text style={styles.bulletText}>{line}</Text>
            </View>
          ))}
        </View>
        <Pressable style={styles.outlineCta} onPress={onRead}>
          <Text style={styles.outlineCtaLabel}>Read our story →</Text>
        </Pressable>
      </View>
    </View>
  );
}

function OurCraftBand({ onReports }: { onReports: () => void }) {
  return (
    <View style={{ paddingBottom: 56 }}>
      <View style={{ paddingHorizontal: 16 }}>
        <Image
          source={getWebImage("our-craft-lab")}
          style={styles.editorialImage}
          resizeMode="cover"
        />
      </View>
      <View style={styles.editorialText}>
        <View style={{ marginBottom: 12 }}>
          <SectionKicker label="OUR CRAFT" />
        </View>
        <Text
          style={[styles.headline, { fontSize: 28, lineHeight: 28 * 1.04 }]}
        >
          Crafting organic gummies{"\n"}with rigorous{" "}
          <Text style={styles.headlineItalic}>testing</Text>.
        </Text>
        <Text style={styles.editorialBody}>
          Every batch goes through Equinox Labs — third-party, ISO-accredited.
          We publish the full report for each lot. If a bottle passes,
          you&apos;ll find the assay attached to the lot code on the label.
        </Text>
        <Pressable style={styles.outlineCta} onPress={onReports}>
          <Text style={styles.outlineCtaLabel}>See our reports →</Text>
        </Pressable>
      </View>
    </View>
  );
}

function IngredientsBand() {
  const origins: { o: string; i: string }[] = [
    { o: "HIMALAYAS", i: "Shilajit" },
    { o: "IRISH COAST", i: "Sea Moss" },
    { o: "TAMIL NADU", i: "Turmeric" },
  ];
  return (
    <View style={{ paddingBottom: 56 }}>
      <View style={{ paddingHorizontal: 16 }}>
        <Image
          source={getWebImage("sourcing-women")}
          style={styles.editorialImage}
          resizeMode="cover"
        />
      </View>
      <View style={styles.editorialText}>
        <View style={{ marginBottom: 12 }}>
          <SectionKicker label="INGREDIENTS" />
        </View>
        <Text
          style={[styles.headline, { fontSize: 28, lineHeight: 28 * 1.04 }]}
        >
          Find Your <Text style={styles.headlineItalic}>Ingredients</Text>.
        </Text>
        <Text style={styles.editorialBody}>
          Shilajit from the Himalayas. Sea moss from Irish coasts. Turmeric from
          Tamil Nadu. We don&apos;t substitute origin.
        </Text>
        <View style={styles.originRow}>
          {origins.map((t) => (
            <View key={t.i} style={styles.originCell}>
              <Text style={styles.originKicker}>{t.o}</Text>
              <Text style={styles.originName}>{t.i}</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  );
}

function OurVoiceBand() {
  return (
    <View style={{ paddingBottom: 56 }}>
      <View style={{ paddingHorizontal: 16 }}>
        <Image
          source={getWebImage("voice-turmeric")}
          style={styles.editorialImage}
          resizeMode="cover"
        />
      </View>
      <View style={styles.editorialText}>
        <View style={{ marginBottom: 12 }}>
          <SectionKicker label="OUR VOICE" />
        </View>
        <Text
          style={[styles.headline, { fontSize: 28, lineHeight: 28 * 1.04 }]}
        >
          Influencing Our <Text style={styles.headlineItalic}>Voice</Text>.
        </Text>
        <Text style={styles.voiceAccent}>
          Harnessing the Power of Ancient Remedies.
        </Text>
        <Text style={styles.editorialBody}>
          Curated reading from naturopaths, dietitians and integrative MDs we
          actually quote on the box. Long-form, no clickbait.
        </Text>
      </View>
    </View>
  );
}

function EveryDayBand({ onShop }: { onShop: () => void }) {
  return (
    <View style={{ paddingBottom: 56 }}>
      <View style={{ paddingHorizontal: 16 }}>
        <Image
          source={getWebImage("gummies-in-hands")}
          style={styles.editorialImage}
          resizeMode="cover"
        />
      </View>
      <View style={styles.editorialText}>
        <View style={{ marginBottom: 12 }}>
          <SectionKicker label="MADE FOR EVERY DAY" />
        </View>
        <Text
          style={[styles.headline, { fontSize: 28, lineHeight: 28 * 1.04 }]}
        >
          One a day. The rest takes care{"\n"}of{" "}
          <Text style={styles.headlineItalic}>itself</Text>.
        </Text>
        <Text style={styles.editorialBody}>
          No timing. No tinctures. No 30-minute morning stack. Two gummies,
          chewed with breakfast.
        </Text>
        <Pressable style={styles.solidCta} onPress={onShop}>
          <Text style={styles.solidCtaLabel}>Shop the lineup</Text>
          <Text style={styles.solidCtaLabel}> →</Text>
        </Pressable>
      </View>
    </View>
  );
}

// ─── Styles ──────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  wrap: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  searchWrap: { paddingHorizontal: 16, paddingTop: 12 },
  searchField: {
    height: 46,
    borderRadius: 99,
    backgroundColor: colors.bgAlt,
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    gap: 10,
  },
  searchHint: {
    fontFamily: typography.body,
    fontSize: 14,
    color: colors.textTertiary,
  },
  searchTerm: {
    fontFamily: typography.serifItalic,
    fontSize: 16,
    color: colors.textSecondary,
  },

  // hero
  heroSection: { marginTop: 16, marginBottom: 40 },
  heroPhoto: {
    width: "100%",
    aspectRatio: 16 / 9,
    backgroundColor: colors.surfaceWarm,
    overflow: "hidden",
  },
  heroVignette: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0)",
  },
  heroText: {
    paddingHorizontal: 24,
    paddingTop: 28,
  },
  heroHeadline: {
    fontFamily: typography.serifNative,
    fontWeight: "700",
    fontSize: 36,
    lineHeight: 36 * 1.04,
    color: colors.textPrimary,
    letterSpacing: -0.5,
    marginBottom: 14,
  },
  heroBody: {
    fontFamily: typography.body,
    fontSize: 14.5,
    color: colors.textSecondary,
    lineHeight: 14.5 * 1.5,
    marginBottom: 20,
  },
  heroCta: {
    height: 44,
    paddingHorizontal: 22,
    borderRadius: 99,
    backgroundColor: colors.brand,
    alignSelf: "flex-start",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  heroCtaLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 14,
    color: colors.white,
    letterSpacing: 0.2,
  },

  // products
  productSection: { paddingHorizontal: 16, paddingBottom: 56 },
  productGrid: {
    marginTop: 22,
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  gridSlot: {
    flexBasis: "47.5%",
    flexGrow: 1,
  },

  // section head
  sectionHead: {
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "space-between",
    gap: 12,
  },
  headline: {
    fontFamily: typography.serifNative,
    fontWeight: "700",
    color: colors.textPrimary,
    letterSpacing: -0.5,
  },
  headlineItalic: {
    fontFamily: typography.serifItalic,
  },
  viewAll: { paddingBottom: 4 },
  viewAllLabel: {
    fontFamily: typography.body,
    fontSize: 12.5,
    fontWeight: "500",
    color: colors.textSecondary,
  },
  headPad: { paddingHorizontal: 16, paddingBottom: 22 },

  // pillars
  pillarRow: {
    flexDirection: "row",
    gap: 16,
    alignItems: "center",
    backgroundColor: colors.bgAlt,
    borderRadius: 18,
    padding: 20,
  },
  pillarGlyph: {
    width: 56,
    height: 56,
    borderRadius: 14,
    backgroundColor: colors.bg,
    alignItems: "center",
    justifyContent: "center",
  },
  pillarDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.brand,
  },
  pillarTitle: {
    fontFamily: typography.serifNative,
    fontSize: 22,
    fontWeight: "600",
    color: colors.textPrimary,
    lineHeight: 22 * 1.1,
    marginTop: 4,
    marginBottom: 4,
  },
  pillarDesc: {
    fontFamily: typography.body,
    fontSize: 13,
    color: colors.textSecondary,
    lineHeight: 13 * 1.5,
  },

  // editorial bands
  editorialImage: {
    width: "100%",
    aspectRatio: 4 / 3,
    borderRadius: 18,
    backgroundColor: colors.surfaceWarm,
  },
  editorialText: {
    paddingHorizontal: 24,
    paddingTop: 24,
  },
  editorialBody: {
    marginTop: 14,
    fontFamily: typography.body,
    fontSize: 14.5,
    color: colors.textSecondary,
    lineHeight: 14.5 * 1.5,
  },
  bulletRow: {
    flexDirection: "row",
    gap: 12,
    alignItems: "flex-start",
  },
  bullet: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.brand,
    marginTop: 9,
  },
  bulletText: {
    flex: 1,
    fontFamily: typography.body,
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 14 * 1.5,
  },

  // CTAs
  outlineCta: {
    marginTop: 22,
    alignSelf: "flex-start",
    height: 44,
    paddingHorizontal: 22,
    borderRadius: 99,
    borderWidth: 1,
    borderColor: colors.brand,
    flexDirection: "row",
    alignItems: "center",
  },
  outlineCtaLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 14,
    color: colors.brand,
    letterSpacing: 0.2,
  },
  solidCta: {
    marginTop: 18,
    alignSelf: "flex-start",
    height: 44,
    paddingHorizontal: 22,
    borderRadius: 99,
    backgroundColor: colors.brand,
    flexDirection: "row",
    alignItems: "center",
  },
  solidCtaLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 14,
    color: colors.white,
    letterSpacing: 0.2,
  },

  // origins
  originRow: {
    marginTop: 20,
    flexDirection: "row",
    gap: 10,
  },
  originCell: {
    flex: 1,
    borderTopWidth: 1,
    borderTopColor: "rgba(30,30,30,0.08)",
    paddingTop: 10,
  },
  originKicker: {
    fontFamily: typography.body,
    fontSize: 10,
    letterSpacing: 1.2,
    color: colors.textTertiary,
    marginBottom: 4,
  },
  originName: {
    fontFamily: typography.serifItalic,
    fontSize: 17,
    color: colors.brand,
    lineHeight: 17 * 1.1,
  },

  voiceAccent: {
    fontFamily: typography.serifItalic,
    fontSize: 19,
    lineHeight: 19 * 1.25,
    color: colors.textSecondary,
    marginTop: 12,
    marginBottom: 16,
  },
});
