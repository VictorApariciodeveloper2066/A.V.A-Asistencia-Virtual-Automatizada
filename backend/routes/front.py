from flask import Blueprint, render_template, session, redirect, url_for, request
from backend.models import User, Course, User_course, Asistencia
from backend.extensions import db
from datetime import date, timedelta, datetime

front_bp = Blueprint('front', __name__)

@front_bp.route('/')
def index():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and user.role in ('student', 'teacher'):
            return redirect(url_for('front.dashboard'))
        return redirect(url_for('front.predashboard'))
    return render_template('index.html')

@front_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('front.index'))
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('front.index'))
    if user.role not in ('student', 'teacher'):
        return redirect(url_for('front.predashboard'))
    # Query courses associated with this user
    courses = db.session.query(Course).join(User_course, Course.id == User_course.course_id).filter(User_course.user_id == user.id).all()

    # Weekday names (Spanish) and organize courses by day index (1=Monday ... 7=Sunday)
    weekday_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    slots_by_day = {i: [] for i in range(1, 8)}
    now = datetime.now()
    current_time = now.time()
    for c in courses:
        item = {
            'id': c.id,
            'name': c.name,
            'aula': c.aula,
            'dia': c.dia,
            'start_time': c.start_time.strftime('%H:%M') if c.start_time else '',
            'end_time': c.end_time.strftime('%H:%M') if c.end_time else ''
        }
        # Show attendance button only when today is the course day and current time is within start/end
        can_mark = False
        try:
            if c.start_time and c.end_time:
                # Support Course.dia stored as 1..7 (Mon..Sun) or 0..6 (Mon..Sun)
                today_idx1 = now.weekday() + 1
                if isinstance(c.dia, int):
                    if 1 <= c.dia <= 7:
                        day_matches = (today_idx1 == c.dia)
                    else:
                        day_matches = (now.weekday() == c.dia)
                else:
                    day_matches = False
                can_mark = day_matches and (c.start_time <= current_time <= c.end_time)
        except Exception:
            can_mark = False
        item['can_mark'] = can_mark
        slots_by_day.setdefault(c.dia, []).append(item)

    # If user is a teacher, build students_by_course for active classes
    students_by_course = {}
    try:
        if user.role == 'teacher':
            current_day = now.weekday() + 1
            for c in courses:
                # check active session
                is_active = False
                try:
                    if isinstance(c.dia, int):
                        if 1 <= c.dia <= 7:
                            day_matches = (current_day == c.dia)
                        else:
                            day_matches = (now.weekday() == c.dia)
                    else:
                        day_matches = False
                    is_active = day_matches and (c.start_time <= current_time <= c.end_time)
                except Exception:
                    is_active = False

                if is_active:
                    students = db.session.query(User).join(User_course, User.id == User_course.user_id).filter(User_course.course_id == c.id, User.role != 'teacher').all()
                    students_by_course[c.id] = students
    except Exception:
        students_by_course = {}

    # Build values expected by the template:
    # - days_names: 1-based mapping for weekdays used in the template (1..5)
    # - week_dates: mapping day index -> date string for current week
    # - today_index: current weekday as 1=Monday..7=Sunday
    # - schedule: alias for slots_by_day
    today = date.today()
    today_index = today.weekday() + 1

    # week start (Monday)
    week_start = today - timedelta(days=today.weekday())
    week_dates = {i: (week_start + timedelta(days=(i - 1))).strftime('%d %b') for i in range(1, 6)}

    # Attendance counts for the current week (Mon-Sun)
    week_end = week_start + timedelta(days=6)
    attended_count = db.session.query(Asistencia).filter(Asistencia.user_id == user.id, Asistencia.state == 'Presente', Asistencia.date >= week_start, Asistencia.date <= week_end).count()

    # Total classes this week: count user's courses that fall on weekdays (Mon-Fri)
    total_classes = 0
    for c in courses:
        try:
            if isinstance(c.dia, int):
                if 1 <= c.dia <= 5:
                    total_classes += 1
                elif 0 <= c.dia <= 4:
                    total_classes += 1
        except Exception:
            continue

    days_names = {i + 1: weekday_names[i] for i in range(5)}

    # Provide course count for the template (avoid calling InstrumentedList.count())
    course_count = len(courses)

    return render_template('dashboard.html', user=user, username=session['username'], schedule=slots_by_day, days_names=days_names, week_dates=week_dates, today_index=today_index, today=today, course_count=course_count, attended_count=attended_count, total_classes=total_classes, courses=courses, students_by_course=students_by_course)


@front_bp.route('/asistencia/<int:course_id>')
def ver_asistencia(course_id):
    if 'username' not in session:
        return redirect(url_for('front.login_page'))
    profesor = User.query.filter_by(username=session['username']).first()
    if not profesor or profesor.role != 'teacher':
        return redirect(url_for('front.index'))

    course = Course.query.get_or_404(course_id)

    # verify class is active (optional: restrict access to class time)
    now = datetime.now()
    try:
        current_day = now.weekday() + 1
        is_active = (isinstance(course.dia, int) and ((1 <= course.dia <= 7 and course.dia == current_day) or (0 <= course.dia <= 6 and course.dia == now.weekday())) and course.start_time <= now.time() <= course.end_time)
    except Exception:
        is_active = False

    # get enrolled students (role == student)
    alumnos_inscritos = db.session.query(User).join(User_course, User.id == User_course.user_id).filter(User_course.course_id == course_id, User.role == 'student').all()

    # Get today's attendance for this course and map by user_id
    today = date.today()
    asistencias_hoy = Asistencia.query.filter_by(course_id=course_id, date=today).all()
    mapa_asistencia = {a.user_id: a.state for a in asistencias_hoy}

    # Get pending justificativos for this course
    from backend.models import Justificativo
    justificativos_pendientes = Justificativo.query.filter_by(course_id=course_id, estado='Pendiente').all()

    # Build a simple list/dict for the template so the template doesn't need to access model attrs directly
    lista_final = []
    for alumno in alumnos_inscritos:
        primer_nombre = getattr(alumno, 'primer_nombre', None) or None
        primer_apellido = getattr(alumno, 'primer_apellido', None) or None
        ci = getattr(alumno, 'ci', None) or getattr(alumno, 'cedula', None) or None
        nombre_completo = f"{primer_apellido or ''}, {primer_nombre or alumno.username or ''}".strip().strip(',')
        inicial = (primer_nombre[0] if primer_nombre else (alumno.username[0] if getattr(alumno, 'username', None) else 'U')).upper()
        lista_final.append({
            'id': alumno.id,
            'nombre_completo': nombre_completo,
            'cedula': ci or 'S/N',
            'estado_actual': mapa_asistencia.get(alumno.id, 'Ausente'),
            'inicial': inicial,
            # expose some raw fields in case template needs them
            'primer_nombre': primer_nombre,
            'primer_apellido': primer_apellido,
            'username': getattr(alumno, 'username', None)
        })

    return render_template('Asistencia.html', alumnos=lista_final, course=course, profesor=profesor, now=now, is_active=is_active, justificativos_pendientes=justificativos_pendientes)


@front_bp.route('/justificativos/<int:course_id>')
def ver_justificativos(course_id):
    if 'username' not in session:
        return redirect(url_for('front.login_page'))
    profesor = User.query.filter_by(username=session['username']).first()
    if not profesor or profesor.role != 'teacher':
        return redirect(url_for('front.index'))

    course = Course.query.get_or_404(course_id)
    from backend.models import Justificativo
    justificativos = Justificativo.query.filter_by(course_id=course_id, estado='Pendiente').all()
    
    return render_template('Reportes.html', course=course, justificativos=justificativos)

@front_bp.route('/cargar_justificativo')
def cargar_justificativo():
    if 'username' not in session:
        return redirect(url_for('front.login_page'))
    user = User.query.filter_by(username=session['username']).first()
    if not user or user.role != 'student':
        return redirect(url_for('front.index'))
    
    courses = db.session.query(Course).join(User_course, Course.id == User_course.course_id).filter(User_course.user_id == user.id).all()
    return render_template('carga_justificativos.html', user=user, courses=courses)

@front_bp.route('/ver_archivo/<filename>')
def ver_archivo(filename):
    if 'username' not in session:
        return redirect(url_for('front.login_page'))
    return render_template('ver_archivo.html', filename=filename)

@front_bp.route('/login')
def login_page():
    return render_template('login.html')


@front_bp.route('/recuperar')
def recuperar_page():
    return render_template('Recuperar.html')


@front_bp.route('/restablecer/<token>')
def restablecer_page(token):
    return render_template('Restablecer.html', token=token)

@front_bp.route('/register')
def register_page():
    return render_template('register.html')

@front_bp.route('/predashboard')
def predashboard():
    if 'username' not in session:
        return redirect(url_for('front.login_page'))
    user = User.query.filter_by(username=session['username']).first()
    if user and user.role in ('student', 'teacher'):
        return redirect(url_for('front.dashboard'))
    return render_template('Predashboard.html')

@front_bp.route('/set_role', methods=['POST'])
def set_role():
    if 'username' not in session:
        return redirect(url_for('front.login_page'))
    role = request.form.get('role')
    if role not in ('student', 'teacher'):
        return redirect(url_for('front.predashboard'))
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('front.index'))
    if user.role not in ('student', 'teacher'):
        user.role = role
        db.session.commit()
    return redirect(url_for('front.dashboard'))
