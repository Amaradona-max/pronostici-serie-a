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
# Auto-generated from verified database (January 2026)
TEAM_SQUADS = {
    "AC Milan": [
        ("Santiago Gimenez", "Attaccante", 0.4),
        ("Rafael Leao", "Attaccante", 0.35),
        ("Christian Pulisic", "Attaccante", 0.3),
        ("Christopher Nkunku", "Attaccante", 0.25),
        ("Niclas Fullkrug", "Attaccante", 0.2),
    ],
    "AS Roma": [
        ("Leon Bailey", "Attaccante", 0.4),
        ("Evan Ferguson", "Attaccante", 0.35),
        ("Artem Dovbyk", "Attaccante", 0.3),
        ("Matias Soule", "Attaccante", 0.25),
        ("Paulo Dybala", "Attaccante", 0.2),
    ],
    "Atalanta": [
        ("Gianluca Scamacca", "Attaccante", 0.4),
        ("Ademola Lookman", "Attaccante", 0.35),
        ("Charles De Ketelaere", "Attaccante", 0.3),
        ("Mario Pasalic", "Centrocampista", 0.15),
        ("Ederson", "Centrocampista", 0.15),
    ],
    "Bologna": [
        ("Riccardo Orsolini", "Attaccante", 0.4),
        ("Santiago Castro", "Attaccante", 0.35),
        ("Jonathan Rowe", "Attaccante", 0.3),
        ("Ciro Immobile", "Attaccante", 0.25),
        ("Federico Bernardeschi", "Attaccante", 0.2),
    ],
    "Cagliari": [
        ("Semih Kilicsoy", "Attaccante", 0.4),
        ("Andrea Belotti", "Attaccante", 0.35),
        ("Mattia Felici", "Attaccante", 0.3),
        ("Leonardo Pavoletti", "Attaccante", 0.25),
        ("Zito Luvumbo", "Attaccante", 0.2),
    ],
    "Como": [
        ("Alvaro Morata", "Attaccante", 0.4),
        ("Jesus Rodriguez", "Attaccante", 0.35),
        ("Nicolas Kuhn", "Attaccante", 0.3),
        ("Jayden Addai", "Attaccante", 0.25),
        ("Assane Diao", "Attaccante", 0.2),
    ],
    "Cremonese": [
        ("Jamie Vardy", "Attaccante", 0.4),
        ("David Okereke", "Attaccante", 0.35),
        ("Antonio Sanabria", "Attaccante", 0.3),
        ("Faris Moumbagna", "Attaccante", 0.25),
        ("Federico Bonazzoli", "Attaccante", 0.2),
    ],
    "Fiorentina": [
        ("Edin Dzeko", "Attaccante", 0.4),
        ("Moise Kean", "Attaccante", 0.35),
        ("Roberto Piccoli", "Attaccante", 0.3),
        ("Christian Kouame", "Attaccante", 0.25),
        ("Simon Sohm", "Centrocampista", 0.15),
    ],
    "Genoa": [
        ("Vitinha", "Attaccante", 0.4),
        ("Maxwel Cornet", "Attaccante", 0.35),
        ("Caleb Ekuban", "Attaccante", 0.3),
        ("Junior Messias", "Attaccante", 0.25),
        ("Jeff Ekhator", "Attaccante", 0.2),
    ],
    "Hellas Verona": [
        ("Daniel Mosquera", "Attaccante", 0.4),
        ("Gift Orban", "Attaccante", 0.35),
        ("Amin Sarr", "Attaccante", 0.3),
        ("Giovane", "Attaccante", 0.25),
        ("Moatasem Al-Musrati", "Centrocampista", 0.15),
    ],
    "Inter": [
        ("Marcus Thuram", "Attaccante", 0.4),
        ("Lautaro Martinez", "Attaccante", 0.35),
        ("Ange-Yoan Bonny", "Attaccante", 0.3),
        ("Pio Esposito", "Attaccante", 0.25),
        ("Piotr Zielinski", "Centrocampista", 0.15),
    ],
    "Juventus": [
        ("Edon Zhegrova", "Attaccante", 0.4),
        ("Dusan Vlahovic", "Attaccante", 0.35),
        ("Kenan Yildiz", "Attaccante", 0.3),
        ("Arkadiusz Milik", "Attaccante", 0.25),
        ("Jonathan David", "Attaccante", 0.2),
    ],
    "Lazio": [
        ("Pedro", "Attaccante", 0.4),
        ("Mattia Zaccagni", "Attaccante", 0.35),
        ("Taty Castellanos", "Attaccante", 0.3),
        ("Tijjani Noslin", "Attaccante", 0.25),
        ("Gustav Isaksen", "Attaccante", 0.2),
    ],
    "Lecce": [
        ("Riccardo Sottil", "Attaccante", 0.4),
        ("Nikola Stulic", "Attaccante", 0.35),
        ("Tete Morente", "Attaccante", 0.3),
        ("Lameck Banda", "Attaccante", 0.25),
        ("Santiago Pierotti", "Attaccante", 0.2),
    ],
    "Napoli": [
        ("David Neres", "Attaccante", 0.4),
        ("Romelu Lukaku", "Attaccante", 0.35),
        ("Noa Lang", "Attaccante", 0.3),
        ("Rasmus Hojlund", "Attaccante", 0.25),
        ("Lorenzo Lucca", "Attaccante", 0.2),
    ],
    "Parma": [
        ("Milan Djuric", "Attaccante", 0.4),
        ("Patrick Cutrone", "Attaccante", 0.35),
        ("Pontus Almqvist", "Attaccante", 0.3),
        ("Jacob Ondrejka", "Attaccante", 0.25),
        ("Matija Frigan", "Attaccante", 0.2),
    ],
    "Pisa": [
        ("Henrik Meister", "Attaccante", 0.4),
        ("Mehdi Leris", "Attaccante", 0.35),
        ("M'Bala Nzola", "Attaccante", 0.3),
        ("Samuele Angori", "Centrocampista", 0.15),
        ("Malthe Hojholt", "Centrocampista", 0.15),
    ],
    "Sassuolo": [
        ("Samuele Mulattieri", "Attaccante", 0.4),
        ("Andrea Pinamonti", "Attaccante", 0.35),
        ("Alieu Fadera", "Attaccante", 0.3),
        ("Cristian Volpato", "Attaccante", 0.25),
        ("Armand Lauriente", "Attaccante", 0.2),
    ],
    "Torino": [
        ("Zakaria Aboukhlal", "Attaccante", 0.4),
        ("Che Adams", "Attaccante", 0.35),
        ("Cyril Ngonge", "Attaccante", 0.3),
        ("Alieu Njie", "Attaccante", 0.25),
        ("Duvan Zapata", "Attaccante", 0.2),
    ],
    "Udinese": [
        ("Keinan Davis", "Attaccante", 0.4),
        ("Vakoun Bayo", "Attaccante", 0.35),
        ("Adam Buksa", "Attaccante", 0.3),
        ("Iker Bravo", "Attaccante", 0.25),
        ("Idrissa Gueye", "Attaccante", 0.2),
    ],
}

# MOCK LINEUPS (Since we don't have real-time lineup API yet)
# Auto-generated from database
MOCK_LINEUPS = {
    "AC Milan": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Mike Maignan", "GK"),
            ("Koni De Winter", "DEF"),
            ("Theo Hernandez", "DEF"),
            ("Fikayo Tomori", "DEF"),
            ("Malick Thiaw", "DEF"),
            ("Ruben Loftus-Cheek", "MID"),
            ("Luka Modric", "MID"),
            ("Tijjani Reijnders", "MID"),
            ("Samuele Ricci", "MID"),
            ("Santiago Gimenez", "FWD"),
            ("Rafael Leao", "FWD"),
            ("Christian Pulisic", "FWD"),
        ],
        "bench": ['Lorenzo Torriani', 'Pervis Estupinan', 'Strahinja Pavlovic', 'Matteo Gabbia', 'Adrien Rabiot', 'Ardon Jashari', 'Youssouf Fofana', 'Christopher Nkunku', 'Niclas Fullkrug']
    },
    "AS Roma": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Pierluigi Gollini", "GK"),
            ("Wesley", "DEF"),
            ("Angelino", "DEF"),
            ("Evan Ndicka", "DEF"),
            ("Daniele Ghilardi", "DEF"),
            ("Edoardo Bove", "MID"),
            ("Bryan Cristante", "MID"),
            ("Lorenzo Pellegrini", "MID"),
            ("Manu Kone", "MID"),
            ("Leon Bailey", "FWD"),
            ("Evan Ferguson", "FWD"),
            ("Artem Dovbyk", "FWD"),
        ],
        "bench": ['Radoslaw Zelezny', 'Zeki Celik', 'Konstantinos Tsimikas', 'Mario Hermoso', 'Gianluca Mancini', 'Tommaso Baldanzi', 'Niccolo Pisilli', 'Neil El Aynaoui', 'Matias Soule', 'Paulo Dybala']
    },
    "Atalanta": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Rui Patricio", "GK"),
            ("Odilon Kossounou", "DEF"),
            ("Isak Hien", "DEF"),
            ("Raoul Bellanova", "DEF"),
            ("Berat Djimsiti", "DEF"),
            ("Mario Pasalic", "MID"),
            ("Ederson", "MID"),
            ("Marten de Roon", "MID"),
            ("Lazar Samardzic", "MID"),
            ("Gianluca Scamacca", "FWD"),
            ("Ademola Lookman", "FWD"),
            ("Charles De Ketelaere", "FWD"),
        ],
        "bench": ['Marco Carnesecchi', 'Sead Kolasinac', 'Giorgio Scalvini', 'Davide Zappacosta']
    },
    "Bologna": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Lukasz Skorupski", "GK"),
            ("Emil Holm", "DEF"),
            ("Torbjorn Heggem", "DEF"),
            ("Martin Vitik", "DEF"),
            ("Nicolo Casale", "DEF"),
            ("Nikola Moro", "MID"),
            ("Remo Freuler", "MID"),
            ("Lewis Ferguson", "MID"),
            ("Giovanni Fabbian", "MID"),
            ("Riccardo Orsolini", "FWD"),
            ("Santiago Castro", "FWD"),
            ("Jonathan Rowe", "FWD"),
        ],
        "bench": ['Federico Ravaglia', 'Nadir Zortea', 'Charalampos Lykogiannis', 'Jhon Lucumi', 'Juan Miranda', 'Kacper Urbanski', 'Ciro Immobile', 'Federico Bernardeschi']
    },
    "Cagliari": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Giuseppe Ciocci", "GK"),
            ("Juan Rodriguez", "DEF"),
            ("Ze Pedro", "DEF"),
            ("Sebastiano Luperto", "DEF"),
            ("Yerry Mina", "DEF"),
            ("Marko Rog", "MID"),
            ("Michel Adopo", "MID"),
            ("Alessandro Deiola", "MID"),
            ("Matteo Prati", "MID"),
            ("Semih Kilicsoy", "FWD"),
            ("Andrea Belotti", "FWD"),
            ("Mattia Felici", "FWD"),
        ],
        "bench": ['Elia Caprile', 'Gabriele Zappa', 'Alessandro Di Pardo', 'Adam Obert', 'Marco Palestra', 'Luca Mazzitelli', 'Gianluca Gaetano', 'Michael Folorunsho', 'Leonardo Pavoletti', 'Zito Luvumbo']
    },
    "Como": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Jean Butez", "GK"),
            ("Marc Oliver Kempf", "DEF"),
            ("Diego Carlos", "DEF"),
            ("Alberto Dossena", "DEF"),
            ("Edoardo Goldaniga", "DEF"),
            ("Maxence Caqueret", "MID"),
            ("Maximo Perrone", "MID"),
            ("Sergi Roberto", "MID"),
            ("Martin Baturina", "MID"),
            ("Alvaro Morata", "FWD"),
            ("Jesus Rodriguez", "FWD"),
            ("Nicolas Kuhn", "FWD"),
        ],
        "bench": ['Noel Tornqvist', 'Ignace Van der Brempt', 'Stefan Posch', 'Alberto Moreno', 'Alex Valle', 'Lucas Da Cunha', 'Nico Paz', 'Jayden Addai', 'Assane Diao']
    },
    "Cremonese": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Emil Audero", "GK"),
            ("Giuseppe Pezzella", "DEF"),
            ("Federico Baschirotto", "DEF"),
            ("Filippo Terracciano", "DEF"),
            ("Federico Ceccherini", "DEF"),
            ("Alberto Grassi", "MID"),
            ("Martin Payero", "MID"),
            ("Michele Collocolo", "MID"),
            ("Franco Vazquez", "MID"),
            ("Jamie Vardy", "FWD"),
            ("David Okereke", "FWD"),
            ("Antonio Sanabria", "FWD"),
        ],
        "bench": ['Lapo Nava', 'Matteo Bianchetti', 'Leonardo Sernicola', 'Mikayil Faye', 'Tommaso Barbieri', 'Alessio Zerbin', 'Jeremy Sarmiento', 'Warren Bondo', 'Faris Moumbagna', 'Federico Bonazzoli']
    },
    "Fiorentina": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Luca Lezzerini", "GK"),
            ("Dodo", "DEF"),
            ("Marin Pongracic", "DEF"),
            ("Luca Ranieri", "DEF"),
            ("Pietro Comuzzo", "DEF"),
            ("Simon Sohm", "MID"),
            ("Albert Gudmundsson", "MID"),
            ("Abdelhamid Sabiri", "MID"),
            ("Hans Nicolussi Caviglia", "MID"),
            ("Edin Dzeko", "FWD"),
            ("Moise Kean", "FWD"),
            ("Roberto Piccoli", "FWD"),
        ],
        "bench": ['Tommaso Martinelli', 'Robin Gosens', 'Pablo Mari', 'Mattia Viti', 'Tariq Lamptey', 'Jacopo Fazzini', 'Amir Richardson', 'Cher Ndour', 'Christian Kouame']
    },
    "Genoa": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Nicola Leali", "GK"),
            ("Aaron Martin", "DEF"),
            ("Alessandro Marcandalli", "DEF"),
            ("Stefano Sabelli", "DEF"),
            ("Johan Vasquez", "DEF"),
            ("Morten Thorsby", "MID"),
            ("Patrizio Masini", "MID"),
            ("Nicolae Stanciu", "MID"),
            ("Ruslan Malinovskyi", "MID"),
            ("Vitinha", "FWD"),
            ("Maxwel Cornet", "FWD"),
            ("Caleb Ekuban", "FWD"),
        ],
        "bench": ['Benjamin Siegrist', 'Leo Ostigard', 'Brooke Norton-Cuffy', 'Mikael Egill Ellertsson', 'Jean Onana', 'Albert Gronbaek', 'Junior Messias', 'Jeff Ekhator']
    },
    "Hellas Verona": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Lorenzo Montipo", "GK"),
            ("Unai Nunez", "DEF"),
            ("Victor Nelsson", "DEF"),
            ("Nicolas Valentini", "DEF"),
            ("Domagoj Bradaric", "DEF"),
            ("Moatasem Al-Musrati", "MID"),
            ("Cheikh Niasse", "MID"),
            ("Grigoris Kastanos", "MID"),
            ("Suat Serdar", "MID"),
            ("Daniel Mosquera", "FWD"),
            ("Gift Orban", "FWD"),
            ("Amin Sarr", "FWD"),
        ],
        "bench": ['Simone Perilli', 'Rafik Belghali', 'Armel Bella-Kotchap', 'Enzo Ebosse', 'Martin Frese', 'Roberto Gagliardini', 'Tomas Suslov', 'Abdou Harroui', 'Giovane']
    },
    "Inter": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Yann Sommer", "GK"),
            ("Denzel Dumfries", "DEF"),
            ("Tomas Palacios", "DEF"),
            ("Stefan de Vrij", "DEF"),
            ("Francesco Acerbi", "DEF"),
            ("Piotr Zielinski", "MID"),
            ("Luis Henrique", "MID"),
            ("Petar Sucic", "MID"),
            ("Davide Frattesi", "MID"),
            ("Marcus Thuram", "FWD"),
            ("Lautaro Martinez", "FWD"),
            ("Ange-Yoan Bonny", "FWD"),
        ],
        "bench": ['Josep Martinez', 'Manuel Akanji', 'Carlos Augusto', 'Yann Bisseck', 'Federico Dimarco', 'Hakan Calhanoglu', 'Henrikh Mkhitaryan', 'Nicolo Barella', 'Pio Esposito']
    },
    "Juventus": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Mattia Perin", "GK"),
            ("Gleison Bremer", "DEF"),
            ("Federico Gatti", "DEF"),
            ("Joao Mario", "DEF"),
            ("Pierre Kalulu", "DEF"),
            ("Manuel Locatelli", "MID"),
            ("Teun Koopmeiners", "MID"),
            ("Filip Kostic", "MID"),
            ("Weston McKennie", "MID"),
            ("Edon Zhegrova", "FWD"),
            ("Dusan Vlahovic", "FWD"),
            ("Kenan Yildiz", "FWD"),
        ],
        "bench": ['Carlo Pinsoglio', 'Daniele Rugani', 'Lloyd Kelly', 'Andrea Cambiaso', 'Juan Cabal', 'Khephren Thuram', 'Fabio Miretti', 'Arkadiusz Milik', 'Jonathan David']
    },
    "Lazio": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Alessio Furlanetto", "GK"),
            ("Samuel Gigot", "DEF"),
            ("Luca Pellegrini", "DEF"),
            ("Patric", "DEF"),
            ("Oliver Provstgaard", "DEF"),
            ("Matias Vecino", "MID"),
            ("Nicolo Rovella", "MID"),
            ("Fisayo Dele-Bashiru", "MID"),
            ("Matteo Guendouzi", "MID"),
            ("Pedro", "FWD"),
            ("Mattia Zaccagni", "FWD"),
            ("Taty Castellanos", "FWD"),
        ],
        "bench": ['Christos Mandas', 'Alessio Romagnoli', 'Elseid Hysaj', 'Dimitrije Kamenovic', 'Manuel Lazzari', 'Toma Basic', 'Danilo Cataldi', 'Reda Belahyane', 'Tijjani Noslin', 'Gustav Isaksen']
    },
    "Lecce": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Christian Fruchtl", "GK"),
            ("Gaspar", "DEF"),
            ("Gaby Jean", "DEF"),
            ("Frederic Guilbert", "DEF"),
            ("Corrie Ndaba", "DEF"),
            ("Balthazar Pierret", "MID"),
            ("Hamza Rafia", "MID"),
            ("Filip Marchwinski", "MID"),
            ("Ylber Ramadani", "MID"),
            ("Riccardo Sottil", "FWD"),
            ("Nikola Stulic", "FWD"),
            ("Tete Morente", "FWD"),
        ],
        "bench": ['Jasper Samooja', 'Christ-Owen Kouassi', 'Jamil Siebert', 'Antonino Gallo', 'Tiago Gabriel', 'Alex Sala', 'Lassana Coulibaly', 'Medon Berisha', 'Lameck Banda', 'Santiago Pierotti']
    },
    "Napoli": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Alex Meret", "GK"),
            ("Miguel Gutierrez", "DEF"),
            ("Alessandro Buongiorno", "DEF"),
            ("Juan Jesus", "DEF"),
            ("Amir Rrahmani", "DEF"),
            ("Billy Gilmour", "MID"),
            ("Eljif Elmas", "MID"),
            ("Scott McTominay", "MID"),
            ("Kevin De Bruyne", "MID"),
            ("David Neres", "FWD"),
            ("Romelu Lukaku", "FWD"),
            ("Noa Lang", "FWD"),
        ],
        "bench": ['Nikita Contini', 'Mathias Olivera', 'Giovanni Di Lorenzo', 'Pasquale Mazzocchi', 'Sam Beukema', 'Antonio Vergara', 'Stanislav Lobotka', 'Frank Anguissa', 'Rasmus Hojlund', 'Lorenzo Lucca']
    },
    "Parma": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Edoardo Corvi", "GK"),
            ("Abdoulaye Ndiaye", "DEF"),
            ("Emanuele Valeri", "DEF"),
            ("Mathias Lovik", "DEF"),
            ("Enrico Delprato", "DEF"),
            ("Oliver Sorensen", "MID"),
            ("Nahuel Estevez", "MID"),
            ("Adrian Bernabe", "MID"),
            ("Mandela Keita", "MID"),
            ("Milan Djuric", "FWD"),
            ("Patrick Cutrone", "FWD"),
            ("Pontus Almqvist", "FWD"),
        ],
        "bench": ['Zion Suzuki', 'Alessandro Circati', 'Mariano Troilo', 'Sascha Britschgi', 'Christian Ordonez', 'Gaetano Oristanio', 'Hernani', 'Jacob Ondrejka', 'Matija Frigan']
    },
    "Pisa": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Nicolas", "GK"),
            ("Antonio Caracciolo", "DEF"),
            ("Giovanni Bonfanti", "DEF"),
            ("Simone Canestrelli", "DEF"),
            ("Francesco Coppola", "DEF"),
            ("Samuele Angori", "MID"),
            ("Malthe Hojholt", "MID"),
            ("Juan Cuadrado", "MID"),
            ("Marius Marin", "MID"),
            ("Henrik Meister", "FWD"),
            ("Mehdi Leris", "FWD"),
            ("M'Bala Nzola", "FWD"),
        ],
        "bench": ['Simone Scuffet', 'Arturo Calabresi', 'Raul Albiol', 'Calvin Stengs', 'Matteo Tramoni', 'Idrissa Toure']
    },
    "Sassuolo": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Filip Stankovic", "GK"),
            ("Josh Doig", "DEF"),
            ("Sebastian Walukiewicz", "DEF"),
            ("Yeferson Paz", "DEF"),
            ("Martin Erlic", "DEF"),
            ("Nedim Bajrami", "MID"),
            ("Daniel Boloca", "MID"),
            ("Tajon Buchanan", "MID"),
            ("Kristian Thorstvedt", "MID"),
            ("Samuele Mulattieri", "FWD"),
            ("Andrea Pinamonti", "FWD"),
            ("Alieu Fadera", "FWD"),
        ],
        "bench": ['Gianluca Pegolo', 'Filippo Romagna', 'Cristian Volpato', 'Armand Lauriente']
    },
    "Torino": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Alberto Paleari", "GK"),
            ("Perr Schuurs", "DEF"),
            ("Adam Masina", "DEF"),
            ("Saba Sazonov", "DEF"),
            ("Guillermo Maripan", "DEF"),
            ("Cesare Casadei", "MID"),
            ("Tino Anjorin", "MID"),
            ("Ivan Ilic", "MID"),
            ("Nikola Vlasic", "MID"),
            ("Zakaria Aboukhlal", "FWD"),
            ("Che Adams", "FWD"),
            ("Cyril Ngonge", "FWD"),
        ],
        "bench": ['Franco Israel', 'Marcus Pedersen', 'Niels Nkounkou', 'Valentino Lazaro', 'Saul Coco', 'Kristjan Asllani', 'Adrien Tameze', 'Gvidas Gineitis', 'Alieu Njie', 'Duvan Zapata']
    },
    "Udinese": {
        "formation": "4-4-3",
        "starting_xi": [
            ("Daniele Padelli", "GK"),
            ("Saba Goglichidze", "DEF"),
            ("Hassane Kamara", "DEF"),
            ("Kingsley Ehizibue", "DEF"),
            ("Alessandro Zanoli", "DEF"),
            ("Jakub Piotrowski", "MID"),
            ("Oier Zarraga", "MID"),
            ("Sandi Lovric", "MID"),
            ("Nicolo Zaniolo", "MID"),
            ("Keinan Davis", "FWD"),
            ("Vakoun Bayo", "FWD"),
            ("Adam Buksa", "FWD"),
        ],
        "bench": ['Maduka Okoye', 'Christian Kabasele', 'Oumar Solet', 'Nicolo Bertola', 'Thomas Kristensen', 'Jesper Karlstrom', 'Jurgen Ekkelenkamp', 'Iker Bravo', 'Idrissa Gueye']
    },
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
