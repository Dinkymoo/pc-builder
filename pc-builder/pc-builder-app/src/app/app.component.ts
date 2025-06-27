import { Component } from '@angular/core';
import { GraphicCard } from './components/models/part';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css'],
    standalone: false
})
export class AppComponent {
  title = 'PC Builder UI';
  selectedGraphicCards: GraphicCard[] = [];

  constructor() {}

  onGraphicCardAdded(card: GraphicCard) {
    if (!this.selectedGraphicCards.some(c => c.id === card.id)) {
      this.selectedGraphicCards.push(card);
    }
  }
}