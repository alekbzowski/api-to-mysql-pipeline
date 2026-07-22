import os
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def run_etl():
    # 1. Wczytanie konfiguracji z pliku .env
    load_dotenv()

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    api_key = os.getenv("FOOTBALL_API_KEY")

    if not all([db_user, db_password, db_host, db_name, api_key]):
        raise ValueError("Brak wymaganych zmiennych środowiskowych w pliku .env!")

    # 2. Połączenie z bazą danych MySQL
    connection_string = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"
    engine = create_engine(connection_string)

    # 3. Pobranie meczów z API
    url = "https://api.football-data.org/v4/competitions/PL/matches"
    headers = {"X-Auth-Token": api_key}

    print("Łączenie z API Football Data...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        matches = response.json().get("matches", [])
        print(f"Pobrano {len(matches)} meczów z API.")

        # 4. Zapytanie SQL z zabezpieczeniem przed dublowaniem rekordów
        insert_query = text("""
            INSERT INTO matches (id, competition_name, home_team, away_team, score_home, score_away, status, match_date)
            VALUES (:id, :comp_name, :home, :away, :score_home, :score_away, :status, :match_date)
            ON DUPLICATE KEY UPDATE
                score_home = VALUES(score_home),
                score_away = VALUES(score_away),
                status = VALUES(status);
        """)

        # 5. Wykonanie zapisu w bazie
        with engine.begin() as conn:
            for m in matches:
                conn.execute(insert_query, {
                    "id": m["id"],
                    "comp_name": m["competition"]["name"],
                    "home": m["homeTeam"]["name"],
                    "away": m["awayTeam"]["name"],
                    "score_home": m["score"]["fullTime"]["home"],
                    "score_away": m["score"]["fullTime"]["away"],
                    "status": m["status"],
                    "match_date": m["utcDate"].replace("T", " ").replace("Z", "")
                })
                
        print("Pipeline zakończony sukcesem: Dane pomyślnie zapisane/zaktualizowane w MySQL!")
    else:
        print(f"Błąd pobierania danych z API. Kod HTTP: {response.status_code}")

if __name__ == "__main__":
    run_etl()