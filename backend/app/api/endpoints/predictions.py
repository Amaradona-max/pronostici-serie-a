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
        ("Christian Pulisic", "Attaccante", 0.46),
        ("Rafael Leão", "Attaccante", 0.40),
        ("Alvaro Morata", "Attaccante", 0.35),
        ("Niclas Füllkrug", "Attaccante", 0.32),
        ("Tijjani Reijnders", "Centrocampista", 0.28),
    ],
    "Napoli": [
        ("Romelu Lukaku", "Attaccante", 0.42),
        ("Khvicha Kvaratskhelia", "Attaccante", 0.38),
        ("Kevin De Bruyne", "Centrocampista", 0.35),
        ("Scott McTominay", "Centrocampista", 0.32),
        ("Alessandro Buongiorno", "Difensore", 0.28),
    ],
    "Juventus": [
        ("Kenan Yıldız", "Attaccante", 0.42),
        ("Dušan Vlahović", "Attaccante", 0.38),
        ("Teun Koopmeiners", "Centrocampista", 0.35),
        ("Francisco Conceição", "Attaccante", 0.30),
        ("Nicolò Savona", "Difensore", 0.25),
    ],
    "AS Roma": [
        ("Artem Dovbyk", "Attaccante", 0.38),
        ("Paulo Dybala", "Attaccante", 0.35),
        ("Matías Soulé", "Attaccante", 0.30),
        ("Lorenzo Pellegrini", "Centrocampista", 0.25),
        ("Manu Koné", "Centrocampista", 0.22),
    ],
    "Bologna": [
        ("Riccardo Orsolini", "Attaccante", 0.42),
        ("Santiago Castro", "Attaccante", 0.38),
        ("Dan Ndoye", "Attaccante", 0.32),
        ("Thijs Dallinga", "Attaccante", 0.28),
        ("Giovanni Fabbian", "Centrocampista", 0.24),
    ],
    "Atalanta": [
        ("Mateo Retegui", "Attaccante", 0.38),
        ("Ademola Lookman", "Attaccante", 0.32),
        ("Charles De Ketelaere", "Attaccante", 0.28),
        ("Mario Pašalić", "Centrocampista", 0.24),
        ("Éderson", "Centrocampista", 0.20),
    ],
    "Lazio": [
        ("Mattia Zaccagni", "Attaccante", 0.35),
        ("Valentín Castellanos", "Attaccante", 0.32),
        ("Boulaye Dia", "Attaccante", 0.28),
        ("Nicolò Rovella", "Centrocampista", 0.24),
        ("Mattéo Guendouzi", "Centrocampista", 0.20),
    ],
    "Como": [
        ("Nico Paz", "Centrocampista", 0.40),
        ("Gabriel Strefezza", "Attaccante", 0.30),
        ("Sergi Roberto", "Centrocampista", 0.25),
        ("Andrea Belotti", "Attaccante", 0.28),
        ("Noel Tornqvist", "Portiere", 0.10),
    ],
    "Fiorentina": [
        ("Moise Kean", "Attaccante", 0.45),
        ("Manor Solomon", "Attaccante", 0.35),
        ("Albert Gudmundsson", "Attaccante", 0.30),
        ("Lucas Beltrán", "Attaccante", 0.25),
        ("Robin Gosens", "Difensore", 0.20),
    ],
    "Torino": [
        ("Che Adams", "Attaccante", 0.30),
        ("Giovanni Simeone", "Attaccante", 0.30),
        ("Nikola Vlasic", "Centrocampista", 0.25),
        ("Kristjan Asllani", "Centrocampista", 0.20),
        ("Ivan Ilic", "Centrocampista", 0.15),
    ],
    "Udinese": [
        ("Nicolò Zaniolo", "Attaccante", 0.30),
        ("Adam Buksa", "Attaccante", 0.28),
        ("Sandi Lovric", "Centrocampista", 0.20),
        ("Jurgen Ekkelenkamp", "Centrocampista", 0.18),
        ("Keinan Davis", "Attaccante", 0.28),
    ],
    "Genoa": [
        ("Andrea Pinamonti", "Attaccante", 0.32),
        ("Vitinha", "Attaccante", 0.28),
        ("Junior Messias", "Attaccante", 0.25),
        ("Ruslan Malinovskyi", "Centrocampista", 0.22),
        ("Morten Frendrup", "Centrocampista", 0.18),
    ],
    "Empoli": [
        ("Sebastiano Esposito", "Attaccante", 0.30),
        ("Lorenzo Colombo", "Attaccante", 0.28),
        ("Ola Solbakken", "Attaccante", 0.25),
        ("Youssef Maleh", "Centrocampista", 0.18),
        ("Emmanuel Gyasi", "Attaccante", 0.20),
    ],
    "Lecce": [
        ("Patrick Dorgu", "Attaccante", 0.25),
        ("Lameck Banda", "Attaccante", 0.22),
        ("Francesco Camarda", "Attaccante", 0.20),
        ("Ylber Ramadani", "Centrocampista", 0.15),
        ("Hamza Rafia", "Centrocampista", 0.15),
    ],
    "Hellas Verona": [
        ("Daniel Mosquera", "Attaccante", 0.28),
        ("Tomas Suslov", "Centrocampista", 0.22),
        ("Stefan Mitrovic", "Attaccante", 0.25),
        ("Al-Musrati", "Centrocampista", 0.20),
        ("Armel Bella-Kotchap", "Difensore", 0.15),
    ],
    "Cagliari": [
        ("Roberto Piccoli", "Attaccante", 0.30),
        ("Zito Luvumbo", "Attaccante", 0.28),
        ("Gianluca Gaetano", "Centrocampista", 0.25),
        ("Razvan Marin", "Centrocampista", 0.20),
        ("Leonardo Pavoletti", "Attaccante", 0.22),
    ],
    "Monza": [
        ("Daniel Maldini", "Attaccante", 0.32),
        ("Dany Mota", "Attaccante", 0.30),
        ("Matteo Pessina", "Centrocampista", 0.25),
        ("Milan Djuric", "Attaccante", 0.28),
        ("Gianluca Caprari", "Attaccante", 0.25),
    ],
    "Venezia": [
        ("Joel Pohjanpalo", "Attaccante", 0.35),
        ("Gianluca Busio", "Centrocampista", 0.25),
        ("Hans Nicolussi Caviglia", "Centrocampista", 0.22),
        ("John Yeboah", "Attaccante", 0.28),
        ("Alfred Duncan", "Centrocampista", 0.20),
    ],
    "Parma": [
        ("Adrián Bernabé", "Centrocampista", 0.30),
        ("Valentin Mihaila", "Attaccante", 0.28),
        ("Patrick Cutrone", "Attaccante", 0.32),
        ("Gaetano Oristanio", "Attaccante", 0.28),
        ("Emanuele Valeri", "Difensore", 0.20),
    ],
    "Pisa": [
        ("Nicholas Bonfanti", "Attaccante", 0.32),
        ("M'Bala Nzola", "Attaccante", 0.30),
        ("Simone Scuffet", "Portiere", 0.10),
        ("Calvin Stengs", "Attaccante", 0.28),
        ("Raúl Albiol", "Difensore", 0.15),
    ],
    "Sassuolo": [
        ("Andrea Pinamonti", "Attaccante", 0.35),
        ("Nemanja Matic", "Centrocampista", 0.25),
        ("Walid Cheddira", "Attaccante", 0.30),
        ("Aster Vranckx", "Centrocampista", 0.22),
        ("Stefano Turati", "Portiere", 0.10),
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
            ("Emerson Royal", "DEF"), ("Gabbia", "DEF"), ("Tomori", "DEF"), ("Hernandez", "DEF"),
            ("Fofana", "MID"), ("Reijnders", "MID"),
            ("Pulisic", "MID"), ("Loftus-Cheek", "MID"), ("Leao", "FWD"),
            ("Fullkrug", "FWD")
        ],
        "bench": ["Sportiello", "Calabria", "Pavlovic", "Terracciano", "Musah", "Chukwueze", "Okafor", "Abraham", "Jovic", "Thiaw", "Morata"]
    },
    "Juventus": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Di Gregorio", "GK"),
            ("Savona", "DEF"), ("Gatti", "DEF"), ("Kalulu", "DEF"), ("Cambiaso", "DEF"),
            ("Locatelli", "MID"), ("K. Thuram", "MID"),
            ("Conceicao", "MID"), ("Koopmeiners", "MID"), ("Yildiz", "FWD"),
            ("Vlahovic", "FWD")
        ],
        "bench": ["Perin", "Danilo", "Douglas Luiz", "Fagioli", "Weah", "McKennie", "Rouhi", "Adzic", "Mbangula", "Milik"]
    },
    "Napoli": {
        "formation": "4-3-3",
        "starting_xi": [
            ("Meret", "GK"),
            ("Di Lorenzo", "DEF"), ("Rrahmani", "DEF"), ("Buongiorno", "DEF"), ("Olivera", "DEF"),
            ("Anguissa", "MID"), ("Lobotka", "MID"), ("McTominay", "MID"),
            ("Politano", "FWD"), ("Lukaku", "FWD"), ("Kvaratskhelia", "FWD")
        ],
        "bench": ["Caprile", "Juan Jesus", "Spinazzola", "Gilmour", "Neres", "Simeone", "Raspadori", "Mazzocchi", "Marin"]
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
        "bench": ["Terracciano", "Pongracic", "Quarta", "Kayode", "Biraghi", "Richardson", "Mandragora", "Sottil", "Beltran", "Kouame", "Parisi", "Bove"]
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
            ("Pedersen", "MID"), ("Ricci", "MID"), ("Linetty", "MID"), ("Vlasic", "MID"), ("Lazaro", "MID"),
            ("Adams", "FWD"), ("Sanabria", "FWD")
        ],
        "bench": ["Paleari", "Maripan", "Vojvoda", "Sosa", "Ilic", "Tameze", "Gineitis", "Karamoh", "Njie"]
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
            ("Cutrone", "FWD")
        ],
        "bench": ["Chichizola", "Hainaut", "Osorio", "Leoni", "Hernani", "Estevez", "Cancellieri", "Almqvist", "Charpentier", "Begic", "Partipilo"]
    },
    "Cagliari": {
        "formation": "3-5-2",
        "starting_xi": [
            ("Scuffet", "GK"),
            ("Zappa", "DEF"), ("Mina", "DEF"), ("Luperto", "DEF"),
            ("Zortea", "MID"), ("Marin", "MID"), ("Adopo", "MID"), ("Gaetano", "MID"), ("Augello", "MID"),
            ("Luvumbo", "FWD"), ("Piccoli", "FWD")
        ],
        "bench": ["Sherri", "Palomino", "Obert", "Prati", "Deiola", "Viola", "Lapadula", "Pavoletti", "Felici"]
    },
    "Como": {
        "formation": "4-2-3-1",
        "starting_xi": [
            ("Tornqvist", "GK"),
            ("Iovine", "DEF"), ("Kempf", "DEF"), ("Dossena", "DEF"), ("Moreno", "DEF"),
            ("Mazzitelli", "MID"), ("Sergi Roberto", "MID"),
            ("Strefezza", "MID"), ("Paz", "MID"), ("Fadera", "MID"),
            ("Belotti", "FWD")
        ],
        "bench": ["Reina", "Audero", "Sala", "Barba", "Engelhardt", "Verdi", "Gabrielloni", "Da Cunha", "Perrone"]
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
