import type { ProductRecommendation, WellnessGoal } from "@/types/domain";

export interface AICoachService {
  recommendProducts(
    goal: WellnessGoal,
    context?: string,
  ): Promise<ProductRecommendation[]>;
  explainIngredient(ingredientSlug: string): Promise<string>;
  answerWellnessQuestion(question: string): Promise<string>;
}
