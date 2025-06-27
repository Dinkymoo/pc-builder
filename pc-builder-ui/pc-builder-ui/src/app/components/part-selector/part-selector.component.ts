import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { HttpClientService } from '../../services/http-client.service';
import { GraphicCard } from './test-data';

export interface Category {
  name: string;
  graphicCards: GraphicCard[];
}

@Component({
  selector: 'app-part-selector',
  templateUrl: './part-selector.component.html',
  styleUrls: ['./part-selector.component.css'],
  standalone: false
})
export class PartSelectorComponent implements OnInit {
  @Input() filteredGraphicCards: GraphicCard[] = []; // Initialize as empty, will be set in ngOnInit
  @Input() category: string = 'All'; // Default to 'All', will be set by parent component
  @Input() summaryMode: boolean = false; // Default to false, will be set by parent component
  @Output() onGraphicCardSelect: EventEmitter<GraphicCard> = new EventEmitter<GraphicCard>();
  constructor(
    private httpClient: HttpClientService
  ) {
    if (this.summaryMode === false) {
      httpClient.setBaseUrl('http://127.0.0.1:8000/api')
      this.httpClient.get<GraphicCard[]>('graphic-cards').subscribe(
        (data: GraphicCard[]) => {
          // Always show all cards by default, regardless of category
          this.filteredGraphicCards = data;
          console.log('Fetched graphic cards from API:', this.filteredGraphicCards, 'Category:', this.category);
        },
        (error) => {
          console.error('Error fetching graphic cards:', error);
          // Fallback to test data if API call fails
          this.filteredGraphicCards = [];
        }
      );
    }
    else {
      // If summaryMode is true, we can set filteredGraphicCards to an empty array or handle it differently
      this.filteredGraphicCards = [];
    }
  }

  ngOnInit(): void {
    console.log('PartSelectorComponent initialized with category:', this.category);
  }

  onGraphicCardAdded(card: GraphicCard) {
    console.log('Graphic card added:', card);
    this.onGraphicCardSelect.emit(card);
  }

  onFilterChangeHandler(filtered: GraphicCard[]) {
    // this.filteredGraphicCards = filtered;
    // this.onGraphicCardSelect.emit(filtered);
  }

  isCompatible(card: GraphicCard, selectedGraphicCards: GraphicCard[]): boolean {
    if (!card.compatibility) return true;
    return selectedGraphicCards.every(selectedCard => {
      // Implement compatibility logic if needed
      return true;
    });
  }

  getImageUrl(card: GraphicCard): string {
    return card.imageUrl || 'assets/images/default-part-image.png';
  }

  getDescription(card: GraphicCard): string {
    return card.description || 'No description available';
  }

  getPrice(card: GraphicCard): string {
    return card.price ? `$${card.price.toFixed(2)}` : 'Price not available';
  }

  getName(card: GraphicCard): string {
    return card.name || 'Unnamed Part';
  }

  getId(card: GraphicCard): number {
    return card.id || -1;
  }

  getCategoryName(): string {
    switch (this.category) {
      case 'cpu': return 'CPU';
      case 'gpu': return 'GPU';
      case 'ram': return 'RAM';
      case 'storage': return 'Storage';
      case 'psu': return 'Power Supply Unit (PSU)';
      case 'case': return 'Case';
      default: return 'Unknown Category';
    }
  }

  getCategoryIcon(): string {
    switch (this.category) {
      case 'cpu': return 'cpu';
      case 'gpu': return 'graphic_eq';
      case 'ram': return 'memory';
      case 'storage': return 'storage';
      case 'psu': return 'power';
      case 'case': return 'case';
      default: return 'help';
    }
  }

  getCategoryColor(): string {
    switch (this.category) {
      case 'cpu': return '#ff9800';
      case 'gpu': return '#2196f3';
      case 'ram': return '#4caf50';
      case 'storage': return '#9c27b0';
      case 'psu': return '#f44336';
      case 'case': return '#607d8b';
      default: return '#9e9e9e';
    }
  }

  getCategoryDescription(): string {
    switch (this.category) {
      case 'cpu': return 'Central Processing Unit (CPU) is the brain of your computer, handling all instructions.';
      case 'gpu': return 'Graphics Processing Unit (GPU) is responsible for rendering images, animations, and video.';
      case 'ram': return 'Random Access Memory (RAM) is the short-term memory of your computer, storing data for quick access.';
      case 'storage': return 'Storage refers to the long-term memory of your computer, where data is stored permanently.';
      case 'psu': return 'Power Supply Unit (PSU) provides power to all components of your computer.';
      case 'case': return 'The case houses all the components of your computer, providing protection and cooling.';
      default: return 'Unknown category. Please select a valid part category.';
    }
  }

  getCategoryImageUrl(): string {
    switch (this.category) {
      case 'cpu': return 'assets/images/cpu.png';
      case 'gpu': return 'assets/images/gpu.png';
      case 'ram': return 'assets/images/ram.png';
      case 'storage': return 'assets/images/storage.png';
      case 'psu': return 'assets/images/psu.png';
      case 'case': return 'assets/images/case.png';
      default: return 'assets/images/default.png';
    }
  }

  getCategoryId(): number {
    switch (this.category) {
      case 'cpu': return 1;
      case 'gpu': return 2;
      case 'ram': return 3;
      case 'storage': return 4;
      case 'psu': return 5;
      case 'case': return 6;
      default: return 0;
    }
  }

  getCategoryCompatibility(): string[] {
    switch (this.category) {
      case 'cpu': return ['motherboard', 'cooler'];
      case 'gpu': return ['motherboard', 'power supply'];
      case 'ram': return ['motherboard'];
      case 'storage': return ['motherboard', 'power supply'];
      case 'psu': return ['motherboard', 'case'];
      case 'case': return ['motherboard', 'power supply', 'cooler'];
      default: return [];
    }
  }
}