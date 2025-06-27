import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CompatibilityCheckerComponent } from './compatibility-checker.component';

describe('CompatibilityCheckerComponent', () => {
  let component: CompatibilityCheckerComponent;
  let fixture: ComponentFixture<CompatibilityCheckerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CompatibilityCheckerComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CompatibilityCheckerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
