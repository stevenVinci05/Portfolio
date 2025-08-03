from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Project, ContactMessage, Review
import os
import requests
import re
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Configurazione Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///portfolio.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Inizializzazione Database e Login Manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Per favore effettua il login per accedere a questa pagina.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_email_address(email):
    """
    Verifica se l'email è valida e se il dominio esiste
    """
    try:
        # Verifica formato email e dominio
        valid = validate_email(email, check_deliverability=True)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)

def extract_github_info(github_url):
    """
    Estrae username e repository name da un URL GitHub
    """
    if not github_url:
        return None, None
    
    # Pattern per diversi formati di URL GitHub
    patterns = [
        r'github\.com/([^/]+)/([^/]+)\.git$',
        r'github\.com/([^/]+)/([^/]+)/?$',
        r'github\.com/([^/]+)/([^/]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, github_url)
        if match:
            username = match.group(1)
            repo_name = match.group(2)
            # Rimuovi .git se presente
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            return username, repo_name
    
    return None, None

def get_github_file_content(username, repo_name, file_path, branch='main'):
    """
    Recupera il contenuto di un file da GitHub usando l'API pubblica
    """
    try:
        url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{file_path}"
        params = {'ref': branch}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('type') == 'file':
                import base64
                content = base64.b64decode(data['content']).decode('utf-8')
                return content
        elif response.status_code == 404:
            # Prova con 'master' se 'main' non funziona
            if branch == 'main':
                return get_github_file_content(username, repo_name, file_path, 'master')
        
        return None
    except Exception as e:
        print(f"Errore nel recupero del file {file_path}: {e}")
        return None

def get_project_code_files(project):
    """
    Recupera i file di codice principali dal repository del progetto
    """
    if not project.github_repo:
        return {}
    
    username, repo_name = extract_github_info(project.github_repo)
    if not username or not repo_name:
        return {}
    
    # Lista dei file da cercare (in ordine di priorità)
    file_patterns = [
        # Python
        'app.py', 'main.py', 'run.py', 'server.py',
        'requirements.txt', 'setup.py', 'config.py',
        # JavaScript/Node.js
        'package.json', 'index.js', 'app.js', 'server.js',
        # HTML/CSS
        'index.html', 'style.css', 'styles.css',
        # Altri
        'README.md', 'Dockerfile', '.env.example'
    ]
    
    code_files = {}
    
    for file_path in file_patterns:
        content = get_github_file_content(username, repo_name, file_path)
        if content:
            # Determina il linguaggio basato sull'estensione
            ext = file_path.split('.')[-1] if '.' in file_path else ''
            language_map = {
                'py': 'python',
                'js': 'javascript',
                'html': 'html',
                'css': 'css',
                'md': 'markdown',
                'json': 'json',
                'txt': 'text'
            }
            language = language_map.get(ext, 'text')
            
            code_files[file_path] = {
                'content': content,
                'language': language
            }
            
            # Limita a 5 file per non sovraccaricare la pagina
            if len(code_files) >= 5:
                break
    
    return code_files

# Route principale - Homepage
@app.route('/')
def index():
    try:
        # Verifica se il database esiste
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        
        # Ottieni i progetti in evidenza dal database
        featured_projects = Project.query.filter_by(featured=True).order_by(Project.created_at.desc()).limit(3).all()
        return render_template('index.html', featured_projects=featured_projects)
    except Exception as e:
        print(f"Errore nella homepage: {e}")
        # Se c'è un errore, prova a inizializzare il database
        try:
            create_admin()
            featured_projects = Project.query.filter_by(featured=True).order_by(Project.created_at.desc()).limit(3).all()
            return render_template('index.html', featured_projects=featured_projects)
        except Exception as e2:
            print(f"Errore critico: {e2}")
            return render_template('index.html', featured_projects=[])

# Route per la pagina Chi Sono
@app.route('/about')
def about():
    return render_template('about.html')

# Route per la pagina Progetti
@app.route('/projects')
def projects():
    try:
        # Verifica se il database esiste
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        
        projects_list = Project.query.order_by(Project.created_at.desc()).all()
        return render_template('projects.html', projects=projects_list)
    except Exception as e:
        print(f"Errore nella pagina progetti: {e}")
        # Se c'è un errore, prova a inizializzare il database
        try:
            create_admin()
            projects_list = Project.query.order_by(Project.created_at.desc()).all()
            return render_template('projects.html', projects=projects_list)
        except Exception as e2:
            print(f"Errore critico: {e2}")
            return render_template('projects.html', projects=[])

# Route per la pagina Contatti
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Gestione del form di contatto
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validazione dei campi obbligatori
        if not name or not email or not subject or not message:
            flash('Tutti i campi sono obbligatori!', 'error')
            return render_template('contact.html')
        
        # Verifica email
        is_valid_email, email_result = validate_email_address(email)
        if not is_valid_email:
            flash(f'Email non valida: {email_result}', 'error')
            return render_template('contact.html')
        
        # Salva il messaggio nel database
        contact_message = ContactMessage(
            name=name,
            email=email_result,  # Usa l'email normalizzata
            subject=subject,
            message=message
        )
        
        db.session.add(contact_message)
        db.session.commit()
        
        flash('Grazie per il tuo messaggio! Ti risponderò presto.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# Route per visualizzare il codice di un progetto
@app.route('/project/<int:project_id>/code')
def project_code(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Recupera i file di codice dal repository GitHub
    code_files = get_project_code_files(project)
    
    return render_template('project_code.html', project=project, code_files=code_files)

# Route per la pagina Recensioni
@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        # Gestione del form di recensione
        name = request.form.get('name', '').strip()
        rating = request.form.get('rating', '').strip()
        comment = request.form.get('comment', '').strip()
        
        # Validazione dei campi obbligatori
        if not name or not rating or not comment:
            flash('Tutti i campi sono obbligatori!', 'error')
            return render_template('reviews.html', reviews=[], average_rating=0)
        
        # Validazione rating (1-5)
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                flash('Il rating deve essere tra 1 e 5 stelle!', 'error')
                return render_template('reviews.html', reviews=[], average_rating=0)
        except ValueError:
            flash('Rating non valido!', 'error')
            return render_template('reviews.html', reviews=[], average_rating=0)
        
        # Salva la recensione nel database
        review = Review(
            name=name,
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Grazie per la tua recensione! Sarà visibile dopo l\'approvazione.', 'success')
        return redirect(url_for('reviews'))
    
    # Ottieni recensioni approvate per la visualizzazione
    try:
        approved_reviews = Review.query.filter_by(approved=True).order_by(Review.created_at.desc()).all()
        
        # Calcola la media delle stelle
        if approved_reviews:
            total_rating = sum(review.rating for review in approved_reviews)
            average_rating = round(total_rating / len(approved_reviews), 1)
        else:
            average_rating = 0
        
        return render_template('reviews.html', reviews=approved_reviews, average_rating=average_rating)
    except Exception as e:
        print(f"Errore nella pagina recensioni: {e}")
        return render_template('reviews.html', reviews=[], average_rating=0)

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenziali non valide!', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logout effettuato con successo!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/dashboard.html', projects=projects)

@app.route('/admin/projects/new', methods=['GET', 'POST'])
@login_required
def admin_new_project():
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Validazione dei campi obbligatori
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title or not description:
            flash('Titolo e descrizione sono obbligatori!', 'error')
            return render_template('admin/project_form.html')
        
        project = Project(
            title=title,
            description=description,
            image=request.form.get('image', 'project-default.jpg'),
            github_repo=request.form.get('github_repo'),
            category=request.form.get('category', 'web'),
            featured=bool(request.form.get('featured'))
        )
        # Gestione tecnologie con pulizia degli spazi
        technologies = request.form.get('technologies', '').strip()
        if technologies:
            tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
            project.set_technologies_list(tech_list)
        else:
            project.set_technologies_list([])
        
        db.session.add(project)
        db.session.commit()
        flash('Progetto creato con successo!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/project_form.html')

@app.route('/admin/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_project(project_id):
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.image = request.form.get('image')
        project.github_repo = request.form.get('github_repo')
        project.category = request.form.get('category')
        project.featured = bool(request.form.get('featured'))
        # Gestione tecnologie con pulizia degli spazi
        technologies = request.form.get('technologies', '').strip()
        if technologies:
            tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
            project.set_technologies_list(tech_list)
        else:
            project.set_technologies_list([])
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Progetto aggiornato con successo!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/project_form.html', project=project)

@app.route('/admin/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def admin_delete_project(project_id):
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Progetto eliminato con successo!', 'success')
    return redirect(url_for('admin_dashboard'))

# Admin Messages Routes
@app.route('/admin/messages')
@login_required
def admin_messages():
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

# Admin Users Routes
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    # Solo Sterben può gestire gli utenti
    if current_user.username != 'Sterben':
        flash('Solo Sterben può gestire gli utenti admin!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
def admin_new_user():
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    # Solo Sterben può creare nuovi admin
    if current_user.username != 'Sterben':
        flash('Solo Sterben può creare nuovi utenti admin!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validazione
        if not username or not email or not password:
            flash('Tutti i campi sono obbligatori!', 'error')
            return render_template('admin/user_form.html')
        
        if password != confirm_password:
            flash('Le password non coincidono!', 'error')
            return render_template('admin/user_form.html')
        
        # Verifica se l'username esiste già
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username già esistente!', 'error')
            return render_template('admin/user_form.html')
        
        # Verifica email
        is_valid_email, email_result = validate_email_address(email)
        if not is_valid_email:
            flash(f'Email non valida: {email_result}', 'error')
            return render_template('admin/user_form.html')
        
        # Crea nuovo admin
        new_admin = User(
            username=username,
            email=email_result,
            is_admin=True
        )
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        flash('Nuovo admin creato con successo!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html')

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    # Solo Sterben può eliminare utenti
    if current_user.username != 'Sterben':
        flash('Solo Sterben può eliminare utenti admin!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Non permettere di eliminare se stesso
        if user.id == current_user.id:
            flash('Non puoi eliminare il tuo account!', 'error')
            return redirect(url_for('admin_users'))
        
        # Non permettere di eliminare Sterben
        if user.username == 'Sterben':
            flash('Non puoi eliminare l\'account Sterben!', 'error')
            return redirect(url_for('admin_users'))
        
        db.session.delete(user)
        db.session.commit()
        flash('Utente eliminato con successo!', 'success')
    except Exception as e:
        print(f"Errore durante l'eliminazione dell'utente: {e}")
        flash('Errore durante l\'eliminazione dell\'utente!', 'error')
    
    return redirect(url_for('admin_users'))

# Admin Reviews Routes
@app.route('/admin/reviews')
@login_required
def admin_reviews():
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/admin/reviews/<int:review_id>/approve', methods=['POST'])
@login_required
def admin_approve_review(review_id):
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    try:
        review = Review.query.get_or_404(review_id)
        review.approved = True
        db.session.commit()
        flash('Recensione approvata con successo!', 'success')
    except Exception as e:
        print(f"Errore durante l'approvazione della recensione: {e}")
        flash('Errore durante l\'approvazione della recensione!', 'error')
    
    return redirect(url_for('admin_reviews'))

@app.route('/admin/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
def admin_delete_review(review_id):
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    try:
        review = Review.query.get_or_404(review_id)
        db.session.delete(review)
        db.session.commit()
        flash('Recensione eliminata con successo!', 'success')
    except Exception as e:
        print(f"Errore durante l'eliminazione della recensione: {e}")
        flash('Errore durante l\'eliminazione della recensione!', 'error')
    
    return redirect(url_for('admin_reviews'))

@app.route('/admin/messages/<int:message_id>/read', methods=['POST'])
@login_required
def admin_mark_read(message_id):
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    message = ContactMessage.query.get_or_404(message_id)
    message.read = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def admin_delete_message(message_id):
    if not current_user.is_admin:
        flash('Accesso non autorizzato!', 'error')
        return redirect(url_for('index'))
    
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Messaggio eliminato con successo!', 'success')
    return redirect(url_for('admin_messages'))

# API Routes per AJAX
@app.route('/api/projects')
def api_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects])

@app.route('/api/messages')
def api_messages():
    messages = ContactMessage.query.all()
    return jsonify([message.to_dict() for message in messages])

# Route per inizializzare il database (solo per debug)
@app.route('/init-db')
def init_database():
    try:
        create_admin()
        return jsonify({'success': True, 'message': 'Database inizializzato con successo'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Route per gestire errori 404
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Route per gestire errori 500
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Funzione per creare il database e l'admin iniziale
def create_admin():
    with app.app_context():
        try:
            # Forza la creazione di tutte le tabelle
            db.drop_all()  # Rimuove tabelle esistenti
            db.create_all()  # Ricrea tutte le tabelle
            
            # Crea admin se non esiste
            admin = User.query.filter_by(username='Sterben').first()
            if not admin:
                admin = User(
                    username='Sterben',
                    email='admin@portfolio.com',
                    is_admin=True
                )
                admin.set_password('Ste@2025!')  # Credenziali personalizzate
                db.session.add(admin)
                db.session.commit()
                print("✅ Database creato e admin configurato: username='Sterben', password='Ste@2025!'")
            else:
                print("✅ Database già configurato")
        except Exception as e:
            print(f"❌ Errore durante la creazione del database: {e}")
            db.session.rollback()
            # Prova a creare solo le tabelle senza admin
            try:
                db.create_all()
                print("✅ Tabelle create senza admin")
            except Exception as e2:
                print(f"❌ Errore critico nella creazione tabelle: {e2}")

if __name__ == '__main__':
    create_admin()  # Crea database e admin
    # Avvia il server per deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
