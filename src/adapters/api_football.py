# src/adapters/api_football.py
import http.client
import json
from typing import List, Optional
from src.ports.football_api import FootballAPI
from src.domain.models import Match

class ApiFootballAdapter(FootballAPI):
    
    def __init__(self, api_key: str, api_host: str):
        self.api_key = api_key
        self.api_host = api_host

    def _get_headers(self) -> dict:
        return {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.api_host,
            'Content-Type': "application/json"
        }

    def fetch_today_matches(self, 
                            date_str: str, 
                            #country_id: str, 
                            team_id: str) -> List[Match]:
        conn = http.client.HTTPSConnection(self.api_host)
        #url = f"/?action=get_events&from={date_str}&to={date_str}&country_id={country_id}&team_id={team_id}"
        url = f"/?action=get_events&from={date_str}&to={date_str}&team_id={team_id}"
        
        try:
            conn.request("GET", url, headers=self._get_headers())
            res = conn.getresponse()
            data_json = json.loads(res.read())
            
            if isinstance(data_json, list):
                return [self._map_to_domain(event) for event in data_json]
            elif isinstance(data_json, dict) and data_json.get("error") == 404:
                print(f"API Info: {data_json.get('message')}")
        except Exception as e:
            print(f"Error fetching today's matches: {e}")
        return []

    def fetch_live_match_details(self, match_id: str) -> Optional[Match]:
        conn = http.client.HTTPSConnection(self.api_host)
        url = f"/?action=get_events&match_id={match_id}"
        
        try:
            conn.request("GET", url, headers=self._get_headers())
            res = conn.getresponse()
            data_json = json.loads(res.read())
            
            if isinstance(data_json, list) and data_json:
                return self._map_to_domain(data_json[0])
        except Exception as e:
            print(f"Error fetching live match details: {e}")
        return None

    def _map_to_domain(self, event: dict) -> Match:
        """Transforma la estructura cruda de la API al modelo estructurado de Dominio."""
        substitutions = event.get("substitutions", {"home": [], "away": []})
        if isinstance(substitutions, list):  # Proteccion si la API devuelve lista vacía en vez de dict
            substitutions = {"home": [], "away": []}

        return Match.from_dict({
            "match_date": event.get("match_date"),
            "match_time": event.get("match_time"),
            "home_team": event.get("match_hometeam_name"),
            "away_team": event.get("match_awayteam_name"),
            "league_name": event.get("league_name"),
            "league_id": event.get("league_id"),
            "match_id": event.get("match_id"),
            "match_live": event.get("match_live", "0"),
            "match_stadium": event.get("match_stadium", ""),
            "match_status": event.get("match_status", ""),
            "home_score": event.get("match_hometeam_score", "0"),
            "away_score": event.get("match_awayteam_score", "0"),
            "cards": event.get("cards", []),
            "substitutions": {
                "home": substitutions.get("home", []),
                "away": substitutions.get("away", [])
            },
            "goalscorer": event.get("goalscorer", [])
        })