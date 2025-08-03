#!/usr/bin/env python3
"""
Test script per verificare la funzionalità di recupero codice da GitHub
"""

from app import app, extract_github_info, get_github_file_content, get_project_code_files
from models import Project

def test_github_info_extraction():
    """Testa l'estrazione delle informazioni GitHub"""
    print("🧪 Test estrazione info GitHub...")
    
    test_urls = [
        "https://github.com/stevenVinci05/Morfeo.git",
        "https://github.com/stevenVinci05/Morfeo",
        "https://github.com/username/repo-name",
        "https://github.com/user/project/",
        "invalid-url"
    ]
    
    for url in test_urls:
        username, repo = extract_github_info(url)
        print(f"URL: {url}")
        print(f"  Username: {username}")
        print(f"  Repository: {repo}")
        print()

def test_github_file_retrieval():
    """Testa il recupero di file da GitHub"""
    print("🧪 Test recupero file GitHub...")
    
    # Test con un repository pubblico noto
    username = "octocat"
    repo_name = "Hello-World"
    file_path = "README.md"
    
    content = get_github_file_content(username, repo_name, file_path)
    if content:
        print(f"✅ File {file_path} recuperato con successo!")
        print(f"Lunghezza contenuto: {len(content)} caratteri")
        print(f"Prime 100 caratteri: {content[:100]}...")
    else:
        print(f"❌ Impossibile recuperare il file {file_path}")

def test_project_code_files():
    """Testa la funzionalità completa per un progetto"""
    print("🧪 Test recupero file progetto...")
    
    with app.app_context():
        # Crea un progetto di test
        test_project = Project(
            title="Test Project",
            description="Un progetto di test",
            github_repo="https://github.com/stevenVinci05/Morfeo.git"
        )
        
        code_files = get_project_code_files(test_project)
        
        if code_files:
            print(f"✅ Trovati {len(code_files)} file di codice:")
            for filename, file_data in code_files.items():
                print(f"  - {filename} ({file_data['language']})")
                print(f"    Lunghezza: {len(file_data['content'])} caratteri")
        else:
            print("⚠️ Nessun file di codice trovato (potrebbe essere normale se il repo non ha i file cercati)")

def main():
    """Esegue tutti i test"""
    print("🚀 Test funzionalità GitHub Code Retrieval")
    print("=" * 50)
    
    test_github_info_extraction()
    test_github_file_retrieval()
    test_project_code_files()
    
    print("✅ Test completati!")

if __name__ == '__main__':
    main() 