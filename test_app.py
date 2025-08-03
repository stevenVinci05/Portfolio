#!/usr/bin/env python3
"""
Test script per verificare che l'applicazione Flask funzioni correttamente
"""

from app import app, db
from models import Project

def test_database_connection():
    """Testa la connessione al database e le query"""
    with app.app_context():
        try:
            # Test query per tutti i progetti
            all_projects = Project.query.all()
            print(f"✅ Tutti i progetti: {len(all_projects)}")
            for project in all_projects:
                print(f"  - {project.title} (ID: {project.id})")
            
            # Test query per progetti in evidenza
            featured_projects = Project.query.filter_by(featured=True).all()
            print(f"✅ Progetti in evidenza: {len(featured_projects)}")
            for project in featured_projects:
                print(f"  - {project.title} (featured: {project.featured})")
            
            # Test accesso ai campi del modello
            if all_projects:
                project = all_projects[0]
                print(f"✅ Test campi modello:")
                print(f"  - title: {project.title}")
                print(f"  - description: {project.description[:50]}...")
                print(f"  - github_repo: {project.github_repo}")
                print(f"  - category: {project.category}")
                print(f"  - technologies: {project.get_technologies_list()}")
                print(f"  - featured: {project.featured}")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore nel test: {e}")
            return False

def test_routes():
    """Testa le route principali"""
    with app.test_client() as client:
        try:
            # Test homepage
            response = client.get('/')
            print(f"✅ Homepage status: {response.status_code}")
            
            # Test pagina progetti
            response = client.get('/projects')
            print(f"✅ Pagina progetti status: {response.status_code}")
            
            # Test route codice progetto (se esistono progetti)
            with app.app_context():
                projects = Project.query.all()
                if projects:
                    project_id = projects[0].id
                    response = client.get(f'/project/{project_id}/code')
                    print(f"✅ Route codice progetto status: {response.status_code}")
                else:
                    print("⚠️ Nessun progetto trovato per testare la route codice")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore nel test delle route: {e}")
            return False

if __name__ == '__main__':
    print("🧪 Avvio test applicazione...")
    print("\n1. Test connessione database:")
    db_success = test_database_connection()
    
    print("\n2. Test route:")
    routes_success = test_routes()
    
    if db_success and routes_success:
        print("\n✅ Tutti i test sono passati!")
        print("🎉 L'applicazione dovrebbe funzionare correttamente.")
    else:
        print("\n❌ Alcuni test sono falliti.")
        print("🔧 Controlla gli errori sopra.") 