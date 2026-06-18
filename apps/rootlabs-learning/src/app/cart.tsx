/**
 * Cart — pixel-faithful port of design_handoff/source/screens/cart.jsx.
 *
 *  Sticky header (back + "Your Cart" centered) → free-shipping band with
 *  progress bar → cart item rows (84px peach thumb + tone/name/size + qty
 *  stepper + price) → promo "Add a code" row → totals (Subtotal / You save
 *  / Shipping / Total) → fixed bottom Checkout pill → Pitch-moment bottom
 *  sheet (slide-up over backdrop, with code block).
 */

import React from "react";
import {
  Animated,
  Easing,
  Image,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  View,
} from "react-native";
import Svg, { Circle, Path } from "react-native-svg";
import { ArrowLeft } from "lucide-react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { colors, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { SectionKicker } from "@components/primitives/SectionKicker";
import { useCart } from "@hooks/useCart";
import productsData from "@/data/products.json";
import type { Product } from "@/types/domain";

const ALL_PRODUCTS = productsData as Product[];
const FREESHIP = 50;

function familyTone(p: Product): string {
  const fam = (p as any).family ?? "general";
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

export default function CartScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { cart, updateQty, removeItem, addItem } = useCart();
  const [sheet, setSheet] = React.useState(false);

  const items = cart?.items ?? [];
  const detailedItems = items
    .map((i) => ({
      product: ALL_PRODUCTS.find((p) => p.slug === i.productSlug),
      qty: i.qty,
    }))
    .filter((x): x is { product: Product; qty: number } => !!x.product);

  const subtotal = detailedItems.reduce(
    (s, x) => s + x.product.price * x.qty,
    0,
  );
  const wasTotal = detailedItems.reduce(
    (s, x) => s + (x.product.mrp ?? x.product.price) * x.qty,
    0,
  );
  const savings = Math.max(0, wasTotal - subtotal);
  const remaining = Math.max(0, FREESHIP - subtotal);
  const pct = Math.min(100, (subtotal / FREESHIP) * 100);

  return (
    <View style={styles.wrap}>
      {/* Header */}
      <View style={[styles.header, { paddingTop: insets.top }]}>
        <View style={styles.headerRow}>
          <Pressable
            onPress={() => router.back()}
            style={styles.iconBtn}
            hitSlop={6}
          >
            <ArrowLeft size={20} color={colors.textPrimary} strokeWidth={1.8} />
          </Pressable>
          <Text style={styles.headerTitle}>Your Cart</Text>
          <View style={{ width: 40 }} />
        </View>
      </View>

      <ScrollView contentContainerStyle={{ paddingBottom: 140 }}>
        {/* Free shipping band */}
        <View
          style={{ paddingTop: 18, paddingHorizontal: 16, paddingBottom: 4 }}
        >
          <View style={styles.shipBand}>
            <View style={styles.shipHead}>
              <TruckSvg />
              <Text style={styles.shipText}>
                {remaining > 0 ? (
                  <>
                    You&rsquo;re{" "}
                    <Text style={styles.shipAccent}>
                      ${remaining.toFixed(2)}
                    </Text>{" "}
                    away from free shipping.
                  </>
                ) : (
                  <>
                    <Text style={styles.shipAccent}>Free shipping</Text>{" "}
                    unlocked.
                  </>
                )}
              </Text>
            </View>
            <View style={styles.shipBarTrack}>
              <View style={[styles.shipBarFill, { width: `${pct}%` }]} />
            </View>
          </View>
        </View>

        {/* Items */}
        <View
          style={{
            paddingHorizontal: 16,
            paddingTop: 16,
            paddingBottom: 8,
            gap: 12,
          }}
        >
          {detailedItems.length === 0 ? (
            <View style={{ paddingVertical: 60, alignItems: "center" }}>
              <Text style={styles.emptyText}>Your cart is empty.</Text>
            </View>
          ) : (
            detailedItems.map(({ product, qty }) => {
              const tone = familyTone(product);
              const imgSrc = product.image
                ? { uri: `https://cdn.shopify.com/...` }
                : undefined;
              const localImg = require("@/data/product-images").getProductImage(
                product.slug,
              );
              return (
                <View key={product.slug} style={styles.itemRow}>
                  <View style={styles.itemThumb}>
                    {localImg ? (
                      <Image
                        source={localImg}
                        style={styles.itemImg}
                        resizeMode="contain"
                      />
                    ) : null}
                  </View>
                  <View style={{ flex: 1, minWidth: 0 }}>
                    <Text style={styles.itemTone}>{tone}</Text>
                    <Text style={styles.itemName}>{product.name}</Text>
                    <Text style={styles.itemSize}>{product.pack}</Text>
                    <View style={styles.itemFooter}>
                      <View style={styles.qtyPill}>
                        <Pressable
                          onPress={() =>
                            qty <= 1
                              ? removeItem(product.slug)
                              : updateQty(product.slug, qty - 1)
                          }
                          style={styles.qtyBtn}
                        >
                          <Text style={styles.qtyBtnLabel}>−</Text>
                        </Pressable>
                        <Text style={styles.qtyValue}>{qty}</Text>
                        <Pressable
                          onPress={() => updateQty(product.slug, qty + 1)}
                          style={styles.qtyBtn}
                        >
                          <Text style={styles.qtyBtnLabel}>+</Text>
                        </Pressable>
                      </View>
                      <View style={styles.itemPriceRow}>
                        {product.mrp ? (
                          <Text style={styles.itemMrp}>
                            ${Math.round(product.mrp * qty)}
                          </Text>
                        ) : null}
                        <Text style={styles.itemPrice}>
                          ${(product.price * qty).toFixed(2)}
                        </Text>
                      </View>
                    </View>
                  </View>
                </View>
              );
            })
          )}
        </View>

        {/* Promo row */}
        {detailedItems.length > 0 ? (
          <View
            style={{ paddingTop: 8, paddingHorizontal: 16, paddingBottom: 20 }}
          >
            <View style={styles.promoRow}>
              <PromoCheckSvg />
              <View style={{ flex: 1 }}>
                <Text style={styles.promoTitle}>Add a code</Text>
                <Text style={styles.promoSub}>
                  Subscriber and referral codes accepted
                </Text>
              </View>
              <ArrowRightSvg color={colors.textSecondary} />
            </View>
          </View>
        ) : null}

        {/* Totals */}
        {detailedItems.length > 0 ? (
          <View style={{ paddingHorizontal: 22, paddingBottom: 16 }}>
            <View style={styles.totals}>
              <TotalRow label="Subtotal" value={`$${subtotal.toFixed(2)}`} />
              {savings > 0 ? (
                <TotalRow
                  label="You save"
                  value={`−$${savings.toFixed(2)}`}
                  valueColor={colors.accent}
                />
              ) : null}
              <TotalRow
                label="Shipping"
                value={subtotal >= FREESHIP ? "Free" : "At checkout"}
              />
              <View style={styles.totalsDivider} />
              <TotalRow label="Total" value={`$${subtotal.toFixed(2)}`} bold />
            </View>
          </View>
        ) : null}
      </ScrollView>

      {/* Sticky checkout bar */}
      {detailedItems.length > 0 ? (
        <View
          style={[
            styles.stickyBar,
            { paddingBottom: Math.max(insets.bottom, 16) + 16 },
          ]}
        >
          <Pressable onPress={() => setSheet(true)} style={styles.checkoutBtn}>
            <Text style={styles.checkoutLabel}>Checkout</Text>
            <View style={styles.checkoutDivider} />
            <Text style={styles.checkoutLabel}>${subtotal.toFixed(2)}</Text>
          </Pressable>
        </View>
      ) : null}

      {/* Pitch sheet modal */}
      <PitchSheetModal visible={sheet} onClose={() => setSheet(false)} />
    </View>
  );
}

function TotalRow({
  label,
  value,
  bold = false,
  valueColor,
}: {
  label: string;
  value: string;
  bold?: boolean;
  valueColor?: string;
}) {
  return (
    <View style={styles.totalRow}>
      <Text
        style={[
          styles.totalLabel,
          bold && {
            color: colors.textPrimary,
            fontWeight: "600",
            fontSize: 14,
          },
        ]}
      >
        {label}
      </Text>
      <Text
        style={[
          styles.totalValue,
          bold && {
            fontFamily: typography.serifNative,
            fontWeight: "700",
            fontSize: 22,
          },
          valueColor ? { color: valueColor } : null,
        ]}
      >
        {value}
      </Text>
    </View>
  );
}

function PitchSheetModal({
  visible,
  onClose,
}: {
  visible: boolean;
  onClose: () => void;
}) {
  const insets = useSafeAreaInsets();
  const translateY = React.useRef(new Animated.Value(600)).current;
  const opacity = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.timing(translateY, {
          toValue: 0,
          duration: 350,
          easing: Easing.bezier(0.2, 0.7, 0.3, 1),
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      translateY.setValue(600);
      opacity.setValue(0);
    }
  }, [visible]);

  return (
    <Modal
      visible={visible}
      transparent
      animationType="none"
      onRequestClose={onClose}
    >
      <Animated.View
        style={[styles.backdrop, { opacity }]}
        pointerEvents="auto"
      >
        <Pressable style={StyleSheet.absoluteFill} onPress={onClose} />
      </Animated.View>
      <Animated.View
        style={[
          styles.sheet,
          { paddingBottom: 42 + insets.bottom, transform: [{ translateY }] },
        ]}
      >
        <View style={styles.dragHandle} />
        <View style={styles.sheetIcon}>
          <Svg width={26} height={26} viewBox="0 0 24 24" fill="none">
            <Path
              d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"
              stroke={colors.accent}
              strokeWidth={1.6}
              strokeLinecap="round"
            />
            <Circle
              cx={12}
              cy={12}
              r={3.5}
              stroke={colors.accent}
              strokeWidth={1.6}
            />
          </Svg>
        </View>
        <View style={{ marginBottom: 10 }}>
          <SectionKicker label="PITCH MOMENT · ENG DEMO" tone="muted" />
        </View>
        <Text style={styles.sheetHeadline}>
          Checkout is <Text style={styles.sheetItalic}>coming soon</Text>.
        </Text>
        <Text style={styles.sheetBody}>
          Shopify integration is pending company API access. The app&rsquo;s
          architecture supports it via a single import swap in{" "}
          <Text style={styles.sheetInlineCode}>src/services/index.ts</Text>.
        </Text>

        <View style={styles.codeBlock}>
          <Text style={styles.codeComment}>{"// today"}</Text>
          <Text style={styles.codeLine}>
            export {"{"} mockCheckout as checkout {"}"} from
            &lsquo;./mock&rsquo;;
          </Text>
          <Text style={[styles.codeComment, { marginTop: 6 }]}>
            {"// flip to live"}
          </Text>
          <Text style={styles.codeLine}>
            export {"{"} shopifyCheckout as checkout {"}"} from
            &lsquo;./shopify&rsquo;;
          </Text>
        </View>

        <View style={styles.sheetButtons}>
          <Pressable onPress={onClose} style={styles.sheetBackBtn}>
            <Text style={styles.sheetBackLabel}>Back to cart</Text>
          </Pressable>
          <Pressable onPress={onClose} style={styles.sheetNotifyBtn}>
            <Text style={styles.sheetNotifyLabel}>Notify me at launch</Text>
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
      </Animated.View>
    </Modal>
  );
}

function TruckSvg() {
  return (
    <Svg width={20} height={20} viewBox="0 0 24 24" fill="none">
      <Path
        d="M3 7h11l4 4v6h-2M14 17h-5"
        stroke={colors.brand}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <Circle cx={7} cy={17} r={2} stroke={colors.brand} strokeWidth={1.5} />
      <Circle cx={17} cy={17} r={2} stroke={colors.brand} strokeWidth={1.5} />
    </Svg>
  );
}

function PromoCheckSvg() {
  return (
    <Svg width={18} height={18} viewBox="0 0 24 24" fill="none">
      <Path
        d="M9 12l2 2 4-4M3 12a9 9 0 1 0 18 0 9 9 0 0 0-18 0z"
        stroke={colors.brand}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

function ArrowRightSvg({ color }: { color: string }) {
  return (
    <Svg width={14} height={14} viewBox="0 0 16 16" fill="none">
      <Path
        d="M3 8h10M9 4l4 4-4 4"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },

  header: {
    backgroundColor: colors.bg,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "rgba(30,30,30,0.08)",
  },
  headerRow: {
    height: 48,
    paddingHorizontal: 14,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  iconBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(254,248,243,0.85)",
    alignItems: "center",
    justifyContent: "center",
  },
  headerTitle: {
    fontFamily: typography.serifNative,
    fontWeight: "600",
    fontSize: 20,
    color: colors.textPrimary,
  },

  // free shipping band
  shipBand: {
    backgroundColor: colors.bgAlt,
    borderRadius: 16,
    paddingHorizontal: 18,
    paddingVertical: 16,
  },
  shipHead: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: 10,
  },
  shipText: {
    flex: 1,
    fontFamily: typography.body,
    fontSize: 13,
    color: colors.textSecondary,
    lineHeight: 13 * 1.5,
  },
  shipAccent: { color: colors.brand, fontWeight: "700" },
  shipBarTrack: {
    height: 6,
    borderRadius: 99,
    backgroundColor: colors.white,
    overflow: "hidden",
  },
  shipBarFill: { height: "100%", backgroundColor: colors.brand },

  // items
  itemRow: {
    flexDirection: "row",
    gap: 14,
    padding: 14,
    backgroundColor: colors.white,
    borderRadius: 16,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: "rgba(30,30,30,0.08)",
  },
  itemThumb: {
    width: 84,
    height: 84,
    borderRadius: 12,
    backgroundColor: colors.surfaceWarm,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  },
  itemImg: { width: "88%", height: "88%" },
  itemTone: {
    fontFamily: typography.body,
    fontSize: 10.5,
    fontWeight: "500",
    letterSpacing: 0.6,
    color: colors.textTertiary,
    marginBottom: 2,
  },
  itemName: {
    fontFamily: typography.serifNative,
    fontWeight: "600",
    fontSize: 17,
    lineHeight: 17 * 1.1,
    color: colors.textPrimary,
  },
  itemSize: {
    fontFamily: typography.body,
    fontSize: 11.5,
    color: colors.textTertiary,
    marginTop: 2,
  },
  itemFooter: {
    marginTop: 12,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  qtyPill: {
    height: 32,
    borderRadius: 99,
    borderWidth: 1,
    borderColor: "rgba(30,30,30,0.08)",
    flexDirection: "row",
    alignItems: "center",
    overflow: "hidden",
  },
  qtyBtn: {
    width: 32,
    height: 32,
    alignItems: "center",
    justifyContent: "center",
  },
  qtyBtnLabel: {
    fontFamily: typography.body,
    fontSize: 16,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  qtyValue: {
    minWidth: 22,
    textAlign: "center",
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 13,
    color: colors.textPrimary,
  },
  itemPriceRow: { flexDirection: "row", alignItems: "baseline", gap: 6 },
  itemMrp: {
    fontFamily: typography.body,
    fontSize: 11.5,
    color: colors.textTertiary,
    textDecorationLine: "line-through",
  },
  itemPrice: {
    fontFamily: typography.body,
    fontWeight: "700",
    fontSize: 15,
    color: colors.textPrimary,
  },

  emptyText: {
    fontFamily: typography.body,
    fontSize: 15,
    color: colors.textSecondary,
  },

  // promo row
  promoRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: colors.bgAlt,
    borderRadius: 14,
  },
  promoTitle: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 13,
    color: colors.textPrimary,
  },
  promoSub: {
    fontFamily: typography.body,
    fontSize: 11,
    color: colors.textTertiary,
    marginTop: 1,
  },

  // totals
  totals: {
    paddingTop: 16,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: "rgba(30,30,30,0.08)",
    gap: 10,
  },
  totalRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "baseline",
  },
  totalLabel: {
    fontFamily: typography.body,
    fontSize: 13,
    fontWeight: "500",
    color: colors.textSecondary,
  },
  totalValue: {
    fontFamily: typography.body,
    fontSize: 14,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  totalsDivider: {
    height: 1,
    backgroundColor: "rgba(30,30,30,0.08)",
    marginVertical: 6,
  },

  // sticky bar
  stickyBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: "rgba(254,248,243,0.96)",
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: "rgba(30,30,30,0.08)",
    paddingHorizontal: 16,
    paddingTop: 12,
  },
  checkoutBtn: {
    width: "100%",
    height: 52,
    borderRadius: 26,
    backgroundColor: colors.brand,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
  },
  checkoutLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 15,
    letterSpacing: 0.3,
    color: colors.white,
  },
  checkoutDivider: {
    width: 1,
    height: 16,
    backgroundColor: "rgba(255,255,255,0.3)",
  },

  // pitch sheet
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.36)",
  },
  sheet: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: colors.bg,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingTop: 14,
    paddingHorizontal: 22,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -20 },
    shadowOpacity: 0.2,
    shadowRadius: 60,
    elevation: 24,
  },
  dragHandle: {
    width: 44,
    height: 4,
    borderRadius: 2,
    backgroundColor: "rgba(30,30,30,0.08)",
    alignSelf: "center",
    marginBottom: 18,
  },
  sheetIcon: {
    width: 56,
    height: 56,
    borderRadius: 16,
    backgroundColor: colors.brandDark,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 18,
  },
  sheetHeadline: {
    fontFamily: typography.serifNative,
    fontWeight: "700",
    fontSize: 26,
    lineHeight: 26 * 1.05,
    color: colors.textPrimary,
    marginBottom: 14,
    letterSpacing: -0.3,
  },
  sheetItalic: {
    fontFamily: typography.serifItalic,
  },
  sheetBody: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 14 * 1.5,
    color: colors.textSecondary,
    marginBottom: 18,
  },
  sheetInlineCode: {
    fontFamily: typography.body,
    fontSize: 12.5,
    color: colors.brand,
    backgroundColor: colors.bgAlt,
  },
  codeBlock: {
    backgroundColor: colors.bgAlt,
    borderRadius: 14,
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginBottom: 22,
  },
  codeLine: {
    fontFamily: typography.body,
    fontSize: 12,
    color: colors.textSecondary,
    lineHeight: 12 * 1.55,
  },
  codeComment: {
    fontFamily: typography.body,
    fontSize: 12,
    color: colors.textTertiary,
    lineHeight: 12 * 1.55,
  },
  sheetButtons: { flexDirection: "row", gap: 10 },
  sheetBackBtn: {
    flex: 1,
    height: 46,
    borderRadius: 23,
    borderWidth: 1,
    borderColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "transparent",
  },
  sheetBackLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 13.5,
    color: colors.brand,
  },
  sheetNotifyBtn: {
    flex: 1.4,
    height: 46,
    borderRadius: 23,
    backgroundColor: colors.brand,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  sheetNotifyLabel: {
    fontFamily: typography.body,
    fontWeight: "600",
    fontSize: 13.5,
    color: colors.white,
  },
});
