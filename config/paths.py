import os
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).parent.parent)
DATABASE = os.path.join(*[PROJECT_ROOT, 'database', 'sandeliapp.db'])
