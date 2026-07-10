# cron_match_scheduler.py
import os
import datetime
# datetime ficticio de tu mockup
today = datetime.datetime.now().strftime("%Y-%m-%d")
#today = "2026-06-30" 
# from datetime import datetime; today = datetime.now().strftime("%Y-%m-%d")

from dotenv import load_dotenv
from src.adapters import JSONMatchRepository, ApiFootballAdapter

def main():
    load_dotenv()
    
    # Rutas absolutas configurables
    MATCH_SAVED_FILE = os.getenv("MATCH_SAVED_FILE", "match_saved.json")
    LOG_FILE = os.getenv("LOG_FILE", "cron_output.log")
    
    repo = JSONMatchRepository(MATCH_SAVED_FILE)
    log = JSONMatchRepository(LOG_FILE)
    
    # Se existe, borramos
    if repo.file_weight() > 0:
        repo.clear_matches()
    
    if log.file_weight() > 0:
        log.clear_matches()

    api = ApiFootballAdapter(
        api_key=os.getenv("X-RapidAPI-Key"),
        api_host=os.getenv("X-RapidAPI-Host")
    )
    try:    
        print(f"Buscando partidos para el día: {today}...")
        matches = api.fetch_today_matches(
            date_str=today,
            #country_id=os.getenv("COUNTRY_ID"),
            team_id=os.getenv("TEAM_ID")
        )
    except Exception as e:
        print(f"Erro ao obter partidos: {e}")
        matches = []
    # Guardamos los partidos obtenidos en el repositorio JSON
    if matches:
        repo.save_matches(matches)
        print(f"¡Partido programado gardado con éxito! ({matches[0].home_team} vs {matches[0].away_team})")
    else:
        print("Non se encontraron eventos para hoxe.")

if __name__ == "__main__":
    main()