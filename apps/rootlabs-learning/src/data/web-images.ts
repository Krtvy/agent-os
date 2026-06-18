/**
 * Editorial-asset slug → bundled image.
 *
 * Sources are pre-cropped JPEGs in assets/images/web/, downloaded from
 * the live rootlabs.co Shopify CDN and reframed so the subject sits in
 * the center 4:3 (or 16:9 for hero / 1:1 for portraits) band. This is
 * the form the README "Image sizing cheatsheet" expects — every editorial
 * Image still passes aspectRatio + resizeMode="cover" at the call site.
 *
 * Bundled local assets are preferred over the raw CDN URLs because:
 *   - Pre-cropped to the design aspect (no in-flight reframing)
 *   - Ship offline (no first-paint network round-trip)
 *   - Cache-busted by the bundle version, not by ?v= query strings
 *
 * To refresh: re-download from the rootlabs.co/cdn/shop/files/<slug>
 * URL listed in design_handoff_root_labs_mobile/source/screens/home.jsx,
 * pre-crop to the spec aspect, save to assets/images/web/<slug>.jpg.
 */

import type { ImageSourcePropType } from "react-native";

const ASSETS = {
  // 16:9 cinematic hero (man at beach)
  "hero-lifestyle": require("../../assets/images/web/hero-lifestyle.jpg"),

  // 4:3 editorial photos
  "story-family": require("../../assets/images/web/story-family.jpg"),
  "our-craft-lab": require("../../assets/images/web/our-craft-lab.jpg"),
  "sourcing-women": require("../../assets/images/web/sourcing-women.jpg"),
  "voice-turmeric": require("../../assets/images/web/voice-turmeric.jpg"),
  "gummies-in-hands": require("../../assets/images/web/gummies-in-hands.jpg"),

  // Portraits — founder (120×120 circle) + doctor carousel (280×200 cards)
  "founder-mayank": require("../../assets/images/web/founder-mayank.jpg"),
  "doctor-appelhans": require("../../assets/images/web/doctor-appelhans.jpg"),
  "doctor-christiansen": require("../../assets/images/web/doctor-christiansen.jpg"),
} satisfies Record<string, ImageSourcePropType>;

export type WebImageKey = keyof typeof ASSETS;

export function getWebImage(key: WebImageKey): ImageSourcePropType {
  return ASSETS[key];
}
