import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    title: 'Rivelune Immobilier, assistant (démo)',
    loadComponent: () =>
      import('./features/assistant/assistant-page').then((m) => m.AssistantPage),
  },
  {
    path: 'comment-ca-marche',
    title: 'Comment ça marche, assistant IA pour agences',
    loadComponent: () =>
      import('./features/how-it-works/how-it-works-page').then((m) => m.HowItWorksPage),
  },
  { path: '**', redirectTo: '' },
];
