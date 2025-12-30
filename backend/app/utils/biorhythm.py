"""
Biorhythm Calculation Module

Calcola i bioritmi di un calciatore basandosi sulla data di nascita.

I bioritmi seguono tre cicli sinusoidali dalla nascita:
- Fisico: 23 giorni - influenza forza, resistenza, coordinazione
- Emotivo: 28 giorni - influenza umore, creatività, stabilità
- Intellettuale: 33 giorni - influenza concentrazione, memoria, tattica

Formula: sin(2π × giorni_dalla_nascita / periodo) × 100
Valore da -100 a +100:
  > 50: Eccellente
  0-50: Buono
  -50-0: Basso
  < -50: Critico

References:
- https://www.biorhythm-calculator.net/
- https://en.wikipedia.org/wiki/Biorhythm_(pseudoscience)
"""

import math
from datetime import datetime, date, timezone
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class BiorhythmScore:
    """Punteggi dei tre bioritmi di un calciatore"""
    physical: float  # -100 to +100
    emotional: float  # -100 to +100
    intellectual: float  # -100 to +100
    overall: float  # Media ponderata
    status: str  # "excellent", "good", "low", "critical"


# Costanti dei cicli biorhythmici (in giorni)
PHYSICAL_CYCLE = 23
EMOTIONAL_CYCLE = 28
INTELLECTUAL_CYCLE = 33

# Pesi per calcolo overall (fisico più importante per calciatori)
PHYSICAL_WEIGHT = 0.5
EMOTIONAL_WEIGHT = 0.3
INTELLECTUAL_WEIGHT = 0.2


def calculate_days_since_birth(birthdate: date, target_date: date = None) -> int:
    """
    Calcola i giorni trascorsi dalla nascita fino alla data target.

    Args:
        birthdate: Data di nascita del calciatore
        target_date: Data per cui calcolare il bioritmo (default: oggi)

    Returns:
        Numero di giorni dalla nascita
    """
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    delta = target_date - birthdate
    return delta.days


def calculate_biorhythm_value(days_since_birth: int, cycle_length: int) -> float:
    """
    Calcola il valore di un singolo bioritmo usando la formula sinusoidale.

    Args:
        days_since_birth: Giorni dalla nascita
        cycle_length: Lunghezza del ciclo in giorni (23, 28, o 33)

    Returns:
        Valore del bioritmo da -100 a +100
    """
    # Formula: sin(2π × giorni / periodo) × 100
    radians = 2 * math.pi * days_since_birth / cycle_length
    value = math.sin(radians) * 100
    return round(value, 2)


def get_biorhythm_status(overall_score: float) -> str:
    """
    Determina lo stato generale basato sul punteggio overall.

    Args:
        overall_score: Punteggio medio ponderato

    Returns:
        Status: "excellent", "good", "low", "critical"
    """
    if overall_score > 50:
        return "excellent"
    elif overall_score > 0:
        return "good"
    elif overall_score > -50:
        return "low"
    else:
        return "critical"


def calculate_player_biorhythm(
    birthdate: date,
    target_date: date = None
) -> BiorhythmScore:
    """
    Calcola tutti i bioritmi di un calciatore per una data specifica.

    Args:
        birthdate: Data di nascita del calciatore
        target_date: Data per cui calcolare (default: oggi)

    Returns:
        BiorhythmScore con tutti i valori calcolati
    """
    days = calculate_days_since_birth(birthdate, target_date)

    # Calcola i tre bioritmi
    physical = calculate_biorhythm_value(days, PHYSICAL_CYCLE)
    emotional = calculate_biorhythm_value(days, EMOTIONAL_CYCLE)
    intellectual = calculate_biorhythm_value(days, INTELLECTUAL_CYCLE)

    # Calcola punteggio overall (media ponderata)
    overall = (
        physical * PHYSICAL_WEIGHT +
        emotional * EMOTIONAL_WEIGHT +
        intellectual * INTELLECTUAL_WEIGHT
    )
    overall = round(overall, 2)

    # Determina status
    status = get_biorhythm_status(overall)

    return BiorhythmScore(
        physical=physical,
        emotional=emotional,
        intellectual=intellectual,
        overall=overall,
        status=status
    )


def get_critical_days(
    birthdate: date,
    start_date: date,
    days_ahead: int = 7
) -> Dict[str, list]:
    """
    Identifica i giorni critici (quando un bioritmo attraversa lo zero).

    Args:
        birthdate: Data di nascita
        start_date: Data di inizio
        days_ahead: Quanti giorni guardare avanti

    Returns:
        Dict con liste di date critiche per ogni tipo di bioritmo
    """
    critical = {
        'physical': [],
        'emotional': [],
        'intellectual': []
    }

    for i in range(days_ahead):
        current_date = start_date + datetime.timedelta(days=i)
        days = calculate_days_since_birth(birthdate, current_date)

        # Un giorno è critico se il bioritmo è vicino a zero (±5)
        physical = calculate_biorhythm_value(days, PHYSICAL_CYCLE)
        emotional = calculate_biorhythm_value(days, EMOTIONAL_CYCLE)
        intellectual = calculate_biorhythm_value(days, INTELLECTUAL_CYCLE)

        if abs(physical) < 5:
            critical['physical'].append(current_date)
        if abs(emotional) < 5:
            critical['emotional'].append(current_date)
        if abs(intellectual) < 5:
            critical['intellectual'].append(current_date)

    return critical


def get_biorhythm_forecast(
    birthdate: date,
    start_date: date,
    days_ahead: int = 7
) -> list[Tuple[date, BiorhythmScore]]:
    """
    Calcola la previsione dei bioritmi per i prossimi giorni.

    Args:
        birthdate: Data di nascita
        start_date: Data di inizio
        days_ahead: Quanti giorni prevedere

    Returns:
        Lista di tuple (data, BiorhythmScore)
    """
    forecast = []

    for i in range(days_ahead):
        target_date = start_date + datetime.timedelta(days=i)
        score = calculate_player_biorhythm(birthdate, target_date)
        forecast.append((target_date, score))

    return forecast


def compare_team_biorhythms(
    team_birthdates: list[date],
    match_date: date
) -> Dict:
    """
    Calcola i bioritmi medi di una squadra per una partita.

    Args:
        team_birthdates: Lista delle date di nascita dei giocatori
        match_date: Data della partita

    Returns:
        Dict con medie di squadra e distribuzione
    """
    if not team_birthdates:
        return {
            'avg_physical': 0,
            'avg_emotional': 0,
            'avg_intellectual': 0,
            'avg_overall': 0,
            'players_excellent': 0,
            'players_good': 0,
            'players_low': 0,
            'players_critical': 0
        }

    scores = [calculate_player_biorhythm(bd, match_date) for bd in team_birthdates]

    # Calcola medie
    avg_physical = sum(s.physical for s in scores) / len(scores)
    avg_emotional = sum(s.emotional for s in scores) / len(scores)
    avg_intellectual = sum(s.intellectual for s in scores) / len(scores)
    avg_overall = sum(s.overall for s in scores) / len(scores)

    # Conta giocatori per status
    status_counts = {
        'excellent': sum(1 for s in scores if s.status == 'excellent'),
        'good': sum(1 for s in scores if s.status == 'good'),
        'low': sum(1 for s in scores if s.status == 'low'),
        'critical': sum(1 for s in scores if s.status == 'critical')
    }

    return {
        'avg_physical': round(avg_physical, 2),
        'avg_emotional': round(avg_emotional, 2),
        'avg_intellectual': round(avg_intellectual, 2),
        'avg_overall': round(avg_overall, 2),
        'players_excellent': status_counts['excellent'],
        'players_good': status_counts['good'],
        'players_low': status_counts['low'],
        'players_critical': status_counts['critical'],
        'total_players': len(team_birthdates)
    }
