from .document_reader_interface import DocumentReaderInterface
from .extractor_interface import ExtractorInterface
from .comparison_interface import ComparisonInterface
from .ranking_interface import RankingInterface
from .communication_interface import CommunicationInterface

__all__ = [
    'DocumentReaderInterface',
    'ExtractorInterface', 
    'ComparisonInterface',
    'RankingInterface',
    'CommunicationInterface'
]