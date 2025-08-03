#!/usr/bin/env python3
"""
Script per migrare il database dal vecchio formato al nuovo formato
Vecchio: link e github separati
Nuovo: github_repo unico
"""

from app import app, db
from models import Project

def migrate_database():
    """Migra i dati dal vecchio formato al nuovo"""
    with app.app_context():
        try:
            # Ottieni tutti i progetti
            projects = Project.query.all()
            
            print(f"Trovati {len(projects)} progetti da migrare...")
            
            for project in projects:
                print(f"Migrando progetto: {project.title}")
                
                # Se il progetto ha sia link che github, usa github come repository principale
                if hasattr(project, 'github') and hasattr(project, 'link'):
                    if project.github:
                        project.github_repo = project.github
                        print(f"  - Usato GitHub: {project.github}")
                    elif project.link:
                        project.github_repo = project.link
                        print(f"  - Usato Link come repository: {project.link}")
                    else:
                        project.github_repo = None
                        print(f"  - Nessun repository trovato")
                
                # Rimuovi i vecchi campi se esistono
                if hasattr(project, 'link'):
                    delattr(project, 'link')
                if hasattr(project, 'github'):
                    delattr(project, 'github')
            
            # Salva le modifiche
            db.session.commit()
            print("✅ Migrazione completata con successo!")
            
        except Exception as e:
            print(f"❌ Errore durante la migrazione: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_database() 