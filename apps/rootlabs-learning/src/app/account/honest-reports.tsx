import React, { useEffect, useState } from "react";
import { View, ScrollView, StyleSheet, Pressable, Alert } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ArrowLeft, ShieldCheck } from "lucide-react-native";
import { colors, spacing, radius } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { CertPDFRow } from "@components/rootlabs-specific/CertPDFRow";
import type { CertReport, Product } from "@/types/domain";
import { services } from "@/services";

export default function HonestReportsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [reports, setReports] = useState<CertReport[]>([]);
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    services.analytics.screen("honest-reports");
    (async () => {
      const r = (await import("@/data/cert-reports.json"))
        .default as CertReport[];
      setReports(r);
      const productsList = await Promise.all(
        r.map((rep) => services.products.getBySlug(rep.productSlug)),
      );
      setProducts(productsList.filter((p): p is Product => p !== null));
    })();
  }, []);

  return (
    <View style={styles.wrap}>
      <View style={[styles.header, { paddingTop: insets.top }]}>
        <Pressable onPress={() => router.back()} hitSlop={8}>
          <ArrowLeft size={24} color={colors.textPrimary} />
        </Pressable>
        <Text variant="display3" weight="bold">
          Honest Reports
        </Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView contentContainerStyle={{ paddingBottom: spacing.xxl }}>
        <View style={styles.intro}>
          <ShieldCheck size={32} color={colors.brand} />
          <Text
            variant="display3"
            weight="bold"
            style={{ marginTop: spacing.sm }}
          >
            We test every batch. Every result is public.
          </Text>
          <Text
            variant="bodySmall"
            tone="secondary"
            style={{ marginTop: spacing.xs }}
          >
            Independent third-party lab reports for every product, every
            manufacturing batch.
          </Text>
        </View>

        {reports.map((report) => {
          const product = products.find((p) => p.slug === report.productSlug);
          return (
            <View
              key={report.productSlug + report.batchNumber}
              style={styles.productBlock}
            >
              <View style={styles.productHead}>
                <Text variant="bodyLarge" weight="bold">
                  {product?.name ?? report.productSlug}
                </Text>
                <Text variant="micro" tone="tertiary" style={{ marginTop: 2 }}>
                  Batch {report.batchNumber} · Mfg. {report.manufactureDate}
                </Text>
              </View>
              {report.panels.map((panel) => (
                <CertPDFRow
                  key={panel.name}
                  panel={panel}
                  onPress={() =>
                    Alert.alert(
                      `${panel.name} Report`,
                      `${panel.verdict}\n\n${panel.summary ?? ""}\n\nIn the production build, this opens the actual signed PDF (already bundled in assets/cert-pdfs/) using a PDF viewer component. The 5 PDFs are in place; the viewer integration is the only remaining wiring.`,
                    )
                  }
                />
              ))}
              <View style={styles.footer}>
                <Text variant="micro" tone="tertiary">
                  Tested by {report.testedBy}
                </Text>
                {report.testedByCIN ? (
                  <Text variant="tiny" tone="tertiary">
                    CIN {report.testedByCIN} · Independent third-party · NABL
                    accredited
                  </Text>
                ) : null}
              </View>
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.sm,
  },
  intro: {
    padding: spacing.lg,
    alignItems: "center",
  },
  productBlock: {
    backgroundColor: colors.white,
    marginHorizontal: spacing.md,
    marginBottom: spacing.lg,
    borderRadius: radius.lg,
    overflow: "hidden",
  },
  productHead: {
    padding: spacing.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  footer: {
    padding: spacing.md,
    backgroundColor: colors.bgAlt,
  },
});
