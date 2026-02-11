from backend.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=True, default=None)
    career = db.Column(db.String(150), nullable=True)
    primer_nombre = db.Column(db.String(100), nullable=True)
    primer_apellido = db.Column(db.String(100), nullable=True)
    ci = db.Column(db.String(20), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    notificaciones_activas = db.Column(db.Boolean, default=True)
    formato_hora = db.Column(db.String(10), default='12h')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    # Relación para acceder a los cursos del usuario fácilmente
    courses = db.relationship('Course', secondary='user_course', backref=db.backref('users', lazy='dynamic'))
    # La tabla Asistencia ya está bien definida, la usaremos tal cual:
    # id, user_id, course_id, date, time, state

class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    aula = db.Column(db.String(100), nullable=True)
    dia = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    # Dynamic session code for attendance (set by teacher)
    session_code = db.Column(db.String(10), nullable=True)
    session_expires = db.Column(db.DateTime, nullable=True)


class User_course(db.Model):
    __tablename__ = 'user_course'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


class Asistencia(db.Model):
    __tablename__ = 'asistencia'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    state = db.Column(db.String(50), nullable=False)


class Justificativo(db.Model):
    __tablename__ = 'justificativo'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    fecha_clase = db.Column(db.String(20), nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    archivo_nombre = db.Column(db.String(100))
    estado = db.Column(db.String(20), default='Pendiente')

    usuario = db.relationship('User', backref='justificativos')
    curso = db.relationship('Course', backref='justificativos')


class HistorialAsistencia(db.Model):
    __tablename__ = 'historial_asistencia'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    codigo_sesion = db.Column(db.String(20), nullable=False)
    total_alumnos = db.Column(db.Integer, default=0)
    total_presentes = db.Column(db.Integer, default=0)
    total_justificados = db.Column(db.Integer, default=0)
    total_ausentes = db.Column(db.Integer, default=0)

    curso = db.relationship('Course', backref='historiales')
    detalles = db.relationship('DetalleAsistencia', backref='historial', cascade='all, delete-orphan')


class DetalleAsistencia(db.Model):
    __tablename__ = 'detalle_asistencia'

    id = db.Column(db.Integer, primary_key=True)
    historial_id = db.Column(db.Integer, db.ForeignKey('historial_asistencia.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    usuario = db.relationship('User', backref='detalles_asistencia')
