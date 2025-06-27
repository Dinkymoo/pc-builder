import { Component, Input, OnInit } from '@angular/core';
import { GraphicCard } from '../models/part';

@Component({
  selector: 'app-build-summary',
  templateUrl: './build-summary.component.html',
  styleUrls: ['./build-summary.component.css'],
  standalone: false
})
export class BuildSummaryComponent implements OnInit {

  @Input() selectedGraphicCards: GraphicCard[] = [];
  constructor() { }

  ngOnInit(): void {
  }
}
