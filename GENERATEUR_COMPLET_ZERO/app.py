#!/usr/bin/env python3
"""
API Flask - Générateur Factures FINAL
✅ Validation téléphone/code postal
✅ Nettoyage automatique
✅ Interface complète
"""

from flask import Flask, request, send_file, jsonify, render_template_string
from flask_cors import CORS
import os
import sys
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from facture_generator_free_mobile_FINAL import FactureGeneratorFreeRedact

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = "/tmp/factures" if os.path.exists("/tmp") else "./factures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    generator = FactureGeneratorFreeRedact()
    GENERATOR_OK = True
except Exception as e:
    print(f"❌ Erreur : {e}")
    generator = None
    GENERATOR_OK = False

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Générateur de Factures Free Mobile</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; }
        .optional { color: #999; font-weight: normal; font-size: 12px; }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 8px;
            display: none;
        }
        .result.success {
            background: #d4edda;
            border: 2px solid #c3e6cb;
            color: #155724;
        }
        .result.error {
            background: #f8d7da;
            border: 2px solid #f5c6cb;
            color: #721c24;
        }
        .info-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }
        .info-box div {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }
        .info-box .total {
            font-weight: bold;
            font-size: 16px;
            padding-top: 10px;
            border-top: 2px solid #667eea;
            margin-top: 10px;
        }
        .date-info {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            border-radius: 6px;
            margin: 15px 0;
            font-weight: 600;
        }
        .download-btn {
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
        }
        .loading { display: none; text-align: center; margin-top: 20px; }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .hint { color: #999; font-size: 12px; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 Générateur de Factures</h1>
        <p class="subtitle">Free Mobile - Génération automatique</p>
        
        <form id="factureForm">
            <div class="form-group">
                <label>Nom complet *</label>
                <input type="text" name="nom_complet" required placeholder="Ex: DUPONT Marie">
            </div>
            
            <div class="form-group">
                <label>Entreprise <span class="optional">(optionnel)</span></label>
                <input type="text" name="entreprise" placeholder="Ex: DUPONT CONSULTING">
            </div>
            
            <div class="row">
                <div class="form-group">
                    <label>Téléphone *</label>
                    <input type="tel" name="telephone" required placeholder="0612345678">
                    <div class="hint">10 chiffres (espaces/tirets acceptés)</div>
                </div>
                
                <div class="form-group">
                    <label>SIRET <span class="optional">(auto)</span></label>
                    <input type="text" name="siret" placeholder="Auto-généré">
                </div>
            </div>
            
            <div class="form-group">
                <label>Adresse ligne 1 *</label>
                <input type="text" name="adresse_ligne1" required placeholder="10 Rue de la Paix">
            </div>
            
            <div class="form-group">
                <label>Adresse ligne 2 <span class="optional">(optionnel)</span></label>
                <input type="text" name="adresse_ligne2" placeholder="Appartement 5">
            </div>
            
            <div class="row">
                <div class="form-group">
                    <label>Code postal *</label>
                    <input type="text" name="code_postal" required placeholder="75001">
                    <div class="hint">5 chiffres</div>
                </div>
                <div class="form-group">
                    <label>Ville *</label>
                    <input type="text" name="ville" required placeholder="PARIS">
                </div>
            </div>
            
            <button type="submit">🚀 Générer la facture</button>
        </form>
        
        <div class="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #667eea;">Génération en cours...</p>
        </div>
        
        <div class="result" id="result"></div>
    </div>
    
    <script>
        const form = document.getElementById('factureForm');
        const result = document.getElementById('result');
        const loading = document.querySelector('.loading');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                if (value.trim()) data[key] = value.trim();
            }
            
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    
                    const dateFacture = response.headers.get('X-Date-Facture') || 'N/A';
                    const prixHT = response.headers.get('X-Prix-HT') || '0.00';
                    const prixTVA = response.headers.get('X-Prix-TVA') || '0.00';
                    const prixTTC = response.headers.get('X-Prix-TTC') || '0.00';
                    const identifiant = response.headers.get('X-Identifiant') || 'N/A';
                    
                    result.className = 'result success';
                    result.innerHTML = `
                        <strong>✅ Succès !</strong><br>
                        Facture générée avec succès !<br><br>
                        
                        <div class="date-info">
                            📅 Date : ${dateFacture}
                        </div>
                        
                        <div class="info-box">
                            <div><span>Prix HT :</span><span>${prixHT} €</span></div>
                            <div><span>TVA (20%) :</span><span>${prixTVA} €</span></div>
                            <div class="total"><span>Prix TTC :</span><span>${prixTTC} €</span></div>
                        </div>
                        
                        <small>Identifiant : ${identifiant}</small><br>
                        
                        <a href="${url}" download="facture.pdf" class="download-btn">
                            📥 Télécharger la facture
                        </a>
                    `;
                    result.style.display = 'block';
                    form.reset();
                } else {
                    const error = await response.json();
                    result.className = 'result error';
                    result.innerHTML = `<strong>❌ Erreur</strong><br>${error.error || 'Erreur inconnue'}`;
                    result.style.display = 'block';
                }
            } catch (error) {
                result.className = 'result error';
                result.innerHTML = `<strong>❌ Erreur</strong><br>${error.message}`;
                result.style.display = 'block';
            } finally {
                loading.style.display = 'none';
            }
        });
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate_facture():
    try:
        if not GENERATOR_OK or generator is None:
            return jsonify({'error': 'Générateur non initialisé'}), 500
        
        data = request.json
        
        # Valider champs requis
        required = ['nom_complet', 'telephone', 'adresse_ligne1', 'code_postal', 'ville']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'Champ requis : {field}'}), 400
        
        # NETTOYER LE TÉLÉPHONE (enlever espaces, tirets, points)
        tel = data['telephone']
        tel = re.sub(r'[\s\-\.\(\)]', '', tel)
        
        if not tel.isdigit():
            return jsonify({'error': 'Téléphone doit contenir uniquement des chiffres'}), 400
        
        if len(tel) != 10:
            return jsonify({'error': f'Téléphone invalide : {len(tel)} chiffres (10 requis)'}), 400
        
        data['telephone'] = tel
        
        # NETTOYER LE CODE POSTAL
        code_postal = data['code_postal']
        code_postal = re.sub(r'\s', '', code_postal)
        
        if not code_postal.isdigit() or len(code_postal) != 5:
            return jsonify({'error': 'Code postal invalide (5 chiffres requis)'}), 400
        
        data['code_postal'] = code_postal
        
        # Générer
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"facture_{timestamp}.pdf"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        file_path, template_name, replacements = generator.generate_facture(data, output_path)
        
        # Envoyer
        response = send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
        response.headers['X-Filename'] = filename
        response.headers['X-Date-Facture'] = data.get('date_facture', 'N/A')
        response.headers['X-Prix-HT'] = data.get('prix_ht', '0.00')
        response.headers['X-Prix-TVA'] = data.get('prix_tva', '0.00')
        response.headers['X-Prix-TTC'] = data.get('prix_ttc', '0.00')
        response.headers['X-Identifiant'] = data.get('identifiant', 'N/A')
        
        return response
        
    except Exception as e:
        print(f"Erreur : {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok' if GENERATOR_OK else 'error'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
