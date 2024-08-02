import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from .extensions.db import db
from .models import dbSchema

@click.command('create-admin')
@click.argument('username')
@click.argument('password')
@with_appcontext
def create_admin(username, password):
    """Create a new admin user."""
    try:
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_admin = dbSchema.Admin(username=username, password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        click.echo(f"Admin user {username} created successfully.")
    except Exception as e:
        db.session.rollback()
        click.echo(f"Error creating admin user: {str(e)}")

def init_app(app):
    app.cli.add_command(create_admin)