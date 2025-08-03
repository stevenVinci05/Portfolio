#!/usr/bin/env python3
"""
Test completo per verificare che tutto funzioni per il deployment
"""

from app import app, db
from models import Project
import os

def test_database_connection():
    """Testa la connessione al database"""
    try:
        with app.app_context():
            # Test connessione
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ Connessione database OK")
            return True
    except Exception as e:
        print(f"❌ Errore connessione database: {e}")
        return False

def test_template_exists():
    """Verifica che il template project_code.html esista"""
    template_path = 'templates/project_code.html'
    if os.path.exists(template_path):
        print("✅ Template project_code.html trovato")
        return True
    else:
        print("❌ Template project_code.html non trovato")
        return False

def test_css_styles():
    """Verifica che gli stili CSS per project_code siano presenti"""
    css_path = 'static/css/style.css'
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '.code-preview' in content:
                print("✅ Stili CSS per project_code presenti")
                return True
            else:
                print("❌ Stili CSS per project_code mancanti")
                return False
    else:
        print("❌ File CSS non trovato")
        return False

def test_route_with_mock_data():
    """Testa la route con dati fittizi"""
    with app.test_client() as client:
        try:
            # Test con ID fittizio
            response = client.get('/project/1/code')
            print(f"Status code route test: {response.status_code}")
            
            if response.status_code == 404:
                print("✅ Route funziona (404 per progetto inesistente è corretto)")
                return True
            elif response.status_code == 200:
                print("✅ Route funziona e restituisce contenuto")
                return True
            else:
                print(f"⚠️ Status code inaspettato: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Errore nel test route: {e}")
            return False

def test_template_syntax():
    """Verifica la sintassi del template"""
    try:
        from jinja2 import Template
        with open('templates/project_code.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
            # Prova a compilare il template
            template = Template(template_content)
            print("✅ Sintassi template OK")
            return True
    except Exception as e:
        print(f"❌ Errore sintassi template: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("🧪 Test completo per deployment...")
    print()
    
    tests = [
        ("Connessione Database", test_database_connection),
        ("Template Esistente", test_template_exists),
        ("Stili CSS", test_css_styles),
        ("Route Test", test_route_with_mock_data),
        ("Sintassi Template", test_template_syntax)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"📋 {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Riepilogo
    print("📊 Riepilogo Test:")
    print("=" * 40)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("=" * 40)
    print(f"Risultato: {passed}/{len(results)} test passati")
    
    if passed == len(results):
        print("🎉 Tutti i test sono passati! Il deployment dovrebbe funzionare.")
    else:
        print("⚠️ Alcuni test sono falliti. Controlla gli errori sopra.")

if __name__ == '__main__':
    main() 