import type { Cart, CartItem } from "@/types/domain";

export interface CheckoutService {
  getCart(): Promise<Cart>;
  addItem(productSlug: string, qty?: number): Promise<Cart>;
  updateQty(productSlug: string, qty: number): Promise<Cart>;
  removeItem(productSlug: string): Promise<Cart>;
  clearCart(): Promise<Cart>;
  openCheckout(): Promise<{
    status: "completed" | "cancelled" | "unavailable";
    message?: string;
  }>;
}
