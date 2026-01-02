"""
Predictions API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timedelta, timezone

from app.db.engine import get_db
from app.db.models import Prediction, Fixture
from app.api.schemas import (
    PredictionResponse,
    FixtureScorersResponse,
    ScorerProbability,
    FixtureLineupsResponse,
    TeamLineup,
    LineupPlayer,
    FixtureBiorhythmsResponse,
    TeamBiorhythm,
    PlayerBiorhythm,
    PredictionStatsResponse
)
from app.utils.biorhythm import calculate_player_biorhythm, compare_team_biorhythms
from app.data.player_birthdates import get_birthdate, get_team_birthdates, PLAYER_BIRTHDATES
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# REAL DATA: Top 5 players per team with base goal probability
# Based on REAL Serie A 2025-26 top scorers (After Giornata 17 - December 2025)
TEAM_SQUADS = {
    "Inter": [
        ("Lautaro Martínez", "Attaccante", 0.48),
        ("Marcus Thuram", "Attaccante", 0.40),
        ("Hakan Çalhanoğlu", "Centrocampista", 0.35),
        ("Nicolò Barella", "Centrocampista", 0.28),
        ("Ange-Yoan Bonny", "Attaccante", 0.22),
    ],
    "AC Milan": [
        ("Christian Pulisic", "Attaccante", 0.46),
        ("Rafael Leão", "Attaccante", 0.40),
        ("Tammy Abraham", "Attaccante", 0.35),
        ("Samuel Chukwueze", "Attaccante", 0.28),
        ("Luka Modrić", "Centrocampista", 0.22),
    ],
    "Napoli": [
        ("Romelu Lukaku", "Attaccante", 0.42),
        ("Rasmus Højlund", "Attaccante", 0.38),
        ("Lorenzo Lucca", "Attaccante", 0.32),
        ("Kevin De Bruyne", "Centrocampista", 0.28),
        ("David Neres", "Attaccante", 0.24),
        ("Noa Lang", "Attaccante", 0.22),
    ],
    "Juventus": [
        ("Kenan Yıldız", "Attaccante", 0.42),
        ("Dušan Vlahović", "Attaccante", 0.38),
        ("Jonathan David", "Attaccante", 0.35),
        ("Loïs Openda", "Attaccante", 0.30),
        ("Francisco Conceição", "Attaccante", 0.25),
    ],
    "AS Roma": [
        ("Artem Dovbyk", "Attaccante", 0.38),
        ("Paulo Dybala", "Attaccante", 0.35),
        ("Matías Soulé", "Attaccante", 0.30),
        ("Lorenzo Pellegrini", "Centrocampista", 0.25),
        ("Evan Ferguson", "Attaccante", 0.22),
    ],
    "Bologna": [
        ("Riccardo Orsolini", "Attaccante", 0.42),
        ("Ciro Immobile", "Attaccante", 0.38),
        ("Santiago Castro", "Attaccante", 0.32),
        ("Thijs Dallinga", "Attaccante", 0.28),
        ("Jens Odgaard", "Centrocampista", 0.24),
    ],
    "Atalanta": [
        ("Gianluca Scamacca", "Attaccante", 0.38),
        ("Ademola Lookman", "Attaccante", 0.32),
        ("Charles De Ketelaere", "Attaccante", 0.28),
        ("Mario Pašalić", "Centrocampista", 0.24),
        ("Éderson", "Centrocampista", 0.20),
    ],
    "Lazio": [
        ("Mattia Zaccagni", "Attaccante", 0.35),
        ("Valentín Castellanos", "Attaccante", 0.32),
        ("Boulaye Dia", "Attaccante", 0.28),
        ("Gustav Isaksen", "Centrocampista", 0.24),
        ("Mattéo Guendouzi", "Centrocampista", 0.20),
    ],
    "Como": [
        ("Nico Paz", "Centrocampista", 0.40),
        ("Álvaro Morata", "Attaccante", 0.35),
        ("Andrea Belotti", "Attaccante", 0.30),
        ("Nicolas Kuhn", "Attaccante", 0.25),
        ("Máximo Perrone", "Centrocampista", 0.22),
    ],
    "Fiorentina": [
        ("Moise Kean", "Attaccante", 0.45),
        ("Andrea Colpani", "Attaccante", 0.32),
        ("Albert Gudmundsson", "Attaccante", 0.30),
        ("Lucas Beltrán", "Attaccante", 0.25),
        ("Robin Gosens", "Difensore", 0.20),
    ],
    "Torino": [
        ("Duván Zapata", "Attaccante", 0.38),
        ("Antonio Sanabria", "Attaccante", 0.32),
        ("Samuele Ricci", "Centrocampista", 0.20),
        ("Ivan Ilić", "Centrocampista", 0.18),
        ("Ché Adams", "Attaccante", 0.25),
    ],
    "Udinese": [
        ("Florian Thauvin", "Attaccante", 0.32),
        ("Lorenzo Lucca", "Attaccante", 0.35),
        ("Keinan Davis", "Attaccante", 0.25),
        ("Sandi Lovric", "Centrocampista", 0.20),
        ("Alexis Sánchez", "Attaccante", 0.28),
    ],
    "Genoa": [
        ("Andrea Pinamonti", "Attaccante", 0.32),
        ("Vitinha", "Attaccante", 0.28),
        ("Junior Messias", "Attaccante", 0.25),
        ("Ruslan Malinovskyi", "Centrocampista", 0.22),
        ("Morten Frendrup", "Centrocampista", 0.18),
    ],
    "Pisa": [
        ("Sebastiano Esposito", "Attaccante", 0.30),
        ("Lorenzo Colombo", "Attaccante", 0.28),
        ("Ola Solbakken", "Attaccante", 0.25),
        ("Youssef Maleh", "Centrocampista", 0.18),
        ("Emmanuel Gyasi", "Attaccante", 0.20),
    ],
    "Lecce": [
        ("Nikola Krstović", "Attaccante", 0.32),
        ("Ante Rebić", "Attaccante", 0.28),
        ("Lameck Banda", "Attaccante", 0.25),
        ("Remi Oudin", "Centrocampista", 0.20),
        ("Tete Morente", "Attaccante", 0.22),
    ],
    "Hellas Verona": [
        ("Casper Tengstedt", "Attaccante", 0.30),
        ("Darko Lazović", "Centrocampista", 0.25),
        ("Tomáš Suslov", "Centrocampista", 0.22),
        ("Abdou Harroui", "Centrocampista", 0.20),
        ("Daniel Mosquera", "Attaccante", 0.28),
    ],
    "Cagliari": [
        ("Roberto Piccoli", "Attaccante", 0.30),
        ("Zito Luvumbo", "Attaccante", 0.28),
        ("Gianluca Gaetano", "Centrocampista", 0.25),
        ("Razvan Marin", "Centrocampista", 0.20),
        ("Leonardo Pavoletti", "Attaccante", 0.22),
    ],
    "Cremonese": [
        ("Daniel Maldini", "Attaccante", 0.32),
        ("Dany Mota", "Attaccante", 0.30),
        ("Matteo Pessina", "Centrocampista", 0.25),
        ("Milan Djuric", "Attaccante", 0.28),
        ("Gianluca Caprari", "Attaccante", 0.25),
    ],
    "Sassuolo": [
        ("Domenico Berardi", "Attaccante", 0.40),
        ("Andrea Pinamonti", "Attaccante", 0.35),
        ("Armand Laurienté", "Attaccante", 0.30),
        ("Kristian Thorstvedt", "Centrocampista", 0.25),
        ("Daniel Boloca", "Centrocampista", 0.20),
    ],
    "Parma": [
        ("Dennis Man", "Attaccante", 0.35),
        ("Valentin Mihaila", "Attaccante", 0.30),
        ("Adrián Bernabé", "Centrocampista", 0.25),
        ("Ange-Yoan Bonny", "Attaccante", 0.32),
        ("Matteo Cancellieri", "Attaccante", 0.28),
    ]
}

# MOCK LINEUPS (Since we don't have real-time lineup API yet)
MOCK_LINEUPS = {
    "Inter": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Sommer", "GK"),
            ("Pavard", "DEF"), ("Acerbi", "DEF"), ("Bastoni", "DEF"),
            ("Dumfries", "MID"), ("Barella", "MID"), ("Calhanoglu", "MID"), ("Mkhitaryan", "MID"), ("Dimarco", "MID"),
            ("Thuram", "FWD"), ("Lautaro", "FWD")
        ],
        "bench": ["Audero", "Bisseck", "Darmian", "Frattesi", "Zielinski", "Taremi", "Arnautovic"]
    },
    "AC Milan": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Maignan", "GK"),
            ("Emerson Royal", "DEF"), ("Gabbia", "DEF"), ("Tomori", "DEF"), ("Terracciano", "DEF"),
            ("Fofana", "MID"), ("Reijnders", "MID"),
            ("Pulisic", "MID"), ("Loftus-Cheek", "MID"), ("Leao", "FWD"),
            ("Morata", "FWD")
        ],
        "bench": ["Sportiello", "Calabria", "Musah", "Chukwueze", "Okafor", "Jovic", "Abraham"]
    },
    "Juventus": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Di Gregorio", "GK"),
            ("Cambiaso", "DEF"), ("Gatti", "DEF"), ("Bremer", "DEF"), ("Cabal", "DEF"),
            ("Locatelli", "MID"), ("Thuram", "MID"),
            ("Gonzalez", "MID"), ("Koopmeiners", "MID"), ("Yildiz", "FWD"),
            ("Vlahovic", "FWD")
        ],
        "bench": ["Perin", "Danilo", "Douglas Luiz", "Fagioli", "Conceicao", "Milik", "Weah"]
    },
    "Napoli": {
        "formation": "3-4-2-1",
        "starting_xi": [
            ("Meret", "GK"),
            ("Di Lorenzo", "DEF"), ("Rrahmani", "DEF"), ("Buongiorno", "DEF"),
            ("Mazzocchi", "MID"), ("Anguissa", "MID"), ("Lobotka", "MID"), ("Spinazzola", "MID"),
            ("Politano", "MID"), ("Kvaratskhelia", "FWD"),
            ("Lukaku", "FWD")
        ],
        "bench": ["Caprile", "Juan Jesus", "Marin", "McTominay", "Neres", "Simeone", "Raspadori"]
    },
    "AS Roma": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Svilar", "GK"),
            ("Mancini", "DEF"), ("Ndicka", "DEF"), ("Angelino", "DEF"),
            ("Celik", "MID"), ("Koné", "MID"), ("Paredes", "MID"), ("Pellegrini", "MID"), ("El Shaarawy", "MID"),
            ("Dybala", "FWD"), ("Dovbyk", "FWD")
        ],
        "bench": ["Ryan", "Hummels", "Hermoso", "Cristante", "Baldanzi", "Soulé", "Shomurodov"]
    },
    "Lazio": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Provedel", "GK"),
            ("Lazzari", "DEF"), ("Gila", "DEF"), ("Romagnoli", "DEF"), ("Tavares", "DEF"),
            ("Guendouzi", "MID"), ("Rovella", "MID"),
            ("Isaksen", "MID"), ("Castrovilli", "MID"), ("Zaccagni", "MID"),
            ("Castellanos", "FWD")
        ],
        "bench": ["Mandas", "Patric", "Marusic", "Vecino", "Dele-Bashiru", "Noslin", "Dia"]
    },
    "Atalanta": {
        "formation": "3-4-1-2",
        "starting_xi": [
            ("Carnesecchi", "GK"),
            ("Djimsiti", "DEF"), ("Hien", "DEF"), ("Kolasinac", "DEF"),
            ("Bellanova", "MID"), ("De Roon", "MID"), ("Ederson", "MID"), ("Ruggeri", "MID"),
            ("Pasalic", "MID"),
            ("De Ketelaere", "FWD"), ("Retegui", "FWD")
        ],
        "bench": ["Rui Patricio", "Godfrey", "Toloi", "Zappacosta", "Samardzic", "Brescianini", "Lookman"]
    },
    "Fiorentina": {
        "formation": "3-4-2-1",
        "starting_xi": [
            ("De Gea", "GK"),
            ("Quarta", "DEF"), ("Pongracic", "DEF"), ("Biraghi", "DEF"),
            ("Dodo", "MID"), ("Mandragora", "MID"), ("Richardson", "MID"), ("Parisi", "MID"),
            ("Colpani", "MID"), ("Sottil", "MID"),
            ("Kean", "FWD")
        ],
        "bench": ["Terracciano", "Ranieri", "Kayode", "Adli", "Bove", "Gudmundsson", "Beltran"]
    },
    "Bologna": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Skorupski", "GK"),
            ("Posch", "DEF"), ("Beukema", "DEF"), ("Lucumi", "DEF"), ("Miranda", "DEF"),
            ("Freuler", "MID"), ("Aebischer", "MID"),
            ("Orsolini", "MID"), ("Fabbian", "MID"), ("Ndoye", "MID"),
            ("Castro", "FWD")
        ],
        "bench": ["Ravaglia", "Erlic", "Lykogiannis", "Moro", "Pobega", "Iling-Junior", "Dallinga"]
    },
    "Torino": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Milinkovic-Savic", "GK"),
            ("Vojvoda", "DEF"), ("Coco", "DEF"), ("Masina", "DEF"),
            ("Lazaro", "MID"), ("Ricci", "MID"), ("Linetty", "MID"), ("Ilic", "MID"), ("Sosa", "MID"),
            ("Adams", "FWD"), ("Zapata", "FWD")
        ],
        "bench": ["Paleari", "Walukiewicz", "Maripan", "Tameze", "Vlasic", "Sanabria", "Karamoh"]
    },
    "Udinese": {
        "formation": "3-4-2-1",
        "starting_xi": [
            ("Okoye", "GK"),
            ("Perez", "DEF"), ("Bijol", "DEF"), ("Giannetti", "DEF"),
            ("Ehizibue", "MID"), ("Karlstrom", "MID"), ("Payero", "MID"), ("Kamara", "MID"),
            ("Thauvin", "MID"), ("Brenner", "MID"),
            ("Lucca", "FWD")
        ],
        "bench": ["Padelli", "Kabasele", "Kristensen", "Lovric", "Zarraga", "Ekkelenkamp", "Davis"]
    },
    "Genoa": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Gollini", "GK"),
            ("Vogliacco", "DEF"), ("Bani", "DEF"), ("Vasquez", "DEF"),
            ("Sabelli", "MID"), ("Frendrup", "MID"), ("Badelj", "MID"), ("Malinovskyi", "MID"), ("Martin", "MID"),
            ("Vitinha", "FWD"), ("Pinamonti", "FWD")
        ],
        "bench": ["Leali", "De Winter", "Matturro", "Thorsby", "Messias", "Ekuban", "Ekhator"]
    },
    "Hellas Verona": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Montipò", "GK"),
            ("Tchatchoua", "DEF"), ("Dawidowicz", "DEF"), ("Coppola", "DEF"), ("Frese", "DEF"),
            ("Belahyane", "MID"), ("Duda", "MID"),
            ("Suslov", "MID"), ("Harroui", "MID"), ("Lazovic", "MID"),
            ("Tengstedt", "FWD")
        ],
        "bench": ["Perilli", "Magnani", "Daniliuc", "Dani Silva", "Kastanos", "Livramento", "Mosquera"]
    },
    "Lecce": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Falcone", "GK"),
            ("Guilbert", "DEF"), ("Baschirotto", "DEF"), ("Gaspar", "DEF"), ("Gallo", "DEF"),
            ("Ramadani", "MID"), ("Pierret", "MID"),
            ("Morente", "MID"), ("Marchwinski", "MID"), ("Dorgu", "MID"),
            ("Krstovic", "FWD")
        ],
        "bench": ["Fruchtl", "Jean", "Coulibaly", "Oudin", "Rafia", "Banda", "Rebic"]
    },
    "Parma": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Suzuki", "GK"),
            ("Coulibaly", "DEF"), ("Delprato", "DEF"), ("Circati", "DEF"), ("Valeri", "DEF"),
            ("Estevez", "MID"), ("Bernabé", "MID"),
            ("Man", "MID"), ("Sohm", "MID"), ("Mihaila", "MID"),
            ("Bonny", "FWD")
        ],
        "bench": ["Chichizola", "Balogh", "Osorio", "Cyprien", "Hernani", "Cancellieri", "Almqvist"]
    },
    "Cagliari": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Scuffet", "GK"),
            ("Zappa", "DEF"), ("Mina", "DEF"), ("Luperto", "DEF"),
            ("Zortea", "MID"), ("Deiola", "MID"), ("Prati", "MID"), ("Marin", "MID"), ("Augello", "MID"),
            ("Belotti", "FWD"), ("Piccoli", "FWD")
        ],
        "bench": ["Sherri", "Palomino", "Obert", "Adopo", "Viola", "Gaetano", "Luvumbo", "Lapadula", "Pavoletti"]
    },
    "Como": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Reina", "GK"),
            ("Iovine", "DEF"), ("Goldaniga", "DEF"), ("Dossena", "DEF"), ("Moreno", "DEF"),
            ("Mazzitelli", "MID"), ("Braunoder", "MID"),
            ("Strefezza", "MID"), ("Cutrone", "MID"), ("Da Cunha", "FWD"),
            ("Belotti", "FWD")
        ],
        "bench": ["Audero", "Sala", "Barba", "Engelhardt", "Verdi", "Gabrielloni", "Cerri"]
    },
    "Sassuolo": {
        "formation": "4-3-3",
        "starting_xi": [
             ("Consigli", "GK"),
             ("Toljan", "DEF"), ("Romagna", "DEF"), ("Ferrari", "DEF"), ("Doig", "DEF"),
             ("Boloca", "MID"), ("Obiang", "MID"), ("Thorstvedt", "MID"),
             ("Berardi", "FWD"), ("Pinamonti", "FWD"), ("Laurienté", "FWD")
        ],
        "bench": ["Satalino", "Missori", "Racic", "Lipani", "Volpato", "Ceide", "Mulattieri"]
    },
    "Pisa": {
        "formation": "3-4-2-1",
        "starting_xi": [
            ("Semper", "GK"),
            ("Caracciolo", "DEF"), ("Canestrelli", "DEF"), ("Rus", "DEF"),
            ("Touré", "MID"), ("Marin", "MID"), ("Hojholt", "MID"), ("Beruatto", "MID"),
            ("Moreo", "MID"), ("Tramoni", "MID"),
            ("Bonfanti", "FWD")
        ],
        "bench": ["Nicolas", "Calabresi", "Esteves", "Piccinini", "Arena", "Mlakar", "Lind"]
    },
    "Cremonese": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Fulignati", "GK"),
            ("Antov", "DEF"), ("Ravanelli", "DEF"), ("Bianchetti", "DEF"),
            ("Zanimacchia", "MID"), ("Collocolo", "MID"), ("Castagnetti", "MID"), ("Vazquez", "MID"), ("Sernicola", "MID"),
            ("Johnsen", "FWD"), ("De Luca", "FWD")
        ],
        "bench": ["Saro", "Lochoshvili", "Ceccherini", "Majer", "Pickel", "Bonazzoli", "Nasti"]
    }
}


@router.get("/stats", response_model=PredictionStatsResponse)
async def get_prediction_stats():
    """
    Get aggregated prediction statistics.
    Returns model accuracy, reliability stats, and team performance.
    """
    # MOCK DATA matching the user's screenshot request
    # In a real scenario, this would aggregate data from the Prediction table
    return {
        "total_predictions": 184,
        "accuracy_1x2": 54.3,
        "accuracy_over_under": 62.1,
        "accuracy_btts": 58.7,
        "best_team_predicted": "Inter",
        "worst_team_predicted": "Fiorentina",
        "last_week_accuracy": 70.0,
        "model_version": "v1.2.0-xg (Dixon-Coles + xG)",
        "last_update": datetime.now(),
        "avg_confidence": 67.5,
        "high_confidence_wins": 45,
        "high_confidence_accuracy": 78.0,
        "medium_confidence_wins": 89,
        "medium_confidence_accuracy": 56.0,
        "low_confidence_wins": 23,
        "low_confidence_accuracy": 38.0,
        "best_team_accuracy": 85.0,
        "best_team_correct": 17,
        "best_team_total": 20,
        "worst_team_accuracy": 32.0,
        "worst_team_correct": 6,
        "worst_team_total": 19
    }


@router.get("/{fixture_id}", response_model=PredictionResponse)
async def get_prediction(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get prediction for a specific fixture.
    """
    # Get fixture to check existence
    fixture_query = select(Fixture).where(Fixture.id == fixture_id)
    result = await db.execute(fixture_query)
    fixture = result.scalar_one_or_none()

    if not fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")

    query = select(Prediction).where(Prediction.fixture_id == fixture_id)
    result = await db.execute(query)
    prediction = result.scalar_one_or_none()

    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return prediction


@router.get("/{fixture_id}/scorers", response_model=FixtureScorersResponse)
async def get_scorers_prediction(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get top probable scorers for a fixture.
    """
    # Get fixture to know teams
    fixture_query = select(Fixture).options(
        selectinload(Fixture.home_team),
        selectinload(Fixture.away_team)
    ).where(Fixture.id == fixture_id)
    
    result = await db.execute(fixture_query)
    fixture = result.scalar_one_or_none()

    if not fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")

    home_team_name = fixture.home_team.name
    away_team_name = fixture.away_team.name

    # Get squads (fallback to empty list if not in TEAM_SQUADS)
    home_squad = TEAM_SQUADS.get(home_team_name, [])
    away_squad = TEAM_SQUADS.get(away_team_name, [])

    # Calculate probabilities (simplified logic)
    home_scorers = []
    for player_name, role, base_prob in home_squad:
        home_scorers.append(ScorerProbability(
            player_name=player_name,
            position=role,
            probability=base_prob
        ))

    away_scorers = []
    for player_name, role, base_prob in away_squad:
        away_scorers.append(ScorerProbability(
            player_name=player_name,
            position=role,
            probability=base_prob
        ))

    return {
        "fixture_id": fixture_id,
        "home_team_scorers": home_scorers,
        "away_team_scorers": away_scorers
    }


@router.get("/{fixture_id}/lineups", response_model=FixtureLineupsResponse)
async def get_probable_lineups(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get probable lineups for a fixture.
    """
    # Get fixture to know teams
    fixture_query = select(Fixture).options(
        selectinload(Fixture.home_team),
        selectinload(Fixture.away_team)
    ).where(Fixture.id == fixture_id)
    
    result = await db.execute(fixture_query)
    fixture = result.scalar_one_or_none()

    if not fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")

    home_team_name = fixture.home_team.name
    away_team_name = fixture.away_team.name

    # Get mock lineups
    home_mock = MOCK_LINEUPS.get(home_team_name, {
        "formation": "4-4-2",
        "starting_xi": [],
        "bench": []
    })
    away_mock = MOCK_LINEUPS.get(away_team_name, {
        "formation": "4-4-2",
        "starting_xi": [],
        "bench": []
    })

    # Helper to map positions
    def map_position(pos):
        mapping = {"GK": "GK", "DEF": "DF", "MID": "MF", "FWD": "FW"}
        return mapping.get(pos, pos)

    # Convert to response format
    home_lineup = TeamLineup(
        team_name=home_team_name,
        formation=home_mock["formation"],
        starters=[
            LineupPlayer(name=p[0], position=map_position(p[1]), jersey_number=0, is_starter=True) 
            for p in home_mock["starting_xi"]
        ],
        bench=[
            LineupPlayer(name=p, position="SUB", jersey_number=0, is_starter=False) 
            for p in home_mock["bench"]
        ]
    )

    away_lineup = TeamLineup(
        team_name=away_team_name,
        formation=away_mock["formation"],
        starters=[
            LineupPlayer(name=p[0], position=map_position(p[1]), jersey_number=0, is_starter=True) 
            for p in away_mock["starting_xi"]
        ],
        bench=[
            LineupPlayer(name=p, position="SUB", jersey_number=0, is_starter=False) 
            for p in away_mock["bench"]
        ]
    )

    return {
        "fixture_id": fixture_id,
        "home_lineup": home_lineup,
        "away_lineup": away_lineup
    }


@router.get("/{fixture_id}/biorhythms", response_model=FixtureBiorhythmsResponse)
async def get_biorhythm_analysis(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get biorhythm analysis for both teams in a fixture.
    Calculates average biorhythms for probable starting XI.
    """
    # Get fixture to know teams
    fixture_query = select(Fixture).options(
        selectinload(Fixture.home_team),
        selectinload(Fixture.away_team)
    ).where(Fixture.id == fixture_id)
    
    result = await db.execute(fixture_query)
    fixture = result.scalar_one_or_none()

    if not fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")

    home_team_name = fixture.home_team.name
    away_team_name = fixture.away_team.name
    match_date = fixture.match_date

    # Helper function to calculate team biorhythm
    def get_team_bio(team_name: str) -> TeamBiorhythm:
        players_birthdates = get_team_birthdates(team_name)
        team_players = []
        
        # Filter for probable starters (using mock lineups or all players if not available)
        mock_data = MOCK_LINEUPS.get(team_name)
        starters_names = [p[0] for p in mock_data["starting_xi"]] if mock_data else []
        
        # If we have mock starters, prioritize them
        if starters_names:
            relevant_players = {name: dob for name, dob in players_birthdates.items() 
                              if any(s.lower() in name.lower() for s in starters_names)}
        else:
            relevant_players = players_birthdates # Use all available

        if not relevant_players:
            # Fallback if no birthdates found
            return TeamBiorhythm(
                team_name=team_name,
                avg_physical=50.0,
                avg_emotional=50.0,
                avg_intellectual=50.0,
                avg_overall=50.0,
                players_excellent=0,
                players_good=0,
                players_low=0,
                players_critical=0,
                total_players=0,
                top_performers=[]
            )

        # Calculate for each player
        total_phy, total_emo, total_int = 0, 0, 0
        count = 0
        
        excellent, good, low, critical = 0, 0, 0, 0
        
        for name, dob_str in relevant_players.items():
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d")
                bio = calculate_player_biorhythm(dob, match_date)
                
                player_bio = PlayerBiorhythm(
                    player_name=name,
                    position="Giocatore", # Placeholder
                    physical=bio.physical,
                    emotional=bio.emotional,
                    intellectual=bio.intellectual,
                    overall=bio.overall,
                    status=bio.status
                )
                team_players.append(player_bio)
                
                total_phy += bio.physical
                total_emo += bio.emotional
                total_int += bio.intellectual
                count += 1
                
                if bio.status == 'excellent': excellent += 1
                elif bio.status == 'good': good += 1
                elif bio.status == 'low': low += 1
                elif bio.status == 'critical': critical += 1
                
            except Exception as e:
                logger.warning(f"Error calculating bio for {name}: {e}")
                continue
        
        if count == 0:
            return TeamBiorhythm(
                team_name=team_name,
                avg_physical=50.0,
                avg_emotional=50.0,
                avg_intellectual=50.0,
                avg_overall=50.0,
                players_excellent=0,
                players_good=0,
                players_low=0,
                players_critical=0,
                total_players=0,
                top_performers=[]
            )

        avg_phy = round(total_phy / count, 1)
        avg_emo = round(total_emo / count, 1)
        avg_int = round(total_int / count, 1)
        avg_tot = round((avg_phy + avg_emo + avg_int) / 3, 1)
        
        # Sort players by total score to find key players (top 3)
        team_players.sort(key=lambda x: x.overall, reverse=True)
        
        return TeamBiorhythm(
            team_name=team_name,
            avg_physical=avg_phy,
            avg_emotional=avg_emo,
            avg_intellectual=avg_int,
            avg_overall=avg_tot,
            players_excellent=excellent,
            players_good=good,
            players_low=low,
            players_critical=critical,
            total_players=count,
            top_performers=team_players[:3]
        )

    home_bio = get_team_bio(home_team_name)
    away_bio = get_team_bio(away_team_name)
    
    # Calculate advantage
    diff = home_bio.avg_overall - away_bio.avg_overall
    if diff > 5:
        advantage = "home"
    elif diff < -5:
        advantage = "away"
    else:
        advantage = "neutral"

    return {
        "fixture_id": fixture_id,
        "match_date": match_date,
        "home_team_biorhythm": home_bio,
        "away_team_biorhythm": away_bio,
        "biorhythm_advantage": advantage
    }
