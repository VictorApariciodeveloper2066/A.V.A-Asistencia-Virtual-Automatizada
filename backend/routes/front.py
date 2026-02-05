from flask import Blueprint, render_template, session, redirect, url_for, request
from backend.models import User, Course, User_course
from backend.extensions import db
from datetime import date
from datetime import timedelta

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
    for c in courses:
        item = {
            'id': c.id,
            'name': c.name,
            'aula': c.aula,
            'dia': c.dia,
            'start_time': c.start_time.strftime('%H:%M') if c.start_time else '',
            'end_time': c.end_time.strftime('%H:%M') if c.end_time else ''
        }
        slots_by_day.setdefault(c.dia, []).append(item)

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

    days_names = {i + 1: weekday_names[i] for i in range(5)}

    # Provide a small proxy so template's `user.courses.count()` works
    class _CoursesProxy:
        def __init__(self, items):
            self._items = items
        def count(self):
            return len(self._items)

    user.courses = _CoursesProxy(courses)

    return render_template('dashboard.html', user=user, username=session['username'], schedule=slots_by_day, days_names=days_names, week_dates=week_dates, today_index=today_index, today=today)

@front_bp.route('/login')
def login_page():
    return render_template('login.html')

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
