import React from "react";
import { Image, StyleSheet, View } from "react-native";
import { BadgeCheck } from "lucide-react-native";
import { colors, radius, typography } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { getWebImage, type WebImageKey } from "@/data/web-images";

/**
 * Doctor endorsement card — pixel-faithful to Claude Design's
 * DoctorCarousel item: cream-alt card, 20 radius, 280px wide; 200px hero
 * portrait at top; serif italic quote; verified-tick + sans semibold name;
 * tracked credentials line.
 */

const SLUG_TO_IMAGE: Record<string, WebImageKey> = {
  "douglas-christianson": "doctor-christiansen",
  "kristy-appelhans": "doctor-appelhans",
};

const CREDENTIALS: Record<string, string> = {
  "kristy-appelhans": "Toxicologist · 20+ yrs reviewing supplement safety",
  "douglas-christianson": "Integrative Medicine · Naturopathic Doctor",
};

const QUOTES: Record<string, string> = {
  "kristy-appelhans":
    "Every Root Labs batch passes the same five-panel screen we run at the FDA. That’s not the floor — that’s the bar.",
  "douglas-christianson":
    "I send my patients to Root Labs because I can read the assay myself. That’s rare in this industry.",
};

interface Doctor {
  slug: string;
  name: string;
  credentials?: string;
  school?: string;
  endorsementQuote?: string;
  verified?: boolean;
}

interface DoctorEndorsementCardProps {
  doctor: Doctor;
}

export function DoctorEndorsementCard({ doctor }: DoctorEndorsementCardProps) {
  const imageKey = SLUG_TO_IMAGE[doctor.slug];
  const quote = QUOTES[doctor.slug] ?? doctor.endorsementQuote ?? "";
  const creds =
    CREDENTIALS[doctor.slug] ??
    [doctor.credentials, doctor.school].filter(Boolean).join(" · ");

  return (
    <View style={styles.card}>
      {imageKey ? (
        <Image
          source={getWebImage(imageKey)}
          style={styles.portrait}
          resizeMode="cover"
        />
      ) : (
        <View style={[styles.portrait, styles.portraitFallback]} />
      )}
      <View style={styles.body}>
        <Text style={styles.quote}>&ldquo;{quote}&rdquo;</Text>
        <View style={styles.nameRow}>
          <BadgeCheck size={13} color={colors.brand} />
          <Text style={styles.name}>{doctor.name}</Text>
        </View>
        <Text style={styles.creds}>{creds}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.bgAlt,
    borderRadius: 20,
    width: 280,
    overflow: "hidden",
  },
  portrait: {
    width: "100%",
    height: 200,
    backgroundColor: colors.surfaceWarm,
  },
  portraitFallback: {},
  body: {
    paddingTop: 18,
    paddingHorizontal: 18,
    paddingBottom: 20,
  },
  quote: {
    fontFamily: typography.serifItalic,
    fontSize: 18,
    lineHeight: 18 * 1.25,
    color: colors.textPrimary,
    marginBottom: 14,
  },
  nameRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginTop: 4,
  },
  name: {
    fontFamily: typography.body,
    fontSize: 12.5,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  creds: {
    fontFamily: typography.body,
    fontSize: 11.5,
    color: colors.textTertiary,
    marginTop: 4,
    lineHeight: 11.5 * 1.4,
  },
});
