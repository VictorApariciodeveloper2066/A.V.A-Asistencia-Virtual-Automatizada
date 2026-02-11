import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL no configurada")
    exit(1)

engine = create_engine(DATABASE_URL)

tables = ['user', 'course', 'user_course', 'asistencia', 'justificativo', 'historial_asistencia', 'detalle_asistencia', 'log_asistencia']

with engine.connect() as conn:
    for table in tables:
        try:
            result = conn.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM {table}"))
            conn.commit()
            print(f"✓ Secuencia de {table} reseteada")
        except Exception as e:
            print(f"✗ Error en {table}: {e}")

print("\n✅ Secuencias sincronizadas")
