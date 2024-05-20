from flask.cli import FlaskGroup
from Website import create_app, db
from flask_migrate import Migrate

app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

cli = FlaskGroup(create_app=create_app)

# Add Flask-Migrate commands to the CLI
# cli.add_command('db', MigrateCommand)

if __name__ == '__main__':
    cli()
