import { useCallback, useEffect, useState } from "react";
import { services } from "@/services";
import type { User, WellnessGoal } from "@/types/domain";

export function useUser() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    const u = await services.auth.getCurrentUser();
    setUser(u);
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const updateGoal = useCallback(async (goal: WellnessGoal) => {
    const u = await services.auth.updateGoal(goal);
    setUser(u);
    services.analytics.track("goal_updated", { goal });
    return u;
  }, []);

  const toggleSaved = useCallback(async (productSlug: string) => {
    const u = await services.auth.toggleSaved(productSlug);
    setUser(u);
    services.analytics.track("saved_toggled", {
      productSlug,
      saved: u.savedProductSlugs.includes(productSlug),
    });
    return u;
  }, []);

  const signInAnonymous = useCallback(async () => {
    const u = await services.auth.signInAnonymous();
    setUser(u);
    return u;
  }, []);

  const signOut = useCallback(async () => {
    await services.auth.signOut();
    setUser(null);
  }, []);

  const isSaved = useCallback(
    (productSlug: string) =>
      user?.savedProductSlugs.includes(productSlug) ?? false,
    [user],
  );

  return {
    user,
    loading,
    updateGoal,
    toggleSaved,
    signInAnonymous,
    signOut,
    isSaved,
    refresh,
  };
}
