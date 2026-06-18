/**
 * Domain types — the shared vocabulary every service interface and screen consumes.
 * Keep this file pure type definitions; no runtime code.
 */

// ─── Wellness goals (used in onboarding + recommendations) ────────
export type WellnessGoal = "energy" | "immunity" | "vitality" | "general";

export const WELLNESS_GOALS: {
  id: WellnessGoal;
  label: string;
  icon: string;
  description: string;
}[] = [
  {
    id: "energy",
    label: "Energy",
    icon: "⚡",
    description: "Sustained, clean energy without the crash",
  },
  {
    id: "immunity",
    label: "Immunity",
    icon: "🛡",
    description: "Resilience for daily life",
  },
  {
    id: "vitality",
    label: "Vitality",
    icon: "🌱",
    description: "Whole-body wellness from the roots up",
  },
  {
    id: "general",
    label: "General",
    icon: "✨",
    description: "I want to feel better, broadly",
  },
];

// ─── Product ──────────────────────────────────────────────────────
export interface ProductSubscription {
  available: boolean;
  interval: "monthly" | "quarterly";
  discountPct: number;
}

export interface Product {
  slug: string;
  name: string;
  pack?: string;
  subtitle?: string;
  price: number;
  mrp?: number;
  currency: "USD";
  image: string;
  gallery?: string[];
  claims: string[];
  ingredients: string[]; // slugs into Ingredient[]
  goals: WellnessGoal[];
  description: string;
  longDescription?: string;
  subscription?: ProductSubscription;
  certs?: string[]; // panel names: aflatoxin / allergen / gluten / heavy-metals / pesticide
  rating: number;
  reviewCount: number;
  inStock?: boolean;
}

// ─── Ingredient ───────────────────────────────────────────────────
export interface Ingredient {
  slug: string;
  name: string;
  tagline: string;
  origin?: string;
  benefits: string[];
  scientificName?: string;
  form?: string;
  bioavailability?: string;
  shortDescription: string;
  longDescription?: string;
  icon: string;
}

// ─── Article ──────────────────────────────────────────────────────
export interface Article {
  slug: string;
  title: string;
  category: string;
  readTimeMin: number;
  publishedWeek: number; // 1..52 — used to cycle the weekly drop
  heroImage: string;
  summary: string;
  body: string;
  linkedProducts?: string[]; // product slugs
}

// ─── Doctor ───────────────────────────────────────────────────────
export interface Doctor {
  slug: string;
  name: string;
  credentials: string;
  school?: string;
  specialty?: string;
  yearsOfPractice?: number;
  photo: string;
  endorsementQuote: string;
  verified: boolean;
}

// ─── Review ───────────────────────────────────────────────────────
export interface Review {
  id: string;
  productSlug: string;
  authorName: string;
  authorAge?: number;
  authorCity?: string;
  rating: number; // 1..5
  title?: string;
  body: string;
  date: string; // ISO
  verifiedPurchase?: boolean;
}

// ─── Cert Report ──────────────────────────────────────────────────
export interface CertPanel {
  name: string;
  parameters: number;
  verdict: string;
  summary?: string;
  pdfPath: string;
}

export interface CertReport {
  productSlug: string;
  batchNumber: string;
  manufactureDate: string;
  testedBy: string;
  testedByCIN?: string;
  panels: CertPanel[];
}

// ─── User (mock for now) ──────────────────────────────────────────
export interface User {
  id: string;
  name?: string;
  email?: string;
  phone?: string;
  goal?: WellnessGoal;
  savedProductSlugs: string[];
  joinedAt: string; // ISO
}

// ─── Cart (mock for now) ──────────────────────────────────────────
export interface CartItem {
  productSlug: string;
  qty: number;
  subscription?: boolean;
}

export interface Cart {
  id: string;
  items: CartItem[];
  subtotal: number;
  total: number;
  currency: "USD";
}

// ─── AI Recommendation ────────────────────────────────────────────
export interface ProductRecommendation {
  productSlug: string;
  rationale: string;
  confidence?: number;
}
