import os
import sys

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
# We place backend.db in the api/ directory to ensure it is bundled
db_path = os.path.join(current_dir, 'backend.db')
if os.path.exists(db_path):
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    print(f"Vercel: Using database at {db_path}")
else:
    print(f"Vercel: Warning - Database file not found at {db_path}")

try:
    from backend.app.main import app
except ImportError as e:
    # Fallback if backend.app cannot be imported directly, try app from backend dir
    try:
        from app.main import app
    except ImportError:
        raise e
