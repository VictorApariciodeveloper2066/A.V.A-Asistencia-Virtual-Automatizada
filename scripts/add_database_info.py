import sqlite3
import os
from werkzeug.security import generate_password_hash

def seed_data():
    db_path = 'instance/users.db' if os.path.exists('instance/users.db') else 'users.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Password hash común para pruebas: "estudiante123"
    password_hash = generate_password_hash("estudiante123")
    
    # Lista de alumnos con perfiles hispanos
    alumnos = [
        ('jmarquez', 'juan.marquez@mail.com', 'Juan', 'Carlos', 'Márquez', 'Rodríguez', 'V-25.123.456'),
        ('mgarcia', 'maria.garcia@mail.com', 'María', 'Elena', 'García', 'Pérez', 'V-26.789.012'),
        ('lortiz', 'luis.ortiz@mail.com', 'Luis', 'Alberto', 'Ortiz', 'Castillo', 'V-24.555.666'),
        ('asosa', 'ana.sosa@mail.com', 'Ana', 'Beatriz', 'Sosa', 'Méndez', 'V-27.111.222'),
        ('dflores', 'diego.flores@mail.com', 'Diego', 'Armando', 'Flores', 'Vivas', 'V-23.444.888'),
        ('cvargas', 'carla.vargas@mail.com', 'Carla', 'Patricia', 'Vargas', 'Luna', 'V-28.999.000'),
        ('rreyes', 'ricardo.reyes@mail.com', 'Ricardo', 'José', 'Reyes', 'Guzmán', 'V-22.333.444'),
        ('slimones', 'sofia.limones@mail.com', 'Sofía', 'Isabel', 'Limones', 'Torres', 'V-29.000.111'),
        ('mcampos', 'miguel.campos@mail.com', 'Miguel', 'Ángel', 'Campos', 'Rivas', 'V-21.222.333'),
        ('erivas', 'elena.rivas@mail.com', 'Elena', 'Victoria', 'Rivas', 'Pinto', 'V-25.666.777')
    ]

    print(f"Insertando alumnos en {db_path}...")

    for username, email, p_nom, s_nom, p_ape, s_ape, ci in alumnos:
        try:
            cursor.execute('''
                INSERT INTO user (username, email, password, role, career, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, ci)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, 'student', 'ingenieria_en_sistemas', p_nom, s_nom, p_ape, s_ape, ci))
            
            # Obtener el ID del alumno insertado
            user_id = cursor.lastrowid
            
            # ASIGNACIÓN AUTOMÁTICA A QUÍMICA (Asumiendo que el ID de Química es 1)
            # Si no sabes el ID, esto vincula al alumno con el curso ID 1
            cursor.execute('INSERT OR IGNORE INTO user_course (user_id, course_id) VALUES (?, ?)', (user_id, 1))
            
        except sqlite3.IntegrityError:
            print(f"El usuario {username} ya existe, saltando...")

    conn.commit()
    conn.close()
    print("✅ 10 alumnos creados y vinculados al curso con ID 1.")

if __name__ == "__main__":
    seed_data()