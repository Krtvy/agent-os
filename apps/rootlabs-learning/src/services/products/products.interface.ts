import type { Product, WellnessGoal } from "@/types/domain";

export interface ProductsService {
  list(filter?: {
    goal?: WellnessGoal;
    category?: string;
    limit?: number;
  }): Promise<Product[]>;
  getBySlug(slug: string): Promise<Product | null>;
  search(query: string): Promise<Product[]>;
  related(slug: string, limit?: number): Promise<Product[]>;
}
