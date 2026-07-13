from src.scanners.dataset_scanner import DatasetScanner
from src.extractors.schema_extractor import SchemaExtractor
from src.extractors.statistics_extractor import StatisticsExtractor
from src.detectors.pk_detector import PrimaryKeyDetector
from src.detectors.fk_detector import ForeignKeyDetector
from src.detectors.relationship_detector import RelationshipDetector
from src.extractors.datatype_detector import DatatypeDetector
from src.extractors.memory_analyzer import MemoryAnalyzer
from src.extractors.health_summary import HealthSummary
from src.generators.dictionary_generator import DictionaryGenerator


def main():

    print("\nPhase 1.1 - Dataset Inventory")
    DatasetScanner().scan()

    print("\nPhase 1.2 - Schema Metadata")
    SchemaExtractor().extract()

    print("\nPhase 1.3 - Statistics Engine")
    StatisticsExtractor().extract()
    
    print("\nPhase 1.4 - Primary Key Candidate Detection")
    PrimaryKeyDetector().detect()
    
    print("\nPhase 1.5 - Foreign Key Candidate Detection")
    ForeignKeyDetector().detect()

    print("\nPhase 1.6 - Relationship Suggestion Engine")
    RelationshipDetector().detect()

    print("\nPhase 1.7 - Intelligent Datatype Detection")
    DatatypeDetector().detect()

    print("\nPhase 1.8 - Data Dictionary Generator")
    DictionaryGenerator().generate()

    print("\nPhase 1.9 - Memory Analysis")
    MemoryAnalyzer().analyze()

    print("\nPhase 1.10 - Dataset Health Summary")
    HealthSummary().summarize()

if __name__ == "__main__":
    main()