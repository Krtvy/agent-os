import React from "react";
import { View, ScrollView, StyleSheet, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import {
  ArrowLeft,
  MapPin,
  Package,
  Megaphone,
  Wallet,
  CreditCard,
  Bell,
  HelpCircle,
  Phone,
  ShieldCheck,
  FileText,
  Heart,
} from "lucide-react-native";
import { colors, spacing, radius } from "@/design-system/theme";
import { Text } from "@components/primitives/Text";
import { Button } from "@components/primitives/Button";
import { MenuRow } from "@components/content/MenuRow";
import { useUser } from "@hooks/useUser";

export default function AccountScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user, signOut } = useUser();

  return (
    <View style={[styles.wrap]}>
      <View style={[styles.header, { paddingTop: insets.top }]}>
        <Pressable
          onPress={() => router.back()}
          hitSlop={8}
          style={styles.backBtn}
        >
          <ArrowLeft size={20} color={colors.white} />
        </Pressable>
        <Text variant="display3" weight="bold">
          Your Account
        </Text>
        <View style={{ width: 36 }} />
      </View>

      <ScrollView
        contentContainerStyle={{ paddingBottom: spacing.xxl + insets.bottom }}
      >
        <View style={styles.profile}>
          <View style={styles.avatar} />
          <View style={{ flex: 1 }}>
            <Text variant="body" weight="semibold">
              {user?.name ?? "Demo User"}
            </Text>
            <Text variant="bodySmall" tone="tertiary">
              {user?.email ?? user?.phone ?? "Tap to sign in"}
            </Text>
          </View>
        </View>

        <MenuRow
          icon={<MapPin size={20} color={colors.textPrimary} />}
          title="Address"
          subtitle="View or edit saved addresses"
          onPress={() => {}}
        />
        <MenuRow
          icon={<Package size={20} color={colors.textPrimary} />}
          title="Orders"
          subtitle="Your order history"
          onPress={() => {}}
        />
        <MenuRow
          icon={<Heart size={20} color={colors.textPrimary} />}
          title="Saved"
          subtitle={`${user?.savedProductSlugs.length ?? 0} products`}
          onPress={() => router.push("/(tabs)/saved")}
        />
        <MenuRow
          icon={<Megaphone size={20} color={colors.textPrimary} />}
          title="Refer your friends"
          subtitle="Earn up to $25"
          onPress={() => {}}
        />
        <MenuRow
          icon={<Wallet size={20} color={colors.textPrimary} />}
          title="Root Wallet"
          subtitle="$0"
          onPress={() => {}}
        />
        <MenuRow
          icon={<CreditCard size={20} color={colors.textPrimary} />}
          title="Payment Methods"
          subtitle="Manage your saved payment methods"
          onPress={() => {}}
        />
        <MenuRow
          icon={<Bell size={20} color={colors.textPrimary} />}
          title="Notification Settings"
          subtitle="Enable or disable app notifications"
          onPress={() => {}}
        />
        <MenuRow
          icon={<HelpCircle size={20} color={colors.textPrimary} />}
          title="FAQ"
          subtitle="Frequently Asked Questions"
          onPress={() => {}}
        />
        <MenuRow
          icon={<Phone size={20} color={colors.textPrimary} />}
          title="Contact Us"
          subtitle="Chat with us"
          onPress={() => {}}
        />
        <MenuRow
          icon={<ShieldCheck size={20} color={colors.textPrimary} />}
          title="Privacy Policy"
          onPress={() => {}}
        />
        <MenuRow
          icon={<FileText size={20} color={colors.textPrimary} />}
          title="Terms of Service"
          onPress={() => {}}
        />

        {/* The Honest Reports row — Mosaic's signature trust feature, mapped to Rootlabs */}
        <MenuRow
          icon={<ShieldCheck size={20} color={colors.brand} />}
          title="Honest Reports"
          subtitle="Check batch test reports for every product"
          onPress={() => router.push("/account/honest-reports")}
        />

        <View style={styles.footer}>
          <Text variant="micro" tone="tertiary" center>
            Root Labs v0.1.0 (demo build)
          </Text>
          <View
            style={{ marginTop: spacing.md, paddingHorizontal: spacing.md }}
          >
            <Button
              label="Logout"
              variant="destructive"
              fullWidth
              onPress={async () => {
                await signOut();
                router.replace("/");
              }}
            />
          </View>
        </View>
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
    paddingBottom: spacing.md,
    backgroundColor: colors.bg,
  },
  backBtn: {
    width: 36,
    height: 36,
    borderRadius: radius.sm,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  profile: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    padding: spacing.md,
    backgroundColor: colors.white,
    marginBottom: spacing.sm,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.surfaceWarm,
  },
  footer: {
    marginTop: spacing.xl,
    alignItems: "center",
  },
});
