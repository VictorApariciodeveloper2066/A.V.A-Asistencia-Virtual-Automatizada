from flask import Blueprint, request, session, jsonify, redirect, url_for
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


@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('front.index'))


@auth_bp.route('/generate_code/<int:course_id>', methods=['POST'])
def generate_code(course_id):
    # local imports to avoid modifying top-level import list
    from datetime import datetime, date, timedelta
    import secrets, string

    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    user = User.query.filter_by(username=session['username']).first()
    if not user or user.role != 'teacher':
        return jsonify({"error": "Solo profesores pueden generar códigos"}), 403

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Curso no encontrado"}), 404

    # generate 5-char alphanumeric code
    alphabet = string.ascii_uppercase + string.digits
    new_code = ''.join(secrets.choice(alphabet) for _ in range(5))

    # set expiry at today's course end_time if available, otherwise 1 hour from now
    now = datetime.now()
    expires = None
    try:
        if course.end_time:
            expires = datetime.combine(date.today(), course.end_time)
            if expires < now:
                expires = now + timedelta(hours=1)
    except Exception:
        expires = now + timedelta(hours=1)

    course.session_code = new_code
    course.session_expires = expires
    db.session.commit()

    return jsonify({"code": new_code, "expires": expires.isoformat() if expires else None}), 200


@auth_bp.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    from datetime import datetime

    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json() or {}
    course_id = data.get('course_id')
    input_code = data.get('code')

    if not course_id or not input_code:
        return jsonify({"error": "course_id y code son requeridos"}), 400

    user = User.query.filter_by(username=session['username']).first()
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Curso no encontrado"}), 404

    # Verify enrollment
    inscrito = db.session.query(User_course).filter_by(user_id=user.id, course_id=course_id).first()
    if not inscrito:
        return jsonify({"error": "No estás inscrito en este curso"}), 403

    # Verify code
    if not course.session_code or course.session_code != input_code:
        return jsonify({"error": "Código incorrecto"}), 400

    now = datetime.now()
    # verify within expiry
    if course.session_expires and now > course.session_expires:
        return jsonify({"error": "El código ha expirado"}), 400

    # verify day/time
    try:
        current_day = now.weekday() + 1
        if current_day != course.dia:
            return jsonify({"error": "No es el día de la clase"}), 400
        current_time = now.time()
        if not (course.start_time <= current_time <= course.end_time):
            return jsonify({"error": "Fuera del horario de clase"}), 400
    except Exception:
        pass

    # avoid duplicates same day
    exists = Asistencia.query.filter_by(user_id=user.id, course_id=course_id, date=now.date()).first()
    if exists:
        return jsonify({"error": "Ya marcaste asistencia hoy"}), 409

    nueva_asistencia = Asistencia(
        user_id=user.id,
        course_id=course.id,
        date=now.date(),
        time=now.time(),
        state="Presente"
    )
    db.session.add(nueva_asistencia)
    db.session.commit()

    return jsonify({"message": "Asistencia registrada con éxito"}), 201


@auth_bp.route('/bulk_attendance', methods=['POST'])
def bulk_attendance():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    user = User.query.filter_by(username=session['username']).first()
    if not user or user.role != 'teacher':
        return jsonify({"error": "Solo profesores pueden actualizar asistencia masiva"}), 403

    data = request.get_json() or {}
    course_id = data.get('course_id')
    attendance = data.get('attendance', [])

    if not course_id:
        return jsonify({"error": "course_id requerido"}), 400

    now = datetime.now()
    today = now.date()
    current_time = now.time()

    for item in attendance:
        try:
            uid = int(item.get('user_id'))
            state = item.get('state')
            if state not in ('Presente', 'Ausente'):
                continue
        except Exception:
            continue

        asistencia = Asistencia.query.filter_by(user_id=uid, course_id=course_id, date=today).first()
        if not asistencia:
            asistencia = Asistencia(user_id=uid, course_id=course_id, date=today, time=current_time, state=state)
            db.session.add(asistencia)
        else:
            asistencia.state = state

    db.session.commit()
    return jsonify({"message": "Asistencia actualizada correctamente"}), 200