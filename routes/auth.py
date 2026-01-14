
from flask import Blueprint, request, render_template, redirect, url_for, abort, session
from app import User

auth = Blueprint('auth', __name__)


@auth.route('/loginback', methods=['POST'])
def loginback():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # validate input
        if not username or not password:
            return ('Contraseña incorrecta o usuario no encontrado', 403)  # Forbidden

        user = User.query.filter_by(username=username).first()
        if not user:
            return ('Usuario no encontrado', 404)

        if not user.check_password(password):
            return ('Contraseña incorrecta', 401)

        # success
        session['username'] = user.username
        return redirect(url_for('dashboard'))
