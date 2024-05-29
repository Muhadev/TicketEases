import datetime
from flask.cli import FlaskGroup
from Website import create_app, db
from Website.models import User
from flask_migrate import Migrate

app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

cli = FlaskGroup(create_app=create_app)

# Add Flask-Migrate commands to the CLI
# cli.add_command('db', MigrateCommand)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("drop_db")
def drop_db():
    db.drop_all()
    db.session.commit()

@cli.command("create_admin")
def create_admin():
    """Creates the admin user."""
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash="admin",
        admin=True,
        confirmed=True,
        confirmed_on=datetime.datetime.now()
    )
    db.session.add(admin_user)
    db.session.commit()

if __name__ == '__main__':
    cli()
