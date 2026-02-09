import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.extensions import db
from backend.models import User
from app import create_app
import random

app = create_app()

with app.app_context():
    # Obtener todos los usuarios con rol 'student'
    alumnos = User.query.filter_by(role='student').all()
    
    for alumno in alumnos:
        # Generar cédula venezolana aleatoria (V-12345678)
        ci_numero = random.randint(10000000, 30000000)
        alumno.ci = f"V-{ci_numero}"
    
    db.session.commit()
    print(f"Se actualizaron {len(alumnos)} alumnos con cedulas venezolanas")
