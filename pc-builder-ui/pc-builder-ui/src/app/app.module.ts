import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { CommonModule } from '@angular/common';

import { AppComponent } from './app.component';
import { NavbarComponent } from './components/navbar/navbar.component';
import { PartSelectorComponent } from './components/part-selector/part-selector.component';
import { ProductFilterComponent } from './components/product-filter/product-filter.component';
import { BuildSummaryComponent } from './components/build-summary/build-summary.component';
import { CompatibilityCheckerComponent } from './components/compatibility-checker/compatibility-checker.component';
import { GenerateImageComponent } from './components/generate-image/generate-image.component';
import { ImageResultComponent } from './components/image-result/image-result.component';
import { FooterComponent } from './components/footer/footer.component';
import { PartCardComponent } from './components/part-card/part-card.component';

@NgModule({ declarations: [
        AppComponent,
        NavbarComponent,
        PartSelectorComponent,
        ProductFilterComponent,
        BuildSummaryComponent,
        CompatibilityCheckerComponent,
        GenerateImageComponent,
        ImageResultComponent,
        FooterComponent,
        PartCardComponent
    ],
    bootstrap: [AppComponent], imports: [BrowserModule,
        FormsModule,
        CommonModule], providers: [provideHttpClient(withInterceptorsFromDi())] })
export class AppModule { }