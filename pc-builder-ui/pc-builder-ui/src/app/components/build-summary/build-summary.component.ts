import { Component, OnInit } from '@angular/core';
import { GraphicCard } from '../models/part';

@Component({
  selector: 'app-build-summary',
  templateUrl: './build-summary.component.html',
  styleUrls: ['./build-summary.component.css'],
  standalone: false
})
export class BuildSummaryComponent implements OnInit {

  selectedGraphicCards: GraphicCard[] = [];
  constructor() { }

  ngOnInit(): void {
  }

  onGraphicCardSelected(card: GraphicCard): void {
    this.selectedGraphicCards.push(card); // Add the selected card to the array
    console.log('selectedGraphicCards:', this.selectedGraphicCards); // Log when button is clicked
  }
}
