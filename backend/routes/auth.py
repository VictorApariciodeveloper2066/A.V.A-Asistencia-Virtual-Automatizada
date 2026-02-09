from flask import Blueprint, request, session, jsonify, redirect, url_for
from backend.models import User, Course, Asistencia, User_course, Justificativo
from backend.extensions import db
from sqlalchemy import or_
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import secrets, string
from flask_mail import Message
from backend.extensions import mail
import traceback
import os
from werkzeug.utils import secure_filename

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


def generar_token(email):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY', 'supersecretkey'))
    return serializer.dumps(email, salt='recuperar-password-salt')


@auth_bp.route('/recuperar_password', methods=['POST'])
def recuperar_password():
    try:
        data = request.get_json() or {}
        email = data.get('email')

        if not email:
            return jsonify({"error": "El correo es requerido"}), 400

        user = User.query.filter_by(email=email).first()
        if user:
            token = generar_token(email)
            recover_url = url_for('front.restablecer_page', token=token, _external=True)
            # Always print the recovery URL to console for development/testing
            print(f"RECOVERY LINK: {recover_url}")
            current_app.logger.info(f"RECOVERY LINK: {recover_url}")

            msg = Message("Restablecer Contraseña - AVA",
                          sender=current_app.config.get('MAIL_DEFAULT_SENDER', current_app.config.get('MAIL_USERNAME')),
                          recipients=[email])
            msg.body = f"Hola {user.username},\n\nPara restablecer tu contraseña, haz clic en el siguiente enlace:\n{recover_url}\n\nEste enlace expirará en 30 minutos.\nSi no solicitaste este cambio, puedes ignorar este correo."
            try:
                if mail:
                    mail.send(msg)
                else:
                    current_app.logger.debug(f"Mail disabled, recovery link: {recover_url}")
            except Exception as e:
                # Log the error but DO NOT return 500 — allow flow to continue in development.
                current_app.logger.exception('Error sending recovery email')
                traceback.print_exc()
                current_app.logger.error('Continuing despite mail send error; recovery link was: %s', recover_url)
                # Do not expose full trace to client; respond as if instructions were sent.
                # This prevents a 500 when SMTP is not configured during development.
                pass

        # Responder siempre de forma ambigua para seguridad
        return jsonify({"message": "Si el correo está registrado, recibirás un enlace pronto."}), 200
    except Exception as e:
        traceback.print_exc()
        current_app.logger.exception('Unhandled error in recuperar_password')
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@auth_bp.route('/reset/<token>', methods=['POST'])
def reset_with_token(token):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY', 'supersecretkey'))
    try:
        email = serializer.loads(token, salt='recuperar-password-salt', max_age=1800)
    except Exception:
        return jsonify({"error": "El enlace es inválido o ha expirado"}), 400

    data = request.get_json() or {}
    nueva_pass = data.get('password')
    if not nueva_pass:
        return jsonify({"error": "La nueva contraseña es requerida"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        user.set_password(nueva_pass)
        db.session.commit()
        return jsonify({"message": "Contraseña actualizada con éxito"}), 200

    return jsonify({"error": "Usuario no encontrado"}), 404


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


@auth_bp.route('/subir_justificativo', methods=['POST'])
def subir_justificativo():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    user = User.query.filter_by(username=session['username']).first()
    course_id = request.form.get('course_id')
    fecha_clase = request.form.get('fecha_clase')
    motivo = request.form.get('motivo')
    archivo = request.files.get('archivo')
    
    if not course_id or not motivo:
        return jsonify({"error": "Datos incompletos"}), 400
    
    archivo_nombre = None
    if archivo:
        filename = secure_filename(archivo.filename)
        upload_folder = os.path.join(current_app.root_path, '..', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        archivo_nombre = f"{user.id}_{datetime.now().timestamp()}_{filename}"
        archivo.save(os.path.join(upload_folder, archivo_nombre))
    
    justificativo = Justificativo(
        user_id=user.id,
        course_id=course_id,
        fecha_clase=fecha_clase or datetime.now().strftime('%Y-%m-%d'),
        motivo=motivo,
        archivo_nombre=archivo_nombre,
        estado='Pendiente'
    )
    db.session.add(justificativo)
    db.session.commit()
    
    return jsonify({"message": "Justificativo enviado correctamente"}), 201


@auth_bp.route('/resolver_justificativo/<int:justificativo_id>', methods=['POST'])
def resolver_justificativo(justificativo_id):
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    user = User.query.filter_by(username=session['username']).first()
    if not user or user.role != 'teacher':
        return jsonify({"error": "Solo profesores pueden resolver justificativos"}), 403
    
    data = request.get_json() or {}
    nuevo_estado = data.get('estado')
    
    if nuevo_estado not in ('Aceptado', 'Rechazado'):
        return jsonify({"error": "Estado inválido"}), 400
    
    justificativo = Justificativo.query.get(justificativo_id)
    if not justificativo:
        return jsonify({"error": "Justificativo no encontrado"}), 404
    
    justificativo.estado = nuevo_estado
    
    if nuevo_estado == 'Aceptado':
        from datetime import datetime
        try:
            fecha = datetime.strptime(justificativo.fecha_clase, '%Y-%m-%d').date()
        except:
            fecha = datetime.now().date()
        
        asistencia = Asistencia.query.filter_by(
            user_id=justificativo.user_id,
            course_id=justificativo.course_id,
            date=fecha
        ).first()
        
        if asistencia:
            asistencia.state = 'Justificado'
        else:
            nueva_asistencia = Asistencia(
                user_id=justificativo.user_id,
                course_id=justificativo.course_id,
                date=fecha,
                time=datetime.now().time(),
                state='Justificado'
            )
            db.session.add(nueva_asistencia)
    
    db.session.commit()
    return jsonify({"message": f"Justificativo {nuevo_estado.lower()}"}), 200