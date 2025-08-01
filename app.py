from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Project, ContactMessage
import os
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Configurazione Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
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

# Route principale - Homepage
@app.route('/')
def index():
    # Ottieni i progetti in evidenza dal database
    featured_projects = Project.query.filter_by(featured=True).order_by(Project.created_at.desc()).limit(3).all()
    return render_template('index.html', featured_projects=featured_projects)

# Route per la pagina Chi Sono
@app.route('/about')
def about():
    return render_template('about.html')

# Route per la pagina Progetti
@app.route('/projects')
def projects():
    projects_list = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=projects_list)

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
            link=request.form.get('link'),
            github=request.form.get('github'),
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
        project.link = request.form.get('link')
        project.github = request.form.get('github')
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
        db.create_all()
        
        # Crea admin se non esiste
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@portfolio.com',
                is_admin=True
            )
            admin.set_password('admin123')  # Cambia questa password!
            db.session.add(admin)
            db.session.commit()
            print("Admin creato: username='admin', password='admin123'")

if __name__ == '__main__':
    create_admin()  # Crea database e admin
    # Avvia il server per deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
