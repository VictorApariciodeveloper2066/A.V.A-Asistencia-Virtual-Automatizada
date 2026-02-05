import sqlite3
import os

def add_ci_to_user():
    # Detectar ruta de la base de datos (ajusta si usas carpeta instance)
    db_path = 'instance/users.db' if os.path.exists('instance/users.db') else 'users.db'
    
    print(f"Conectando a: {db_path}...")
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # SQL para agregar la columna CI
        # La definimos como VARCHAR(20) y permitimos que sea NULL inicialmente 
        # para no tener conflictos con los usuarios ya existentes.
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN ci VARCHAR(20)")
            conn.commit()
            print("✅ Columna 'ci' agregada con éxito a la tabla 'user'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("⚠️ La columna 'ci' ya existe en la base de datos.")
            else:
                print(f"❌ Error operativo: {e}")

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_ci_to_user()
