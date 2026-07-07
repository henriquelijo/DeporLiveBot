# src/ports/repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models import Match

class MatchRepository(ABC):
    
    @abstractmethod
    def save_matches(self, matches: List[Match]) -> None:
        """Guarda la lista de partidos del día."""
        pass

    @abstractmethod
    def load_matches(self) -> List[Match]:
        """Carga la lista de partidos guardados para el día."""
        pass

    @abstractmethod
    def clear_matches(self) -> None:
        """Elimina el registro de partidos (al finalizar la jornada)."""
        pass