import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Vercel requires /tmp for writable files
os.environ.setdefault('UPLOAD_FOLDER', '/tmp/uploads')

from server_postgres import app, init_db

# Initialize database tables (CREATE IF NOT EXISTS, safe to call repeatedly)
init_db()
