#!/usr/bin/env python3
"""
Script per inizializzare il database su Render
"""

import os
import sys
from app import app, create_admin

def init_database():
    """Inizializza il database"""
    try:
        with app.app_context():
            print("🔄 Inizializzazione database...")
            create_admin()
            print("✅ Database inizializzato con successo!")
            return True
    except Exception as e:
        print(f"❌ Errore durante l'inizializzazione: {e}")
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1) 