/**
 * Mock checkout — persists a cart in AsyncStorage. `openCheckout()` returns
 * 'unavailable' so the UI can show the explicit "Coming soon when company
 * API access lands" message — that IS the pitch moment.
 *
 * ⚠ PLUG IN HERE: replace with `checkout.shopify.ts` (Shopify Storefront
 * Cart API + checkout URL opened in a WebView) when company adopts.
 */

import AsyncStorage from "@react-native-async-storage/async-storage";
import productsData from "@/data/products.json";
import type { Cart, CartItem, Product } from "@/types/domain";
import type { CheckoutService } from "./checkout.interface";

const STORAGE_KEY = "rootlabs:mock-cart";
const FAKE_LATENCY_MS = 100;
const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

const ALL_PRODUCTS = productsData as Product[];

function emptyCart(): Cart {
  return {
    id: `cart-${Date.now()}`,
    items: [],
    subtotal: 0,
    total: 0,
    currency: "USD",
  };
}

function recalculate(items: CartItem[]): Pick<Cart, "subtotal" | "total"> {
  const subtotal = items.reduce((sum, item) => {
    const product = ALL_PRODUCTS.find((p) => p.slug === item.productSlug);
    return sum + (product?.price ?? 0) * item.qty;
  }, 0);
  return { subtotal, total: subtotal };
}

async function loadCart(): Promise<Cart> {
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Cart) : emptyCart();
  } catch {
    return emptyCart();
  }
}

async function saveCart(cart: Cart): Promise<Cart> {
  await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
  return cart;
}

export const mockCheckout: CheckoutService = {
  async getCart() {
    await wait(FAKE_LATENCY_MS);
    return loadCart();
  },

  async addItem(productSlug, qty = 1) {
    await wait(FAKE_LATENCY_MS);
    const cart = await loadCart();
    const existing = cart.items.find((i) => i.productSlug === productSlug);
    const items = existing
      ? cart.items.map((i) =>
          i.productSlug === productSlug ? { ...i, qty: i.qty + qty } : i,
        )
      : [...cart.items, { productSlug, qty }];
    return saveCart({ ...cart, items, ...recalculate(items) });
  },

  async updateQty(productSlug, qty) {
    await wait(FAKE_LATENCY_MS);
    const cart = await loadCart();
    const items =
      qty <= 0
        ? cart.items.filter((i) => i.productSlug !== productSlug)
        : cart.items.map((i) =>
            i.productSlug === productSlug ? { ...i, qty } : i,
          );
    return saveCart({ ...cart, items, ...recalculate(items) });
  },

  async removeItem(productSlug) {
    await wait(FAKE_LATENCY_MS);
    const cart = await loadCart();
    const items = cart.items.filter((i) => i.productSlug !== productSlug);
    return saveCart({ ...cart, items, ...recalculate(items) });
  },

  async clearCart() {
    await wait(FAKE_LATENCY_MS);
    return saveCart(emptyCart());
  },

  async openCheckout() {
    await wait(FAKE_LATENCY_MS);
    // INTENTIONAL: this is the pitch moment. The UI displays this message
    // to the user explaining that checkout will work when the company
    // wires up the Shopify Storefront API.
    return {
      status: "unavailable",
      message:
        "Checkout integration pending company API access. " +
        "Replace `mockCheckout` with `shopifyCheckout` in src/services/index.ts to ship.",
    };
  },
};
