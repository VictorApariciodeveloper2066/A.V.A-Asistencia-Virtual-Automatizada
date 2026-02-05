from flask import Blueprint, request, session, jsonify
from backend.models import User, Course, Asistencia, User_course
from backend.extensions import db
from sqlalchemy import or_
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Allow users to login with either username or email
    user = User.query.filter(or_(User.username == username, User.email == username)).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    session['username'] = user.username

    return jsonify({
        "message": "Login successful",
        "user": {
            "username": user.username,
            "role": user.role
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password required"}), 400

    user_exists = User.query.filter_by(username=username).first()
    email_exists = User.query.filter_by(email=email).first()

    if user_exists:
        return jsonify({"error": "Username already exists"}), 409

    if email_exists:
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "user": {
            "username": new_user.username,
            "email": new_user.email
        }
    }), 201

# Nueva ruta para marcar asistencia

from datetime import datetime
from flask import Blueprint, request, session, jsonify
from backend.models import User, Course, Asistencia, User_course
from backend.extensions import db

# ... dentro de tu blueprint ...

@auth_bp.route('/marcar_asistencia', methods=['POST'])
def marcar_asistencia():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    course_id = data.get('course_id')
    user = User.query.filter_by(username=session['username']).first()
    course = Course.query.get(course_id)

    if not course:
        return jsonify({"error": "Curso no encontrado"}), 404

    # 1. Validar que el alumno está inscrito en este curso
    inscrito = db.session.query(User_course).filter_by(user_id=user.id, course_id=course_id).first()
    if not inscrito:
        return jsonify({"error": "No estás inscrito en este curso"}), 403

    # 2. Validar Horario
    now = datetime.now()
    current_time = now.time()
    current_day = now.weekday() + 1  # 1=Lunes, etc.

    if current_day != course.dia:
        return jsonify({"error": "Hoy no es el día de esta clase"}), 400

    if not (course.start_time <= current_time <= course.end_time):
        return jsonify({"error": "Fuera del horario de clase"}), 400

    # 3. Evitar duplicados el mismo día
    exists = Asistencia.query.filter_by(user_id=user.id, course_id=course_id, date=now.date()).first()
    if exists:
        return jsonify({"error": "Ya marcaste asistencia hoy"}), 409

    # 4. Registrar Asistencia
    nueva_asistencia = Asistencia(
        user_id=user.id,
        course_id=course.id,
        date=now.date(),
        time=current_time,
        state="Presente"
    )
    
    db.session.add(nueva_asistencia)
    db.session.commit()

    return jsonify({"message": "Asistencia registrada con éxito"}), 201