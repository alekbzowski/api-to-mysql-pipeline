import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Ładowanie zmiennych środowiskowych
load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "football_data_db")

# Tworzenie połączenia z bazą MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

headers = {"X-Auth-Token": API_KEY}

def run_etl_matches():
    """Pobiera i zapisuje wyniki meczów."""
    print("--- 1. Pobieranie meczów Premier League ---")
    url = "https://api.football-data.org/v4/competitions/PL/matches"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        matches = response.json().get("matches", [])
        
        # Tworzenie tabeli z kompletem kolumn (w tym comp_name)
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS matches (
                id INT PRIMARY KEY,
                comp_name VARCHAR(100),
                home VARCHAR(100),
                away VARCHAR(100),
                score_home INT,
                score_away INT,
                status VARCHAR(20),
                match_date DATETIME
            );
        """)
        
        insert_query = text("""
            INSERT INTO matches (id, comp_name, home, away, score_home, score_away, status, match_date)
            VALUES (:id, :comp_name, :home, :away, :score_home, :score_away, :status, :match_date)
            ON DUPLICATE KEY UPDATE
                score_home = VALUES(score_home),
                score_away = VALUES(score_away),
                status = VALUES(status);
        """)
        
        with engine.begin() as conn:
            conn.execute(create_table_query)
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
        print("✅ Mecze pomyślnie zaktualizowane w MySQL!")
    else:
        print(f"❌ Błąd pobierania meczów: {response.status_code}")

def run_etl_standings():
    """Pobiera i zapisuje aktualną tabelę ligową."""
    print("--- 2. Pobieranie tabeli ligowej Premier League ---")
    url = "https://api.football-data.org/v4/competitions/PL/standings"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        standings_data = response.json().get("standings", [])[0].get("table", [])
        
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS standings (
                position INT PRIMARY KEY,
                team_name VARCHAR(100),
                played_games INT,
                won INT,
                draw INT,
                lost INT,
                points INT,
                goal_difference INT
            );
        """)
        
        insert_query = text("""
            INSERT INTO standings (position, team_name, played_games, won, draw, lost, points, goal_difference)
            VALUES (:position, :team_name, :played_games, :won, :draw, :lost, :points, :goal_difference)
            ON DUPLICATE KEY UPDATE
                played_games = VALUES(played_games),
                won = VALUES(won),
                draw = VALUES(draw),
                lost = VALUES(lost),
                points = VALUES(points),
                goal_difference = VALUES(goal_difference);
        """)
        
        with engine.begin() as conn:
            conn.execute(create_table_query)
            for item in standings_data:
                conn.execute(insert_query, {
                    "position": item["position"],
                    "team_name": item["team"]["name"],
                    "played_games": item["playedGames"],
                    "won": item["won"],
                    "draw": item["draw"],
                    "lost": item["lost"],
                    "points": item["points"],
                    "goal_difference": item["goalDifference"]
                })
        print("✅ Tabela ligowa pomyślnie zaktualizowana w MySQL!")
    else:
        print(f"❌ Błąd pobierania tabeli ligowej: {response.status_code}")

if __name__ == "__main__":
    run_etl_matches()
    run_etl_standings()
    print("--- Full Pipeline zakończył pracę pomyślnie ---")