import { Component, Output, EventEmitter, Input, OnInit, OnChanges, SimpleChanges, HostListener } from '@angular/core';

export interface SearchFilter {
  searchTerm: string;
  selectedCategory: string;
  priceMin: number | null;
  priceMax: number | null;
}

@Component({
    selector: 'app-product-filter',
    templateUrl: './product-filter.component.html',
    styleUrls: ['./product-filter.component.css'],
    standalone: false
})
export class ProductFilterComponent implements OnInit, OnChanges {
  @Output() filterChanged = new EventEmitter<SearchFilter>();

  @Input() searchTerm: string = '';
  @Input() selectedCategory: string = '';
  @Input() categories: string[] = ['cpu', 'gpu', 'ram'];
  @Input() priceMin: number | null = null;
  @Input() priceMax: number | null = null;

  onPartSelected!: {};
  constructor() {}

  ngOnInit() {
    if (!this.categories || this.categories.length === 0) {
      this.categories = [];
    }
    this.searchTerm = '';
    this.selectedCategory = '';
    this.priceMin = null;
    this.priceMax = null;
  }

  ngOnChanges(changes:any) {
   console.log('Changes detected in ProductFilterComponent:', changes);
  }

  applyFilter() {
    console.log('Applying filter with values:', {
      searchTerm: this.searchTerm,
      selectedCategory: this.selectedCategory,
      priceMin: this.priceMin,
      priceMax: this.priceMax
    });
    this.filterChanged.emit({
      searchTerm: this.searchTerm,
      selectedCategory: this.selectedCategory,
      priceMin: this.priceMin,
      priceMax: this.priceMax
    });
  }

  resetFilter() {
    this.searchTerm = '';
    this.selectedCategory = '';
    this.priceMin = null;
    this.priceMax = null;
    this.applyFilter();
  }
}
