import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.extensions import db
from backend.models import User
from app import create_app

app = create_app()

with app.app_context():
    usuarios = User.query.all()
    print(f"Total usuarios: {len(usuarios)}")
    for u in usuarios:
        print(f"ID: {u.id}, Username: {u.username}, Role: {u.role}, CI: {u.ci}")
