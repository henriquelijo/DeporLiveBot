# src/domain/models.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Substitution:
    time: str
    player_out: str
    player_in: str


@dataclass
class Goalscorer:
    time: str
    home_scorer: str
    away_scorer: str
    score: str
    home_assist: str


@dataclass
class Match:
    match_date: str
    match_time: str
    home_team: str
    away_team: str
    league_name: str
    league_id: str
    match_id: str
    match_live: str
    match_stadium: str
    match_status: str
    home_score: str
    away_score: str
    cards: List[Dict] = field(default_factory=list)
    substitutions: Dict[str, List[Dict]] = field(
        default_factory=lambda: {"home": [], "away": []}
    )
    goalscorer: List[Dict] = field(default_factory=list)

    def is_live(self) -> bool:
        """Determina si el partido está en juego según el flag de la API."""
        return self.match_live == "1"

    def is_finished(self) -> bool:
        """Determina si el partido ha finalizado."""
        return self.match_status.lower() in ["finished", "ft", "finalizado"]

   # Reemplazar el método verify_updates en src/domain/models.py con este:
    def verify_updates(self, fresh_match: "Match") -> List[str]:
        updates = []
        
        # 1. Goles
        if fresh_match.home_score != self.home_score or fresh_match.away_score != self.away_score:
            
            current_goal_identifiers = {
                f"{g.get('time')}-{g.get('home_scorer') or g.get('away_scorer')}-{g.get('score')}"
                for g in self.goalscorer
            }
            fresh_goal_identifiers = {
                f"{g.get('time')}-{g.get('home_scorer') or g.get('away_scorer')}-{g.get('score')}"
                for g in fresh_match.goalscorer
            }

            # Detectar nuevos goles
            new_goals = [
                goal for goal in fresh_match.goalscorer
                if f"{goal.get('time')}-{goal.get('home_scorer') or goal.get('away_scorer')}-{goal.get('score')}" not in current_goal_identifiers
            ]
            for goal in new_goals:
                scorer = goal.get('home_scorer') or goal.get('away_scorer') or "Descoñecido"
                time = goal.get("time", "")
                score = goal.get("score", "")
                updates.append(
                    f"⚽ <b>GOL!</b> ⚽\n"
                    f"<b>{scorer}</b> marcou no minuto {time}.\n"
                    f"Marcador: <b>{fresh_match.home_team}</b> {score} <b>{fresh_match.away_team}</b>"
                )
            
            # Detectar goles anulados o desaparecidos
            cancelled_goals = [
                goal for goal in self.goalscorer
                if f"{goal.get('time')}-{goal.get('home_scorer') or goal.get('away_scorer')}-{goal.get('score')}" not in fresh_goal_identifiers
            ]
            for goal in cancelled_goals:
                scorer = goal.get("home_scorer") or goal.get("away_scorer") or "Descoñecido"
                time = goal.get("time", "")
                updates.append(
                    f"❌ <b>Gol Anulado!</b> ❌\n"
                    f"O gol de <b>{scorer}</b> no minuto {time} foi anulado.\n"
                    f"Marcador actual: <b>{fresh_match.home_team}</b> {fresh_match.home_score} - "
                    f"{fresh_match.away_score} <b>{fresh_match.away_team}</b>"
                )

            # Actualizamos el estado del partido
            self.home_score = fresh_match.home_score
            self.away_score = fresh_match.away_score
            self.goalscorer = fresh_match.goalscorer

        # 2. Tarjetas (Sigue igual...)
        if len(fresh_match.cards) > len(self.cards):
            new_cards = fresh_match.cards[len(self.cards):]
            for card in new_cards:
                card_type = "🟨 Tarxeta Amarela" if "yellow" in card.get("card", "").lower() else "🟥 Tarxeta Vermella"
                player = card.get("player") or card.get("home_fault") or card.get("away_fault") or "Jugador"
                updates.append(f"{card_type} para <b>{player}</b> ({card.get('time', '')})")
            self.cards = fresh_match.cards

        # 3. Cambios de estado (Sigue igual...)
        if fresh_match.match_status != self.match_status:
            if fresh_match.match_status == "Half Time":
                updates.append(
                    f"☕ <b>Descanso</b>\n"
                    f"<b> {fresh_match.home_team}</b> {fresh_match.home_score} - "
                    f"{fresh_match.away_score} <b>{fresh_match.away_team}</b>"
                )
            elif fresh_match.match_status in ["0", "Finished", "FT", "Finalizado"]:
                updates.append(
                    f"🏁 <b>Final do Partido</b>\n\nResultado definitivo:\n"
                    f"<b> {fresh_match.home_team}</b> {fresh_match.home_score} - "
                    f"{fresh_match.away_score} <b>{fresh_match.away_team}</b>"
                )
            self.match_status = fresh_match.match_status
            self.match_live = fresh_match.match_live

        # 4. Sustituciones
        for team_type in ["home", "away"]:
            current_subs = {(s.get("time"), s.get("player_out"), s.get("player_in")) for s in self.substitutions[team_type]}
            for sub in fresh_match.substitutions[team_type]:
                sub_tuple = (sub.get("time"), sub.get("player_out"), sub.get("player_in"))
                if sub_tuple not in current_subs:
                    updates.append(
                        f"🔁 Cambio en {fresh_match.home_team if team_type == 'home' else fresh_match.away_team}: "
                        f"Substituído <b>{sub.get('substitution').split(' | ')[0]}</b> por <b>{sub.get('substitution').split(' | ')[1]}</b> "
                        f"({sub.get('time', '')})"
                    )
        self.substitutions = fresh_match.substitutions
        
        return updates

    def to_dict(self) -> dict:
        """Convierte la entidad de dominio a un diccionario nativo de Python (útil para el JSON)."""
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        """Crea una instancia de Match a partir de un diccionario (útil al leer el JSON o la API)."""
        # Aseguramos que las estructuras anidadas por defecto existan si vienen vacías
        cards = data.get("cards") or []
        goalscorer = data.get("goalscorer") or []
        substitutions = data.get("substitutions") or {"home": [], "away": []}
        
        # Si el JSON viene con listas vacías que contienen un mapa vacío (como en tu ejemplo), limpiamos
        if cards == [{}]: cards = []
        if goalscorer == [{}]: goalscorer = []
        if substitutions.get("home") == [{}]: substitutions["home"] = []
        if substitutions.get("away") == [{}]: substitutions["away"] = []

        return cls(
            match_date=data["match_date"],
            match_time=data["match_time"],
            home_team=data["home_team"],
            away_team=data["away_team"],
            league_name=data["league_name"],
            league_id=data["league_id"],
            match_id=data["match_id"],
            match_live=data["match_live"],
            match_stadium=data.get("match_stadium", ""),
            match_status=data.get("match_status", ""),
            home_score=data.get("home_score", ""),
            away_score=data.get("away_score", ""),
            cards=cards,
            substitutions=substitutions,
            goalscorer=goalscorer
        )
