from ..extensions.db import db
from datetime import datetime

class BaseUser:
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

class User(BaseUser, db.Model):
    __tablename__ = 'users'
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.Integer, db.ForeignKey('admins.id'))

    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
class Admin(BaseUser, db.Model):
    __tablename__ = 'admins'
    deleted_users = db.relationship('User', backref='deleted_by_admin', foreign_keys=[User.deleted_by])

    def __repr__(self):
        return f'<Admin {self.username}>'