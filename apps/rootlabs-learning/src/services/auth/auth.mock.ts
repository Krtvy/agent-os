/**
 * Mock auth — stores user in AsyncStorage. No real auth provider involved.
 *
 * ⚠ PLUG IN HERE: replace with `auth.shopify.ts` (Shopify Customer Accounts)
 * or `auth.firebase.ts` (Firebase Auth) when the company decides.
 */

import AsyncStorage from "@react-native-async-storage/async-storage";
import type { User, WellnessGoal } from "@/types/domain";
import type { AuthService } from "./auth.interface";

const STORAGE_KEY = "rootlabs:mock-user";
const FAKE_LATENCY_MS = 80;
const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function loadUser(): Promise<User | null> {
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

async function saveUser(user: User): Promise<User> {
  await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  return user;
}

function makeAnonymousUser(): User {
  return {
    id: `mock-${Date.now()}`,
    name: undefined,
    email: undefined,
    phone: undefined,
    goal: undefined,
    savedProductSlugs: [],
    joinedAt: new Date().toISOString(),
  };
}

export const mockAuth: AuthService = {
  async getCurrentUser() {
    await wait(FAKE_LATENCY_MS);
    return loadUser();
  },

  async signInWithApple() {
    await wait(FAKE_LATENCY_MS);
    const existing = await loadUser();
    if (existing) return existing;
    return saveUser({
      ...makeAnonymousUser(),
      name: "Demo User",
      email: "demo@rootlabs.co",
    });
  },

  async signInWithGoogle() {
    await wait(FAKE_LATENCY_MS);
    const existing = await loadUser();
    if (existing) return existing;
    return saveUser({
      ...makeAnonymousUser(),
      name: "Demo User",
      email: "demo@rootlabs.co",
    });
  },

  async signInAnonymous() {
    await wait(FAKE_LATENCY_MS);
    const existing = await loadUser();
    if (existing) return existing;
    return saveUser(makeAnonymousUser());
  },

  async signOut() {
    await wait(FAKE_LATENCY_MS);
    await AsyncStorage.removeItem(STORAGE_KEY);
  },

  async updateGoal(goal: WellnessGoal) {
    await wait(FAKE_LATENCY_MS);
    const user = (await loadUser()) ?? makeAnonymousUser();
    return saveUser({ ...user, goal });
  },

  async toggleSaved(productSlug: string) {
    await wait(FAKE_LATENCY_MS);
    const user = (await loadUser()) ?? makeAnonymousUser();
    const saved = user.savedProductSlugs.includes(productSlug)
      ? user.savedProductSlugs.filter((s) => s !== productSlug)
      : [...user.savedProductSlugs, productSlug];
    return saveUser({ ...user, savedProductSlugs: saved });
  },
};
