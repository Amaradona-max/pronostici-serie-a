import os
import sys
import shutil

# Get the current directory (api/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory
project_root = os.path.dirname(current_dir)
# Get the backend directory
backend_dir = os.path.join(project_root, 'backend')

# Add paths to sys.path
sys.path.append(project_root)
sys.path.append(backend_dir)

# Configure Database URL for Vercel
# SQLite in Vercel/Lambda must use /tmp for write access (even for WAL files)
source_db_path = os.path.join(current_dir, 'backend.db')
tmp_db_path = '/tmp/backend.db'

print(f"Vercel Startup: Checking database...")

if os.path.exists(source_db_path):
    print(f"Vercel: Found bundled database at {source_db_path}")
    try:
        # Copy DB to /tmp to allow write access (needed for lock files)
        shutil.copy2(source_db_path, tmp_db_path)
        print(f"Vercel: Copied database to {tmp_db_path}")
        
        # Set DATABASE_URL to use the writable /tmp file
        os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tmp_db_path}"
    except Exception as e:
        print(f"Vercel Error: Failed to copy database to /tmp: {e}")
        # Fallback to source path (might be read-only issue)
        os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{source_db_path}"
else:
    print(f"Vercel Warning: Database file not found at {source_db_path}")
    # If not found, point to /tmp anyway so init_db can create it
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tmp_db_path}"

try:
    from backend.app.main import app
except ImportError as e:
    # Fallback if backend.app cannot be imported directly, try app from backend dir
    try:
        from app.main import app
    except ImportError:
        raise e
