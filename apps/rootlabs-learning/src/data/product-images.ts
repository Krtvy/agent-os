/**
 * Static map of product slug → bundled image asset.
 *
 * Regenerated from the live rootlabs.co catalog on 2026-05-15.
 * Re-run /tmp/regen_rootlabs_catalog.py if the catalog changes.
 */

import type { ImageSourcePropType } from "react-native";

const ASSETS = {
  "ashwa-mag": require("../../assets/images/products/ashwa-mag.png"),
  "alpha-gummies-60s": require("../../assets/images/products/alpha-gummies-60s.png"),
  "alpha-gummies-120s": require("../../assets/images/products/alpha-gummies-120s.png"),
  "immunity-combo": require("../../assets/images/products/immunity-combo.png"),
  "shilajit-gummies-60s": require("../../assets/images/products/shilajit-gummies.png"),
  "shilajit-gummies-120s": require("../../assets/images/products/shilajit-gummies.png"),
  "sea-moss-gummies-60s": require("../../assets/images/products/sea-moss-gummies.png"),
  "sea-moss-gummies-120s": require("../../assets/images/products/sea-moss-gummies.png"),
  "turmeric-gummies-60s": require("../../assets/images/products/turmeric-gummies.png"),
  "turmeric-gummies": require("../../assets/images/products/turmeric-gummies.png"),
} satisfies Record<string, ImageSourcePropType>;

export function getProductImage(slug: string): ImageSourcePropType | undefined {
  return (ASSETS as Record<string, ImageSourcePropType>)[slug];
}
