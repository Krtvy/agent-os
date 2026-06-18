import { useCallback, useEffect, useState } from "react";
import { services } from "@/services";
import type { Cart } from "@/types/domain";

export function useCart() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    const c = await services.checkout.getCart();
    setCart(c);
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const addItem = useCallback(async (productSlug: string, qty = 1) => {
    const c = await services.checkout.addItem(productSlug, qty);
    setCart(c);
    services.analytics.track("cart_add", { productSlug, qty });
    return c;
  }, []);

  const updateQty = useCallback(async (productSlug: string, qty: number) => {
    const c = await services.checkout.updateQty(productSlug, qty);
    setCart(c);
    return c;
  }, []);

  const removeItem = useCallback(async (productSlug: string) => {
    const c = await services.checkout.removeItem(productSlug);
    setCart(c);
    services.analytics.track("cart_remove", { productSlug });
    return c;
  }, []);

  const itemCount = cart?.items.reduce((sum, i) => sum + i.qty, 0) ?? 0;

  return { cart, loading, itemCount, addItem, updateQty, removeItem, refresh };
}
