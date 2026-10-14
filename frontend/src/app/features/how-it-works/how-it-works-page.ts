import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { environment } from '../../../environments/environment';

/** Page du cadre développeur, pour le dirigeant d'agence : l'offre et le fonctionnement. */
@Component({
  selector: 'app-how-it-works-page',
  imports: [RouterLink],
  templateUrl: './how-it-works-page.html',
  styleUrl: './how-it-works-page.css',
})
export class HowItWorksPage {
  protected readonly contactUrl = environment.contactUrl;
  protected readonly repositoryUrl = environment.repositoryUrl;

  protected readonly capabilities = [
    {
      title: 'Répond depuis vos documents',
      text: "Catalogue, grille d'honoraires, procédures : il ne connaît que ce que l'entreprise lui donne.",
    },
    {
      title: 'Cite chaque source',
      text: "Document et page sous chaque réponse, avec l'extrait exact. Le client vérifie en un clic.",
    },
    {
      title: "N'invente pas",
      text: "Si l'information manque, il le dit et renvoie vers l'agence au lieu de deviner.",
    },
    {
      title: 'Reste dans son rôle',
      text: 'Il refuse poliment le hors-sujet et ignore les tentatives de détournement.',
    },
  ];

  protected readonly steps = [
    {
      title: 'La question arrive',
      text: 'Vérifiée, limitée en longueur et en fréquence avant tout appel payant.',
    },
    {
      title: 'Recherche des extraits',
      text: 'Par le sens de la phrase, et par les références exactes comme L-104 que la recherche par le sens rate.',
    },
    {
      title: 'Rédaction encadrée',
      text: "Le modèle reçoit les 6 meilleurs extraits et une consigne stricte : ces textes, rien d'autre.",
    },
    {
      title: 'Réponse et sources',
      text: 'Seules les sources réellement citées sont affichées, avec leur extrait.',
    },
  ];

  protected readonly safeguards = [
    { label: "Clé d'API", value: 'côté serveur uniquement', mono: false },
    { label: 'Par visiteur', value: '20 questions / heure', mono: true },
    { label: 'Pour toute la démo', value: '300 questions / jour', mono: true },
    { label: 'Longueur des réponses', value: 'plafonnée', mono: false },
    { label: 'Panne du fournisseur IA', value: 'nouvel essai automatique, message clair', mono: false },
  ];

  protected readonly stack = [
    { label: 'Serveur', value: 'Python, Flask, en couches' },
    { label: 'Interface', value: 'Angular' },
    { label: 'Modèle IA', value: 'Mistral, fournisseur français, remplaçable' },
    { label: 'Hébergement', value: 'Docker et nginx, avec mes autres démos' },
  ];
}
