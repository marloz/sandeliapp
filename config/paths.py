import os
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).parent.parent)
DATABASE = os.path.join(*[PROJECT_ROOT, "database", "sandeliapp.db"])
LOGO_PATH = Path(PROJECT_ROOT + "/resources/medexy_logo_low_res.jpg")
INVOICE_PATH = Path(PROJECT_ROOT + "/invoice.pdf")
