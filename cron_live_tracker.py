# cron_live_tracker.py
import os
from datetime import datetime
from dotenv import load_dotenv
from src.adapters import JSONMatchRepository, ApiFootballAdapter, TelegramBotAdapter

def main():
    load_dotenv()
    
    MATCH_SAVED_FILE = os.getenv("MATCH_SAVED_FILE", "match_saved.json")
    
    repo = JSONMatchRepository(MATCH_SAVED_FILE)
    saved_matches = repo.load_matches()
    
    if not saved_matches:
        print("No hay partido programado para hoy.")
        return

    match_info = saved_matches[0]
    
    # Control del tiempo de inicio
    now = datetime.now()
    match_datetime = datetime.strptime(f"{match_info.match_date} {match_info.match_time}", "%Y-%m-%d %H:%M")
    
    if now < match_datetime:
        print(f"O partido está programado para as {match_info.match_time}. Aínda non comezou.")
        return
    
    if match_info.match_status in ["Finished", "FT", "After ET", "After Pen."]:
        print("O partido xa rematou. Non hai máis seguimento en directo.")
        return

    # Instanciamos el resto de infraestructura que necesitamos sólo si el partido ya está en juego
    api = ApiFootballAdapter(api_key=os.getenv("X-RapidAPI-Key"), api_host=os.getenv("X-RapidAPI-Host"))
    notifier = TelegramBotAdapter(token=os.getenv("TELEGRAM_TOKEN"), chat_id=os.getenv("TELEGRAM_CHAT_ID"))

    print("O partido xa comezou o está en hora. Solicitando actualización en directo...")

    fresh_match = api.fetch_live_match_details(match_info.match_id)
    #print(f"Datos en directo obtenidos: {fresh_match.match_status if fresh_match else 'No se pudo obtener datos'}")
    if not fresh_match:
        print("No se pudo obtener datos en directo de la API.")
        return
    
    if fresh_match.match_status == "0":
        print("O partido aínda non comezou segundo a API. Esperando á próxima iteración...")
        #return

    if match_info.match_live == "0" and fresh_match.match_live == "1":
        notifier.send_notification("⚽ <b>Empeza o partido</b>")
        match_info.match_status = fresh_match.match_status
        match_info.match_live = fresh_match.match_live
        repo.save_matches([match_info]) # Save after initial notification

    # Dejamos que el DOMINIO compare el estado antiguo con el nuevo y extraiga las alertas
    alerts = match_info.verify_updates(fresh_match)
    
    # Comprobamos si ha terminado para limpiar el Cron o guardar estado intermedio
    if fresh_match.match_status in ["Finished", "FT", "After ET", "After Pen."]:
        print("O partido rematou agora.")
        repo.save_matches([fresh_match])  # Save the finished match details
        
    else:
        
        repo.save_matches([fresh_match]) 

    # Si hay novedades, las notificamos por Telegram
    for alert in alerts:
        
        notifier.send_notification(alert)


if __name__ == "__main__":
    main()
