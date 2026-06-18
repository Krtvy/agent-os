import React from "react";
import { Tabs } from "expo-router";
import { colors, typography } from "@/design-system/theme";
import {
  TabBag,
  TabFlask,
  TabHeart,
  TabSparkle,
} from "@components/primitives/Glyphs";

/**
 * Bottom tab bar — uses the custom SVG glyphs from Claude Design's shared.jsx
 * (sparkle for For You, bag for Shop, flask for Science, heart for Saved).
 * The active state fills the glyph; inactive uses tertiary text color.
 */

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.brand,
        tabBarInactiveTintColor: colors.textTertiary,
        tabBarStyle: {
          backgroundColor: colors.white,
          borderTopColor: colors.border,
          height: 80,
          paddingTop: 8,
          paddingBottom: 32,
        },
        tabBarLabelStyle: {
          fontFamily: typography.body,
          fontSize: 10.5,
          fontWeight: "500",
          letterSpacing: 0.2,
          marginTop: 4,
        },
      }}
    >
      <Tabs.Screen
        name="for-you"
        options={{
          title: "For You",
          tabBarIcon: ({ color, focused }) => (
            <TabSparkle size={22} color={color} filled={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="shop"
        options={{
          title: "Shop",
          tabBarIcon: ({ color, focused }) => (
            <TabBag size={22} color={color} filled={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="science"
        options={{
          title: "Science",
          tabBarIcon: ({ color, focused }) => (
            <TabFlask size={22} color={color} filled={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="saved"
        options={{
          title: "Saved",
          tabBarIcon: ({ color, focused }) => (
            <TabHeart size={22} color={color} filled={focused} />
          ),
        }}
      />
    </Tabs>
  );
}
