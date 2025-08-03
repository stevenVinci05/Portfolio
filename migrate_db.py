#!/usr/bin/env python3
"""
Script per migrare il database dal vecchio formato al nuovo formato
Vecchio: link e github separati
Nuovo: github_repo unico
"""

import sqlite3
import os
from app import app, db
from models import Project

def migrate_database():
    """Migra i dati dal vecchio formato al nuovo"""
    db_path = 'instance/portfolio.db'
    
    if not os.path.exists(db_path):
        print("❌ Database non trovato. Creando nuovo database...")
        with app.app_context():
            db.create_all()
            print("✅ Database creato con successo!")
        return
    
    print("🔄 Iniziando migrazione del database...")
    
    # Connessione diretta al database per le operazioni di schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verifica se la colonna github_repo esiste già
        cursor.execute("PRAGMA table_info(project)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'github_repo' in columns:
            print("✅ La colonna github_repo esiste già. Aggiornando i dati...")
        else:
            print("📝 Aggiungendo la colonna github_repo...")
            cursor.execute("ALTER TABLE project ADD COLUMN github_repo VARCHAR(255)")
            print("✅ Colonna github_repo aggiunta con successo!")
        
        # Ottieni tutti i progetti esistenti
        cursor.execute("SELECT id, title, link, github FROM project")
        projects = cursor.fetchall()
        
        print(f"📊 Trovati {len(projects)} progetti da migrare...")
        
        for project_id, title, link, github in projects:
            print(f"🔄 Migrando progetto: {title}")
            
            # Determina il repository GitHub da usare
            github_repo = None
            if github:
                github_repo = github
                print(f"  - Usato GitHub: {github}")
            elif link:
                github_repo = link
                print(f"  - Usato Link come repository: {link}")
            else:
                print(f"  - Nessun repository trovato")
            
            # Aggiorna il progetto con il nuovo campo
            cursor.execute(
                "UPDATE project SET github_repo = ? WHERE id = ?",
                (github_repo, project_id)
            )
        
        # Rimuovi le vecchie colonne se esistono
        if 'link' in columns:
            print("🗑️ Rimuovendo la colonna link...")
            # SQLite non supporta DROP COLUMN direttamente, quindi ricreiamo la tabella
            cursor.execute("""
                CREATE TABLE project_new (
                    id INTEGER PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL,
                    image VARCHAR(255),
                    github_repo VARCHAR(255),
                    category VARCHAR(50),
                    technologies TEXT,
                    featured BOOLEAN,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """)
            
            cursor.execute("""
                INSERT INTO project_new 
                SELECT id, title, description, image, github_repo, category, technologies, featured, created_at, updated_at 
                FROM project
            """)
            
            cursor.execute("DROP TABLE project")
            cursor.execute("ALTER TABLE project_new RENAME TO project")
            print("✅ Colonna link rimossa con successo!")
        
        if 'github' in columns:
            print("🗑️ Rimuovendo la colonna github...")
            # La colonna github è già stata rimossa nel passaggio precedente
            print("✅ Colonna github rimossa con successo!")
        
        # Commit delle modifiche
        conn.commit()
        print("✅ Migrazione completata con successo!")
        
        # Verifica finale
        cursor.execute("SELECT COUNT(*) FROM project")
        count = cursor.fetchone()[0]
        print(f"📊 Database finale: {count} progetti")
        
    except Exception as e:
        print(f"❌ Errore durante la migrazione: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def verify_migration():
    """Verifica che la migrazione sia stata completata correttamente"""
    with app.app_context():
        try:
            projects = Project.query.all()
            print(f"✅ Verifica completata: {len(projects)} progetti trovati")
            
            for project in projects:
                print(f"  - {project.title}: github_repo = {project.github_repo}")
                
        except Exception as e:
            print(f"❌ Errore nella verifica: {e}")

if __name__ == '__main__':
    print("🚀 Avvio migrazione database...")
    migrate_database()
    print("\n🔍 Verifica migrazione...")
    verify_migration()
    print("\n✅ Migrazione completata!") 