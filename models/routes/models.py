from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, User, db

auth = Blueprint('auth', __name__)

@auth.route('/api/login', methods=['POST'])
def api_login():
	data = request.json
	return {"status": "ok"}


# Other models should reuse the application's `db` and the single `User` model
class Course(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), unique=True, nullable=False)
	aula = db.Column(db.String(100), nullable=True)
	dia = db.Column(db.Integer, nullable=False)
	start_time = db.Column(db.Time, nullable=False)
	end_time = db.Column(db.Time, nullable=False)


class User_course(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


class Asistencia(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
	date = db.Column(db.Date, nullable=False)
	time = db.Column(db.Time, nullable=False)
	state = db.Column(db.String(50), nullable=False)  # e.g., 'present', 'absent'