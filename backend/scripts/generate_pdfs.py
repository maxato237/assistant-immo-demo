"""Génère les 4 PDF de l'agence fictive Rivelune Immobilier.

Chaque section commence par un titre : le découpage de l'indexation
s'appuie sur ces titres pour garder 1 bien = 1 morceau de texte.

Usage : python scripts/generate_pdfs.py
"""

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "documents"

AGENCY = "Rivelune Immobilier"
FOOTER = (
    "Rivelune Immobilier est une agence FICTIVE créée pour une démonstration. "
    "Tél. 04 00 00 00 00 - contact@rivelune-immo.example"
)

# (id, titre, sections) ; une section = (titre, [lignes])
DOCUMENTS = [
    (
        "catalogue-biens",
        "Catalogue des biens",
        [
            ("Biens à la location", [
                "Loyers indiqués hors charges, charges mensuelles en plus. "
                "Honoraires de location : voir le document Honoraires et frais.",
            ]),
            ("L-101 - Studio meublé - Lyon 7e (Guillotière)", [
                "Surface : 24 m². 3e étage sans ascenseur.",
                "Loyer : 560 € + 40 € de charges, soit 600 € charges comprises.",
                "Meublé. DPE : D. Pas d'extérieur.",
                "Disponible immédiatement.",
            ]),
            ("L-102 - T2 - Lyon 4e (Croix-Rousse)", [
                "Surface : 45 m². 2e étage sans ascenseur.",
                "Loyer : 720 € + 60 € de charges, soit 780 € charges comprises.",
                "Non meublé. DPE : C. Balcon de 4 m².",
                "Disponible le 1er novembre 2026.",
            ]),
            ("L-103 - T2 - Villeurbanne (Gratte-Ciel)", [
                "Surface : 50 m². 5e étage avec ascenseur.",
                "Loyer : 750 € + 40 € de charges, soit 790 € charges comprises.",
                "Non meublé. DPE : C. Place de parking en sous-sol incluse.",
                "Disponible le 15 novembre 2026.",
            ]),
            ("L-104 - T2 - Lyon 3e (Part-Dieu)", [
                "Surface : 48 m². 6e étage avec ascenseur.",
                "Loyer : 850 € + 75 € de charges, soit 925 € charges comprises.",
                "Non meublé. DPE : B. Balcon et cave.",
                "Disponible immédiatement.",
            ]),
            ("L-105 - T3 - Lyon 2e (Confluence)", [
                "Surface : 68 m². 4e étage avec ascenseur.",
                "Loyer : 1 150 € + 110 € de charges, soit 1 260 € charges comprises.",
                "Non meublé. DPE : A. Terrasse de 12 m² et place de parking.",
                "Visite virtuelle disponible. Disponible le 1er décembre 2026.",
            ]),
            ("L-106 - T4 - Lyon 8e (Monplaisir)", [
                "Surface : 85 m². Rez-de-chaussée.",
                "Loyer : 1 290 € + 120 € de charges, soit 1 410 € charges comprises.",
                "Non meublé. DPE : D. Jardin privatif de 30 m².",
                "Disponible le 1er novembre 2026.",
            ]),
            ("Biens à la vente", [
                "Prix affichés honoraires d'agence inclus, à la charge du vendeur.",
            ]),
            ("V-201 - T3 - Lyon 6e (Brotteaux)", [
                "Surface : 72 m². 3e étage avec ascenseur.",
                "Prix : 395 000 €. Charges de copropriété : 210 € par mois.",
                "DPE : C. Balcon et cave.",
            ]),
            ("V-202 - Maison 5 pièces - Écully", [
                "Surface : 130 m² sur un terrain de 600 m².",
                "Prix : 690 000 €. DPE : C. Garage double.",
                "Visite virtuelle disponible.",
            ]),
            ("V-203 - T2 - Lyon 7e (Jean Macé)", [
                "Surface : 42 m². 2e étage sans ascenseur.",
                "Prix : 219 000 €. Charges de copropriété : 95 € par mois. DPE : D.",
                "Vendu loué : locataire en place, loyer actuel 690 € charges comprises.",
            ]),
            ("V-204 - T4 - Caluire-et-Cuire", [
                "Surface : 92 m². Dernier étage avec ascenseur.",
                "Prix : 449 000 €. Charges de copropriété : 260 € par mois.",
                "DPE : B. Terrasse et 2 places de parking.",
            ]),
        ],
    ),
    (
        "honoraires-et-frais",
        "Honoraires et frais",
        [
            ("Honoraires de location (à la charge du locataire)", [
                "Lyon et Villeurbanne sont en zone tendue. Nos honoraires respectent "
                "les plafonds de la loi ALUR.",
                "Visite, constitution du dossier et rédaction du bail : 10 € TTC par m² "
                "de surface habitable.",
                "État des lieux d'entrée : 3 € TTC par m² de surface habitable.",
                "Exemple : pour un logement de 50 m², 500 € + 150 €, soit 650 € TTC au total.",
                "Aucun autre frais de dossier n'est demandé au locataire.",
            ]),
            ("Dépôt de garantie", [
                "Logement vide : 1 mois de loyer hors charges.",
                "Logement meublé : 2 mois de loyer hors charges.",
                "Le dépôt de garantie, les honoraires et le premier loyer sont réglés "
                "à la signature du bail.",
            ]),
            ("Honoraires de vente (à la charge du vendeur)", [
                "Honoraires inclus dans le prix affiché.",
                "Prix jusqu'à 200 000 € : 6 % TTC.",
                "Prix de 200 001 € à 400 000 € : 5 % TTC.",
                "Prix au-delà de 400 000 € : 4 % TTC.",
                "L'estimation d'un bien est gratuite et sans engagement.",
            ]),
            ("Gestion locative (pour les propriétaires)", [
                "Honoraires de gestion : 7 % TTC des loyers et charges encaissés.",
                "Garantie loyers impayés en option : 2,5 % TTC des loyers et charges.",
                "Service proposé à Lyon et à Villeurbanne uniquement.",
            ]),
        ],
    ),
    (
        "visites-et-candidature",
        "Visites et dossier de candidature",
        [
            ("Organiser une visite", [
                "Les visites se font uniquement sur rendez-vous, du lundi au samedi, "
                "par téléphone au 04 00 00 00 00 ou par le formulaire de contact du site.",
                "Pour les biens très demandés, des visites groupées peuvent être organisées.",
                "Une visite virtuelle est disponible pour le L-105 et le V-202.",
            ]),
            ("Pièces du dossier de location", [
                "Pièce d'identité en cours de validité.",
                "Les 3 derniers bulletins de salaire.",
                "Contrat de travail ou attestation de l'employeur.",
                "Dernier avis d'imposition.",
                "Justificatif de domicile actuel : 3 dernières quittances de loyer "
                "ou attestation d'hébergement.",
                "Étudiants : certificat de scolarité et dossier d'un garant.",
                "Indépendants : 2 derniers bilans ou attestation de l'expert-comptable.",
                "Les dossiers DossierFacile sont acceptés.",
                "Conformément à la loi, nous ne demandons jamais de relevés bancaires "
                "ni de photo d'identité.",
            ]),
            ("Revenus et garant", [
                "Revenus nets demandés : au moins 3 fois le loyer charges comprises.",
                "Sinon, un garant est nécessaire : personne physique (mêmes pièces que le "
                "locataire) ou garantie Visale d'Action Logement, que nous acceptons.",
            ]),
            ("Réponse et signature du bail", [
                "Réponse sous 72 heures ouvrées après réception d'un dossier complet.",
                "Signature du bail en agence ou par signature électronique.",
            ]),
        ],
    ),
    (
        "faq-agence",
        "Questions fréquentes sur l'agence",
        [
            ("Horaires d'ouverture", [
                "Du lundi au vendredi : 9 h - 12 h 30 et 14 h - 19 h.",
                "Le samedi : 9 h 30 - 17 h sans interruption.",
                "Fermé le dimanche et les jours fériés.",
            ]),
            ("Nous contacter", [
                "Téléphone : 04 00 00 00 00.",
                "Email : contact@rivelune-immo.example. Réponse sous 24 heures ouvrées.",
                "Agence située à Lyon 6e. Accueil en français et en anglais.",
            ]),
            ("Zones couvertes", [
                "Location et vente : Lyon (tous les arrondissements), Villeurbanne, "
                "Caluire-et-Cuire, Écully et Tassin-la-Demi-Lune.",
                "Gestion locative : Lyon et Villeurbanne uniquement.",
            ]),
            ("Faire estimer son bien", [
                "Estimation gratuite et sans engagement, en agence ou à domicile.",
                "Avis de valeur écrit remis sous 48 heures.",
            ]),
        ],
    ),
]


def build_pdf(doc_id: str, title: str, sections: list) -> Path:
    styles = getSampleStyleSheet()
    path = OUT_DIR / f"{doc_id}.pdf"
    doc = SimpleDocTemplate(
        str(path), pagesize=A4, title=title, author=AGENCY,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    story = [
        Paragraph(AGENCY, styles["Title"]),
        Paragraph(title, styles["Heading1"]),
        Spacer(1, 0.4 * cm),
    ]
    for heading, lines in sections:
        story.append(Paragraph(heading, styles["Heading2"]))
        story.extend(Paragraph(line, styles["BodyText"]) for line in lines)
        story.append(Spacer(1, 0.3 * cm))
    story += [Spacer(1, 0.6 * cm), Paragraph(FOOTER, styles["Italic"])]
    doc.build(story)
    return path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for doc_id, title, sections in DOCUMENTS:
        print("généré :", build_pdf(doc_id, title, sections).name)


if __name__ == "__main__":
    main()
