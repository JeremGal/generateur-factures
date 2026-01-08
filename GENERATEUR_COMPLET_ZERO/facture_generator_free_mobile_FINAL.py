#!/usr/bin/env python3
"""
Générateur de Factures Free Mobile - MÉTHODE SEARCH & REPLACE
✅ Cherche et remplace automatiquement (pas de coordonnées)
✅ Fond gris préservé (couleur exacte)
✅ Plus fiable sur tous les environnements
"""

import random
import os
import fitz  # PyMuPDF
from datetime import datetime, timedelta

class FactureGeneratorFreeRedact:
    def __init__(self, template_dir=None):
        if template_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(current_dir, "3.pdf"),
                "3.pdf",
                "/tmp/3.pdf",
                os.path.join(current_dir, "..", "3.pdf"),
            ]
            
            self.template_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.template_path = path
                    break
            
            if not self.template_path:
                raise FileNotFoundError("❌ Template 3.pdf introuvable !")
        else:
            self.template_path = os.path.join(template_dir, "3.pdf")
        
        self.template_name = "Free Mobile"
        
    def generate_numero_client(self):
        return f"{random.randint(1000000000, 9999999999)}"
    
    def generate_siret(self):
        return f"{random.randint(10000000000000, 99999999999999)}"
    
    def generate_identifiant(self):
        return f"{random.randint(1000000000, 9999999999)}"
    
    def generate_date_aleatoire(self):
        aujourd_hui = datetime.now()
        il_y_a_3_mois = aujourd_hui - timedelta(days=90)
        delta_jours = (aujourd_hui - il_y_a_3_mois).days
        jours_aleatoires = random.randint(0, delta_jours)
        date_aleatoire = il_y_a_3_mois + timedelta(days=jours_aleatoires)
        
        mois_fr = {
            1: 'janvier', 2: 'février', 3: 'mars', 4: 'avril',
            5: 'mai', 6: 'juin', 7: 'juillet', 8: 'août',
            9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'décembre'
        }
        
        return f"{date_aleatoire.day} {mois_fr[date_aleatoire.month]} {date_aleatoire.year}"
    
    def generate_prix(self):
        prix_ht = round(random.uniform(10.00, 50.00), 2)
        tva = round(prix_ht * 0.20, 2)
        ttc = round(prix_ht + tva, 2)
        
        return {
            'ht': f"{prix_ht:.2f}",
            'tva': f"{tva:.2f}",
            'ttc': f"{ttc:.2f}"
        }
    
    def generate_facture(self, data, output_path=None):
        """Génère une facture avec search & replace automatique"""
        
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"❌ Template introuvable : {self.template_path}")
        
        # Générer données
        if 'numero_client' not in data or not data['numero_client']:
            data['numero_client'] = self.generate_numero_client()
        if 'siret' not in data or not data['siret']:
            data['siret'] = self.generate_siret()
        if 'identifiant' not in data or not data['identifiant']:
            data['identifiant'] = self.generate_identifiant()
        
        date_facture = self.generate_date_aleatoire()
        data['date_facture'] = date_facture
        prix = self.generate_prix()
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "/tmp" if os.path.exists("/tmp") else "."
            output_path = os.path.join(output_dir, f"facture_{timestamp}.pdf")
        
        # Ouvrir PDF
        doc = fitz.open(self.template_path)
        if len(doc) > 1:
            doc.delete_pages(from_page=1, to_page=len(doc)-1)
        
        page = doc[0]
        replacements = []
        
        entreprise_value = data.get('entreprise') or data['nom_complet']
        adresse_complete = f"{data['adresse_ligne1']} {data.get('adresse_ligne2', '')}".strip()
        
        # Patterns à remplacer avec SEARCH & REPLACE
        patterns_map = [
            ("SOFTSAP CONSULTING", entreprise_value.upper(), False),
            ("Forfait Free 5G SOFTSAP CONSULTING", f"Forfait Free 5G {entreprise_value.upper()}", False),
            ("LAURENT GALLULA", data['nom_complet'].upper(), False),
            # Texte technique REMPLACÉ par l'adresse (pour réduire l'espace)
            ("BAT:1 ESC:2 ETG:1 PTE:38", adresse_complete.upper(), False),
            ("BAT:1ESC:2ETG:1PTE:38", "", False),
            # L'ancienne adresse devient la ville
            ("7 RUE DE BOULAINVILLIERS", f"{data['code_postal']} {data['ville']}".upper(), False),
            ("75016 PARIS", "", False),  # Supprimé car redondant
            ("0661412033", data['telephone'], False),
            ("26056885", data['identifiant'], False),
            ("28 octobre 2025", date_facture, False),
            # Prix avec fond gris
            ("13.33", prix['ht'], True),
            ("2.66", prix['tva'], True),
            ("15.99", prix['ttc'], True),
        ]
        
        for old_text, new_text, sur_fond_gris in patterns_map:
            # Chercher toutes les instances du texte
            text_instances = page.search_for(old_text)
            
            if text_instances:
                for inst in text_instances:
                    # Redacter (supprimer) l'ancien texte
                    if sur_fond_gris:
                        # Rectangle gris pour préserver le fond
                        page.add_redact_annot(inst, fill=(0.859, 0.859, 0.859))
                    else:
                        # Rectangle blanc
                        page.add_redact_annot(inst, fill=(1, 1, 1))
                
                # Appliquer les redactions
                page.apply_redactions()
                
                # Réécrire le nouveau texte si non vide
                if new_text:
                    text_instances = page.search_for(old_text)
                    if not text_instances:
                        # Le texte a été supprimé, on cherche dans le template original
                        doc_temp = fitz.open(self.template_path)
                        if len(doc_temp) > 1:
                            doc_temp.delete_pages(from_page=1, to_page=len(doc_temp)-1)
                        page_temp = doc_temp[0]
                        text_instances = page_temp.search_for(old_text)
                        doc_temp.close()
                    
                    if text_instances:
                        for inst in text_instances:
                            fontsize = inst.height * 0.90
                            text_point = fitz.Point(inst.x0, inst.y0 + inst.height * 0.8)
                            
                            page.insert_text(
                                text_point,
                                new_text,
                                fontsize=fontsize,
                                color=(0, 0, 0),
                                fontname="helv"
                            )
                
                replacements.append(f"{old_text[:30]} → {new_text[:30] if new_text else 'supprimé'}")
        
        # Sauvegarder
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        
        data['prix_ht'] = prix['ht']
        data['prix_tva'] = prix['tva']
        data['prix_ttc'] = prix['ttc']
        
        return output_path, self.template_name, replacements
