# Football Data ETL Pipeline (API to MySQL)

Automatyczny pipeline ETL w Pythonie pobierający dane o meczach z API `football-data.org` i zapisujący je do bazy danych MySQL.

## 🚀 Cechy projektu
* **Idempotentność:** Bezpieczne, wielokrotne uruchamianie skryptu w ciągu dnia bez ryzyka dublowania rekordów (`ON DUPLICATE KEY UPDATE`).
* **Relacyjna baza danych:** Przechowywanie szczegółowych informacji o meczach, wynikach i statusach w MySQL.
* **Eksploracja danych:** Dołączony Jupyter Notebook z analizą i statystykami pobranych meczów.

## 🛠️ Technologie
* Python 3
* MySQL & MySQL Workbench
* SQLAlchemy & Requests
* Pandas & Jupyter Lab

## 📦 Instrukcja uruchomienia

### 1. Instalacja zależności
```bash
pip install -r requirements.txt
```

### 2. Konfiguracja zmiennych środowiskowych
Stwórz plik .env w głównym katalogu projektu i uzupełnij go swoimi danymi:
```env
DB_HOST=localhost
DB_USER=twoj_user
DB_PASSWORD=twoje_haslo
DB_NAME=football_data_db
FOOTBALL_API_KEY=twoj_klucz_api
```
### 3. Uruchomienie skryptu ETL
```bash
python etl_pipeline.py
```
