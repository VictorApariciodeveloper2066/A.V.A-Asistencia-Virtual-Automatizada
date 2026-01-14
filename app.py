from flask import Flask, render_template, send_from_directory, request, flash, redirect, session, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from pathlib import Path
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os


# -----------------------------
# Carga de librerías y entorno
# -----------------------------
load_dotenv()

APP_DIR = Path(__file__).resolve().parent

# -----------------------------
# Configuración de la aplicación (templates / static)
# -----------------------------
app = Flask(
    __name__,
    template_folder=str(APP_DIR / 'Templates'),
    static_folder=str(APP_DIR / 'static' / 'assets'),  # serve files from static/assets
    static_url_path='/static'
)
CORS(app)


app.secret_key = os.getenv('FLASK_SECRET_KEY') or 'supersecretkey'

# -----------------------------
# Configuración de la base de datos (SQLAlchemy)
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------------
# Modelos (ORM)
# -----------------------------
class User(db.Model):
    # Campos del usuario
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    # Usa la columna `password` para mantener compatibilidad con la DB existente
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='student')
    career = db.Column(db.String(150), nullable=True) 

    def set_password(self, password):
        # Guarda el hash de la contraseña en la columna `password`
        self.password = generate_password_hash(password)

    def check_password(self, password):
        # Comprueba la contraseña contra el hash almacenado
        return check_password_hash(self.password, password)



# -----------------------------
# Rutas / Vistas
# -----------------------------
@app.route('/')
def index_root():
    # Página principal; si ya hay sesión, redirige al dashboard
    if "username" in session:
        return redirect('/dashboard')
    return render_template('index.html')

# -----------------------------
# Decoradores
# -----------------------------
def login_is_required(function):
    # Verifica si existe `google_id` en la sesión
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function(*args, **kwargs)

    return wrapper

@app.route('/dashboard')
def dashboard():
    if "username" in session:
        return render_template('dashboard.html', username=session['username'])
    return render_template('index.html')

# -----------------------------
# Autenticación
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # validate input
        if not username or not password:
            return render_template('login.html', error='Por favor ingresa usuario y contraseña', username=username)

        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('login.html', error='Usuario no encontrado', username=username)

        if not user.check_password(password):
            return render_template('login.html', error='Contraseña incorrecta', username=username)

        # success
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    # GET
    return render_template('login.html')


# -----------------------------
# Registro de usuarios
# -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', error="Usuario ya existe")
        else:
            new_user = User(username=username, email=request.form.get('email'))
            new_user.email = request.form.get('email')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            return redirect(url_for('dashboard'))
    # GET
    return render_template('register.html')
    


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index_root'))

@app.route('/predashboard.html', methods=['GET', 'POST'])
def predashboard():
    return render_template('predashboard.html')
# Register `auth` blueprint from routes.auth
try:
    from routes.auth import auth as auth_bp
    app.register_blueprint(auth_bp)
except Exception as _err:
    print('Warning: could not register routes.auth blueprint:', _err)
# -----------------------------
# Punto de entrada
# -----------------------------
if __name__ == '__main__':
    with app.app_context():
        # Crea las tablas definidas por los modelos si no existen
        db.create_all()
    app.run(debug=True)

