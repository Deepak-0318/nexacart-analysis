from src.scanners.dataset_scanner import DatasetScanner
from src.extractors.schema_extractor import SchemaExtractor


def main():

    print("\nPhase 1.1 - Dataset Inventory\n")

    DatasetScanner().scan()

    print("\nPhase 1.2 - Schema Metadata\n")

    SchemaExtractor().extract()


if __name__ == "__main__":
    main()