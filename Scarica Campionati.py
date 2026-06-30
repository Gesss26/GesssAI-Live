import requests
import pandas as pd
from datetime import datetime
import re
import os

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

def clean_team_name(name):
    """Pulisce il nome della squadra rimuovendo testo extra e numeri finali"""
    if not name:
        return ''
    
    # Rimuovi "Winner: X" o "Advancing to next round: X"
    cleaned = re.sub(r'(Winner:|Advancing to next round:).*', '', name).strip()
    
    # Rimuovi numeri finali (es: "South Africa2" -> "South Africa")
    cleaned = re.sub(r'(\d+)$', '', cleaned).strip()
    
    return cleaned

def clean_result(result):
    """Estrae solo i gol regolamentari da risultati con rigori (es: 2(4)-2(3) -> 2-2)"""
    if not result or pd.isna(result):
        return '', 0, 0
    
    result_str = str(result)
    
    # Se contiene rigori (es: "2(4)-2(3)")
    match = re.match(r'(\d+)\(\d+\)-(\d+)\(\d+\)', result_str)
    if match:
        home_goals = int(match.group(1))
        away_goals = int(match.group(2))
        return f"{home_goals}-{away_goals}", home_goals, away_goals
    
    # Risultato normale (es: "2-1")
    match = re.match(r'(\d+)-(\d+)', result_str)
    if match:
        home_goals = int(match.group(1))
        away_goals = int(match.group(2))
        return result_str, home_goals, away_goals
    
    return '', 0, 0

def convert_date(date_str):
    """Converte date da MM/DD/YY a DD/MM/YYYY"""
    if not date_str or pd.isna(date_str):
        return ''
    
    try:
        # Prova formato americano MM/DD/YY
        if '/' in str(date_str):
            parts = str(date_str).split('/')
            if len(parts) == 3:
                month, day, year = parts
                # Se anno a 2 cifre, aggiungi 20
                if len(year) == 2:
                    year = '20' + year
                # Ritorna in formato europeo DD/MM/YYYY
                return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        # Se già nel formato corretto, ritorna così com'è
        return str(date_str)
    except:
        return str(date_str)

def fetch_competition_matches(competition_code, season=2026):
    """Scarica le partite di un campionato"""
    url = f"{BASE_URL}/competitions/{competition_code}/matches?season={season}"
    headers = {'X-Auth-Token': API_KEY}
    
    try:
        print(f"📥 Scaricamento {LEAGUES.get(competition_code, competition_code)}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'matches' not in data:
            print(f"  ⚠️ Nessuna partita trovata")
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
                if match['score'].get('fullTime'):
                    home_goals = match['score']['fullTime'].get('home') or 0
                    away_goals = match['score']['fullTime'].get('away') or 0
                    result = f"{home_goals}-{away_goals}"
            
            # Pulisci nomi squadre
            home_team = clean_team_name(match['homeTeam']['name'])
            away_team = clean_team_name(match['awayTeam']['name'])
            
            # Converti data
            date_formatted = match_date.strftime('%d/%m/%Y')
            time_formatted = match_date.strftime('%H:%M')
            
            matches.append({
                'Campionato': LEAGUES.get(competition_code, competition_code),
                'Giornata': f"Round {match.get('matchday', 0):02d}" if match.get('matchday') else 'Round 00',
                'Data': date_formatted,
                'Ora': time_formatted,
                'SquadraCasa': home_team,
                'SquadraTrasferta': away_team,
                'Stato': status,
                'Risultato': result if status == 'Giocata' else '',
                'GolCasa': home_goals if status == 'Giocata' else 0,
                'GolTrasferta': away_goals if status == 'Giocata' else 0
            })
        
        return matches
    
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Errore: {e}")
        return []

def save_to_excel(matches, filename):
    """Salva le partite in Excel"""
    if not matches:
        print(f"  ⚠️ Nessun dato da salvare")
        return False
    
    df = pd.DataFrame(matches)
    
    # Crea cartella output se non esiste
    if not os.path.exists('campionati'):
        os.makedirs('campionati')
    
    filepath = os.path.join('campionati', filename)
    df.to_excel(filepath, index=False, engine='openpyxl')
    print(f"  ✅ Salvato: {filepath} ({len(matches)} partite)")
    return True

def save_to_csv(matches, filename):
    """Salva le partite in CSV"""
    if not matches:
        return False
    
    df = pd.DataFrame(matches)
    filepath = os.path.join('campionati', filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"  ✅ CSV: {filepath}")
    return True

def main():
    print("=" * 60)
    print("🏆 SCARICAMENTO CAMPIONATI FOOTBALL-DATA.ORG")
    print("=" * 60)
    print()
    
    # Chiedi quale campionato scaricare
    print("Campionati disponibili:")
    for code, name in LEAGUES.items():
        print(f"  {code}: {name}")
    print()
    
    selected = input("Inserisci il codice del campionato (o 'ALL' per tutti): ").strip().upper()
    
    if selected == 'ALL':
        leagues_to_download = list(LEAGUES.keys())
    elif selected in LEAGUES:
        leagues_to_download = [selected]
    else:
        print("❌ Campionato non valido!")
        return
    
    season = input("Inserisci stagione (default 2026): ").strip() or '2026'
    
    total_matches = 0
    
    for code in leagues_to_download:
        matches = fetch_competition_matches(code, season)
        
        if matches:
            league_name = LEAGUES[code].replace(' ', '_')
            
            # Salva in Excel
            save_to_excel(matches, f"{code}_{league_name}.xlsx")
            
            # Salva in CSV
            save_to_csv(matches, f"{code}_{league_name}.csv")
            
            total_matches += len(matches)
    
    print()
    print("=" * 60)
    print(f"✅ SCARICAMENTO COMPLETATO!")
    print(f"📊 Totale partite scaricate: {total_matches}")
    print(f"📁 I file sono nella cartella: campionati")
    print("=" * 60)
    print()
    print("💡 Per importare in GesssAI-Pro:")
    print("   1. Vai su Impostazioni")
    print("   2. Clicca '📂 Seleziona File'")
    print("   3. Seleziona il file Excel/CSV scaricato")
    print()

if __name__ == '__main__':
    main()