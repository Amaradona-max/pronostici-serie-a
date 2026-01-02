import os
import sys

# Add the project root to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure Database URL for Vercel
# We place backend.db in the api/ directory to ensure it is bundled
db_path = os.path.join(os.path.dirname(__file__), 'backend.db')
if os.path.exists(db_path):
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    print(f"Vercel: Using database at {db_path}")
else:
    print(f"Vercel: Warning - Database file not found at {db_path}")

from backend.app.main import app
