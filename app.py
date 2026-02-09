from backend.extensions import db, cors, migrate
from backend.extensions import mail
from backend.routes.auth import auth_bp
from flask import Flask
from backend.routes.auth import auth_bp
from backend.routes.front import front_bp
from dotenv import load_dotenv
from pathlib import Path
import os
import shutil

load_dotenv()
APP_DIR = Path(__file__).resolve().parent

def create_app():
    app = Flask(
        __name__,
        template_folder=str(APP_DIR / 'frontend' / 'templates'),
        static_folder=str(APP_DIR / 'frontend' / 'static' / 'assets'),
        static_url_path='/static'
    )

    # Ensure instance directory exists and prefer instance/user.db as primary DB.
    instance_dir = APP_DIR / 'instance'
    instance_dir.mkdir(parents=True, exist_ok=True)
    instance_db_path = instance_dir / 'users.db'
    # If instance DB doesn't exist but project users.db does, copy it into instance
    project_users_db = APP_DIR / 'users.db'
    try:
        if not instance_db_path.exists() and project_users_db.exists():
            shutil.copy2(project_users_db, instance_db_path)
            print(f"Copied {project_users_db} -> {instance_db_path}")
    except Exception as e:
        print('Failed copying users.db to instance:', e)

    # Load default config from config/default.py if available
    try:
        app.config.from_object('config.default.Config')
    except Exception:
        # fallback to environment variables below
        pass

    # Allow environment variables to override values and ensure secret is set
    app.secret_key = os.getenv('FLASK_SECRET_KEY', app.config.get('SECRET_KEY', 'supersecretkey'))

    # Database configuration (override if needed)
    # Use instance/user.db as primary DB path
    instance_db_path = APP_DIR / 'instance' / 'users.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{instance_db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure mail defaults come from env or config.default
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', app.config.get('MAIL_SERVER', 'smtp.gmail.com'))
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', app.config.get('MAIL_PORT', 587)))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', str(app.config.get('MAIL_USE_TLS', True))) in ('True', 'true', '1')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', app.config.get('MAIL_USERNAME'))
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', app.config.get('MAIL_PASSWORD'))
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config.get('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME')))
    # Mail configuration (can be set via environment variables)
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') in ('True', 'true', '1')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME'))

    db.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    # Ensure DB tables exist for this simple development environment
    try:
        with app.app_context():
            # Quick check: if 'user' table missing, create all tables
            inspector = None
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
            except Exception:
                inspector = None
            if inspector:
                tables = inspector.get_table_names()
                if 'user' not in tables:
                    db.create_all()
    except Exception:
        # if any error occurs here, log it but don't block app startup
        import traceback
        traceback.print_exc()

    app.register_blueprint(front_bp)
    app.register_blueprint(auth_bp)


    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
