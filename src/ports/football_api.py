# src/ports/football_api.py
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import Match

class FootballAPI(ABC):

    @abstractmethod
    def fetch_today_matches(self, date_str: str, country_id: str, team_id: str) -> List[Match]:
        """Obtiene los partidos programados para un equipo en una fecha específica."""
        pass

    @abstractmethod
    def fetch_live_match_details(self, match_id: str) -> Optional[Match]:
        """Obtiene el estado en tiempo real de un partido específico."""
        pass