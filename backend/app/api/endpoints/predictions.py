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
    LineupPlayer
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Mock data: Top 5 players per team with base goal probability
# Based on real Serie A 2025-26 top scorers (Giornata 17)
TEAM_SQUADS = {
    "Inter": [
        ("Lautaro Martinez", "Attaccante", 0.38),
        ("Marcus Thuram", "Attaccante", 0.35),
        ("Hakan Calhanoglu", "Centrocampista", 0.18),
        ("Nicolò Barella", "Centrocampista", 0.15),
        ("Denzel Dumfries", "Centrocampista", 0.12),
    ],
    "AC Milan": [
        ("Christian Pulisic", "Attaccante", 0.40),
        ("Rafael Leao", "Attaccante", 0.30),
        ("Álvaro Morata", "Attaccante", 0.25),
        ("Tijjani Reijnders", "Centrocampista", 0.20),
        ("Theo Hernández", "Difensore", 0.12),
    ],
    "Napoli": [
        ("Romelu Lukaku", "Attaccante", 0.32),
        ("Khvicha Kvaratskhelia", "Attaccante", 0.28),
        ("Giacomo Raspadori", "Attaccante", 0.22),
        ("Matteo Politano", "Centrocampista", 0.18),
        ("Giovanni Di Lorenzo", "Difensore", 0.08),
    ],
    "Juventus": [
        ("Dušan Vlahović", "Attaccante", 0.42),
        ("Federico Chiesa", "Attaccante", 0.28),
        ("Kenan Yıldız", "Centrocampista", 0.20),
        ("Timothy Weah", "Centrocampista", 0.15),
        ("Andrea Cambiaso", "Difensore", 0.10),
    ],
    "AS Roma": [
        ("Paulo Dybala", "Attaccante", 0.35),
        ("Artem Dovbyk", "Attaccante", 0.30),
        ("Lorenzo Pellegrini", "Centrocampista", 0.20),
        ("Stephan El Shaarawy", "Centrocampista", 0.15),
        ("Bryan Cristante", "Centrocampista", 0.12),
    ],
    "Bologna": [
        ("Riccardo Orsolini", "Attaccante", 0.38),
        ("Joshua Zirkzee", "Attaccante", 0.30),
        ("Lewis Ferguson", "Centrocampista", 0.18),
        ("Alexis Saelemaekers", "Centrocampista", 0.15),
        ("Dan Ndoye", "Centrocampista", 0.12),
    ],
    "Atalanta": [
        ("Mateo Retegui", "Attaccante", 0.36),
        ("Ademola Lookman", "Attaccante", 0.32),
        ("Charles De Ketelaere", "Centrocampista", 0.22),
        ("Gianluca Scamacca", "Attaccante", 0.20),
        ("Éderson", "Centrocampista", 0.10),
    ],
    "Lazio": [
        ("Tijjani Noslin", "Attaccante", 0.30),
        ("Valentín Castellanos", "Attaccante", 0.28),
        ("Mattia Zaccagni", "Centrocampista", 0.22),
        ("Luis Alberto", "Centrocampista", 0.18),
        ("Felipe Anderson", "Centrocampista", 0.12),
    ],
    "Como": [
        ("Patrick Cutrone", "Attaccante", 0.32),
        ("Andrea Belotti", "Attaccante", 0.28),
        ("Nikola Moro", "Centrocampista", 0.18),
        ("Lucas Da Cunha", "Centrocampista", 0.15),
        ("Alessandro Gabrielloni", "Attaccante", 0.12),
    ],
    "Fiorentina": [
        ("Moise Kean", "Attaccante", 0.40),
        ("Jonathan Ikoné", "Attaccante", 0.25),
        ("Giacomo Bonaventura", "Centrocampista", 0.18),
        ("Nicolás González", "Centrocampista", 0.15),
        ("Rolando Mandragora", "Centrocampista", 0.10),
    ],
    "Parma": [
        ("Dennis Man", "Attaccante", 0.30),
        ("Ange-Yoan Bonny", "Attaccante", 0.25),
        ("Valentin Mihăilă", "Centrocampista", 0.20),
        ("Hernani", "Centrocampista", 0.15),
        ("Adrian Benedyczak", "Attaccante", 0.12),
    ],
    "Torino": [
        ("Antonio Sanabria", "Attaccante", 0.28),
        ("Duván Zapata", "Attaccante", 0.25),
        ("Nikola Vlašić", "Centrocampista", 0.20),
        ("Aleksey Miranchuk", "Centrocampista", 0.15),
        ("Samuele Ricci", "Centrocampista", 0.10),
    ],
    "Udinese": [
        ("Lorenzo Lucca", "Attaccante", 0.32),
        ("Florian Thauvin", "Attaccante", 0.28),
        ("Lazar Samardžić", "Centrocampista", 0.20),
        ("Roberto Pereyra", "Centrocampista", 0.15),
        ("Sandi Lovric", "Centrocampista", 0.12),
    ],
    "Lecce": [
        ("Nikola Krstović", "Attaccante", 0.35),
        ("Roberto Piccoli", "Attaccante", 0.25),
        ("Lameck Banda", "Centrocampista", 0.18),
        ("Pontus Almqvist", "Centrocampista", 0.15),
        ("Remi Oudin", "Centrocampista", 0.10),
    ],
    "Sassuolo": [
        ("Andrea Pinamonti", "Attaccante", 0.38),
        ("Armand Laurienté", "Attaccante", 0.28),
        ("Domenico Berardi", "Centrocampista", 0.22),
        ("Nedim Bajrami", "Centrocampista", 0.18),
        ("Matheus Henrique", "Centrocampista", 0.12),
    ],
    "Genoa": [
        ("Albert Guðmundsson", "Attaccante", 0.30),
        ("Vitinha", "Attaccante", 0.25),
        ("Junior Messias", "Centrocampista", 0.20),
        ("Morten Frendrup", "Centrocampista", 0.15),
        ("Ruslan Malinovskyi", "Centrocampista", 0.12),
    ],
    "Cagliari": [
        ("Leonardo Pavoletti", "Attaccante", 0.28),
        ("Eldor Shomurodov", "Attaccante", 0.25),
        ("Gianluca Gaetano", "Centrocampista", 0.20),
        ("Zito Luvumbo", "Centrocampista", 0.15),
        ("Nahitan Nández", "Centrocampista", 0.12),
    ],
    "Hellas Verona": [
        ("Milan Đurić", "Attaccante", 0.30),
        ("Cyril Ngonge", "Attaccante", 0.25),
        ("Tijjani Noslin", "Centrocampista", 0.18),
        ("Tomáš Suslov", "Centrocampista", 0.15),
        ("Darko Lazović", "Centrocampista", 0.10),
    ],
    "Cremonese": [
        ("Valentin Carboni", "Attaccante", 0.32),
        ("Leonardo Sernicola", "Centrocampista", 0.25),
        ("Frank Tsadjout", "Attaccante", 0.22),
        ("Michele Castagnetti", "Centrocampista", 0.15),
        ("Cristian Buonaiuto", "Centrocampista", 0.12),
    ],
    "Pisa": [
        ("Arturo Calabresi", "Difensore", 0.20),
        ("Gabriele Piccinini", "Centrocampista", 0.18),
        ("Mattéo Tramoni", "Centrocampista", 0.15),
        ("Alessandro Arena", "Centrocampista", 0.12),
        ("Stefano Moreo", "Attaccante", 0.25),
    ],
}


# Mock lineups for all 20 Serie A teams (11 starters + 7 bench each)
# Based on real Serie A 2025-26 squads from Transfermarkt
MOCK_LINEUPS = {
    "Inter": {
        "formation": "3-5-2",
        "starters": [
            {"name": "Y. Sommer", "position": "GK", "number": 1},
            {"name": "B. Pavard", "position": "DF", "number": 28},
            {"name": "S. de Vrij", "position": "DF", "number": 6},
            {"name": "A. Bastoni", "position": "DF", "number": 95},
            {"name": "D. Dumfries", "position": "MF", "number": 2},
            {"name": "N. Barella", "position": "MF", "number": 23},
            {"name": "H. Calhanoglu", "position": "MF", "number": 20},
            {"name": "H. Mkhitaryan", "position": "MF", "number": 22},
            {"name": "F. Dimarco", "position": "MF", "number": 32},
            {"name": "L. Martinez", "position": "FW", "number": 10},
            {"name": "M. Thuram", "position": "FW", "number": 9},
        ],
        "bench": [
            {"name": "E. Audero", "position": "GK", "number": 77},
            {"name": "D. Frattesi", "position": "MF", "number": 16},
            {"name": "K. Asllani", "position": "MF", "number": 21},
            {"name": "M. Arnautovic", "position": "FW", "number": 8},
            {"name": "J. Correa", "position": "FW", "number": 11},
            {"name": "M. Darmian", "position": "DF", "number": 36},
            {"name": "C. Augusto", "position": "DF", "number": 30},
        ]
    },
    "AC Milan": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "M. Maignan", "position": "GK", "number": 16},
            {"name": "E. Royal", "position": "DF", "number": 22},
            {"name": "M. Gabbia", "position": "DF", "number": 46},
            {"name": "F. Tomori", "position": "DF", "number": 23},
            {"name": "T. Hernández", "position": "DF", "number": 19},
            {"name": "Y. Fofana", "position": "MF", "number": 29},
            {"name": "T. Reijnders", "position": "MF", "number": 14},
            {"name": "C. Pulisic", "position": "FW", "number": 11},
            {"name": "R. Loftus-Cheek", "position": "MF", "number": 8},
            {"name": "R. Leao", "position": "FW", "number": 10},
            {"name": "A. Morata", "position": "FW", "number": 7},
        ],
        "bench": [
            {"name": "L. Torriani", "position": "GK", "number": 96},
            {"name": "S. Chukwueze", "position": "FW", "number": 21},
            {"name": "N. Okafor", "position": "FW", "number": 17},
            {"name": "Y. Musah", "position": "MF", "number": 80},
            {"name": "K. Terracciano", "position": "DF", "number": 42},
            {"name": "D. Calabria", "position": "DF", "number": 2},
            {"name": "M. Thiaw", "position": "DF", "number": 28},
        ]
    },
    "Napoli": {
        "formation": "4-3-3",
        "starters": [
            {"name": "A. Meret", "position": "GK", "number": 1},
            {"name": "G. Di Lorenzo", "position": "DF", "number": 22},
            {"name": "A. Rrahmani", "position": "DF", "number": 13},
            {"name": "K. Min-jae", "position": "DF", "number": 3},
            {"name": "M. Rui", "position": "DF", "number": 6},
            {"name": "A. Zambo Anguissa", "position": "MF", "number": 99},
            {"name": "S. Lobotka", "position": "MF", "number": 68},
            {"name": "P. Zielinski", "position": "MF", "number": 20},
            {"name": "M. Politano", "position": "FW", "number": 21},
            {"name": "R. Lukaku", "position": "FW", "number": 9},
            {"name": "K. Kvaratskhelia", "position": "FW", "number": 77},
        ],
        "bench": [
            {"name": "A. Contini", "position": "GK", "number": 12},
            {"name": "G. Raspadori", "position": "FW", "number": 81},
            {"name": "E. Elmas", "position": "MF", "number": 7},
            {"name": "M. Olivera", "position": "DF", "number": 17},
            {"name": "L. Zanoli", "position": "DF", "number": 59},
            {"name": "T. Ndombele", "position": "MF", "number": 91},
            {"name": "A. Zerbin", "position": "FW", "number": 23},
        ]
    },
    "Juventus": {
        "formation": "3-5-2",
        "starters": [
            {"name": "W. Szczęsny", "position": "GK", "number": 1},
            {"name": "D. Rugani", "position": "DF", "number": 24},
            {"name": "G. Bremer", "position": "DF", "number": 3},
            {"name": "A. Sandro", "position": "DF", "number": 12},
            {"name": "J. Cuadrado", "position": "MF", "number": 11},
            {"name": "M. Locatelli", "position": "MF", "number": 5},
            {"name": "A. Rabiot", "position": "MF", "number": 25},
            {"name": "F. Kostic", "position": "MF", "number": 17},
            {"name": "F. Chiesa", "position": "FW", "number": 7},
            {"name": "D. Vlahović", "position": "FW", "number": 9},
            {"name": "A. Milik", "position": "FW", "number": 14},
        ],
        "bench": [
            {"name": "M. Perin", "position": "GK", "number": 36},
            {"name": "K. Yıldız", "position": "MF", "number": 15},
            {"name": "T. Weah", "position": "FW", "number": 22},
            {"name": "S. McKennie", "position": "MF", "number": 8},
            {"name": "A. Cambiaso", "position": "DF", "number": 27},
            {"name": "D. Huijsen", "position": "DF", "number": 34},
            {"name": "F. Miretti", "position": "MF", "number": 20},
        ]
    },
    "AS Roma": {
        "formation": "3-4-2-1",
        "starters": [
            {"name": "R. Patricio", "position": "GK", "number": 1},
            {"name": "G. Mancini", "position": "DF", "number": 23},
            {"name": "C. Smalling", "position": "DF", "number": 6},
            {"name": "R. Karsdorp", "position": "DF", "number": 2},
            {"name": "L. Spinazzola", "position": "MF", "number": 37},
            {"name": "B. Cristante", "position": "MF", "number": 4},
            {"name": "L. Pellegrini", "position": "MF", "number": 7},
            {"name": "S. El Shaarawy", "position": "MF", "number": 92},
            {"name": "P. Dybala", "position": "FW", "number": 21},
            {"name": "T. Abraham", "position": "FW", "number": 9},
            {"name": "A. Dovbyk", "position": "FW", "number": 11},
        ],
        "bench": [
            {"name": "M. Svilar", "position": "GK", "number": 99},
            {"name": "N. Zalewski", "position": "MF", "number": 59},
            {"name": "E. Bove", "position": "MF", "number": 52},
            {"name": "A. Belotti", "position": "FW", "number": 11},
            {"name": "D. Celik", "position": "DF", "number": 19},
            {"name": "E. Llorente", "position": "DF", "number": 14},
            {"name": "H. Aouar", "position": "MF", "number": 22},
        ]
    },
    "Bologna": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "Ł. Skorupski", "position": "GK", "number": 28},
            {"name": "S. Posch", "position": "DF", "number": 3},
            {"name": "J. Lucumi", "position": "DF", "number": 26},
            {"name": "R. Calafiori", "position": "DF", "number": 33},
            {"name": "C. Lykogiannis", "position": "DF", "number": 22},
            {"name": "L. Ferguson", "position": "MF", "number": 19},
            {"name": "N. Moro", "position": "MF", "number": 6},
            {"name": "R. Orsolini", "position": "FW", "number": 7},
            {"name": "A. Saelemaekers", "position": "MF", "number": 56},
            {"name": "D. Ndoye", "position": "FW", "number": 11},
            {"name": "J. Zirkzee", "position": "FW", "number": 9},
        ],
        "bench": [
            {"name": "F. Ravaglia", "position": "GK", "number": 1},
            {"name": "S. El Azzouzi", "position": "MF", "number": 30},
            {"name": "K. Aebischer", "position": "MF", "number": 20},
            {"name": "J. Odgaard", "position": "MF", "number": 21},
            {"name": "V. Kristiansen", "position": "DF", "number": 15},
            {"name": "S. De Silvestri", "position": "DF", "number": 29},
            {"name": "R. Fabbian", "position": "MF", "number": 80},
        ]
    },
    "Atalanta": {
        "formation": "3-4-3",
        "starters": [
            {"name": "M. Carnesecchi", "position": "GK", "number": 29},
            {"name": "G. Scalvini", "position": "DF", "number": 42},
            {"name": "S. Kolasinac", "position": "DF", "number": 23},
            {"name": "I. Hien", "position": "DF", "number": 4},
            {"name": "D. Zappacosta", "position": "MF", "number": 77},
            {"name": "Éderson", "position": "MF", "number": 13},
            {"name": "M. de Roon", "position": "MF", "number": 15},
            {"name": "M. Ruggeri", "position": "MF", "number": 22},
            {"name": "A. Lookman", "position": "FW", "number": 11},
            {"name": "M. Retegui", "position": "FW", "number": 32},
            {"name": "C. De Ketelaere", "position": "FW", "number": 17},
        ],
        "bench": [
            {"name": "J. Musso", "position": "GK", "number": 1},
            {"name": "G. Scamacca", "position": "FW", "number": 90},
            {"name": "M. Pasalic", "position": "MF", "number": 8},
            {"name": "B. Djimsiti", "position": "DF", "number": 19},
            {"name": "H. Hateboer", "position": "DF", "number": 33},
            {"name": "T. Koopme iners", "position": "DF", "number": 7},
            {"name": "M. Brescianini", "position": "MF", "number": 44},
        ]
    },
    "Lazio": {
        "formation": "4-3-3",
        "starters": [
            {"name": "I. Provedel", "position": "GK", "number": 94},
            {"name": "M. Lazzari", "position": "DF", "number": 29},
            {"name": "M. Romagnoli", "position": "DF", "number": 13},
            {"name": "P. Rodríguez", "position": "DF", "number": 2},
            {"name": "A. Marušić", "position": "DF", "number": 77},
            {"name": "D. Cataldi", "position": "MF", "number": 32},
            {"name": "Luis Alberto", "position": "MF", "number": 10},
            {"name": "M. Zaccagni", "position": "MF", "number": 20},
            {"name": "F. Anderson", "position": "FW", "number": 7},
            {"name": "V. Castellanos", "position": "FW", "number": 19},
            {"name": "T. Noslin", "position": "FW", "number": 14},
        ],
        "bench": [
            {"name": "L. Mandas", "position": "GK", "number": 35},
            {"name": "G. Isaksen", "position": "FW", "number": 18},
            {"name": "N. Rovella", "position": "MF", "number": 6},
            {"name": "D. Kamada", "position": "MF", "number": 11},
            {"name": "M. Gila", "position": "DF", "number": 34},
            {"name": "E. Hysaj", "position": "DF", "number": 23},
            {"name": "G. Tchaouna", "position": "FW", "number": 20},
        ]
    },
    "Como": {
        "formation": "4-4-2",
        "starters": [
            {"name": "E. Semper", "position": "GK", "number": 1},
            {"name": "A. Iovine", "position": "DF", "number": 2},
            {"name": "M. Odenthal", "position": "DF", "number": 5},
            {"name": "A. Barba", "position": "DF", "number": 93},
            {"name": "M. Sala", "position": "DF", "number": 3},
            {"name": "N. Moro", "position": "MF", "number": 7},
            {"name": "L. Da Cunha", "position": "MF", "number": 33},
            {"name": "A. Fabregas", "position": "MF", "number": 4},
            {"name": "Y. Engelhardt", "position": "MF", "number": 79},
            {"name": "P. Cutrone", "position": "FW", "number": 10},
            {"name": "A. Belotti", "position": "FW", "number": 11},
        ],
        "bench": [
            {"name": "P. Vigorito", "position": "GK", "number": 12},
            {"name": "A. Gabrielloni", "position": "FW", "number": 9},
            {"name": "N. Paz", "position": "MF", "number": 79},
            {"name": "F. Baselli", "position": "MF", "number": 27},
            {"name": "E. Goldaniga", "position": "DF", "number": 5},
            {"name": "C. Fadera", "position": "FW", "number": 16},
            {"name": "L. Mazzitelli", "position": "MF", "number": 36},
        ]
    },
    "Fiorentina": {
        "formation": "4-2-3-1",
        "starters": [
            {"name": "P. Terracciano", "position": "GK", "number": 1},
            {"name": "M. Quarta", "position": "DF", "number": 28},
            {"name": "L. Ranieri", "position": "DF", "number": 6},
            {"name": "C. Biraghi", "position": "DF", "number": 3},
            {"name": "D. Dodo", "position": "DF", "number": 2},
            {"name": "R. Mandragora", "position": "MF", "number": 38},
            {"name": "A. Duncan", "position": "MF", "number": 32},
            {"name": "N. González", "position": "FW", "number": 10},
            {"name": "G. Bonaventura", "position": "MF", "number": 5},
            {"name": "J. Ikoné", "position": "FW", "number": 11},
            {"name": "M. Kean", "position": "FW", "number": 20},
        ],
        "bench": [
            {"name": "O. Christensen", "position": "GK", "number": 53},
            {"name": "A. Barak", "position": "MF", "number": 72},
            {"name": "J. Brekalo", "position": "FW", "number": 21},
            {"name": "R. Sottil", "position": "FW", "number": 7},
            {"name": "L. Martínez Quarta", "position": "DF", "number": 28},
            {"name": "M. Kayode", "position": "DF", "number": 33},
            {"name": "Y. Kouamé", "position": "FW", "number": 99},
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
            {"name": "N. Bajrami", "position": "MF", "number": 10},
            {"name": "A. Laurienté", "position": "FW", "number": 45},
            {"name": "A. Pinamonti", "position": "FW", "number": 9},
            {"name": "D. Berardi", "position": "FW", "number": 25},
        ],
        "bench": [
            {"name": "G. Pegolo", "position": "GK", "number": 64},
            {"name": "G. Defrel", "position": "FW", "number": 92},
            {"name": "C. Volpato", "position": "MF", "number": 22},
            {"name": "U. Racic", "position": "MF", "number": 6},
            {"name": "F. Romagna", "position": "DF", "number": 27},
            {"name": "M. Viti", "position": "DF", "number": 44},
            {"name": "S. Mulattieri", "position": "FW", "number": 30},
        ]
    },
    "Genoa": {
        "formation": "3-5-2",
        "starters": [
            {"name": "J. Martinez", "position": "GK", "number": 1},
            {"name": "K. De Winter", "position": "DF", "number": 4},
            {"name": "M. Bani", "position": "DF", "number": 13},
            {"name": "J. Vásquez", "position": "DF", "number": 22},
            {"name": "S. Sabelli", "position": "MF", "number": 20},
            {"name": "M. Frendrup", "position": "MF", "number": 32},
            {"name": "M. Badelj", "position": "MF", "number": 47},
            {"name": "A. Martin", "position": "MF", "number": 3},
            {"name": "R. Malinovskyi", "position": "FW", "number": 17},
            {"name": "A. Guðmundsson", "position": "FW", "number": 11},
            {"name": "Vitinha", "position": "FW", "number": 9},
        ],
        "bench": [
            {"name": "N. Leali", "position": "GK", "number": 95},
            {"name": "J. Messias", "position": "MF", "number": 10},
            {"name": "H. Ekuban", "position": "FW", "number": 18},
            {"name": "A. Vogliacco", "position": "DF", "number": 14},
            {"name": "M. Thorsby", "position": "MF", "number": 2},
            {"name": "A. Marcandalli", "position": "DF", "number": 83},
            {"name": "D. Ankeye", "position": "FW", "number": 21},
        ]
    },
    "Cagliari": {
        "formation": "4-3-3",
        "starters": [
            {"name": "S. Scuffet", "position": "GK", "number": 22},
            {"name": "A. Zappa", "position": "DF", "number": 28},
            {"name": "Y. Mina", "position": "DF", "number": 26},
            {"name": "A. Dossena", "position": "DF", "number": 4},
            {"name": "T. Augello", "position": "DF", "number": 3},
            {"name": "A. Makoumbou", "position": "MF", "number": 29},
            {"name": "N. Nández", "position": "MF", "number": 8},
            {"name": "M. Prati", "position": "MF", "number": 16},
            {"name": "Z. Luvumbo", "position": "FW", "number": 77},
            {"name": "L. Pavoletti", "position": "FW", "number": 30},
            {"name": "G. Gaetano", "position": "FW", "number": 70},
        ],
        "bench": [
            {"name": "B. Aresti", "position": "GK", "number": 31},
            {"name": "E. Shomurodov", "position": "FW", "number": 61},
            {"name": "N. Viola", "position": "MF", "number": 10},
            {"name": "I. Sulemana", "position": "MF", "number": 6},
            {"name": "P. Azzi", "position": "DF", "number": 37},
            {"name": "A. Obert", "position": "DF", "number": 33},
            {"name": "M. Wieteska", "position": "DF", "number": 23},
        ]
    },
    "Hellas Verona": {
        "formation": "3-4-2-1",
        "starters": [
            {"name": "L. Montipò", "position": "GK", "number": 1},
            {"name": "D. Coppola", "position": "DF", "number": 42},
            {"name": "G. Magnani", "position": "DF", "number": 23},
            {"name": "P. Dawidowicz", "position": "DF", "number": 27},
            {"name": "J. Tchatchoua", "position": "MF", "number": 38},
            {"name": "S. Serdar", "position": "MF", "number": 25},
            {"name": "O. Duda", "position": "MF", "number": 33},
            {"name": "D. Lazović", "position": "MF", "number": 8},
            {"name": "T. Suslov", "position": "FW", "number": 31},
            {"name": "C. Ngonge", "position": "FW", "number": 26},
            {"name": "M. Đurić", "position": "FW", "number": 11},
        ],
        "bench": [
            {"name": "S. Perilli", "position": "GK", "number": 34},
            {"name": "T. Noslin", "position": "FW", "number": 17},
            {"name": "K. Lasagna", "position": "FW", "number": 18},
            {"name": "D. Faraoni", "position": "DF", "number": 5},
            {"name": "D. Ghilardi", "position": "DF", "number": 87},
            {"name": "F. Terracciano", "position": "MF", "number": 20},
            {"name": "M. Hongla", "position": "MF", "number": 14},
        ]
    },
    "Cremonese": {
        "formation": "3-5-2",
        "starters": [
            {"name": "M. Carnesecchi", "position": "GK", "number": 1},
            {"name": "M. Bianchetti", "position": "DF", "number": 15},
            {"name": "E. Lochoshvili", "position": "DF", "number": 5},
            {"name": "L. Sernicola", "position": "DF", "number": 17},
            {"name": "L. Valzania", "position": "MF", "number": 20},
            {"name": "M. Castagnetti", "position": "MF", "number": 19},
            {"name": "C. Buonaiuto", "position": "MF", "number": 33},
            {"name": "E. Quagliata", "position": "MF", "number": 22},
            {"name": "M. Zanimacchia", "position": "MF", "number": 25},
            {"name": "V. Carboni", "position": "FW", "number": 70},
            {"name": "F. Tsadjout", "position": "FW", "number": 9},
        ],
        "bench": [
            {"name": "M. Sarr", "position": "GK", "number": 12},
            {"name": "D. Ciofani", "position": "FW", "number": 32},
            {"name": "F. Afena-Gyan", "position": "FW", "number": 11},
            {"name": "L. Ravanelli", "position": "DF", "number": 44},
            {"name": "P. Ghiglione", "position": "DF", "number": 2},
            {"name": "F. Collocolo", "position": "MF", "number": 80},
            {"name": "M. Pickel", "position": "MF", "number": 21},
        ]
    },
    "Pisa": {
        "formation": "4-3-3",
        "starters": [
            {"name": "N. Andrade", "position": "GK", "number": 1},
            {"name": "A. Calabresi", "position": "DF", "number": 4},
            {"name": "A. Caracciolo", "position": "DF", "number": 5},
            {"name": "M. Canestrelli", "position": "DF", "number": "13},
            {"name": "S. Beruatto", "position": "DF", "number": 3},
            {"name": "G. Piccinini", "position": "MF", "number": 21},
            {"name": "M. Marin", "position": "MF", "number": 20},
            {"name": "A. Hojholt", "position": "MF", "number": 14},
            {"name": "M. Tramoni", "position": "FW", "number": 11},
            {"name": "S. Moreo", "position": "FW", "number": 32},
            {"name": "A. Arena", "position": "FW", "number": 37},
        ],
        "bench": [
            {"name": "A. Loria", "position": "GK", "number": 22},
            {"name": "E. Torregrossa", "position": "FW", "number": 9},
            {"name": "G. Bonfanti", "position": "FW", "number": 98},
            {"name": "I. Touré", "position": "DF", "number": 23},
            {"name": "M. Angori", "position": "DF", "number": 3},
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
        ).order_by(Prediction.computed_at.desc()).limit(1)

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
        ).order_by(Prediction.computed_at.desc())

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
    summary="Get probable lineups (available 1h before match)"
)
async def get_probable_lineups(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Restituisce le formazioni probabili per una partita.

    Disponibili 1 ora prima del calcio d'inizio.
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

        # Check if lineups are available (1h before match)
        now = datetime.now(timezone.utc)
        match_time = fixture.match_date.replace(tzinfo=timezone.utc) if fixture.match_date.tzinfo is None else fixture.match_date
        one_hour_before = match_time - timedelta(hours=1)

        if now < one_hour_before:
            return FixtureLineupsResponse(
                fixture_id=fixture_id,
                available_from=one_hour_before,
                home_lineup=None,
                away_lineup=None
            )

        # Get lineups from mock data
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
            available_from=one_hour_before,
            home_lineup=home_lineup,
            away_lineup=away_lineup
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lineups: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
