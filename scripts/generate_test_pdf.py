"""Genere un PDF de test simulant un AO public avec texte extractible."""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sys


def generate_test_pdf(output_path: str = "test_ao.pdf"):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    text_content = """
APPEL D'OFFRES OUVERT

Objet : Construction d'un immeuble de bureaux R+5
Reference : 2024-AO-001234
Date limite de depot : 15/06/2025 12:00
Date de publication : 15/04/2025

Maitre d'ouvrage : Conseil Regional d'Ile-de-France
Code CPV : 45210000 (Travaux de construction de batiments)
Lieu d'execution : Paris (75), Ile-de-France

Montant estime : 2 450 000 EUR TTC
Duree du marche : 18 mois

Description :
Le present marche a pour objet la construction d'un immeuble de bureaux
 de 5 etages avec sous-sol, d'une surface de plancher de 3 500 m2.
Les prestations comprennent :
- Gros oeuvre
- Second oeuvre
- Electricite et plomberie
- Chauffage, ventilation, climatisation

Criteres d'attribution :
- Prix : 60 %
- Valeur technique : 30 %
- Delai d'execution : 10 %

Conditions de participation :
- Capacite professionnelle justifiee (references similaires)
- Garanties decennales et responsabilite civile a jour
- Certifications ISO 9001 et ISO 14001 souhaitees

Contact : marches.publics@iledefrance.fr
Tel : 01 42 75 60 00
    """
    y = height - 50
    for line in text_content.strip().split('\n'):
        c.drawString(50, y, line.strip())
        y -= 14
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()
    print(f"PDF genere : {output_path}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "test_ao.pdf"
    generate_test_pdf(output)
