export interface GraphicCard {
  id: number;
  name: string;
  category: string;
  manufacturer: string;
  price: number;
  inStock: boolean;
  description: string;
  imageUrl: string;
  compatibility?: string[];
}

// Remove 'parts' from Category, only use 'graphicCards'
export interface Category {
  name: string;
  graphicCards: GraphicCard[];
}

export interface PartWithCategory extends GraphicCard {
  category: string;
  categoryId: number;
  categoryName: string;
  categoryIcon: string;
  categoryColor: string;
  categoryDescription: string;
  categoryImageUrl: string;
  categoryCompatibility: string[];
}

export interface PartWithCategoryAndCompatibility extends GraphicCard {
  category: string;
  categoryId: number;
  categoryName: string;
  categoryIcon: string;
  categoryColor: string;
  categoryDescription: string;
  categoryImageUrl: string;
  categoryCompatibility: string[];
  compatibility: string[];
  compatibleWith: GraphicCard[];
  incompatibleWith: GraphicCard[];
  isCompatible: boolean;
  isIncompatible: boolean;
  isSelected: boolean;
  isFiltered: boolean;
  isAvailable: boolean;
  isOutOfStock: boolean;
  isRecommended: boolean;
  isPopular: boolean;
  isNew: boolean;
  isFeatured: boolean;
  isLimitedEdition: boolean;
  isOnSale: boolean;
  isDiscounted: boolean;
  isPreOrder: boolean;
  isBackOrder: boolean;
  isCustomizable: boolean;
  exclusive: boolean;
  discounted: boolean;
  onSale: boolean;
  featured: boolean;
  limitedEdition: boolean;
  available: boolean;
  recommended: boolean;
  popular: boolean;
  new: boolean;
}