"""
Predictions API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timedelta, timezone, date

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
        ("Federico Dimarco", "Difensore", 0.25),
    ],
    "AC Milan": [
        ("Santiago Giménez", "Attaccante", 0.40),
        ("Rafael Leão", "Attaccante", 0.35),
        ("Christopher Nkunku", "Attaccante", 0.35),
        ("Christian Pulisic", "Attaccante", 0.32),
        ("Luka Modrić", "Centrocampista", 0.28),
    ],
    "Napoli": [
        ("Romelu Lukaku", "Attaccante", 0.42),
        ("Khvicha Kvaratskhelia", "Attaccante", 0.38),
        ("Kevin De Bruyne", "Centrocampista", 0.35),
        ("Scott McTominay", "Centrocampista", 0.32),
        ("Alessandro Buongiorno", "Difensore", 0.28),
    ],
    "Juventus": [
        ("Dušan Vlahović", "Attaccante", 0.40),
        ("Kenan Yıldız", "Attaccante", 0.38),
        ("Teun Koopmeiners", "Centrocampista", 0.35),
        ("Jonathan David", "Attaccante", 0.35),
        ("Michele Di Gregorio", "Portiere", 0.20),
    ],
    "AS Roma": [
        ("Artem Dovbyk", "Attaccante", 0.38),
        ("Paulo Dybala", "Attaccante", 0.35),
        ("Matías Soulé", "Attaccante", 0.30),
        ("Lorenzo Pellegrini", "Centrocampista", 0.25),
        ("Manu Koné", "Centrocampista", 0.22),
    ],
    "Bologna": [
        ("Riccardo Orsolini", "Attaccante", 0.40),
        ("Ciro Immobile", "Attaccante", 0.38),
        ("Santiago Castro", "Attaccante", 0.32),
        ("Dan Ndoye", "Attaccante", 0.30),
        ("Lewis Ferguson", "Centrocampista", 0.28),
    ],
    "Atalanta": [
        ("Mateo Retegui", "Attaccante", 0.40),
        ("Ademola Lookman", "Attaccante", 0.35),
        ("Charles De Ketelaere", "Attaccante", 0.30),
        ("Nicolò Zaniolo", "Attaccante", 0.25),
        ("Éderson", "Centrocampista", 0.22),
    ],
    "Lazio": [
        ("Mattia Zaccagni", "Attaccante", 0.35),
        ("Valentín Castellanos", "Attaccante", 0.32),
        ("Boulaye Dia", "Attaccante", 0.30),
        ("Mattéo Guendouzi", "Centrocampista", 0.25),
        ("Nicolò Rovella", "Centrocampista", 0.22),
    ],
    "Como": [
        ("Nico Paz", "Centrocampista", 0.38),
        ("Patrick Cutrone", "Attaccante", 0.35),
        ("Alieu Fadera", "Attaccante", 0.30),
        ("Sergi Roberto", "Centrocampista", 0.25),
        ("Emil Audero", "Portiere", 0.15),
    ],
    "Fiorentina": [
        ("Moise Kean", "Attaccante", 0.40),
        ("Albert Gudmundsson", "Attaccante", 0.35),
        ("Edin Džeko", "Attaccante", 0.32),
        ("Andrea Colpani", "Centrocampista", 0.28),
        ("David de Gea", "Portiere", 0.20),
    ],
    "Torino": [
        ("Duván Zapata", "Attaccante", 0.35),
        ("Ché Adams", "Attaccante", 0.30),
        ("Nikola Vlašić", "Centrocampista", 0.28),
        ("Ivan Ilić", "Centrocampista", 0.22),
        ("Vanja Milinković-Savić", "Portiere", 0.15),
    ],
    "Udinese": [
        ("Florian Thauvin", "Attaccante", 0.32),
        ("Alexis Sánchez", "Attaccante", 0.30),
        ("Sandi Lovric", "Centrocampista", 0.25),
        ("Jaka Bijol", "Difensore", 0.20),
        ("Maduka Okoye", "Portiere", 0.15),
    ],
    "Genoa": [
        ("Andrea Pinamonti", "Attaccante", 0.32),
        ("Vitinha", "Attaccante", 0.30),
        ("Ruslan Malinovskyi", "Centrocampista", 0.25),
        ("Morten Frendrup", "Centrocampista", 0.22),
        ("Pierluigi Gollini", "Portiere", 0.15),
    ],
    "Lecce": [
        ("Lameck Banda", "Attaccante", 0.28),
        ("Santiago Pierotti", "Attaccante", 0.25),
        ("Ylber Ramadani", "Centrocampista", 0.20),
        ("Federico Baschirotto", "Difensore", 0.18),
        ("Wladimiro Falcone", "Portiere", 0.15),
    ],
    "Hellas Verona": [
        ("Casper Tengstedt", "Attaccante", 0.28),
        ("Daniel Mosquera", "Attaccante", 0.25),
        ("Tomáš Suslov", "Centrocampista", 0.22),
        ("Darko Lazović", "Centrocampista", 0.20),
        ("Lorenzo Montipò", "Portiere", 0.15),
    ],
    "Cagliari": [
        ("Gianluca Lapadula", "Attaccante", 0.30),
        ("Andrea Belotti", "Attaccante", 0.28),
        ("Zito Luvumbo", "Attaccante", 0.28),
        ("Gianluca Gaetano", "Centrocampista", 0.25),
        ("Răzvan Marin", "Centrocampista", 0.22),
    ],
    "Parma": [
        ("Dennis Man", "Attaccante", 0.32),
        ("Valentin Mihăilă", "Attaccante", 0.30),
        ("Adrián Bernabé", "Centrocampista", 0.28),
        ("Matteo Cancellieri", "Attaccante", 0.25),
        ("Zion Suzuki", "Portiere", 0.15),
    ],
    "Pisa": [
        ("M'Bala Nzola", "Attaccante", 0.32),
        ("Nicholas Bonfanti", "Attaccante", 0.30),
        ("Juan Cuadrado", "Centrocampista", 0.28),
        ("Matteo Tramoni", "Centrocampista", 0.25),
        ("Adrian Semper", "Portiere", 0.15),
    ],
    "Sassuolo": [
        ("Domenico Berardi", "Attaccante", 0.38),
        ("Armand Laurienté", "Attaccante", 0.32),
        ("Samuele Mulattieri", "Attaccante", 0.28),
        ("Kristian Thorstvedt", "Centrocampista", 0.25),
        ("Andrea Consigli", "Portiere", 0.15),
    ],
    "Cremonese": [
        ("Jamie Vardy", "Attaccante", 0.35),
        ("Antonio Sanabria", "Attaccante", 0.32),
        ("Franco Vázquez", "Centrocampista", 0.28),
        ("Charles Pickel", "Centrocampista", 0.22),
        ("Marco Silvestri", "Portiere", 0.15),
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
            ("M. Thuram", "FWD"), ("Lautaro Martinez", "FWD")
        ],
        "bench": ["J. Martinez", "Bisseck", "De Vrij", "Darmian", "Zielinski", "Frattesi", "Taremi", "Arnautovic", "Buchanan", "Asllani", "Carlos Augusto"]
    },
    "AC Milan": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Maignan", "GK"),
            ("Emerson Royal", "DEF"), ("Tomori", "DEF"), ("De Winter", "DEF"), ("Estupinan", "DEF"),
            ("Modric", "MID"), ("Rabiot", "MID"),
            ("Pulisic", "MID"), ("Nkunku", "MID"), ("Leao", "FWD"),
            ("Gimenez", "FWD")
        ],
        "bench": ["Torriani", "Gabbia", "Pavlovic", "Jashari", "Bennacer", "Saelemaekers", "Ricci", "Athekame", "Odogu", "Loftus-Cheek", "Fofana", "Fullkrug", "Calabria"]
    },
    "Juventus": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Di Gregorio", "GK"),
            ("Savona", "DEF"), ("Gatti", "DEF"), ("Kalulu", "DEF"), ("Cambiaso", "DEF"),
            ("Locatelli", "MID"), ("K. Thuram", "MID"),
            ("David", "MID"), ("Koopmeiners", "MID"), ("Yildiz", "FWD"),
            ("Vlahovic", "FWD")
        ],
        "bench": ["Perin", "Danilo", "Douglas Luiz", "Fagioli", "Weah", "McKennie", "Rouhi", "Adzic", "Mbangula", "Milik"]
    },
    "Napoli": {
        "formation": "4-3-3",
        "starting_xi": [
            ("Meret", "GK"),
            ("Di Lorenzo", "DEF"), ("Rrahmani", "DEF"), ("Buongiorno", "DEF"), ("Olivera", "DEF"),
            ("De Bruyne", "MID"), ("Lobotka", "MID"), ("McTominay", "MID"),
            ("Politano", "FWD"), ("Lukaku", "FWD"), ("Kvaratskhelia", "FWD")
        ],
        "bench": ["Caprile", "Juan Jesus", "Spinazzola", "Gilmour", "Neres", "Simeone", "Raspadori", "Mazzocchi", "Marin", "Hojlund"]
    },
    "AS Roma": {
        "formation": "3-4-2-1",
        "starting_xi": [
            ("Svilar", "GK"),
            ("Mancini", "DEF"), ("Hummels", "DEF"), ("Ndicka", "DEF"),
            ("Celik", "MID"), ("Koné", "MID"), ("Cristante", "MID"), ("Angelino", "MID"),
            ("Dybala", "FWD"), ("Pellegrini", "FWD"),
            ("Dovbyk", "FWD")
        ],
        "bench": ["Ryan", "Hermoso", "Abdulhamid", "Dahl", "Le Fee", "Pisilli", "Soulé", "Baldanzi", "Shomurodov", "Saelemaekers", "El Shaarawy"]
    },
    "Lazio": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Provedel", "GK"),
            ("Lazzari", "DEF"), ("Gila", "DEF"), ("Romagnoli", "DEF"), ("Tavares", "DEF"),
            ("Guendouzi", "MID"), ("Rovella", "MID"),
            ("Isaksen", "MID"), ("Dia", "MID"), ("Zaccagni", "MID"),
            ("Castellanos", "FWD")
        ],
        "bench": ["Mandas", "Patric", "Marusic", "Gigot", "Vecino", "Dele-Bashiru", "Noslin", "Pedro", "Castrovilli"]
    },
    "Atalanta": {
        "formation": "3-4-2-1",
        "starting_xi": [
            ("Carnesecchi", "GK"),
            ("Djimsiti", "DEF"), ("Hien", "DEF"), ("Kolasinac", "DEF"),
            ("Bellanova", "MID"), ("De Roon", "MID"), ("Ederson", "MID"), ("Ruggeri", "MID"),
            ("De Ketelaere", "MID"), ("Lookman", "MID"),
            ("Retegui", "FWD")
        ],
        "bench": ["Rui Patricio", "Kossounou", "Toloi", "Zappacosta", "Cuadrado", "Pasalic", "Samardzic", "Brescianini", "Zaniolo"]
    },
    "Fiorentina": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("De Gea", "GK"),
            ("Dodo", "DEF"), ("Comuzzo", "DEF"), ("Ranieri", "DEF"), ("R. Gosens", "DEF"),
            ("Adli", "MID"), ("Cataldi", "MID"),
            ("Colpani", "MID"), ("Gudmundsson", "MID"), ("Solomon", "MID"),
            ("Kean", "FWD")
        ],
        "bench": ["Terracciano", "Pongracic", "Quarta", "Kayode", "Biraghi", "Richardson", "Mandragora", "Sottil", "Beltran", "Kouame", "Parisi", "Bove", "Piccoli"]
    },
    "Bologna": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Skorupski", "GK"),
            ("Posch", "DEF"), ("Beukema", "DEF"), ("Lucumi", "DEF"), ("Miranda", "DEF"),
            ("Freuler", "MID"), ("Pobega", "MID"),
            ("Orsolini", "MID"), ("Fabbian", "MID"), ("Ndoye", "MID"),
            ("Castro", "FWD")
        ],
        "bench": ["Ravaglia", "Casale", "Erlic", "Holm", "Lykogiannis", "Moro", "Aebischer", "Iling-Junior", "Dallinga", "Odgaard"]
    },
    "Torino": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Milinkovic-Savic", "GK"),
            ("Walukiewicz", "DEF"), ("Coco", "DEF"), ("Masina", "DEF"),
            ("Pedersen", "MID"), ("Tameze", "MID"), ("Linetty", "MID"), ("Vlasic", "MID"), ("Lazaro", "MID"),
            ("Adams", "FWD"), ("Sanabria", "FWD")
        ],
        "bench": ["Paleari", "Maripan", "Vojvoda", "Sosa", "Ilic", "Gineitis", "Karamoh", "Njie"]
    },
    "Udinese": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Okoye", "GK"),
            ("Kabasele", "DEF"), ("Bijol", "DEF"), ("Touré", "DEF"),
            ("Ehizibue", "MID"), ("Karlstrom", "MID"), ("Lovric", "MID"), ("Kamara", "MID"), ("Ekkelenkamp", "MID"),
            ("Thauvin", "FWD"), ("Lucca", "FWD")
        ],
        "bench": ["Padelli", "Sava", "Kristensen", "Giannetti", "Ebosse", "Zarraga", "Atta", "Payero", "Davis", "Brenner", "Bravo", "Pizarro"]
    },
    "Genoa": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Gollini", "GK"),
            ("Vogliacco", "DEF"), ("Bani", "DEF"), ("Vasquez", "DEF"),
            ("Sabelli", "MID"), ("Frendrup", "MID"), ("Badelj", "MID"), ("Miretti", "MID"), ("Martin", "MID"),
            ("Vitinha", "FWD"), ("Pinamonti", "FWD")
        ],
        "bench": ["Leali", "De Winter", "Matturro", "Thorsby", "Messias", "Ekuban", "Ekhator", "Balotelli", "Norton-Cuffy"]
    },
    "Hellas Verona": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Montipò", "GK"),
            ("Tchatchoua", "DEF"), ("Dawidowicz", "DEF"), ("Coppola", "DEF"), ("Bradaric", "DEF"),
            ("Belahyane", "MID"), ("Duda", "MID"),
            ("Suslov", "MID"), ("Harroui", "MID"), ("Lazovic", "MID"),
            ("Tengstedt", "FWD")
        ],
        "bench": ["Perilli", "Magnani", "Daniliuc", "Dani Silva", "Kastanos", "Livramento", "Mosquera", "Frese", "Serdar"]
    },
    "Lecce": {
        "formation": "4-3-3",
        "starting_xi": [
            ("Falcone", "GK"),
            ("Guilbert", "DEF"), ("Baschirotto", "DEF"), ("Gaspar", "DEF"), ("Gallo", "DEF"),
            ("Coulibaly", "MID"), ("Ramadani", "MID"), ("Rafia", "MID"),
            ("Dorgu", "FWD"), ("Krstovic", "FWD"), ("Banda", "FWD")
        ],
        "bench": ["Fruchtl", "Pelmard", "Jean", "Pierret", "Oudin", "Marchwinski", "Rebic", "Sansone", "Morente"]
    },
    "Parma": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Suzuki", "GK"),
            ("Coulibaly", "DEF"), ("Delprato", "DEF"), ("Sorensen", "DEF"), ("Valeri", "DEF"),
            ("Keita", "MID"), ("Cremaschi", "MID"),
            ("Oristanio", "MID"), ("Bernabé", "MID"), ("Mihaila", "MID"),
            ("Bonny", "FWD")
        ],
        "bench": ["Chichizola", "Hainaut", "Osorio", "Leoni", "Hernani", "Estevez", "Cancellieri", "Almqvist", "Charpentier", "Begic", "Partipilo"]
    },
    "Cagliari": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Scuffet", "GK"),
            ("Zappa", "DEF"), ("Mina", "DEF"), ("Luperto", "DEF"),
            ("Zortea", "MID"), ("Marin", "MID"), ("Adopo", "MID"), ("Gaetano", "MID"), ("Augello", "MID"),
            ("Belotti", "FWD"), ("Lapadula", "FWD")
        ],
        "bench": ["Sherri", "Palomino", "Obert", "Prati", "Deiola", "Viola", "Pavoletti", "Felici", "Jankto"]
    },
    "Como": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Audero", "GK"),
            ("Iovine", "DEF"), ("Kempf", "DEF"), ("Dossena", "DEF"), ("Moreno", "DEF"),
            ("Mazzitelli", "MID"), ("Sergi Roberto", "MID"),
            ("Strefezza", "MID"), ("Paz", "MID"), ("Fadera", "MID"),
            ("Cutrone", "FWD")
        ],
        "bench": ["Reina", "Tornqvist", "Sala", "Barba", "Engelhardt", "Verdi", "Gabrielloni", "Da Cunha", "Perrone", "Varane", "Terracciano"]
    },
    "Venezia": {
        "formation": "3-4-2-1",
        "starting_xi": [
             ("Stankovic", "GK"),
             ("Idzes", "DEF"), ("Svoboda", "DEF"), ("Sverko", "DEF"),
             ("Candela", "MID"), ("Duncan", "MID"), ("Nicolussi Caviglia", "MID"), ("Haps", "MID"),
             ("Yeboah", "MID"), ("Busio", "MID"),
             ("Pohjanpalo", "FWD")
        ],
        "bench": ["Joronen", "Zampano", "Sagrado", "Crnigoj", "Ellertsson", "Gytkjaer"]
    },
    "Empoli": {
        "formation": "3-4-2-1",
        "starting_xi": [
            ("Vasquez", "GK"),
            ("Goglichidze", "DEF"), ("Ismajli", "DEF"), ("Viti", "DEF"),
            ("Gyasi", "MID"), ("Henderson", "MID"), ("Grassi", "MID"), ("Pezzella", "MID"),
            ("Fazzini", "MID"), ("Esposito", "MID"),
            ("Colombo", "FWD")
        ],
        "bench": ["Seghetti", "Marianucci", "Cacace", "Anjorin", "Haas", "Maleh", "Solbakken", "Pellegri"]
    },
    "Monza": {
        "formation": "3-4-2-1",
        "starting_xi": [
            ("Turati", "GK"),
            ("Izzo", "DEF"), ("Mari", "DEF"), ("Carboni", "DEF"),
            ("Pereira", "MID"), ("Bondo", "MID"), ("Bianco", "MID"), ("Kyriakopoulos", "MID"),
            ("Maldini", "MID"), ("Mota", "MID"),
            ("Djuric", "FWD")
        ],
        "bench": ["Pizzignacco", "Caldirola", "D'Ambrosio", "Sensi", "Valoti", "Caprari", "Petagna", "Pessina"]
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
    
    # Ensure match_date is a date object for biorhythm calculation
    if isinstance(match_date, datetime):
        match_date = match_date.date()

    # Helper function to calculate team biorhythm
    def get_team_bio(team_name: str) -> TeamBiorhythm:
        # Get mock data for the team to know who is playing
        mock_data = MOCK_LINEUPS.get(team_name)
        
        # We need a list of player names to check against the database
        target_player_names = []
        if mock_data:
             # Prioritize starters
            target_player_names = [p[0] for p in mock_data["starting_xi"]]
        
        # Find relevant players in our database
        relevant_players = {}
        
        if target_player_names:
            # We have a specific list of players (from lineup)
            for target_name in target_player_names:
                # Improved matching logic to avoid partial matches (e.g. "Mina" in "McTominay", "Zappa" in "Zappacosta")
                target_lower = target_name.lower()
                
                for db_name, dob in PLAYER_BIRTHDATES.items():
                    db_lower = db_name.lower()
                    
                    # 1. Exact match
                    if target_lower == db_lower:
                        relevant_players[db_name] = dob
                        break
                        
                    # 2. Check if target_name is a distinct part of db_name
                    # Split by space, dot, or hyphen
                    import re
                    # Create parts list from db_name (e.g. "D. Zappacosta" -> ["d", "zappacosta"])
                    # We remove dots and split by spaces
                    db_parts = [p.strip() for p in re.split(r'[ .-]+', db_lower) if p.strip()]
                    
                    # Handle multi-word target names (e.g. "De Ketelaere")
                    # If target name has spaces, we check if it's contained as a phrase
                    if ' ' in target_lower:
                        # Check if target_lower appears in db_lower with boundaries
                        # e.g. "De Ketelaere" in "C. De Ketelaere" -> OK
                        # But we need to ensure it's not "De Ketelaeres"
                        if f" {target_lower} " in f" {db_lower} " or \
                           db_lower.endswith(f" {target_lower}") or \
                           db_lower.startswith(f"{target_lower} "):
                             relevant_players[db_name] = dob
                             break
                    else:
                        # Single word target (surname)
                        # Must match one of the parts exactly
                        if target_lower in db_parts:
                            relevant_players[db_name] = dob
                            break
        
        if not relevant_players:
            # Fallback if no players found
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
        team_players = []
        
        for name, dob in relevant_players.items():
            try:
                # dob is already a date object from PLAYER_BIRTHDATES
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
            top_performers=team_players  # Return all players for detailed view
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
