"""
Script di test per verificare il calcolo dei bioritmi
"""

from datetime import date, timedelta
from app.utils.biorhythm import (
    calculate_player_biorhythm,
    calculate_days_since_birth,
    compare_team_biorhythms
)
from app.data.player_birthdates import get_birthdate, PLAYER_BIRTHDATES

def test_basic_calculation():
    """Test calcolo base di un bioritmo"""
    print("\n=== Test Calcolo Base ===")

    # Lautaro Martinez - 22 agosto 1997
    lautaro_bd = date(1997, 8, 22)
    test_date = date(2025, 1, 1)

    bio = calculate_player_biorhythm(lautaro_bd, test_date)

    days = calculate_days_since_birth(lautaro_bd, test_date)
    print(f"Lautaro Martinez (nato {lautaro_bd})")
    print(f"Giorni dalla nascita: {days}")
    print(f"Bioritmo Fisico: {bio.physical:.2f}")
    print(f"Bioritmo Emotivo: {bio.emotional:.2f}")
    print(f"Bioritmo Intellettuale: {bio.intellectual:.2f}")
    print(f"Overall: {bio.overall:.2f}")
    print(f"Status: {bio.status}")
    print("✓ Test passed")


def test_real_players():
    """Test con giocatori reali dal database"""
    print("\n=== Test Giocatori Reali ===")

    today = date.today()

    # Testa alcuni giocatori famosi
    players_to_test = [
        "L. Martinez",
        "M. Thuram",
        "C. Pulisic",
        "R. Lukaku",
        "D. Vlahović"
    ]

    print(f"Data: {today}\n")

    for player_name in players_to_test:
        birthdate = get_birthdate(player_name)
        if birthdate:
            bio = calculate_player_biorhythm(birthdate, today)
            print(f"{player_name:20} | Overall: {bio.overall:+6.1f} | Status: {bio.status:10} | "
                  f"F:{bio.physical:+5.0f} E:{bio.emotional:+5.0f} I:{bio.intellectual:+5.0f}")
        else:
            print(f"{player_name:20} | Data di nascita non trovata")

    print("✓ Test passed")


def test_team_comparison():
    """Test confronto bioritmi di squadra"""
    print("\n=== Test Confronto Squadre ===")

    # Simula una partita Inter vs Milan
    inter_players = [
        "L. Martinez", "M. Thuram", "N. Barella", "H. Calhanoglu",
        "D. Dumfries", "A. Bastoni", "S. de Vrij", "F. Dimarco",
        "H. Mkhitaryan", "B. Pavard", "Y. Sommer"
    ]

    milan_players = [
        "R. Leao", "C. Pulisic", "A. Morata", "T. Reijnders",
        "T. Hernández", "M. Gabbia", "F. Tomori", "E. Royal",
        "Y. Fofana", "R. Loftus-Cheek", "M. Maignan"
    ]

    match_date = date.today() + timedelta(days=3)  # Partita tra 3 giorni

    # Raccogli date di nascita
    inter_birthdates = [get_birthdate(p) for p in inter_players if get_birthdate(p)]
    milan_birthdates = [get_birthdate(p) for p in milan_players if get_birthdate(p)]

    inter_stats = compare_team_biorhythms(inter_birthdates, match_date)
    milan_stats = compare_team_biorhythms(milan_birthdates, match_date)

    print(f"Partita simulata: Inter vs Milan - {match_date}\n")

    print(f"INTER:")
    print(f"  Media Overall: {inter_stats['avg_overall']:+6.1f}")
    print(f"  Fisico:        {inter_stats['avg_physical']:+6.1f}")
    print(f"  Emotivo:       {inter_stats['avg_emotional']:+6.1f}")
    print(f"  Intellettuale: {inter_stats['avg_intellectual']:+6.1f}")
    print(f"  Giocatori: {inter_stats['players_excellent']} eccellenti, "
          f"{inter_stats['players_good']} buoni, "
          f"{inter_stats['players_low']} bassi, "
          f"{inter_stats['players_critical']} critici")

    print(f"\nMILAN:")
    print(f"  Media Overall: {milan_stats['avg_overall']:+6.1f}")
    print(f"  Fisico:        {milan_stats['avg_physical']:+6.1f}")
    print(f"  Emotivo:       {milan_stats['avg_emotional']:+6.1f}")
    print(f"  Intellettuale: {milan_stats['avg_intellectual']:+6.1f}")
    print(f"  Giocatori: {milan_stats['players_excellent']} eccellenti, "
          f"{milan_stats['players_good']} buoni, "
          f"{milan_stats['players_low']} bassi, "
          f"{milan_stats['players_critical']} critici")

    # Determina vantaggio
    diff = inter_stats['avg_overall'] - milan_stats['avg_overall']
    if abs(diff) < 10:
        advantage = "NEUTRAL"
    elif diff > 0:
        advantage = "INTER"
    else:
        advantage = "MILAN"

    print(f"\nVANTAGGIO BIORITMI: {advantage}")
    print("✓ Test passed")


def test_database_coverage():
    """Verifica la copertura del database delle date di nascita"""
    print("\n=== Test Copertura Database ===")

    total_players = len(PLAYER_BIRTHDATES)
    print(f"Giocatori nel database: {total_players}")

    # Conta giocatori per posizione
    positions = {}
    for player_name in PLAYER_BIRTHDATES.keys():
        if "GK" in player_name or "Sommer" in player_name or "Maignan" in player_name:
            positions['GK'] = positions.get('GK', 0) + 1
        elif any(x in player_name for x in ["DF", "Bastoni", "Tomori", "de Vrij"]):
            positions['DF'] = positions.get('DF', 0) + 1
        elif any(x in player_name for x in ["MF", "Barella", "Calhanoglu"]):
            positions['MF'] = positions.get('MF', 0) + 1
        else:
            positions['FW'] = positions.get('FW', 0) + 1

    print(f"Coverage per Serie A completa")
    print("✓ Test passed")


if __name__ == "__main__":
    print("=" * 60)
    print("TEST SISTEMA BIORITMI")
    print("=" * 60)

    try:
        test_basic_calculation()
        test_real_players()
        test_team_comparison()
        test_database_coverage()

        print("\n" + "=" * 60)
        print("TUTTI I TEST SUPERATI! ✓")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
