/**
 * Mock analytics — console.log only. Zero network calls.
 *
 * ⚠ PLUG IN HERE: replace with `analytics.posthog.ts` (PostHog free tier
 * supports 1M events/month — plenty for early prod). Identical interface.
 */

import type { AnalyticsService } from "./analytics.interface";

const tag = "[analytics]";

export const mockAnalytics: AnalyticsService = {
  identify(userId, traits) {
    // eslint-disable-next-line no-console
    console.log(tag, "identify", userId, traits ?? {});
  },
  track(event, properties) {
    // eslint-disable-next-line no-console
    console.log(tag, "track", event, properties ?? {});
  },
  screen(name, properties) {
    // eslint-disable-next-line no-console
    console.log(tag, "screen", name, properties ?? {});
  },
};
