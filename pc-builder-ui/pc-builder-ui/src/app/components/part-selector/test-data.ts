
export interface GraphicCard {
    id: number;
    name: string;
    category: string;
    manufacturer: string;
    price: number;
    inStock: boolean;
    description?: string;
    imageUrl?: string;
    compatibility?: string[];
}

