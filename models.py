from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), default='project-default.jpg')
    link = db.Column(db.String(255))
    github = db.Column(db.String(255))
    category = db.Column(db.String(50), default='web')
    technologies = db.Column(db.Text)  # JSON string
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_technologies_list(self):
        """Convert technologies string to list"""
        if self.technologies:
            return self.technologies.split(',')
        return []

    def set_technologies_list(self, tech_list):
        """Convert list to technologies string"""
        self.technologies = ','.join(tech_list) if tech_list else ''

    def to_dict(self):
        """Convert project to dictionary for JSON response"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'link': self.link,
            'github': self.github,
            'category': self.category,
            'technologies': self.get_technologies_list(),
            'featured': self.featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert message to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stelle
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)  # Solo recensioni approvate vengono mostrate
    
    def to_dict(self):
        """Convert review to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'approved': self.approved
        } 