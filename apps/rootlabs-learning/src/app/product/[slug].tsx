/**
 * PDP — Product Detail. Pixel-faithful port of design_handoff/source/screens/pdp.jsx.
 *
 * Sections: peach sticky header (back/heart/cart) → peach hero band (image +
 * badge + 4-dot pager) → name/rating/price block → Subscribe & save row →
 * 4-claim grid → Benefits/Ingredients/Tested-for segmented tabs → Reviews
 * preview → fixed bottom CTA bar (back + Add to Cart).
 */

import React from "react";
import { Image, Pressable, ScrollView, StyleSheet, View } from "react-native";
import Svg, { Path } from "react-native-svg";
import { ArrowLeft, ShoppingCart } from "lucide-react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { colors, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";
import { StarRating } from "@components/primitives/StarRating";
import { VerifiedBadge } from "@components/primitives/Glyphs";
import { services } from "@/services";
import { useUser } from "@hooks/useUser";
import { useCart } from "@hooks/useCart";
import { getProductImage } from "@/data/product-images";
import type { Product } from "@/types/domain";

type TabKey = "benefits" | "ingredients" | "tested";

const TESTS = [
  { panel: "Aflatoxin", value: "< 1 ppb" },
  { panel: "Allergen", value: "None detected" },
  { panel: "Gluten", value: "< 5 ppm" },
  { panel: "Heavy Metals", value: "< 0.1 ppm" },
  { panel: "Pesticide", value: "Below LOD" },
];

const BENEFITS = [
  {
    t: "Supports stress recovery",
    d: "KSM-66 ashwagandha standardized to 5% withanolides.",
  },
  {
    t: "Promotes deep sleep",
    d: "Magnesium glycinate — the form your nervous system actually uses.",
  },
  {
    t: "Daily-use safe",
    d: "No sedatives. No melatonin. No morning grogginess.",
  },
];

const INGREDIENTS_LIST = [
  {
    o: "Himalayas, India",
    name: "KSM-66 Ashwagandha",
    dose: "600 mg",
    form: "Standardized root extract",
  },
  {
    o: "United States",
    name: "Magnesium Glycinate",
    dose: "200 mg",
    form: "Chelated, highly bioavailable",
  },
  {
    o: "Florida, USA",
    name: "Organic Cane Pectin",
    dose: "—",
    form: "Plant-based gelatin alternative",
  },
];

const REVIEWS = [
  {
    initial: "J",
    name: "Jordan M.",
    date: "Mar 12",
    rating: 5,
    text: "Three weeks in. Best sleep I’ve had in years and zero morning fog.",
  },
  {
    initial: "P",
    name: "Priya K.",
    date: "Feb 28",
    rating: 5,
    text: "I called to ask about the magnesium form. They sent me the chromatogram.",
  },
];

function familyTone(product: Product): string {
  const fam = (product as any).family ?? "general";
  switch (fam) {
    case "alpha":
      return "Vitality";
    case "ashwa":
      return "Stress · Sleep";
    case "immunity":
      return "Immunity";
    case "shilajit":
      return "Energy · Endurance";
    case "sea moss":
      return "Thyroid · Skin";
    case "turmeric":
      return "Anti-inflammatory";
    default:
      return "Wellness";
  }
}

export default function PDPScreen() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toggleSaved, isSaved } = useUser();
  const { addItem, itemCount } = useCart();
  const [product, setProduct] = React.useState<Product | null>(null);
  const [tab, setTab] = React.useState<TabKey>("benefits");

  React.useEffect(() => {
    if (!slug) return;
    services.analytics.screen("pdp", { slug });
    (async () => {
      const p = await services.products.getBySlug(slug);
      setProduct(p ?? null);
    })();
  }, [slug]);

  if (!product) {
    return (
      <View
        style={[
          styles.wrap,
          { alignItems: "center", justifyContent: "center" },
        ]}
      >
        <Text variant="body" tone="tertiary">
          Loading…
        </Text>
      </View>
    );
  }

  const saved = isSaved(product.slug);
  const imgSource = getProductImage(product.slug);
  const tone = familyTone(product);
  const badge =
    product.mrp && product.mrp > product.price
      ? `−${Math.round((1 - product.price / product.mrp) * 100)}%`
      : "New";
  const isDiscountBadge = badge.startsWith("−");
  const subPrice = (product.price * 0.85).toFixed(2);

  return (
    <View style={styles.wrap}>
      {/* Peach header — back / heart / cart */}
      <View style={[styles.header, { paddingTop: insets.top }]}>
        <View style={styles.headerRow}>
          <Pressable
            onPress={() => router.back()}
            style={styles.iconBtn}
            hitSlop={6}
          >
            <ArrowLeft size={20} color={colors.textPrimary} strokeWidth={1.8} />
          </Pressable>
          <View style={styles.headerRight}>
            <Pressable
              onPress={() => toggleSaved(product.slug)}
              style={styles.iconBtn}
              hitSlop={6}
            >
              <HeartSvg
                filled={saved}
                color={saved ? colors.accent : colors.textPrimary}
              />
            </Pressable>
            <Pressable
              onPress={() => router.push("/cart")}
              style={styles.iconBtn}
              hitSlop={6}
            >
              <View>
                <ShoppingCart
                  size={20}
                  color={colors.textPrimary}
                  strokeWidth={1.8}
                />
                {itemCount > 0 ? (
                  <View style={styles.cartBadge}>
                    <Text style={styles.cartBadgeLabel}>{itemCount}</Text>
                  </View>
                ) : null}
              </View>
            </Pressable>
          </View>
        </View>
      </View>

      <ScrollView contentContainerStyle={{ paddingBottom: 120 }}>
        {/* Hero band on peach */}
        <View style={styles.heroBand}>
          {imgSource ? (
            <Image
              source={imgSource}
              style={styles.heroImage}
              resizeMode="contain"
            />
          ) : null}
          <View
            style={[
              styles.badge,
              {
                backgroundColor: isDiscountBadge ? colors.accent : colors.brand,
              },
            ]}
          >
            <Text style={styles.badgeLabel}>{badge}</Text>
          </View>
          <View style={styles.dotsRow}>
            {[0, 1, 2, 3].map((i) => (
              <View
                key={i}
                style={[
                  styles.dot,
                  i === 0 ? styles.dotActive : styles.dotInactive,
                ]}
              />
            ))}
          </View>
        </View>

        {/* Name + rating + price */}
        <View style={styles.section}>
          <View style={{ marginBottom: 10 }}>
            <SectionKicker label={tone.toUpperCase()} tone="muted" />
          </View>
          <Text style={styles.productName}>{product.name}</Text>
          <Text style={styles.size}>{product.pack}</Text>

          <View style={styles.ratingRow}>
            <StarRating rating={product.rating} size={13} showNumeric={false} />
            <Text style={styles.ratingValue}>{product.rating.toFixed(1)}</Text>
            <Text style={styles.ratingCount}>
              ({product.reviewCount} reviews)
            </Text>
          </View>

          <View style={styles.priceRow}>
            <Text style={styles.priceMain}>${Math.round(product.price)}</Text>
            {product.mrp ? (
              <>
                <Text style={styles.priceMrp}>${product.mrp}</Text>
                <View style={styles.savePill}>
                  <Text style={styles.savePillLabel}>
                    Save ${Math.round(product.mrp - product.price)}
                  </Text>
                </View>
              </>
            ) : null}
          </View>

          {/* Subscribe & save row */}
          <View style={styles.subRow}>
            <View style={styles.subCheckbox}>
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
            <View style={{ flex: 1 }}>
              <Text style={styles.subTitle}>Subscribe &amp; save 15%</Text>
              <Text style={styles.subDesc}>
                Every 30 days. Skip or cancel anytime.
              </Text>
            </View>
            <Text style={styles.subPrice}>${subPrice}</Text>
          </View>

          {/* Claims grid */}
          <View style={styles.claimsGrid}>
            {[
              "High Potency",
              "No Sugar Added",
              "Clean & Vegan",
              "Made for the American Customer",
            ].map((c) => (
              <View key={c} style={styles.claimCell}>
                <View style={styles.claimDot}>
                  <Svg width={10} height={10} viewBox="0 0 16 16" fill="none">
                    <Path
                      d="M3 8.5l3 3 7-8"
                      stroke="#fff"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </Svg>
                </View>
                <Text style={styles.claimLabel}>{c}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Segmented tabs */}
        <View style={{ paddingHorizontal: 22, paddingBottom: 22 }}>
          <View style={styles.tabsRow}>
            {(
              [
                ["benefits", "Benefits"],
                ["ingredients", "Ingredients"],
                ["tested", "Tested for"],
              ] as const
            ).map(([id, label]) => {
              const active = tab === id;
              return (
                <Pressable
                  key={id}
                  onPress={() => setTab(id)}
                  style={[styles.tabBtn, active && styles.tabBtnActive]}
                >
                  <Text
                    style={[styles.tabLabel, active && styles.tabLabelActive]}
                  >
                    {label}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          {tab === "benefits" ? (
            <View>
              <Text style={styles.bodyText}>
                {product.name} pairs traditional Ayurvedic herbology with a
                modern, bioavailable gummy delivery. Crafted in small batches at
                our facility in Salt Lake City and tested down to the lot.
              </Text>
              <View style={{ gap: 12, marginTop: 18 }}>
                {BENEFITS.map((b) => (
                  <View key={b.t} style={styles.benefitRow}>
                    <View style={styles.benefitPlate}>
                      <View style={styles.benefitDot} />
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={styles.benefitTitle}>{b.t}</Text>
                      <Text style={styles.benefitDesc}>{b.d}</Text>
                    </View>
                  </View>
                ))}
              </View>
            </View>
          ) : null}

          {tab === "ingredients" ? (
            <View style={{ gap: 12 }}>
              {INGREDIENTS_LIST.map((ing) => (
                <View key={ing.name} style={styles.ingCard}>
                  <View style={{ marginBottom: 6 }}>
                    <SectionKicker label={ing.o.toUpperCase()} tone="muted" />
                  </View>
                  <View style={styles.ingRow}>
                    <Text style={styles.ingName}>{ing.name}</Text>
                    <Text style={styles.ingDose}>{ing.dose}</Text>
                  </View>
                  <Text style={styles.ingForm}>{ing.form}</Text>
                </View>
              ))}
            </View>
          ) : null}

          {tab === "tested" ? (
            <View style={styles.testCard}>
              <View style={styles.testHeader}>
                <VerifiedBadge size={16} color={colors.accent} />
                <SectionKicker
                  label="BATCH RL-09142 · TESTED FOR"
                  tone="onDark"
                />
              </View>
              <Text style={styles.testItalic}>
                Five panels. Public report. Lot-traceable.
              </Text>
              <View style={{ gap: 8 }}>
                {TESTS.map((t, i) => (
                  <View
                    key={t.panel}
                    style={[
                      styles.testRow,
                      i < TESTS.length - 1 && styles.testRowDivider,
                    ]}
                  >
                    <VerifiedBadge size={14} color={colors.accent} />
                    <Text style={styles.testPanel}>{t.panel}</Text>
                    <Text style={styles.testValue}>{t.value}</Text>
                    <View style={styles.passBadge}>
                      <Text style={styles.passLabel}>PASS</Text>
                    </View>
                  </View>
                ))}
              </View>
              <Pressable style={styles.downloadBtn}>
                <Text style={styles.downloadLabel}>
                  Download full report (PDF)
                </Text>
              </Pressable>
            </View>
          ) : null}
        </View>

        {/* Reviews preview */}
        <View style={{ paddingHorizontal: 22, paddingBottom: 36 }}>
          <View style={styles.reviewsHead}>
            <SectionKicker
              label={`REVIEWS · ${product.reviewCount}`}
              tone="muted"
            />
            <Text style={styles.seeAll}>See all →</Text>
          </View>
          {REVIEWS.map((r, i) => (
            <View
              key={r.name}
              style={[styles.reviewRow, i === 0 && styles.reviewRowFirst]}
            >
              <View style={styles.reviewMeta}>
                <View style={styles.reviewAvatar}>
                  <Text style={styles.reviewInitial}>{r.initial}</Text>
                </View>
                <Text style={styles.reviewName}>{r.name}</Text>
                <StarRating rating={r.rating} size={11} showNumeric={false} />
                <Text style={styles.reviewDate}>{r.date}</Text>
              </View>
              <Text style={styles.reviewBody}>&ldquo;{r.text}&rdquo;</Text>
            </View>
          ))}
        </View>
      </ScrollView>

      {/* Sticky bottom CTA */}
      <View
        style={[
          styles.stickyCta,
          { paddingBottom: Math.max(insets.bottom, 16) + 16 },
        ]}
      >
        <Pressable onPress={() => router.back()} style={styles.stickyBack}>
          <ArrowLeft size={18} color={colors.textPrimary} strokeWidth={1.8} />
        </Pressable>
        <Pressable
          style={styles.addToCart}
          onPress={() => {
            addItem(product.slug);
            router.push("/cart");
          }}
        >
          <Text style={styles.addToCartLabel}>
            Add to Cart · ${Math.round(product.price)}
          </Text>
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
      </View>
    </View>
  );
}

function HeartSvg({
  filled = false,
  color = colors.textPrimary,
}: {
  filled?: boolean;
  color?: string;
}) {
  return (
    <Svg
      width={20}
      height={20}
      viewBox="0 0 24 24"
      fill={filled ? color : "none"}
      stroke={color}
      strokeWidth={1.6}
    >
      <Path
        d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.5a4.3 4.3 0 0 1 7.5 2.8C19.5 15.9 12 20.5 12 20.5z"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },

  // header
  header: {
    backgroundColor: colors.surfaceWarm,
    zIndex: 30,
  },
  headerRow: {
    height: 48,
    paddingHorizontal: 14,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  headerRight: { flexDirection: "row", gap: 8 },
  iconBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(254,248,243,0.85)",
    alignItems: "center",
    justifyContent: "center",
  },
  cartBadge: {
    position: "absolute",
    top: -3,
    right: -4,
    minWidth: 16,
    height: 16,
    borderRadius: 8,
    paddingHorizontal: 4,
    backgroundColor: colors.accent,
    alignItems: "center",
    justifyContent: "center",
  },
  cartBadgeLabel: {
    color: colors.white,
    fontFamily: typography.body,
    fontSize: 10,
    fontWeight: "700",
  },

  // hero band
  heroBand: {
    backgroundColor: colors.surfaceWarm,
    paddingTop: 6,
    paddingBottom: 30,
    alignItems: "center",
    position: "relative",
  },
  heroImage: { width: "78%", height: 320 },
  badge: {
    position: "absolute",
    top: 12,
    left: 18,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 99,
  },
  badgeLabel: {
    color: colors.white,
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 10.5,
    letterSpacing: 0.6,
  },
  dotsRow: {
    position: "absolute",
    bottom: 14,
    flexDirection: "row",
    gap: 6,
  },
  dot: { height: 6, borderRadius: 3 },
  dotActive: { width: 18, backgroundColor: colors.brand },
  dotInactive: { width: 6, backgroundColor: "rgba(30,30,30,0.18)" },

  // name/rating/price block
  section: { paddingHorizontal: 22, paddingTop: 26 },
  productName: {
    fontFamily: typography.serifNative,
    fontWeight: "700",
    fontSize: 32,
    lineHeight: 32 * 1.05,
    color: colors.textPrimary,
    marginBottom: 6,
  },
  size: {
    fontFamily: typography.body,
    fontSize: 13,
    color: colors.textTertiary,
    marginBottom: 12,
  },
  ratingRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 18,
  },
  ratingValue: {
    fontFamily: typography.body,
    fontSize: 13,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  ratingCount: {
    fontFamily: typography.body,
    fontSize: 12.5,
    color: colors.textTertiary,
  },
  priceRow: {
    flexDirection: "row",
    alignItems: "baseline",
    gap: 10,
    marginBottom: 12,
  },
  priceMain: {
    fontFamily: typography.serifNative,
    fontWeight: "700",
    fontSize: 32,
    color: colors.textPrimary,
  },
  priceMrp: {
    fontFamily: typography.body,
    fontSize: 16,
    color: colors.textTertiary,
    textDecorationLine: "line-through",
  },
  savePill: {
    backgroundColor: "rgba(229,115,46,0.10)",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 99,
  },
  savePillLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 12,
    color: colors.accent,
  },

  // Subscribe & save row
  subRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    backgroundColor: colors.bgAlt,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    marginBottom: 22,
  },
  subCheckbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  subTitle: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 13.5,
    color: colors.textPrimary,
  },
  subDesc: {
    fontFamily: typography.body,
    fontSize: 11.5,
    color: colors.textTertiary,
    marginTop: 2,
  },
  subPrice: {
    fontFamily: typography.serifNative,
    fontWeight: "700",
    fontSize: 16,
    color: colors.brand,
  },

  // claims grid
  claimsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    marginBottom: 28,
  },
  claimCell: {
    flexBasis: "47%",
    flexGrow: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  claimDot: {
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  claimLabel: {
    fontFamily: typography.body,
    fontSize: 12.5,
    fontWeight: "500",
    color: colors.textSecondary,
  },

  // segmented tabs
  tabsRow: {
    flexDirection: "row",
    gap: 4,
    padding: 4,
    backgroundColor: colors.bgAlt,
    borderRadius: 99,
    marginBottom: 22,
  },
  tabBtn: {
    flex: 1,
    height: 36,
    borderRadius: 99,
    alignItems: "center",
    justifyContent: "center",
  },
  tabBtnActive: {
    backgroundColor: colors.white,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 1,
  },
  tabLabel: {
    fontFamily: typography.body,
    fontSize: 12.5,
    fontWeight: "500",
    color: colors.textTertiary,
  },
  tabLabelActive: { color: colors.brand, fontWeight: "600" },

  // tab content
  bodyText: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 14 * 1.5,
    color: colors.textSecondary,
  },
  benefitRow: { flexDirection: "row", gap: 12, alignItems: "flex-start" },
  benefitPlate: {
    width: 26,
    height: 26,
    borderRadius: 8,
    backgroundColor: colors.bgAlt,
    alignItems: "center",
    justifyContent: "center",
  },
  benefitDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.brand,
  },
  benefitTitle: {
    fontFamily: typography.serifNative,
    fontWeight: "600",
    fontSize: 16,
    color: colors.textPrimary,
    marginBottom: 2,
  },
  benefitDesc: {
    fontFamily: typography.body,
    fontSize: 12.5,
    color: colors.textSecondary,
    lineHeight: 12.5 * 1.5,
  },

  ingCard: { padding: 16, backgroundColor: colors.bgAlt, borderRadius: 14 },
  ingRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "baseline",
    marginBottom: 4,
  },
  ingName: {
    fontFamily: typography.serifNative,
    fontWeight: "600",
    fontSize: 18,
    color: colors.textPrimary,
  },
  ingDose: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 13,
    color: colors.brand,
  },
  ingForm: {
    fontFamily: typography.body,
    fontSize: 12.5,
    color: colors.textSecondary,
  },

  // Tested-for card
  testCard: {
    backgroundColor: colors.brandDark,
    borderRadius: 16,
    paddingHorizontal: 18,
    paddingVertical: 20,
    marginBottom: 14,
  },
  testHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 12,
  },
  testItalic: {
    fontFamily: typography.serifItalic,
    fontSize: 22,
    lineHeight: 22 * 1.2,
    color: colors.brandTextOnDark,
    marginBottom: 14,
  },
  testRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingBottom: 8,
  },
  testRowDivider: {
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "rgba(255,255,255,0.10)",
  },
  testPanel: {
    flex: 1,
    fontFamily: typography.body,
    fontSize: 13.5,
    fontWeight: "500",
    color: colors.brandTextOnDark,
  },
  testValue: {
    fontFamily: typography.body,
    fontSize: 11.5,
    color: "rgba(255,255,255,0.55)",
  },
  passBadge: {
    backgroundColor: colors.accent,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 99,
  },
  passLabel: {
    color: colors.brandDark,
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 10.5,
    letterSpacing: 0.6,
  },
  downloadBtn: {
    marginTop: 18,
    height: 40,
    borderRadius: 99,
    backgroundColor: "rgba(255,255,255,0.08)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.20)",
    alignItems: "center",
    justifyContent: "center",
  },
  downloadLabel: {
    color: colors.brandTextOnDark,
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 13,
  },

  // reviews
  reviewsHead: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "baseline",
    marginBottom: 18,
  },
  seeAll: {
    fontFamily: typography.body,
    fontSize: 12.5,
    color: colors.brand,
    fontWeight: "500",
  },
  reviewRow: {
    paddingVertical: 16,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: "rgba(30,30,30,0.08)",
  },
  reviewRowFirst: {},
  reviewMeta: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: 8,
  },
  reviewAvatar: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  reviewInitial: {
    color: colors.white,
    fontFamily: typography.serifNative,
    fontWeight: "600",
    fontSize: 13,
  },
  reviewName: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 13,
    color: colors.textPrimary,
  },
  reviewDate: {
    marginLeft: "auto",
    fontFamily: typography.body,
    fontSize: 11,
    color: colors.textTertiary,
  },
  reviewBody: {
    fontFamily: typography.body,
    fontSize: 13.5,
    lineHeight: 13.5 * 1.5,
    color: colors.textSecondary,
  },

  // sticky CTA
  stickyCta: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: "rgba(254,248,243,0.94)",
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: "rgba(30,30,30,0.08)",
    paddingHorizontal: 16,
    paddingTop: 12,
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  stickyBack: {
    width: 46,
    height: 46,
    borderRadius: 23,
    borderWidth: 1,
    borderColor: "rgba(30,30,30,0.08)",
    alignItems: "center",
    justifyContent: "center",
  },
  addToCart: {
    flex: 1,
    height: 46,
    borderRadius: 23,
    backgroundColor: colors.brand,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 22,
  },
  addToCartLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 14,
    letterSpacing: 0.3,
    color: colors.white,
  },
});
