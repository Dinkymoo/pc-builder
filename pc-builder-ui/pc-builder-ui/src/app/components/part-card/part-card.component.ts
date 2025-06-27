import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Category, GraphicCard, PartWithCategoryAndCompatibility } from '../models/part';

@Component({
  selector: 'app-part-card',
  templateUrl: './part-card.component.html',
  styleUrls: ['./part-card.component.css'],
  standalone: false
})
export class PartCardComponent implements OnInit {

  @Input() part!: PartWithCategoryAndCompatibility;
  @Output() onPartAdded = new EventEmitter<GraphicCard>();
  constructor() { }

  ngOnInit(): void {
  }

  onImageError(event: Event): void {
    const target = event.target as HTMLImageElement;
    target.src = 'assets/images/default-part-image.png'; // Fallback image path
    target.alt = 'Image not available'; // Fallback alt text  
  }

  add(card: GraphicCard) {
    console.log('part-card.component-add', card); // Log to console
    this.onPartAdded.emit(card); // Optional: emit to parent if needed
  }

  isCompatible(selectedGraphicCards: GraphicCard[]): boolean {
    if (!this.part.compatibility) return true;
    return this.part.compatibility.every(compatibilityId =>
      selectedGraphicCards.some(selectedCard => selectedCard.id.toString() === compatibilityId)
    );
  }
  isIncompatible(selectedGraphicCards: GraphicCard[]): boolean {
    if (!this.part.compatibility) return false;
    return selectedGraphicCards.some(selectedCard =>
      !this.part.compatibility.includes(selectedCard.id.toString())
    );
  }
  isSelected(selectedGraphicCards: GraphicCard[]): boolean {
    return selectedGraphicCards.some(selectedCard => selectedCard.id === this.part.id);
  }
  isAvailable(): boolean {
    // Assuming availability is determined by a property in the Part model
    return this.part.available !== false; // Adjust based on your Part model
  }
  isOutOfStock(): boolean {
    // Assuming out of stock is determined by a property in the Part model
    return this.part.available === false; // Adjust based on your Part model
  }
  isRecommended(): boolean {
    // Assuming recommendation is determined by a property in the Part model
    return this.part.recommended === true; // Adjust based on your Part model
  }
  isPopular(): boolean {
    // Assuming popularity is determined by a property in the Part model
    return this.part.popular === true; // Adjust based on your Part model
  }
  isNew(): boolean {
    // Assuming newness is determined by a property in the Part model
    return this.part.new === true; // Adjust based on your Part model
  }
  isFeatured(): boolean {
    // Assuming featured status is determined by a property in the Part model
    return this.part.featured === true; // Adjust based on your Part model
  }
  isLimitedEdition(): boolean {
    // Assuming limited edition status is determined by a property in the Part model
    return this.part.limitedEdition === true; // Adjust based on your Part model
  }
  isOnSale(): boolean {
    // Assuming sale status is determined by a property in the Part model
    return this.part.onSale === true; // Adjust based on your Part model
  }
  isDiscounted(): boolean {
    // Assuming discount status is determined by a property in the Part model
    return this.part.discounted === true; // Adjust based on your Part model
  }
  isExclusive(): boolean {
    // Assuming exclusivity is determined by a property in the Part model
    return this.part.exclusive === true; // Adjust based on your Part model
  }
  isPreOrder(): boolean {
    // Assuming pre-order status is determined by a property in the Part model
    return this.part.isPreOrder === true; // Adjust based on your Part model
  }

  isBackOrder(): boolean {
    // Assuming back-order status is determined by a property in the Part model
    return this.part.isBackOrder === true; // Adjust based on your Part model
  }
  isCustomizable(): boolean {
    // Assuming customizability is determined by a property in the Part model
    return this.part.isCustomizable === true; // Adjust based on your Part model    

  }
  getImageUrl(): string {
    return this.part.imageUrl || 'assets/images/default-part-image.png'; // Adjust the default image path as necessary
  }
  getDescription(): string {
    return this.part.description || 'No description available'; // Adjust as necessary
  }
  getPrice(): string {
    return this.part.price ? `$${this.part.price.toFixed(2)}` : 'Price not available'; // Adjust as necessary
  }
  getName(): string {
    return this.part.name || 'Unnamed Part'; // Adjust as necessary
  }
  getId(): number {
    return this.part.id || -1; // Adjust as necessary
  }
  getCategoryName(): string {
    return this.part.categoryName || 'Unknown Category'; // Adjust as necessary
  }
  getCategoryIcon(): string {
    return this.part.categoryIcon || 'help'; // Adjust as necessary
  }
  getCategoryColor(): string {
    return this.part.categoryColor || '#000000'; // Adjust as necessary
  }
  getCategoryDescription(): string {
    return this.part.categoryDescription || 'No category description available'; // Adjust as necessary
  }
  getCategoryImageUrl(): string {
    return this.part.categoryImageUrl || 'assets/default-category-image.png'; // Adjust the default image path as necessary
  }
  getCategoryCompatibility(): string[] {
    return this.part.categoryCompatibility || []; // Adjust as necessary
  }
  getCategory(): Category {
    return {
      name: this.getCategoryName(),
      graphicCards: [this.part] // Use graphicCards instead of parts
    };
  }
  getPartWithCategoryAndCompatibility(): PartWithCategoryAndCompatibility {
    return {
      ...this.part,
      category: this.getCategoryName(),
      categoryId: this.part.categoryId || -1, // Adjust as necessary
      categoryName: this.getCategoryName(),
      categoryIcon: this.getCategoryIcon(),
      categoryColor: this.getCategoryColor(),
      categoryDescription: this.getCategoryDescription(),
      categoryImageUrl: this.getCategoryImageUrl(),
      categoryCompatibility: this.getCategoryCompatibility()
    };
  }
}