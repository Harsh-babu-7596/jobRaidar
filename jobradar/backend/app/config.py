from pathlib import Path
import os
from dotenv import load_dotenv

# Resolve paths from the backend directory, not the shell's current directory.
BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

DATA_DIR = BACKEND_DIR / "data"
LOG_DIR = BACKEND_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

_default_db = f"sqlite:///{(DATA_DIR / 'jobradar.db').as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL", _default_db)
SCRAPE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL_MINUTES", "15"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
