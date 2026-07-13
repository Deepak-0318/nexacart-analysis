from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

METADATA_DIR = DATA_DIR / "metadata"

INVENTORY_DIR = METADATA_DIR / "inventory"

SCHEMA_DIR = METADATA_DIR/"schema"

STATISTICS_DIR = METADATA_DIR / "statistics"

PRIMARY_KEY_DIR = METADATA_DIR / "primary_keys"

FOREIGN_KEY_DIR = METADATA_DIR / "foreign_keys"

RELATIONSHIP_DIR = METADATA_DIR / "relationships"

DATATYPE_DIR = METADATA_DIR / "datatypes"

DICTIONARY_DIR = METADATA_DIR / "dictionary"

MEMORY_DIR = METADATA_DIR / "memory"

HEALTH_DIR = METADATA_DIR / "health"

SUPPORTED_FILE_TYPES = [
    ".csv",
    ".xlsx",
    ".xls",
]