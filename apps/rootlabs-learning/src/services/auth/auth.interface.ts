import type { User, WellnessGoal } from "@/types/domain";

export interface AuthService {
  getCurrentUser(): Promise<User | null>;
  signInWithApple(): Promise<User>;
  signInWithGoogle(): Promise<User>;
  signInAnonymous(): Promise<User>;
  signOut(): Promise<void>;
  updateGoal(goal: WellnessGoal): Promise<User>;
  toggleSaved(productSlug: string): Promise<User>;
}
