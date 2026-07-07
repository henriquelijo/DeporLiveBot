# src/adapters/json_repository.py
import json
import os
from typing import List
from src.ports.repository import MatchRepository
from src.domain.models import Match

class JSONMatchRepository(MatchRepository):
    
    def __init__(self, file_path: str):
        self.file_path = file_path

    def save_matches(self, matches: List[Match]) -> None:
        data = [match.to_dict() for match in matches]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_matches(self) -> List[Match]:
        
        if not os.path.exists(self.file_path):
            print(f"Archivo {self.file_path} no encontrado. No hay partidos guardados.")
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                
                return [Match.from_dict(m) for m in data]
            except json.JSONDecodeError:
                return []

    def clear_matches(self) -> None:
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def rename_file(self, new_file_path: str) -> None:
        if os.path.exists(self.file_path):
            os.rename(self.file_path, new_file_path)
            self.file_path = new_file_path

    def file_weight(self) -> int:
        """Devuelve el tamaño del archivo en bytes."""
        if os.path.exists(self.file_path):
            return os.path.getsize(self.file_path)
        return 0