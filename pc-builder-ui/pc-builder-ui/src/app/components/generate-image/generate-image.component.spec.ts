import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GenerateImageComponent } from './generate-image.component';

describe('GenerateImageComponent', () => {
  let component: GenerateImageComponent;
  let fixture: ComponentFixture<GenerateImageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GenerateImageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GenerateImageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
