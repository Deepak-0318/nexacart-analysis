from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

METADATA_DIR = DATA_DIR / "metadata"

INVENTORY_DIR = METADATA_DIR / "inventory"

SCHEMA_DIR = METADATA_DIR/"schema"

SUPPORTED_FILE_TYPES = [
    ".csv",
    ".xlsx",
    ".xls",
]