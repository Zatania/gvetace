import click
from flask.cli import AppGroup
from werkzeug.security import generate_password_hash

from core.auth.models import User

group = AppGroup("admin", help="Run administrative commands.")


@group.command(help="Create an administrator user.")
def create_user():
    User.create(
        first_name="Administrator",
        email="admin@asscat.com",
        password=generate_password_hash("password"),
        role=1,
    )
    click.echo("\nAdmin user created successfully.\n")
