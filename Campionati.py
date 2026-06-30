import requests
import pandas as pd
import json
import os
from datetime import datetime

# Configurazione
API_KEY = 'YOUR_FOOTBALL_DATA_API_KEY'  # Sostituisci con la tua API key
BASE_URL = 'https://api.football-data.org/v4'

# Mappatura campionati
LEAGUES = {
    'WC': 'World Cup 2026',
    'PL': 'Premier League',
    'PD': 'La Liga',
    'BL1': 'Bundesliga',
    'SA': 'Serie A',
    'FL1': 'Ligue 1',
    'DED': 'Eredivisie',
    'PPL': 'Primeira Liga',
    'CL': 'Champions League',
    'EL': 'Europa League'
}

def fetch_competition_matches(competition_code, season=2026):
    """Scarica le partite di un campionato"""
    url = f"{BASE_URL}/competitions/{competition_code}/matches?season={season}"
    headers = {'X-Auth-Token': API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'matches' not in data:
            print(f"Nessuna partita trovata per {competition_code}")
            return []
        
        matches = []
        for match in data['matches']:
            match_date = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
            
            # Determina stato
            status = 'Giocata' if match['status'] == 'FINISHED' else 'Futura'
            
            # Estrai risultato
            result = ''
            home_goals = 0
            away_goals = 0
            if match['status'] == 'FINISHED' and match.get('score'):
                home_goals = match['score']['fullTime'].get('home', 0) or 0
                away_goals = match['score']['fullTime'].get('away', 0) or 0
                result = f"{home_goals}-{away_goals}"
            
            matches.append({
                'Campionato': LEAGUES.get(competition_code, competition_code),
                'Giornata': f"Round {match.get('matchday', 0):02d}",
                'Data': match_date.strftime('%m/%d/%y'),
                'Ora': match_date.strftime('%H:%M'),
                'SquadraCasa': match['homeTeam']['name'],
                'SquadraTrasferta': match['awayTeam']['name'],
                'Stato': status,
                'Risultato': result,
                'GolCasa': home_goals,
                'GolTrasferta': away_goals
            })
        
        return matches
    
    except requests.exceptions.RequestException as e:
        print(f"Errore nel scaricare {competition_code}: {e}")
        return []

def save_to_csv(matches, filename):
    """Salva le partite in CSV"""
    if not matches:
        print(f"Nessun dato da salvare per {filename}")
        return
    
    df = pd.DataFrame(matches)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Salvato {filename}: {len(matches)} partite")

def save_to_excel(matches, filename):
    """Salva le partite in Excel"""
    if not matches:
        print(f"Nessun dato da salvare per {filename}")
        return
    
    df = pd.DataFrame(matches)
    df.to_excel(filename, index=False)
    print(f"Salvato {filename}: {len(matches)} partite")

def main():
    print("=" * 60)
    print("🏆 SCARICAMENTO CAMPIONATI FOOTBALL-DATA.ORG")
    print("=" * 60)
    
    # Crea cartella output se non esiste
    output_dir = 'campionati'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Scarica tutti i campionati
    for code, name in LEAGUES.items():
        print(f"\n📥 Scaricamento {name}...")
        
        # Determina la stagione corretta
        season = 2026 if code == 'WC' else 2025
        
        matches = fetch_competition_matches(code, season)
        
        if matches:
            # Salva in CSV
            csv_filename = os.path.join(output_dir, f"{code}_{name.replace(' ', '_')}.csv")
            save_to_csv(matches, csv_filename)
            
            # Salva in Excel
            excel_filename = os.path.join(output_dir, f"{code}_{name.replace(' ', '_')}.xlsx")
            save_to_excel(matches, excel_filename)
            
            print(f"✅ {name}: {len(matches)} partite scaricate")
        else:
            print(f"❌ {name}: nessuna partita trovata")
    
    print("\n" + "=" * 60)
    print("✅ SCARICAMENTO COMPLETATO!")
    print(f"I file sono stati salvati nella cartella: {output_dir}")
    print("=" * 60)

if __name__ == '__main__':
    main()