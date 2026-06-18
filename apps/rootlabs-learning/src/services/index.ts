/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║  THE SERVICES CONTAINER — the single file the company changes    ║
 * ║  to ship this app to production.                                 ║
 * ║                                                                  ║
 * ║  Every screen in this app imports services from HERE, never      ║
 * ║  from `./auth/auth.mock` directly. Swap a `mockX` for `realX`    ║
 * ║  below, and the entire app picks up the new implementation       ║
 * ║  without changing a single screen, component, or hook.           ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

// ─── Mock implementations (used now — works offline, $0 cost) ──────
import { mockAuth } from "./auth/auth.mock";
import { mockProducts } from "./products/products.mock";
import { mockAICoach } from "./ai-coach/ai-coach.mock";
import { mockCheckout } from "./checkout/checkout.mock";
import { mockAnalytics } from "./analytics/analytics.mock";

// ─── Production implementations (commented until company API access lands) ─
// import { shopifyAuth }       from './auth/auth.shopify';
// import { shopifyProducts }   from './products/products.shopify';
// import { claudeAICoach }     from './ai-coach/ai-coach.claude';
// import { shopifyCheckout }   from './checkout/checkout.shopify';
// import { posthogAnalytics }  from './analytics/analytics.posthog';

import type { AuthService } from "./auth/auth.interface";
import type { ProductsService } from "./products/products.interface";
import type { AICoachService } from "./ai-coach/ai-coach.interface";
import type { CheckoutService } from "./checkout/checkout.interface";
import type { AnalyticsService } from "./analytics/analytics.interface";

export interface Services {
  auth: AuthService;
  products: ProductsService;
  aiCoach: AICoachService;
  checkout: CheckoutService;
  analytics: AnalyticsService;
}

/**
 * THE PITCH SENTENCE
 * -------------------
 * "Three to five files. Replace the imports below with their `.shopify`
 *  / `.claude` / `.posthog` counterparts. App ships."
 */
export const services: Services = {
  auth: mockAuth, // → shopifyAuth       when Shopify Customer Accounts API lands
  products: mockProducts, // → shopifyProducts   when Shopify Storefront API lands
  aiCoach: mockAICoach, // → claudeAICoach     when Anthropic API key lands
  checkout: mockCheckout, // → shopifyCheckout   when Shopify Storefront API lands
  analytics: mockAnalytics, // → posthogAnalytics  when PostHog key lands
};

// Re-export storage helper (no adapter pattern — local-only)
export { storage } from "./storage/storage";
