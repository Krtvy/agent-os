/**
 * Mock products service — reads from src/data/products.json.
 *
 * ⚠ PLUG IN HERE: replace this with `products.shopify.ts` when the company
 * provides Shopify Storefront API credentials. The interface contract is in
 * `products.interface.ts` — implement that and the rest of the app stays
 * unchanged.
 */

import productsData from "@/data/products.json";
import type { Product, WellnessGoal } from "@/types/domain";
import type { ProductsService } from "./products.interface";

// Simulate network latency so loading states are visible in dev
const FAKE_LATENCY_MS = 120;
const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

const ALL: Product[] = productsData as Product[];

export const mockProducts: ProductsService = {
  async list(filter) {
    await wait(FAKE_LATENCY_MS);
    let out = [...ALL];
    if (filter?.goal) {
      out = out.filter((p) => p.goals.includes(filter.goal as WellnessGoal));
    }
    if (filter?.limit) {
      out = out.slice(0, filter.limit);
    }
    return out;
  },

  async getBySlug(slug) {
    await wait(FAKE_LATENCY_MS);
    return ALL.find((p) => p.slug === slug) ?? null;
  },

  async search(query) {
    await wait(FAKE_LATENCY_MS);
    const q = query.toLowerCase();
    return ALL.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.ingredients.some((i) => i.toLowerCase().includes(q)),
    );
  },

  async related(slug, limit = 4) {
    await wait(FAKE_LATENCY_MS);
    const product = ALL.find((p) => p.slug === slug);
    if (!product) return [];
    // Related = same goal overlap, excluding self
    return ALL.filter((p) => p.slug !== slug)
      .map((p) => ({
        p,
        score: p.goals.filter((g) => product.goals.includes(g)).length,
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map((x) => x.p);
  },
};
