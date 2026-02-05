import sqlite3
import os

def update_student_careers():
    # Detectar la ruta de la base de datos
    db_path = 'instance/users.db' if os.path.exists('instance/users.db') else 'users.db'
    
    print(f"Conectando a: {db_path}...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ejecutamos la actualización:
        # Filtramos por rol 'student' para no afectar a profesores o admins
        # y cambiamos 'Ingeniería' por 'ingenieria_en_sistemas'
        cursor.execute('''
            UPDATE user 
            SET career = 'ingenieria_en_sistemas' 
            WHERE role = 'student' AND career = 'Ingeniería'
        ''')

        filas_afectadas = cursor.rowcount
        conn.commit()
        
        print(f"✅ Éxito: Se actualizaron {filas_afectadas} alumnos a la carrera 'ingenieria_en_sistemas'.")

    except Exception as e:
        print(f"❌ Error al actualizar: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_student_careers()