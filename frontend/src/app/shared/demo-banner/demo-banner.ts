import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { environment } from '../../../environments/environment';

/** Bandeau du cadre développeur : rappelle que l'agence est fictive et mène au contact. */
@Component({
  selector: 'app-demo-banner',
  imports: [RouterLink],
  templateUrl: './demo-banner.html',
  styleUrl: './demo-banner.css',
})
export class DemoBanner {
  protected readonly contactUrl = environment.contactUrl;
}
