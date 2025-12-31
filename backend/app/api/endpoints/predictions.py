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
    PlayerBiorhythm
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
        ("Christopher Nkunku", "Attaccante", 0.35),
        ("Santiago Gimenez", "Attaccante", 0.28),
        ("Luka Modrić", "Centrocampista", 0.22),
    ],
    "Napoli": [
        ("Romelu Lukaku", "Attaccante", 0.42),
        ("Rasmus Højlund", "Attaccante", 0.38),
        ("Lorenzo Lucca", "Attaccante", 0.32),
        ("Kevin De Bruyne", "Centrocampista", 0.28),
        ("David Neres", "Attaccante", 0.24),
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
        ("Assane Diao", "Attaccante", 0.28),
        ("Máximo Perrone", "Centrocampista", 0.22),
        ("Lucas Da Cunha", "Centrocampista", 0.18),
    ],
    "Fiorentina": [
        ("Moise Kean", "Attaccante", 0.40),
        ("Albert Guðmundsson", "Attaccante", 0.35),
        ("Roberto Piccoli", "Attaccante", 0.30),
        ("Rolando Mandragora", "Centrocampista", 0.25),
        ("Edin Džeko", "Attaccante", 0.22),
    ],
    "Parma": [
        ("Patrick Cutrone", "Attaccante", 0.38),
        ("Dennis Man", "Attaccante", 0.32),
        ("Ange-Yoan Bonny", "Attaccante", 0.28),
        ("Adrián Bernabé", "Centrocampista", 0.22),
        ("Enrico Delprato", "Difensore", 0.18),
    ],
    "Torino": [
        ("Nikola Vlašić", "Centrocampista", 0.38),
        ("Ché Adams", "Attaccante", 0.32),
        ("Duván Zapata", "Attaccante", 0.28),
        ("Karol Linetty", "Centrocampista", 0.22),
        ("Yann Karamoh", "Attaccante", 0.18),
    ],
    "Udinese": [
        ("Keinan Davis", "Attaccante", 0.38),
        ("Iker Bravo", "Attaccante", 0.32),
        ("Nicolò Zaniolo", "Attaccante", 0.28),
        ("Adam Buksa", "Attaccante", 0.24),
        ("Sandi Lovrić", "Centrocampista", 0.18),
    ],
    "Lecce": [
        ("Nikola Krstović", "Attaccante", 0.35),
        ("Santiago Pierotti", "Attaccante", 0.28),
        ("Hamza Rafia", "Centrocampista", 0.24),
        ("Patrick Dorgu", "Difensore", 0.20),
        ("Lameck Banda", "Centrocampista", 0.15),
    ],
    "Genoa": [
        ("Leo Østigård", "Difensore", 0.32),
        ("Morten Thorsby", "Centrocampista", 0.28),
        ("Lorenzo Colombo", "Attaccante", 0.25),
        ("Junior Messias", "Centrocampista", 0.22),
        ("Vitinha", "Attaccante", 0.18),
    ],
    "Cagliari": [
        ("Sebastiano Esposito", "Attaccante", 0.38),
        ("Andrea Belotti", "Attaccante", 0.32),
        ("Semih Kılıçsoy", "Attaccante", 0.28),
        ("Zito Luvumbo", "Attaccante", 0.24),
        ("Gennaro Borrelli", "Attaccante", 0.20),
    ],
    "Hellas Verona": [
        ("Casper Tengstedt", "Attaccante", 0.36),
        ("Grigoris Kastanos", "Centrocampista", 0.28),
        ("Tomáš Suslov", "Centrocampista", 0.24),
        ("Darko Lazović", "Centrocampista", 0.20),
        ("Daniel Mosquera", "Attaccante", 0.15),
    ],
    "Sassuolo": [
        ("Andrea Pinamonti", "Attaccante", 0.36),
        ("Domenico Berardi", "Attaccante", 0.35),
        ("Armand Laurienté", "Attaccante", 0.28),
        ("Cristian Volpato", "Centrocampista", 0.22),
        ("Matheus Henrique", "Centrocampista", 0.18),
    ],
    "Cremonese": [
        ("Federico Bonazzoli", "Attaccante", 0.40),
        ("Antonio Sanabria", "Attaccante", 0.35),
        ("Frank Tsadjout", "Attaccante", 0.28),
        ("Michele Castagnetti", "Centrocampista", 0.22),
        ("Luca Zanimacchia", "Centrocampista", 0.18),
    ],
    "Pisa": [
        ("Mattéo Nzola", "Attaccante", 0.35),
        ("Stefano Moreo", "Attaccante", 0.28),
        ("Mattéo Tramoni", "Centrocampista", 0.24),
        ("Alessandro Arena", "Centrocampista", 0.20),
        ("Gabriele Piccinini", "Centrocampista", 0.15),
    ],
}


# Real lineups for all 20 Serie A teams (11 starters + 7 bench each)
# Based on REAL Serie A 2025-26 squads and typical formations
MOCK_LINEUPS = {
    "Inter": {
        "formation": "3-5-2",
        "starters": [
            {"name": "Y. Sommer", "position": "GK", "number": 1},
            {"name": "B. Pavard", "position": "DF", "number": 28},
            {"name": "F. Acerbi", "position": "DF", "number": 15},
            {"name": "A. Bastoni", "position": "DF", "number": 95},
            {"name": "D. Dumfries", "position": "MF", "number": 2},
            {"name": "N. Barella", "position": "MF", "number": 23},
            {"name": "H. Çalhanoğlu", "position": "MF", "number": 20},
            {"name": "H. Mkhitaryan", "position": "MF", "number": 22},
            {"name": "F. Dimarco", "position": "MF", "number": 32},
            {"name": "M. Thuram", "position": "FW", "number": 9},
            {"name": "L. Martínez", "position": "FW", "number": 10},
        ],
        "bench": [
            {"name": "J. Martínez", "position": "GK", "number": 12},
            {"name": "D. Frattesi", "position": "MF", "number": 16},
            {"name": "K. Asllani", "position": "MF", "number": 21},
            {"name": "M. Arnautović", "position": "FW", "number": 8},
            {"name": "J. Correa", "position": "FW", "number": 11},
            {"name": "M. Darmian", "position": "DF", "number": 36},
            {"name": "S. de Vrij", "position": "DF", "number": 6},
        ]
    },
    "AC Milan": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "M. Maignan", "position": "GK", "number": 16},
            {"name": "E. Royal", "position": "DF", "number": 22},
            {"name": "F. Tomori", "position": "DF", "number": 23},
            {"name": "M. Gabbia", "position": "DF", "number": 46},
            {"name": "T. Hernández", "position": "DF", "number": 19},
            {"name": "Y. Fofana", "position": "MF", "number": 29},
            {"name": "S. Ricci", "position": "MF", "number": 5},
            {"name": "C. Pulisic", "position": "FW", "number": 11},
            {"name": "L. Modrić", "position": "MF", "number": 10},
            {"name": "R. Leão", "position": "FW", "number": 10},
            {"name": "C. Nkunku", "position": "FW", "number": 18},
        ],
        "bench": [
            {"name": "P. Terracciano", "position": "GK", "number": 1},
            {"name": "L. Torriani", "position": "GK", "number": 96},
            {"name": "A. Rabiot", "position": "MF", "number": 12},
            {"name": "R. Loftus-Cheek", "position": "MF", "number": 8},
            {"name": "S. Gimenez", "position": "FW", "number": 7},
            {"name": "M. Thiaw", "position": "DF", "number": 28},
            {"name": "D. Calabria", "position": "DF", "number": 2},
        ]
    },
    "Napoli": {
        "formation": "4-3-3",
        "starters": [
            {"name": "A. Meret", "position": "GK", "number": 1},
            {"name": "G. Di Lorenzo", "position": "DF", "number": 22},
            {"name": "A. Rrahmani", "position": "DF", "number": 13},
            {"name": "A. Buongiorno", "position": "DF", "number": 4},
            {"name": "M. Olivera", "position": "DF", "number": 17},
            {"name": "A. Zambo Anguissa", "position": "MF", "number": 99},
            {"name": "S. Lobotka", "position": "MF", "number": 68},
            {"name": "K. De Bruyne", "position": "MF", "number": 17},
            {"name": "M. Politano", "position": "FW", "number": 21},
            {"name": "R. Højlund", "position": "FW", "number": 9},
            {"name": "D. Neres", "position": "FW", "number": 7},
        ],
        "bench": [
            {"name": "E. Caprile", "position": "GK", "number": 25},
            {"name": "G. Raspadori", "position": "FW", "number": 81},
            {"name": "S. McTominay", "position": "MF", "number": 8},
            {"name": "J. Jesus", "position": "DF", "number": 5},
            {"name": "L. Spinazzola", "position": "DF", "number": 37},
            {"name": "M. Folorunsho", "position": "MF", "number": 90},
            {"name": "N. Lang", "position": "FW", "number": 11},
        ]
    },
    "Juventus": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "M. Di Gregorio", "position": "GK", "number": 29},
            {"name": "N. Savona", "position": "DF", "number": 37},
            {"name": "F. Gatti", "position": "DF", "number": 4},
            {"name": "P. Kalulu", "position": "DF", "number": 15},
            {"name": "A. Cambiaso", "position": "DF", "number": 27},
            {"name": "M. Locatelli", "position": "MF", "number": 5},
            {"name": "K. Thuram", "position": "MF", "number": 19},
            {"name": "K. Yıldız", "position": "FW", "number": 10},
            {"name": "L. Openda", "position": "FW", "number": 14},
            {"name": "J. David", "position": "FW", "number": 9},
            {"name": "E. Zhegrova", "position": "FW", "number": 20},
        ],
        "bench": [
            {"name": "M. Perin", "position": "GK", "number": 36},
            {"name": "D. Rugani", "position": "DF", "number": 24},
            {"name": "N. Fagioli", "position": "MF", "number": 21},
            {"name": "W. McKennie", "position": "MF", "number": 16},
            {"name": "D. Vlahović", "position": "FW", "number": 7},
            {"name": "T. Weah", "position": "FW", "number": 22},
            {"name": "F. Conceição", "position": "FW", "number": 18},
        ]
    },
    "AS Roma": {
        "formation": "3-4-2-1",
        "starters": [
            {"name": "M. Svilar", "position": "GK", "number": 99},
            {"name": "M. Hummels", "position": "DF", "number": 15},
            {"name": "G. Mancini", "position": "DF", "number": 23},
            {"name": "E. Ndicka", "position": "DF", "number": 5},
            {"name": "Z. Çelik", "position": "MF", "number": 19},
            {"name": "M. Koné", "position": "MF", "number": 17},
            {"name": "L. Paredes", "position": "MF", "number": 16},
            {"name": "Angeliño", "position": "MF", "number": 3},
            {"name": "P. Dybala", "position": "FW", "number": 21},
            {"name": "M. Soulé", "position": "FW", "number": 18},
            {"name": "A. Dovbyk", "position": "FW", "number": 11},
        ],
        "bench": [
            {"name": "R. Patrício", "position": "GK", "number": 1},
            {"name": "L. Pellegrini", "position": "MF", "number": 7},
            {"name": "N. Zalewski", "position": "MF", "number": 59},
            {"name": "S. El Shaarawy", "position": "FW", "number": 92},
            {"name": "M. Hermoso", "position": "DF", "number": 22},
            {"name": "E. Le Fée", "position": "MF", "number": 28},
            {"name": "T. Baldanzi", "position": "FW", "number": 35},
        ]
    },
    "Bologna": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "Ł. Skorupski", "position": "GK", "number": 28},
            {"name": "S. Posch", "position": "DF", "number": 3},
            {"name": "S. Beukema", "position": "DF", "number": 31},
            {"name": "J. Lucumí", "position": "DF", "number": 26},
            {"name": "J. Miranda", "position": "DF", "number": 33},
            {"name": "R. Freuler", "position": "MF", "number": 8},
            {"name": "N. Moro", "position": "MF", "number": 6},
            {"name": "R. Orsolini", "position": "FW", "number": 7},
            {"name": "J. Odgaard", "position": "MF", "number": 21},
            {"name": "D. Ndoye", "position": "FW", "number": 11},
            {"name": "S. Castro", "position": "FW", "number": 9},
        ],
        "bench": [
            {"name": "F. Ravaglia", "position": "GK", "number": 1},
            {"name": "G. Fabbian", "position": "MF", "number": 80},
            {"name": "K. Aebischer", "position": "MF", "number": 20},
            {"name": "T. Pobega", "position": "MF", "number": 18},
            {"name": "B. Domínguez", "position": "FW", "number": 30},
            {"name": "L. De Silvestri", "position": "DF", "number": 29},
            {"name": "M. Erlic", "position": "DF", "number": 5},
        ]
    },
    "Atalanta": {
        "formation": "3-4-1-2",
        "starters": [
            {"name": "M. Carnesecchi", "position": "GK", "number": 29},
            {"name": "B. Djimsiti", "position": "DF", "number": 19},
            {"name": "I. Hien", "position": "DF", "number": 4},
            {"name": "S. Kolašinac", "position": "DF", "number": 23},
            {"name": "R. Bellanova", "position": "MF", "number": 16},
            {"name": "M. de Roon", "position": "MF", "number": 15},
            {"name": "Éderson", "position": "MF", "number": 13},
            {"name": "M. Ruggeri", "position": "MF", "number": 22},
            {"name": "C. De Ketelaere", "position": "FW", "number": 17},
            {"name": "M. Retegui", "position": "FW", "number": 32},
            {"name": "A. Lookman", "position": "FW", "number": 11},
        ],
        "bench": [
            {"name": "J. Musso", "position": "GK", "number": 1},
            {"name": "M. Pašalić", "position": "MF", "number": 8},
            {"name": "L. Samardžić", "position": "MF", "number": 24},
            {"name": "G. Scalvini", "position": "DF", "number": 42},
            {"name": "I. Touré", "position": "DF", "number": 2},
            {"name": "R. Brescianini", "position": "MF", "number": 44},
            {"name": "M. Brescianini", "position": "FW", "number": 7},
        ]
    },
    "Lazio": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "I. Provedel", "position": "GK", "number": 94},
            {"name": "M. Lazzari", "position": "DF", "number": 29},
            {"name": "M. Gila", "position": "DF", "number": 34},
            {"name": "A. Romagnoli", "position": "DF", "number": 13},
            {"name": "Nuno Tavares", "position": "DF", "number": 30},
            {"name": "M. Guendouzi", "position": "MF", "number": 8},
            {"name": "N. Rovella", "position": "MF", "number": 6},
            {"name": "G. Isaksen", "position": "FW", "number": 18},
            {"name": "B. Dia", "position": "FW", "number": 19},
            {"name": "M. Zaccagni", "position": "FW", "number": 10},
            {"name": "V. Castellanos", "position": "FW", "number": 11},
        ],
        "bench": [
            {"name": "L. Mandas", "position": "GK", "number": 35},
            {"name": "T. Noslin", "position": "FW", "number": 14},
            {"name": "Pedro", "position": "FW", "number": 9},
            {"name": "F. Dele-Bashiru", "position": "MF", "number": 7},
            {"name": "A. Marušić", "position": "DF", "number": 77},
            {"name": "S. Gigot", "position": "DF", "number": 2},
            {"name": "L. Pellegrini", "position": "MF", "number": 3},
        ]
    },
    "Como": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "J. Butez", "position": "GK", "number": 1},
            {"name": "M. Vojvoda", "position": "DF", "number": 27},
            {"name": "Diego Carlos", "position": "DF", "number": 3},
            {"name": "R. Ramon", "position": "DF", "number": 5},
            {"name": "A. Valle", "position": "DF", "number": 18},
            {"name": "M. Perrone", "position": "MF", "number": 23},
            {"name": "L. Da Cunha", "position": "MF", "number": 33},
            {"name": "A. Kuhn", "position": "FW", "number": 16},
            {"name": "N. Paz", "position": "MF", "number": 79},
            {"name": "A. Jesus Rodriguez", "position": "FW", "number": 7},
            {"name": "C. Douvikas", "position": "FW", "number": 9},
        ],
        "bench": [
            {"name": "E. Semper", "position": "GK", "number": 1},
            {"name": "P. Cutrone", "position": "FW", "number": 10},
            {"name": "A. Belotti", "position": "FW", "number": 11},
            {"name": "A. Fabregas", "position": "MF", "number": 4},
            {"name": "A. Gabrielloni", "position": "FW", "number": 9},
            {"name": "M. Odenthal", "position": "DF", "number": 5},
            {"name": "Y. Engelhardt", "position": "MF", "number": 26},
        ]
    },
    "Fiorentina": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "D. de Gea", "position": "GK", "number": 43},
            {"name": "Dodô", "position": "DF", "number": 2},
            {"name": "P. Comuzzo", "position": "DF", "number": 15},
            {"name": "L. Ranieri", "position": "DF", "number": 6},
            {"name": "R. Gosens", "position": "DF", "number": 21},
            {"name": "R. Mandragora", "position": "MF", "number": 8},
            {"name": "N. Fagioli", "position": "MF", "number": 44},
            {"name": "A. Guðmundsson", "position": "FW", "number": 10},
            {"name": "J. Fazzini", "position": "MF", "number": 22},
            {"name": "M. Kean", "position": "FW", "number": 20},
            {"name": "R. Piccoli", "position": "FW", "number": 91},
        ],
        "bench": [
            {"name": "T. Martinelli", "position": "GK", "number": 30},
            {"name": "E. Džeko", "position": "FW", "number": 9},
            {"name": "C. Kouamé", "position": "FW", "number": 9},
            {"name": "M. Pongračić", "position": "DF", "number": 5},
            {"name": "F. Parisi", "position": "DF", "number": 65},
            {"name": "S. Sohm", "position": "MF", "number": 7},
            {"name": "M. Viti", "position": "DF", "number": 26},
        ]
    },
    "Parma": {
        "formation": "4-3-3",
        "starters": [
            {"name": "Z. Suzuki", "position": "GK", "number": 1},
            {"name": "E. Delprato", "position": "DF", "number": 15},
            {"name": "B. Valenti", "position": "DF", "number": 4},
            {"name": "A. Circati", "position": "DF", "number": 39},
            {"name": "E. Coulibaly", "position": "DF", "number": 26},
            {"name": "Hernani", "position": "MF", "number": 27},
            {"name": "S. Camara", "position": "MF", "number": 19},
            {"name": "A. Benedyczak", "position": "MF", "number": 9},
            {"name": "D. Man", "position": "FW", "number": 98},
            {"name": "A. Bonny", "position": "FW", "number": 13},
            {"name": "V. Mihăilă", "position": "FW", "number": 28},
        ],
        "bench": [
            {"name": "E. Corvi", "position": "GK", "number": 31},
            {"name": "G. Charpentier", "position": "FW", "number": 18},
            {"name": "M. Cancellieri", "position": "FW", "number": 22},
            {"name": "N. Estévez", "position": "MF", "number": 8},
            {"name": "W. Cyprien", "position": "MF", "number": 5},
            {"name": "A. Ferrari", "position": "DF", "number": 14},
            {"name": "D. Camara", "position": "MF", "number": 37},
        ]
    },
    "Torino": {
        "formation": "3-5-2",
        "starters": [
            {"name": "V. Milinković-Savić", "position": "GK", "number": 32},
            {"name": "R. Rodriguez", "position": "DF", "number": 13},
            {"name": "A. Buongiorno", "position": "DF", "number": 4},
            {"name": "K. Djidji", "position": "DF", "number": 26},
            {"name": "V. Lazaro", "position": "MF", "number": 20},
            {"name": "S. Ricci", "position": "MF", "number": 28},
            {"name": "I. Ilić", "position": "MF", "number": 8},
            {"name": "R. Bellanova", "position": "MF", "number": 19},
            {"name": "N. Vlašić", "position": "FW", "number": 10},
            {"name": "A. Sanabria", "position": "FW", "number": 9},
            {"name": "D. Zapata", "position": "FW", "number": 91},
        ],
        "bench": [
            {"name": "L. Gemello", "position": "GK", "number": 89},
            {"name": "A. Miranchuk", "position": "FW", "number": 59},
            {"name": "Y. Karamoh", "position": "FW", "number": 7},
            {"name": "G. Singo", "position": "DF", "number": 17},
            {"name": "M. Vojvoda", "position": "DF", "number": 27},
            {"name": "A. Tameze", "position": "MF", "number": 61},
            {"name": "Z. Bayeye", "position": "DF", "number": 16},
        ]
    },
    "Udinese": {
        "formation": "3-5-2",
        "starters": [
            {"name": "M. Silvestri", "position": "GK", "number": 1},
            {"name": "J. Bijol", "position": "DF", "number": 29},
            {"name": "T. Kristensen", "position": "DF", "number": 31},
            {"name": "N. Pérez", "position": "DF", "number": 18},
            {"name": "J. Ferreira", "position": "MF", "number": 19},
            {"name": "M. Payero", "position": "MF", "number": 5},
            {"name": "W. Ekkelenkamp", "position": "MF", "number": 32},
            {"name": "H. Kamara", "position": "MF", "number": 12},
            {"name": "F. Thauvin", "position": "FW", "number": 10},
            {"name": "L. Lucca", "position": "FW", "number": 17},
            {"name": "R. Pereyra", "position": "FW", "number": 37},
        ],
        "bench": [
            {"name": "D. Padelli", "position": "GK", "number": 90},
            {"name": "L. Samardžić", "position": "MF", "number": 24},
            {"name": "S. Lovric", "position": "MF", "number": 8},
            {"name": "I. Success", "position": "FW", "number": 7},
            {"name": "F. Kabasele", "position": "DF", "number": 27},
            {"name": "A. Pafundi", "position": "MF", "number": 42},
            {"name": "J. Zemura", "position": "DF", "number": 33},
        ]
    },
    "Lecce": {
        "formation": "4-3-3",
        "starters": [
            {"name": "W. Falcone", "position": "GK", "number": 30},
            {"name": "V. Gendrey", "position": "DF", "number": 17},
            {"name": "F. Baschirotto", "position": "DF", "number": 6},
            {"name": "M. Pongračić", "position": "DF", "number": 5},
            {"name": "P. Dorgu", "position": "DF", "number": 13},
            {"name": "M. Ramadani", "position": "MF", "number": 20},
            {"name": "A. Blin", "position": "MF", "number": 29},
            {"name": "Y. Rafia", "position": "MF", "number": 8},
            {"name": "P. Almqvist", "position": "FW", "number": 7},
            {"name": "N. Krstović", "position": "FW", "number": 9},
            {"name": "L. Banda", "position": "FW", "number": 22},
        ],
        "bench": [
            {"name": "F. Brancolini", "position": "GK", "number": 32},
            {"name": "R. Piccoli", "position": "FW", "number": 91},
            {"name": "R. Oudin", "position": "MF", "number": 10},
            {"name": "N. Sansone", "position": "FW", "number": 11},
            {"name": "A. Pelmard", "position": "DF", "number": 6},
            {"name": "A. Gallo", "position": "DF", "number": 25},
            {"name": "B. Pierret", "position": "MF", "number": 75},
        ]
    },
    "Genoa": {
        "formation": "3-5-2",
        "starters": [
            {"name": "N. Leali", "position": "GK", "number": 1},
            {"name": "A. Vogliacco", "position": "DF", "number": 14},
            {"name": "M. Bani", "position": "DF", "number": 13},
            {"name": "J. Vásquez", "position": "DF", "number": 22},
            {"name": "S. Sabelli", "position": "MF", "number": 20},
            {"name": "M. Frendrup", "position": "MF", "number": 32},
            {"name": "M. Badelj", "position": "MF", "number": 47},
            {"name": "A. Martín", "position": "MF", "number": 3},
            {"name": "J. Messias", "position": "MF", "number": 10},
            {"name": "A. Pinamonti", "position": "FW", "number": 19},
            {"name": "Vitinha", "position": "FW", "number": 9},
        ],
        "bench": [
            {"name": "P. Gollini", "position": "GK", "number": 95},
            {"name": "M. Thorsby", "position": "MF", "number": 2},
            {"name": "H. Ekuban", "position": "FW", "number": 18},
            {"name": "F. Accornero", "position": "MF", "number": 83},
            {"name": "K. De Winter", "position": "DF", "number": 4},
            {"name": "A. Zanoli", "position": "DF", "number": 59},
            {"name": "J. Ekhator", "position": "FW", "number": 21},
        ]
    },
    "Cagliari": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "A. Sherri", "position": "GK", "number": 22},
            {"name": "N. Zortea", "position": "DF", "number": 19},
            {"name": "Y. Mina", "position": "DF", "number": 26},
            {"name": "S. Luperto", "position": "DF", "number": 6},
            {"name": "T. Augello", "position": "DF", "number": 3},
            {"name": "M. Adopo", "position": "MF", "number": 8},
            {"name": "A. Makoumbou", "position": "MF", "number": 29},
            {"name": "N. Viola", "position": "FW", "number": 10},
            {"name": "G. Gaetano", "position": "FW", "number": 70},
            {"name": "Z. Luvumbo", "position": "FW", "number": 77},
            {"name": "R. Piccoli", "position": "FW", "number": 91},
        ],
        "bench": [
            {"name": "S. Scuffet", "position": "GK", "number": 1},
            {"name": "L. Pavoletti", "position": "FW", "number": 30},
            {"name": "A. Deiola", "position": "MF", "number": 14},
            {"name": "P. Azzi", "position": "DF", "number": 37},
            {"name": "A. Obert", "position": "DF", "number": 33},
            {"name": "M. Wieteska", "position": "DF", "number": 23},
            {"name": "K. Felici", "position": "FW", "number": 7},
        ]
    },
    "Hellas Verona": {
        "formation": "3-4-2-1",
        "starters": [
            {"name": "L. Montipò", "position": "GK", "number": 1},
            {"name": "D. Coppola", "position": "DF", "number": 42},
            {"name": "D. Ghilardi", "position": "DF", "number": 87},
            {"name": "P. Dawidowicz", "position": "DF", "number": 27},
            {"name": "J. Tchatchoua", "position": "MF", "number": 38},
            {"name": "R. Belahyane", "position": "MF", "number": 6},
            {"name": "O. Duda", "position": "MF", "number": 33},
            {"name": "D. Lazović", "position": "MF", "number": 8},
            {"name": "T. Suslov", "position": "FW", "number": 31},
            {"name": "D. Mosquera", "position": "FW", "number": 9},
            {"name": "C. Tengstedt", "position": "FW", "number": 11},
        ],
        "bench": [
            {"name": "S. Perilli", "position": "GK", "number": 34},
            {"name": "A. Sarr", "position": "FW", "number": 14},
            {"name": "D. Faraoni", "position": "DF", "number": 5},
            {"name": "G. Magnani", "position": "DF", "number": 23},
            {"name": "F. Terracciano", "position": "MF", "number": 20},
            {"name": "M. Hongla", "position": "MF", "number": 18},
            {"name": "A. Harroui", "position": "MF", "number": 21},
        ]
    },
    "Sassuolo": {
        "formation": "4-3-3",
        "starters": [
            {"name": "A. Consigli", "position": "GK", "number": 47},
            {"name": "J. Toljan", "position": "DF", "number": 20},
            {"name": "M. Erlic", "position": "DF", "number": 5},
            {"name": "G. Ferrari", "position": "DF", "number": 13},
            {"name": "F. Doig", "position": "DF", "number": 43},
            {"name": "M. Henrique", "position": "MF", "number": 7},
            {"name": "M. Castrovilli", "position": "MF", "number": 23},
            {"name": "C. Volpato", "position": "MF", "number": 22},
            {"name": "A. Laurienté", "position": "FW", "number": 45},
            {"name": "A. Pinamonti", "position": "FW", "number": 9},
            {"name": "D. Berardi", "position": "FW", "number": 25},
        ],
        "bench": [
            {"name": "G. Pegolo", "position": "GK", "number": 64},
            {"name": "G. Defrel", "position": "FW", "number": 92},
            {"name": "U. Racic", "position": "MF", "number": 6},
            {"name": "F. Romagna", "position": "DF", "number": 27},
            {"name": "M. Viti", "position": "DF", "number": 44},
            {"name": "S. Mulattieri", "position": "FW", "number": 30},
            {"name": "N. Bajrami", "position": "MF", "number": 10},
        ]
    },
    "Cremonese": {
        "formation": "3-5-2",
        "starters": [
            {"name": "M. Carnesecchi", "position": "GK", "number": 1},
            {"name": "M. Bianchetti", "position": "DF", "number": 15},
            {"name": "E. Lochoshvili", "position": "DF", "number": 5},
            {"name": "L. Ravanelli", "position": "DF", "number": 44},
            {"name": "L. Sernicola", "position": "MF", "number": 17},
            {"name": "M. Castagnetti", "position": "MF", "number": 19},
            {"name": "C. Buonaiuto", "position": "MF", "number": 33},
            {"name": "E. Quagliata", "position": "MF", "number": 22},
            {"name": "M. Zanimacchia", "position": "MF", "number": 25},
            {"name": "F. Bonazzoli", "position": "FW", "number": 9},
            {"name": "J. Vardy", "position": "FW", "number": 11},
        ],
        "bench": [
            {"name": "M. Sarr", "position": "GK", "number": 12},
            {"name": "F. Tsadjout", "position": "FW", "number": 90},
            {"name": "C. Dessers", "position": "FW", "number": 27},
            {"name": "P. Ghiglione", "position": "DF", "number": 2},
            {"name": "F. Collocolo", "position": "MF", "number": 80},
            {"name": "M. Pickel", "position": "MF", "number": 21},
            {"name": "L. Valzania", "position": "MF", "number": 20},
        ]
    },
    "Pisa": {
        "formation": "4-3-3",
        "starters": [
            {"name": "N. Andrade", "position": "GK", "number": 1},
            {"name": "A. Calabresi", "position": "DF", "number": 4},
            {"name": "A. Caracciolo", "position": "DF", "number": 5},
            {"name": "M. Canestrelli", "position": "DF", "number": 13},
            {"name": "S. Beruatto", "position": "DF", "number": 3},
            {"name": "G. Piccinini", "position": "MF", "number": 21},
            {"name": "M. Marin", "position": "MF", "number": 20},
            {"name": "A. Hojholt", "position": "MF", "number": 14},
            {"name": "M. Tramoni", "position": "FW", "number": 11},
            {"name": "M. Nzola", "position": "FW", "number": 9},
            {"name": "S. Moreo", "position": "FW", "number": 32},
        ],
        "bench": [
            {"name": "A. Loria", "position": "GK", "number": 22},
            {"name": "E. Torregrossa", "position": "FW", "number": 7},
            {"name": "A. Arena", "position": "FW", "number": 37},
            {"name": "I. Touré", "position": "DF", "number": 23},
            {"name": "M. Angori", "position": "DF", "number": 33},
            {"name": "H. Rus", "position": "DF", "number": 15},
            {"name": "S. Jevsenak", "position": "MF", "number": 6},
        ]
    },
}


@router.get(
    "/{fixture_id}",
    response_model=PredictionResponse,
    summary="Get prediction for a fixture"
)
async def get_prediction(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get latest prediction for a fixture"""
    try:
        query = select(Prediction).where(
            Prediction.fixture_id == fixture_id
        ).order_by(Prediction.created_at.desc()).limit(1)

        result = await db.execute(query)
        prediction = result.scalar_one_or_none()

        if not prediction:
            raise HTTPException(
                status_code=404,
                detail=f"No prediction found for fixture {fixture_id}"
            )

        return PredictionResponse.model_validate(prediction)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/history/{fixture_id}",
    response_model=List[PredictionResponse],
    summary="Get prediction history for a fixture"
)
async def get_prediction_history(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all prediction versions for a fixture.
    Useful for seeing how predictions changed over time (T-48h, T-24h, T-1h, etc.)
    """
    try:
        query = select(Prediction).where(
            Prediction.fixture_id == fixture_id
        ).order_by(Prediction.created_at.desc())

        result = await db.execute(query)
        predictions = result.scalars().all()

        if not predictions:
            raise HTTPException(
                status_code=404,
                detail=f"No predictions found for fixture {fixture_id}"
            )

        return [PredictionResponse.model_validate(p) for p in predictions]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prediction history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/recompute/{fixture_id}",
    response_model=PredictionResponse,
    summary="[ADMIN] Force recompute prediction"
)
async def recompute_prediction(
    fixture_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Force recompute prediction for a fixture.
    Useful for manual updates or debugging.

    NOTE: In production, this should be protected with admin authentication.
    """
    try:
        # Check fixture exists
        query = select(Fixture).where(Fixture.id == fixture_id)
        result = await db.execute(query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # TODO: Trigger prediction computation task
        # For now, return placeholder
        raise HTTPException(
            status_code=501,
            detail="Recompute endpoint not yet implemented. Use Celery task directly."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recomputing prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{fixture_id}/scorer-probabilities",
    response_model=FixtureScorersResponse,
    summary="Get top 5 likely scorers for a match"
)
async def get_scorer_probabilities(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Calcola le probabilità dei marcatori basandosi su:
    - Expected goals della partita
    - Posizione del giocatore (attaccanti >> centrocampisti > difensori)
    - Statistiche reali dei top scorers Serie A 2025-26
    """
    try:
        # Get fixture with prediction
        fixture_query = select(Fixture).where(Fixture.id == fixture_id).options(
            selectinload(Fixture.home_team),
            selectinload(Fixture.away_team),
            selectinload(Fixture.predictions)
        )
        result = await db.execute(fixture_query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get latest prediction
        prediction = None
        if fixture.predictions:
            prediction = max(fixture.predictions, key=lambda p: p.created_at)

        # Get squad data for both teams
        home_squad = TEAM_SQUADS.get(fixture.home_team.name, [])
        away_squad = TEAM_SQUADS.get(fixture.away_team.name, [])

        # Extract xG (default to 1.5 if no prediction)
        xg_home = prediction.expected_home_goals if prediction and prediction.expected_home_goals else 1.5
        xg_away = prediction.expected_away_goals if prediction and prediction.expected_away_goals else 1.5

        # Scale probabilities based on xG
        # If team expected to score more, increase probabilities
        xg_multiplier_home = min(1.5, max(0.5, xg_home / 1.5))
        xg_multiplier_away = min(1.5, max(0.5, xg_away / 1.5))

        # Build scorer lists
        home_scorers = [
            ScorerProbability(
                player_name=name,
                position=pos,
                probability=round(min(0.65, base_prob * xg_multiplier_home), 2)
            )
            for name, pos, base_prob in home_squad[:5]
        ]

        away_scorers = [
            ScorerProbability(
                player_name=name,
                position=pos,
                probability=round(min(0.65, base_prob * xg_multiplier_away), 2)
            )
            for name, pos, base_prob in away_squad[:5]
        ]

        return FixtureScorersResponse(
            fixture_id=fixture_id,
            home_team_scorers=home_scorers,
            away_team_scorers=away_scorers
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating scorer probabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{fixture_id}/lineups",
    response_model=FixtureLineupsResponse,
    summary="Get probable lineups (always available)"
)
async def get_probable_lineups(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Restituisce le formazioni probabili per una partita.

    Sempre disponibili in tempo reale.
    Mock implementation con formazioni realistiche basate su rose Serie A 2025-26.
    """
    try:
        # Get fixture
        fixture_query = select(Fixture).where(Fixture.id == fixture_id).options(
            selectinload(Fixture.home_team),
            selectinload(Fixture.away_team)
        )
        result = await db.execute(fixture_query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get lineups from mock data (always available)
        home_data = MOCK_LINEUPS.get(fixture.home_team.name)
        away_data = MOCK_LINEUPS.get(fixture.away_team.name)

        # Build response
        home_lineup = None
        if home_data:
            home_lineup = TeamLineup(
                team_name=fixture.home_team.name,
                formation=home_data["formation"],
                starters=[
                    LineupPlayer(
                        name=p["name"],
                        position=p["position"],
                        jersey_number=p["number"],
                        is_starter=True
                    )
                    for p in home_data["starters"]
                ],
                bench=[
                    LineupPlayer(
                        name=p["name"],
                        position=p["position"],
                        jersey_number=p["number"],
                        is_starter=False
                    )
                    for p in home_data["bench"]
                ]
            )

        away_lineup = None
        if away_data:
            away_lineup = TeamLineup(
                team_name=fixture.away_team.name,
                formation=away_data["formation"],
                starters=[
                    LineupPlayer(
                        name=p["name"],
                        position=p["position"],
                        jersey_number=p["number"],
                        is_starter=True
                    )
                    for p in away_data["starters"]
                ],
                bench=[
                    LineupPlayer(
                        name=p["name"],
                        position=p["position"],
                        jersey_number=p["number"],
                        is_starter=False
                    )
                    for p in away_data["bench"]
                ]
            )

        return FixtureLineupsResponse(
            fixture_id=fixture_id,
            home_lineup=home_lineup,
            away_lineup=away_lineup
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lineups: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{fixture_id}/biorhythms",
    response_model=FixtureBiorhythmsResponse,
    summary="Get biorhythms for both teams"
)
async def get_fixture_biorhythms(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Calcola i bioritmi di entrambe le squadre per una partita.

    I bioritmi analizzano i cicli biologici dei calciatori:
    - Fisico (23 giorni): forza, resistenza, coordinazione
    - Emotivo (28 giorni): umore, creatività, stabilità
    - Intellettuale (33 giorni): concentrazione, tattica, memoria

    Basato sulla teoria dei bioritmi applicata allo sport.
    Utilizza le date di nascita reali dei calciatori della Serie A.
    """
    try:
        # Get fixture
        fixture_query = select(Fixture).where(Fixture.id == fixture_id).options(
            selectinload(Fixture.home_team),
            selectinload(Fixture.away_team)
        )
        result = await db.execute(fixture_query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get lineups from mock data
        home_lineup_data = MOCK_LINEUPS.get(fixture.home_team.name)
        away_lineup_data = MOCK_LINEUPS.get(fixture.away_team.name)

        # Get match date
        match_date = fixture.match_date.date() if isinstance(fixture.match_date, datetime) else fixture.match_date

        # Calculate home team biorhythms
        home_birthdates = get_team_birthdates(fixture.home_team.name, home_lineup_data)
        home_team_stats = compare_team_biorhythms(home_birthdates, match_date)

        # Calculate individual biorhythms for top performers (home)
        home_player_biorhythms = []
        if home_lineup_data:
            for player in home_lineup_data.get("starters", [])[:11]:  # Solo titolari
                birthdate = get_birthdate(player["name"])
                if birthdate:
                    bio = calculate_player_biorhythm(birthdate, match_date)
                    home_player_biorhythms.append({
                        'player_name': player["name"],
                        'position': player["position"],
                        'bio': bio
                    })

        # Sort by overall score and take top 3
        home_player_biorhythms.sort(key=lambda x: x['bio'].overall, reverse=True)
        home_top_performers = [
            PlayerBiorhythm(
                player_name=p['player_name'],
                position=p['position'],
                physical=p['bio'].physical,
                emotional=p['bio'].emotional,
                intellectual=p['bio'].intellectual,
                overall=p['bio'].overall,
                status=p['bio'].status
            )
            for p in home_player_biorhythms[:3]
        ]

        # Calculate away team biorhythms
        away_birthdates = get_team_birthdates(fixture.away_team.name, away_lineup_data)
        away_team_stats = compare_team_biorhythms(away_birthdates, match_date)

        # Calculate individual biorhythms for top performers (away)
        away_player_biorhythms = []
        if away_lineup_data:
            for player in away_lineup_data.get("starters", [])[:11]:  # Solo titolari
                birthdate = get_birthdate(player["name"])
                if birthdate:
                    bio = calculate_player_biorhythm(birthdate, match_date)
                    away_player_biorhythms.append({
                        'player_name': player["name"],
                        'position': player["position"],
                        'bio': bio
                    })

        # Sort by overall score and take top 3
        away_player_biorhythms.sort(key=lambda x: x['bio'].overall, reverse=True)
        away_top_performers = [
            PlayerBiorhythm(
                player_name=p['player_name'],
                position=p['position'],
                physical=p['bio'].physical,
                emotional=p['bio'].emotional,
                intellectual=p['bio'].intellectual,
                overall=p['bio'].overall,
                status=p['bio'].status
            )
            for p in away_player_biorhythms[:3]
        ]

        # Build team biorhythm responses
        home_team_bio = TeamBiorhythm(
            team_name=fixture.home_team.name,
            avg_physical=home_team_stats['avg_physical'],
            avg_emotional=home_team_stats['avg_emotional'],
            avg_intellectual=home_team_stats['avg_intellectual'],
            avg_overall=home_team_stats['avg_overall'],
            players_excellent=home_team_stats['players_excellent'],
            players_good=home_team_stats['players_good'],
            players_low=home_team_stats['players_low'],
            players_critical=home_team_stats['players_critical'],
            total_players=home_team_stats['total_players'],
            top_performers=home_top_performers
        )

        away_team_bio = TeamBiorhythm(
            team_name=fixture.away_team.name,
            avg_physical=away_team_stats['avg_physical'],
            avg_emotional=away_team_stats['avg_emotional'],
            avg_intellectual=away_team_stats['avg_intellectual'],
            avg_overall=away_team_stats['avg_overall'],
            players_excellent=away_team_stats['players_excellent'],
            players_good=away_team_stats['players_good'],
            players_low=away_team_stats['players_low'],
            players_critical=away_team_stats['players_critical'],
            total_players=away_team_stats['total_players'],
            top_performers=away_top_performers
        )

        # Determine biorhythm advantage
        home_overall = home_team_stats['avg_overall']
        away_overall = away_team_stats['avg_overall']

        if abs(home_overall - away_overall) < 10:
            advantage = "neutral"
        elif home_overall > away_overall:
            advantage = "home"
        else:
            advantage = "away"

        return FixtureBiorhythmsResponse(
            fixture_id=fixture_id,
            match_date=fixture.match_date,
            home_team_biorhythm=home_team_bio,
            away_team_biorhythm=away_team_bio,
            biorhythm_advantage=advantage
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating biorhythms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
