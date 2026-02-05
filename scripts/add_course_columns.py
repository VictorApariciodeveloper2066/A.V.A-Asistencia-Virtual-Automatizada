from pathlib import Path
import sqlite3

# locate database.db in the project root (two levels up from this script)
db_path = Path(__file__).resolve().parents[1] / 'users.db'
print('Using database at:', db_path)
if not db_path.exists():
    print('Database file not found; aborting.')
    raise SystemExit(1)

con = sqlite3.connect(str(db_path))
cur = con.cursor()

# Add columns if they don't already exist (SQLite allows ADD COLUMN)
try:
    cur.execute("ALTER TABLE course ADD COLUMN session_code VARCHAR(10);")
    print('Added column session_code')
except sqlite3.OperationalError as e:
    print('session_code likely exists or error:', e)

try:
    cur.execute("ALTER TABLE course ADD COLUMN session_expires DATETIME;")
    print('Added column session_expires')
except sqlite3.OperationalError as e:
    print('session_expires likely exists or error:', e)

con.commit()
con.close()
print('Done')
