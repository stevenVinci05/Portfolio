#!/usr/bin/env python3
"""
Test script per verificare la route project_code
"""

from app import app
from models import Project

def test_project_code_route():
    """Testa la route project_code"""
    with app.test_client() as client:
        try:
            # Test con un ID di progetto valido (se esistono progetti)
            with app.app_context():
                projects = Project.query.all()
                if projects:
                    project_id = projects[0].id
                    print(f"Testing route with project ID: {project_id}")
                    
                    response = client.get(f'/project/{project_id}/code')
                    print(f"Status code: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✅ Route funziona correttamente!")
                        print(f"Response length: {len(response.data)} bytes")
                        
                        # Verifica che il contenuto contenga elementi del template
                        content = response.data.decode('utf-8')
                        if 'project.title' in content or 'Visualizzazione del codice' in content:
                            print("✅ Template viene renderizzato correttamente!")
                        else:
                            print("⚠️ Template potrebbe non essere renderizzato correttamente")
                    else:
                        print(f"❌ Route restituisce status code: {response.status_code}")
                        
                else:
                    print("⚠️ Nessun progetto trovato nel database")
                    print("Testando con ID fittizio...")
                    
                    # Test con ID fittizio per vedere se la route esiste
                    response = client.get('/project/999/code')
                    print(f"Status code con ID fittizio: {response.status_code}")
                    
                    if response.status_code == 404:
                        print("✅ Route esiste ma progetto non trovato (corretto)")
                    else:
                        print(f"⚠️ Status code inaspettato: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore nel test: {e}")
            return False

if __name__ == '__main__':
    print("🧪 Test route project_code...")
    success = test_project_code_route()
    
    if success:
        print("\n✅ Test completato!")
    else:
        print("\n❌ Test fallito!") 