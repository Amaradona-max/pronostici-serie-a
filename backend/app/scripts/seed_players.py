"""
Script to seed Serie A players into database
Run with: python -m app.scripts.seed_players
"""

import asyncio
import logging
from sqlalchemy import select

from app.db.engine import AsyncSessionLocal
from app.db.models import Team, Player

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Complete Serie A 2025/2026 players data (Updated to Jan 2026)
PLAYERS_DATA = {
    "Inter": [
        {"name": "Yann Sommer", "position": "GK", "number": 1, "nationality": "Switzerland"},
        {"name": "Josep Martinez", "position": "GK", "number": 13, "nationality": "Spain"},
        {"name": "Benjamin Pavard", "position": "DF", "number": 28, "nationality": "France"},
        {"name": "Alessandro Bastoni", "position": "DF", "number": 95, "nationality": "Italy"},
        {"name": "Francesco Acerbi", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Manuel Akanji", "position": "DF", "number": 25, "nationality": "Switzerland"},
        {"name": "Stefan de Vrij", "position": "DF", "number": 6, "nationality": "Netherlands"},
        {"name": "Denzel Dumfries", "position": "DF", "number": 2, "nationality": "Netherlands"},
        {"name": "Federico Dimarco", "position": "DF", "number": 32, "nationality": "Italy"},
        {"name": "Carlos Augusto", "position": "DF", "number": 30, "nationality": "Brazil"},
        {"name": "Matteo Darmian", "position": "DF", "number": 36, "nationality": "Italy"},
        {"name": "Hakan Calhanoglu", "position": "MF", "number": 20, "nationality": "Turkey"},
        {"name": "Nicolò Barella", "position": "MF", "number": 23, "nationality": "Italy"},
        {"name": "Davide Frattesi", "position": "MF", "number": 16, "nationality": "Italy"},
        {"name": "Piotr Zielinski", "position": "MF", "number": 7, "nationality": "Poland"},
        {"name": "Petar Sucic", "position": "MF", "number": 14, "nationality": "Croatia"},
        {"name": "Henrikh Mkhitaryan", "position": "MF", "number": 22, "nationality": "Armenia"},
        {"name": "Kristjan Asllani", "position": "MF", "number": 21, "nationality": "Albania"},
        {"name": "Lautaro Martinez", "position": "FW", "number": 10, "nationality": "Argentina"},
        {"name": "Marcus Thuram", "position": "FW", "number": 9, "nationality": "France"},
        {"name": "Mehdi Taremi", "position": "FW", "number": 99, "nationality": "Iran"},
        {"name": "Luis Henrique", "position": "FW", "number": 11, "nationality": "Brazil"},
        {"name": "Ange-Yoan Bonny", "position": "FW", "number": 13, "nationality": "France"},
    ],
    "AC Milan": [
        {"name": "Mike Maignan", "position": "GK", "number": 16, "nationality": "France"},
        {"name": "Marco Sportiello", "position": "GK", "number": 57, "nationality": "Italy"},
        {"name": "Fikayo Tomori", "position": "DF", "number": 23, "nationality": "England"},
        {"name": "Malick Thiaw", "position": "DF", "number": 28, "nationality": "Germany"},
        {"name": "Strahinja Pavlovic", "position": "DF", "number": 31, "nationality": "Serbia"},
        {"name": "Theo Hernandez", "position": "DF", "number": 19, "nationality": "France"},
        {"name": "Emerson Royal", "position": "DF", "number": 22, "nationality": "Brazil"},
        {"name": "Davide Calabria", "position": "DF", "number": 2, "nationality": "Italy"},
        {"name": "Pervis Estupinan", "position": "DF", "number": 30, "nationality": "Ecuador"},
        {"name": "Luka Modric", "position": "MF", "number": 10, "nationality": "Croatia"},
        {"name": "Tijjani Reijnders", "position": "MF", "number": 14, "nationality": "Netherlands"},
        {"name": "Samuele Ricci", "position": "MF", "number": 28, "nationality": "Italy"},
        {"name": "Ruben Loftus-Cheek", "position": "MF", "number": 8, "nationality": "England"},
        {"name": "Youssouf Fofana", "position": "MF", "number": 29, "nationality": "France"},
        {"name": "Adrien Rabiot", "position": "MF", "number": 25, "nationality": "France"},
        {"name": "Christian Pulisic", "position": "FW", "number": 11, "nationality": "USA"},
        {"name": "Rafael Leao", "position": "FW", "number": 10, "nationality": "Portugal"},
        {"name": "Tammy Abraham", "position": "FW", "number": 90, "nationality": "England"},
        {"name": "Samuel Chukwueze", "position": "FW", "number": 21, "nationality": "Nigeria"},
        {"name": "Noah Okafor", "position": "FW", "number": 17, "nationality": "Switzerland"},
    ],
    "Juventus": [
        {"name": "Michele Di Gregorio", "position": "GK", "number": 29, "nationality": "Italy"},
        {"name": "Mattia Perin", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Gleison Bremer", "position": "DF", "number": 3, "nationality": "Brazil"},
        {"name": "Federico Gatti", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Pierre Kalulu", "position": "DF", "number": 15, "nationality": "France"},
        {"name": "Joao Mario", "position": "DF", "number": 23, "nationality": "Portugal"},
        {"name": "Andrea Cambiaso", "position": "DF", "number": 27, "nationality": "Italy"},
        {"name": "Juan Cabal", "position": "DF", "number": 32, "nationality": "Colombia"},
        {"name": "Teun Koopmeiners", "position": "MF", "number": 8, "nationality": "Netherlands"},
        {"name": "Manuel Locatelli", "position": "MF", "number": 5, "nationality": "Italy"},
        {"name": "Khephren Thuram", "position": "MF", "number": 19, "nationality": "France"},
        {"name": "Douglas Luiz", "position": "MF", "number": 26, "nationality": "Brazil"},
        {"name": "Weston McKennie", "position": "MF", "number": 16, "nationality": "USA"},
        {"name": "Kenan Yildiz", "position": "FW", "number": 10, "nationality": "Turkey"},
        {"name": "Dusan Vlahovic", "position": "FW", "number": 9, "nationality": "Serbia"},
        {"name": "Jonathan David", "position": "FW", "number": 11, "nationality": "Canada"},
        {"name": "Lois Openda", "position": "FW", "number": 17, "nationality": "Belgium"},
        {"name": "Edon Zhegrova", "position": "FW", "number": 7, "nationality": "Kosovo"},
        {"name": "Timothy Weah", "position": "FW", "number": 22, "nationality": "USA"},
        {"name": "Francisco Conceicao", "position": "FW", "number": 30, "nationality": "Portugal"},
    ],
    "Atalanta": [
        {"name": "Marco Carnesecchi", "position": "GK", "number": 29, "nationality": "Italy"},
        {"name": "Rui Patricio", "position": "GK", "number": 28, "nationality": "Portugal"},
        {"name": "Giorgio Scalvini", "position": "DF", "number": 42, "nationality": "Italy"},
        {"name": "Isak Hien", "position": "DF", "number": 4, "nationality": "Sweden"},
        {"name": "Berat Djimsiti", "position": "DF", "number": 19, "nationality": "Albania"},
        {"name": "Sead Kolasinac", "position": "DF", "number": 23, "nationality": "Bosnia"},
        {"name": "Odilon Kossounou", "position": "DF", "number": 3, "nationality": "Ivory Coast"},
        {"name": "Raoul Bellanova", "position": "DF", "number": 16, "nationality": "Italy"},
        {"name": "Davide Zappacosta", "position": "DF", "number": 77, "nationality": "Italy"},
        {"name": "Nicola Zalewski", "position": "DF", "number": 59, "nationality": "Poland"},
        {"name": "Ederson", "position": "MF", "number": 13, "nationality": "Brazil"},
        {"name": "Marten de Roon", "position": "MF", "number": 15, "nationality": "Netherlands"},
        {"name": "Mario Pasalic", "position": "MF", "number": 8, "nationality": "Croatia"},
        {"name": "Lazar Samardzic", "position": "MF", "number": 24, "nationality": "Serbia"},
        {"name": "Yunus Musah", "position": "MF", "number": 80, "nationality": "USA"},
        {"name": "Kamaldeen Sulemana", "position": "MF", "number": 7, "nationality": "Ghana"},
        {"name": "Charles De Ketelaere", "position": "FW", "number": 17, "nationality": "Belgium"},
        {"name": "Ademola Lookman", "position": "FW", "number": 11, "nationality": "Nigeria"},
        {"name": "Gianluca Scamacca", "position": "FW", "number": 9, "nationality": "Italy"},
        {"name": "Nikola Krstovic", "position": "FW", "number": 99, "nationality": "Montenegro"},
        {"name": "Nicolo Zaniolo", "position": "FW", "number": 10, "nationality": "Italy"},
    ],
    "Napoli": [
        {"name": "Alex Meret", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Elia Caprile", "position": "GK", "number": 25, "nationality": "Italy"},
        {"name": "Alessandro Buongiorno", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Amir Rrahmani", "position": "DF", "number": 13, "nationality": "Kosovo"},
        {"name": "Sam Beukema", "position": "DF", "number": 31, "nationality": "Netherlands"},
        {"name": "Giovanni Di Lorenzo", "position": "DF", "number": 22, "nationality": "Italy"},
        {"name": "Mathias Olivera", "position": "DF", "number": 17, "nationality": "Uruguay"},
        {"name": "Leonardo Spinazzola", "position": "DF", "number": 37, "nationality": "Italy"},
        {"name": "Stanislav Lobotka", "position": "MF", "number": 68, "nationality": "Slovakia"},
        {"name": "Frank Anguissa", "position": "MF", "number": 99, "nationality": "Cameroon"},
        {"name": "Scott McTominay", "position": "MF", "number": 8, "nationality": "Scotland"},
        {"name": "Kevin De Bruyne", "position": "MF", "number": 17, "nationality": "Belgium"},
        {"name": "Billy Gilmour", "position": "MF", "number": 6, "nationality": "Scotland"},
        {"name": "Khvicha Kvaratskhelia", "position": "FW", "number": 77, "nationality": "Georgia"},
        {"name": "Romelu Lukaku", "position": "FW", "number": 9, "nationality": "Belgium"},
        {"name": "Rasmus Hojlund", "position": "FW", "number": 11, "nationality": "Denmark"},
        {"name": "Lorenzo Lucca", "position": "FW", "number": 20, "nationality": "Italy"},
        {"name": "Matteo Politano", "position": "FW", "number": 21, "nationality": "Italy"},
        {"name": "David Neres", "position": "FW", "number": 7, "nationality": "Brazil"},
        {"name": "Giacomo Raspadori", "position": "FW", "number": 81, "nationality": "Italy"},
        {"name": "Cyril Ngonge", "position": "FW", "number": 26, "nationality": "Belgium"},
        {"name": "Noa Lang", "position": "FW", "number": 10, "nationality": "Netherlands"},
    ],
    "Lazio": [
        {"name": "Ivan Provedel", "position": "GK", "number": 94, "nationality": "Italy"},
        {"name": "Christos Mandas", "position": "GK", "number": 35, "nationality": "Greece"},
        {"name": "Alessio Romagnoli", "position": "DF", "number": 13, "nationality": "Italy"},
        {"name": "Mario Gila", "position": "DF", "number": 34, "nationality": "Spain"},
        {"name": "Samuel Gigot", "position": "DF", "number": 2, "nationality": "France"},
        {"name": "Nuno Tavares", "position": "DF", "number": 30, "nationality": "Portugal"},
        {"name": "Manuel Lazzari", "position": "DF", "number": 29, "nationality": "Italy"},
        {"name": "Luca Pellegrini", "position": "DF", "number": 3, "nationality": "Italy"},
        {"name": "Nicolo Rovella", "position": "MF", "number": 6, "nationality": "Italy"},
        {"name": "Matteo Guendouzi", "position": "MF", "number": 8, "nationality": "France"},
        {"name": "Fisayo Dele-Bashiru", "position": "MF", "number": 7, "nationality": "Nigeria"},
        {"name": "Gaetano Castrovilli", "position": "MF", "number": 22, "nationality": "Italy"},
        {"name": "Mattia Zaccagni", "position": "FW", "number": 10, "nationality": "Italy"},
        {"name": "Taty Castellanos", "position": "FW", "number": 11, "nationality": "Argentina"},
        {"name": "Boulaye Dia", "position": "FW", "number": 19, "nationality": "Senegal"},
        {"name": "Gustav Isaksen", "position": "FW", "number": 18, "nationality": "Denmark"},
        {"name": "Tijjani Noslin", "position": "FW", "number": 14, "nationality": "Netherlands"},
        {"name": "Pedro", "position": "FW", "number": 9, "nationality": "Spain"},
    ],
    "AS Roma": [
        {"name": "Mile Svilar", "position": "GK", "number": 99, "nationality": "Belgium"},
        {"name": "Mathew Ryan", "position": "GK", "number": 98, "nationality": "Australia"},
        {"name": "Gianluca Mancini", "position": "DF", "number": 23, "nationality": "Italy"},
        {"name": "Evan Ndicka", "position": "DF", "number": 5, "nationality": "Ivory Coast"},
        {"name": "Mario Hermoso", "position": "DF", "number": 22, "nationality": "Spain"},
        {"name": "Wesley Franca", "position": "DF", "number": 2, "nationality": "Brazil"},
        {"name": "Angelino", "position": "DF", "number": 3, "nationality": "Spain"},
        {"name": "Zeki Celik", "position": "DF", "number": 19, "nationality": "Turkey"},
        {"name": "Bryan Cristante", "position": "MF", "number": 4, "nationality": "Italy"},
        {"name": "Manu Kone", "position": "MF", "number": 17, "nationality": "France"},
        {"name": "Lorenzo Pellegrini", "position": "MF", "number": 7, "nationality": "Italy"},
        {"name": "Enzo Le Fee", "position": "MF", "number": 28, "nationality": "France"},
        {"name": "Niccolo Pisilli", "position": "MF", "number": 61, "nationality": "Italy"},
        {"name": "Paulo Dybala", "position": "FW", "number": 21, "nationality": "Argentina"},
        {"name": "Artem Dovbyk", "position": "FW", "number": 11, "nationality": "Ukraine"},
        {"name": "Matias Soule", "position": "FW", "number": 18, "nationality": "Argentina"},
        {"name": "Evan Ferguson", "position": "FW", "number": 9, "nationality": "Ireland"},
        {"name": "Stephan El Shaarawy", "position": "FW", "number": 92, "nationality": "Italy"},
        {"name": "Alexis Saelemaekers", "position": "FW", "number": 56, "nationality": "Belgium"},
    ],
    "Fiorentina": [
        {"name": "David de Gea", "position": "GK", "number": 43, "nationality": "Spain"},
        {"name": "Pietro Terracciano", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Lucas Martinez Quarta", "position": "DF", "number": 28, "nationality": "Argentina"},
        {"name": "Marin Pongracic", "position": "DF", "number": 5, "nationality": "Croatia"},
        {"name": "Luca Ranieri", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Pietro Comuzzo", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Dodô", "position": "DF", "number": 2, "nationality": "Brazil"},
        {"name": "Robin Gosens", "position": "DF", "number": 21, "nationality": "Germany"},
        {"name": "Michael Kayode", "position": "DF", "number": 33, "nationality": "Italy"},
        {"name": "Tariq Lamptey", "position": "DF", "number": 48, "nationality": "Ghana"},
        {"name": "Rolando Mandragora", "position": "MF", "number": 38, "nationality": "Italy"},
        {"name": "Yacine Adli", "position": "MF", "number": 29, "nationality": "France"},
        {"name": "Edoardo Bove", "position": "MF", "number": 4, "nationality": "Italy"},
        {"name": "Amir Richardson", "position": "MF", "number": 24, "nationality": "Morocco"},
        {"name": "Andrea Colpani", "position": "MF", "number": 23, "nationality": "Italy"},
        {"name": "Nicolo Fagioli", "position": "MF", "number": 44, "nationality": "Italy"},
        {"name": "Simon Sohm", "position": "MF", "number": 7, "nationality": "Switzerland"},
        {"name": "Cher Ndour", "position": "MF", "number": 27, "nationality": "Italy"},
        {"name": "Hans Nicolussi Caviglia", "position": "MF", "number": 14, "nationality": "Italy"},
        {"name": "Abdelhamid Sabiri", "position": "MF", "number": 11, "nationality": "Morocco"},
        {"name": "Albert Gudmundsson", "position": "FW", "number": 10, "nationality": "Iceland"},
        {"name": "Moise Kean", "position": "FW", "number": 20, "nationality": "Italy"},
        {"name": "Edin Dzeko", "position": "FW", "number": 9, "nationality": "Bosnia"},
        {"name": "Roberto Piccoli", "position": "FW", "number": 91, "nationality": "Italy"},
        {"name": "Christian Kouame", "position": "FW", "number": 99, "nationality": "Ivory Coast"},
        {"name": "Jonathan Ikone", "position": "FW", "number": 11, "nationality": "France"},
        {"name": "Riccardo Sottil", "position": "FW", "number": 7, "nationality": "Italy"},
    ],
    "Bologna": [
        {"name": "Lukasz Skorupski", "position": "GK", "number": 28, "nationality": "Poland"},
        {"name": "Federico Ravaglia", "position": "GK", "number": 34, "nationality": "Italy"},
        {"name": "Stefan Posch", "position": "DF", "number": 3, "nationality": "Austria"},
        {"name": "Jhon Lucumi", "position": "DF", "number": 26, "nationality": "Colombia"},
        {"name": "Martin Erlic", "position": "DF", "number": 5, "nationality": "Croatia"},
        {"name": "Martin Vitik", "position": "DF", "number": 4, "nationality": "Czech Republic"},
        {"name": "Juan Miranda", "position": "DF", "number": 33, "nationality": "Spain"},
        {"name": "Charalampos Lykogiannis", "position": "DF", "number": 22, "nationality": "Greece"},
        {"name": "Nadir Zortea", "position": "DF", "number": 21, "nationality": "Italy"},
        {"name": "Remo Freuler", "position": "MF", "number": 8, "nationality": "Switzerland"},
        {"name": "Lewis Ferguson", "position": "MF", "number": 19, "nationality": "Scotland"},
        {"name": "Giovanni Fabbian", "position": "MF", "number": 80, "nationality": "Italy"},
        {"name": "Nikola Moro", "position": "MF", "number": 6, "nationality": "Croatia"},
        {"name": "Kacper Urbanski", "position": "MF", "number": 82, "nationality": "Poland"},
        {"name": "Riccardo Orsolini", "position": "FW", "number": 7, "nationality": "Italy"},
        {"name": "Dan Ndoye", "position": "FW", "number": 11, "nationality": "Switzerland"},
        {"name": "Ciro Immobile", "position": "FW", "number": 17, "nationality": "Italy"},
        {"name": "Santiago Castro", "position": "FW", "number": 9, "nationality": "Argentina"},
        {"name": "Jonathan Rowe", "position": "FW", "number": 10, "nationality": "England"},
        {"name": "Federico Bernardeschi", "position": "FW", "number": 33, "nationality": "Italy"},
    ],
    "Torino": [
        {"name": "Vanja Milinkovic-Savic", "position": "GK", "number": 32, "nationality": "Serbia"},
        {"name": "Alberto Paleari", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Saul Coco", "position": "DF", "number": 23, "nationality": "Equatorial Guinea"},
        {"name": "Guillermo Maripan", "position": "DF", "number": 13, "nationality": "Chile"},
        {"name": "Adam Masina", "position": "DF", "number": 5, "nationality": "Morocco"},
        {"name": "Sebastian Walukiewicz", "position": "DF", "number": 4, "nationality": "Poland"},
        {"name": "Valentino Lazaro", "position": "DF", "number": 20, "nationality": "Austria"},
        {"name": "Borna Sosa", "position": "DF", "number": 24, "nationality": "Croatia"},
        {"name": "Marcus Pedersen", "position": "DF", "number": 16, "nationality": "Norway"},
        {"name": "Ivan Ilic", "position": "MF", "number": 8, "nationality": "Serbia"},
        {"name": "Karol Linetty", "position": "MF", "number": 77, "nationality": "Poland"},
        {"name": "Nikola Vlasic", "position": "MF", "number": 10, "nationality": "Croatia"},
        {"name": "Duvan Zapata", "position": "FW", "number": 91, "nationality": "Colombia"},
        {"name": "Ché Adams", "position": "FW", "number": 18, "nationality": "Scotland"},
        {"name": "Yann Karamoh", "position": "FW", "number": 7, "nationality": "France"},
    ],
    "Udinese": [
        {"name": "Maduka Okoye", "position": "GK", "number": 40, "nationality": "Nigeria"},
        {"name": "Razvan Sava", "position": "GK", "number": 90, "nationality": "Romania"},
        {"name": "Jaka Bijol", "position": "DF", "number": 29, "nationality": "Slovenia"},
        {"name": "Thomas Kristensen", "position": "DF", "number": 31, "nationality": "Denmark"},
        {"name": "Christian Kabasele", "position": "DF", "number": 27, "nationality": "Belgium"},
        {"name": "Kingsley Ehizibue", "position": "DF", "number": 19, "nationality": "Netherlands"},
        {"name": "Hassane Kamara", "position": "DF", "number": 11, "nationality": "France"},
        {"name": "Sandi Lovric", "position": "MF", "number": 8, "nationality": "Slovenia"},
        {"name": "Jesper Karlstrom", "position": "MF", "number": 25, "nationality": "Sweden"},
        {"name": "Jurgen Ekkelenkamp", "position": "MF", "number": 32, "nationality": "Netherlands"},
        {"name": "Florian Thauvin", "position": "FW", "number": 10, "nationality": "France"},
        {"name": "Brenner", "position": "FW", "number": 22, "nationality": "Brazil"},
        {"name": "Keinan Davis", "position": "FW", "number": 9, "nationality": "England"},
        {"name": "Alexis Sanchez", "position": "FW", "number": 7, "nationality": "Chile"},
        {"name": "Iker Bravo", "position": "FW", "number": 21, "nationality": "Spain"},
    ],
    "Sassuolo": [
        {"name": "Stefano Turati", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Andrea Consigli", "position": "GK", "number": 47, "nationality": "Italy"},
        {"name": "Jeremy Toljan", "position": "DF", "number": 22, "nationality": "Germany"},
        {"name": "Josh Doig", "position": "DF", "number": 3, "nationality": "Scotland"},
        {"name": "Filippo Romagna", "position": "DF", "number": 19, "nationality": "Italy"},
        {"name": "Daniel Boloca", "position": "MF", "number": 11, "nationality": "Romania"},
        {"name": "Kristian Thorstvedt", "position": "MF", "number": 42, "nationality": "Norway"},
        {"name": "Pedro Obiang", "position": "MF", "number": 14, "nationality": "Equatorial Guinea"},
        {"name": "Domenico Berardi", "position": "FW", "number": 10, "nationality": "Italy"},
        {"name": "Armand Laurienté", "position": "FW", "number": 45, "nationality": "France"},
        {"name": "Samuele Mulattieri", "position": "FW", "number": 8, "nationality": "Italy"},
        {"name": "Cristian Volpato", "position": "FW", "number": 23, "nationality": "Italy"},
    ],
    "Parma": [
        {"name": "Zion Suzuki", "position": "GK", "number": 31, "nationality": "Japan"},
        {"name": "Leandro Chichizola", "position": "GK", "number": 1, "nationality": "Argentina"},
        {"name": "Enrico Delprato", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Botond Balogh", "position": "DF", "number": 4, "nationality": "Hungary"},
        {"name": "Alessandro Circati", "position": "DF", "number": 39, "nationality": "Australia"},
        {"name": "Emanuele Valeri", "position": "DF", "number": 14, "nationality": "Italy"},
        {"name": "Nahuel Estevez", "position": "MF", "number": 8, "nationality": "Argentina"},
        {"name": "Adrian Bernabe", "position": "MF", "number": 10, "nationality": "Spain"},
        {"name": "Hernani", "position": "MF", "number": 27, "nationality": "Brazil"},
        {"name": "Benjamin Cremaschi", "position": "MF", "number": 30, "nationality": "USA"},
        {"name": "Dennis Man", "position": "FW", "number": 98, "nationality": "Romania"},
        {"name": "Valentin Mihaila", "position": "FW", "number": 28, "nationality": "Romania"},
        {"name": "Matteo Cancellieri", "position": "FW", "number": 22, "nationality": "Italy"},
        {"name": "Gabriel Charpentier", "position": "FW", "number": 9, "nationality": "France"},
    ],
    "Cagliari": [
        {"name": "Simone Scuffet", "position": "GK", "number": 22, "nationality": "Italy"},
        {"name": "Alen Sherri", "position": "GK", "number": 1, "nationality": "Albania"},
        {"name": "Sebastiano Luperto", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Yerry Mina", "position": "DF", "number": 26, "nationality": "Colombia"},
        {"name": "Gabriele Zappa", "position": "DF", "number": 28, "nationality": "Italy"},
        {"name": "Tommaso Augello", "position": "DF", "number": 3, "nationality": "Italy"},
        {"name": "Mateusz Wieteska", "position": "DF", "number": 23, "nationality": "Poland"},
        {"name": "Razvan Marin", "position": "MF", "number": 18, "nationality": "Romania"},
        {"name": "Alessandro Deiola", "position": "MF", "number": 14, "nationality": "Italy"},
        {"name": "Matteo Prati", "position": "MF", "number": 16, "nationality": "Italy"},
        {"name": "Gianluca Gaetano", "position": "MF", "number": 70, "nationality": "Italy"},
        {"name": "Michel Adopo", "position": "MF", "number": 8, "nationality": "France"},
        {"name": "Michael Folorunsho", "position": "MF", "number": 90, "nationality": "Italy"},
        {"name": "Zito Luvumbo", "position": "FW", "number": 77, "nationality": "Angola"},
        {"name": "Leonardo Pavoletti", "position": "FW", "number": 30, "nationality": "Italy"},
        {"name": "Gianluca Lapadula", "position": "FW", "number": 9, "nationality": "Peru"},
        {"name": "Sebastiano Esposito", "position": "FW", "number": 99, "nationality": "Italy"},
        {"name": "Semih Kilicsoy", "position": "FW", "number": 24, "nationality": "Turkey"},
    ],
    "Lecce": [
        {"name": "Wladimiro Falcone", "position": "GK", "number": 30, "nationality": "Italy"},
        {"name": "Christian Fruchtl", "position": "GK", "number": 1, "nationality": "Germany"},
        {"name": "Federico Baschirotto", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Kialonda Gaspar", "position": "DF", "number": 4, "nationality": "Angola"},
        {"name": "Patrick Dorgu", "position": "DF", "number": 13, "nationality": "Denmark"},
        {"name": "Antonino Gallo", "position": "DF", "number": 25, "nationality": "Italy"},
        {"name": "Ylber Ramadani", "position": "MF", "number": 20, "nationality": "Albania"},
        {"name": "Balthazar Pierret", "position": "MF", "number": 5, "nationality": "France"},
        {"name": "Hamza Rafia", "position": "MF", "number": 8, "nationality": "Tunisia"},
        {"name": "Lassana Coulibaly", "position": "MF", "number": 29, "nationality": "Mali"},
        {"name": "Lameck Banda", "position": "FW", "number": 22, "nationality": "Zambia"},
        {"name": "Santiago Pierotti", "position": "FW", "number": 50, "nationality": "Argentina"},
        {"name": "Nikola Stulic", "position": "FW", "number": 9, "nationality": "Serbia"},
        {"name": "Francesco Camarda", "position": "FW", "number": 73, "nationality": "Italy"},
    ],
    "Como": [
        {"name": "Pepe Reina", "position": "GK", "number": 25, "nationality": "Spain"},
        {"name": "Emil Audero", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Alberto Dossena", "position": "DF", "number": 13, "nationality": "Italy"},
        {"name": "Marc-Oliver Kempf", "position": "DF", "number": 2, "nationality": "Germany"},
        {"name": "Edoardo Goldaniga", "position": "DF", "number": 5, "nationality": "Italy"},
        {"name": "Alberto Moreno", "position": "DF", "number": 18, "nationality": "Spain"},
        {"name": "Ignace Van der Brempt", "position": "DF", "number": 3, "nationality": "Belgium"},
        {"name": "Diego Carlos", "position": "DF", "number": 20, "nationality": "Brazil"},
        {"name": "Sergi Roberto", "position": "MF", "number": 23, "nationality": "Spain"},
        {"name": "Maximo Perrone", "position": "MF", "number": 32, "nationality": "Argentina"},
        {"name": "Luca Mazzitelli", "position": "MF", "number": 36, "nationality": "Italy"},
        {"name": "Nico Paz", "position": "MF", "number": 10, "nationality": "Argentina"},
        {"name": "Lucas Da Cunha", "position": "MF", "number": 33, "nationality": "France"},
        {"name": "Gabriel Strefezza", "position": "FW", "number": 7, "nationality": "Brazil"},
        {"name": "Alvaro Morata", "position": "FW", "number": 9, "nationality": "Spain"},
        {"name": "Andrea Belotti", "position": "FW", "number": 11, "nationality": "Italy"},
        {"name": "Patrick Cutrone", "position": "FW", "number": 63, "nationality": "Italy"},
        {"name": "Assane Diao", "position": "FW", "number": 19, "nationality": "Spain"},
        {"name": "Jesus Rodriguez", "position": "FW", "number": 14, "nationality": "Spain"},
    ],
    "Hellas Verona": [
        {"name": "Lorenzo Montipo", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Simone Perilli", "position": "GK", "number": 34, "nationality": "Italy"},
        {"name": "Pawel Dawidowicz", "position": "DF", "number": 27, "nationality": "Poland"},
        {"name": "Diego Coppola", "position": "DF", "number": 42, "nationality": "Italy"},
        {"name": "Giangiacomo Magnani", "position": "DF", "number": 23, "nationality": "Italy"},
        {"name": "Jackson Tchatchoua", "position": "DF", "number": 38, "nationality": "Cameroon"},
        {"name": "Domagoj Bradaric", "position": "DF", "number": 12, "nationality": "Croatia"},
        {"name": "Ondrej Duda", "position": "MF", "number": 33, "nationality": "Slovakia"},
        {"name": "Suat Serdar", "position": "MF", "number": 25, "nationality": "Germany"},
        {"name": "Tomas Suslov", "position": "MF", "number": 31, "nationality": "Slovakia"},
        {"name": "Darko Lazovic", "position": "MF", "number": 8, "nationality": "Serbia"},
        {"name": "Reda Belahyane", "position": "MF", "number": 6, "nationality": "France"},
        {"name": "Casper Tengstedt", "position": "FW", "number": 11, "nationality": "Denmark"},
        {"name": "Daniel Mosquera", "position": "FW", "number": 9, "nationality": "Colombia"},
        {"name": "Dailon Livramento", "position": "FW", "number": 14, "nationality": "Netherlands"},
    ],
    "Genoa": [
        {"name": "Pierluigi Gollini", "position": "GK", "number": 95, "nationality": "Italy"},
        {"name": "Nicola Leali", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Johan Vasquez", "position": "DF", "number": 22, "nationality": "Mexico"},
        {"name": "Mattia Bani", "position": "DF", "number": 13, "nationality": "Italy"},
        {"name": "Koni De Winter", "position": "DF", "number": 4, "nationality": "Belgium"},
        {"name": "Aaron Martin", "position": "DF", "number": 3, "nationality": "Spain"},
        {"name": "Stefano Sabelli", "position": "DF", "number": 20, "nationality": "Italy"},
        {"name": "Leo Ostigard", "position": "DF", "number": 55, "nationality": "Norway"},
        {"name": "Morten Frendrup", "position": "MF", "number": 32, "nationality": "Denmark"},
        {"name": "Milan Badelj", "position": "MF", "number": 47, "nationality": "Croatia"},
        {"name": "Ruslan Malinovskyi", "position": "MF", "number": 17, "nationality": "Ukraine"},
        {"name": "Morten Thorsby", "position": "MF", "number": 2, "nationality": "Norway"},
        {"name": "Fabio Miretti", "position": "MF", "number": 23, "nationality": "Italy"},
        {"name": "Nicolae Stanciu", "position": "MF", "number": 10, "nationality": "Romania"},
        {"name": "Valentin Carboni", "position": "MF", "number": 44, "nationality": "Argentina"},
        {"name": "Andrea Pinamonti", "position": "FW", "number": 9, "nationality": "Italy"},
        {"name": "Vitinha", "position": "FW", "number": 9, "nationality": "Portugal"},
        {"name": "Lorenzo Colombo", "position": "FW", "number": 29, "nationality": "Italy"},
        {"name": "Albert Gronbaek", "position": "FW", "number": 30, "nationality": "Denmark"},
    ],
    "Cremonese": [
        {"name": "Marco Silvestri", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Andreas Jungdal", "position": "GK", "number": 22, "nationality": "Denmark"},
        {"name": "Federico Ceccherini", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Luka Lochoshvili", "position": "DF", "number": 44, "nationality": "Georgia"},
        {"name": "Leonardo Sernicola", "position": "DF", "number": 17, "nationality": "Italy"},
        {"name": "Valentin Antov", "position": "DF", "number": 26, "nationality": "Bulgaria"},
        {"name": "Mikayil Faye", "position": "DF", "number": 30, "nationality": "Senegal"},
        {"name": "Michele Castagnetti", "position": "MF", "number": 19, "nationality": "Italy"},
        {"name": "Charles Pickel", "position": "MF", "number": 6, "nationality": "Switzerland"},
        {"name": "Franco Vazquez", "position": "MF", "number": 20, "nationality": "Argentina"},
        {"name": "Jari Vandeputte", "position": "MF", "number": 71, "nationality": "Belgium"},
        {"name": "Warren Bondo", "position": "MF", "number": 38, "nationality": "France"},
        {"name": "Jamie Vardy", "position": "FW", "number": 9, "nationality": "England"},
        {"name": "Antonio Sanabria", "position": "FW", "number": 11, "nationality": "Paraguay"},
        {"name": "Alessio Zerbin", "position": "FW", "number": 23, "nationality": "Italy"},
        {"name": "Federico Bonazzoli", "position": "FW", "number": 99, "nationality": "Italy"},
    ],
    "Pisa": [
        {"name": "Adrian Semper", "position": "GK", "number": 47, "nationality": "Croatia"},
        {"name": "Nicolas", "position": "GK", "number": 1, "nationality": "Brazil"},
        {"name": "Simone Canestrelli", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Antonio Caracciolo", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Tommaso Barbieri", "position": "DF", "number": 33, "nationality": "Italy"},
        {"name": "Pietro Beruatto", "position": "DF", "number": 20, "nationality": "Italy"},
        {"name": "Marius Marin", "position": "MF", "number": 8, "nationality": "Romania"},
        {"name": "Idrissa Touré", "position": "MF", "number": 15, "nationality": "Germany"},
        {"name": "Michel Aebischer", "position": "MF", "number": 20, "nationality": "Switzerland"},
        {"name": "Juan Cuadrado", "position": "MF", "number": 7, "nationality": "Colombia"},
        {"name": "Matteo Tramoni", "position": "MF", "number": 11, "nationality": "France"},
        {"name": "M'Bala Nzola", "position": "FW", "number": 18, "nationality": "Angola"},
        {"name": "Stefano Moreo", "position": "FW", "number": 32, "nationality": "Italy"},
        {"name": "Nicholas Bonfanti", "position": "FW", "number": 9, "nationality": "Italy"},
    ],
}

async def validate_players():
    """
    Validate PLAYERS_DATA for duplicates and DB mismatches.
    Returns a dict with:
      - duplicates: players appearing in multiple teams (from PLAYERS_DATA)
      - db_mismatches: players in DB whose team differs from PLAYERS_DATA mapping
      - summary: counts per team
    """
    # Build name -> teams mapping from PLAYERS_DATA
    name_teams = {}
    for team, players in PLAYERS_DATA.items():
        for p in players:
            name = p["name"].strip()
            name_teams.setdefault(name, set()).add(team)

    duplicates = [
        {"name": name, "teams": sorted(list(teams))}
        for name, teams in name_teams.items()
        if len(teams) > 1
    ]

    summary = {team: len(players) for team, players in PLAYERS_DATA.items()}

    # Check DB mismatches
    db_mismatches = []
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Player))
        players_db = result.scalars().all()

        # Create team id -> name map
        teams_res = await db.execute(select(Team))
        teams = {t.id: t.name for t in teams_res.scalars().all()}

        for player in players_db:
            expected_teams = name_teams.get(player.name)
            actual_team = teams.get(player.team_id)
            if expected_teams and actual_team and actual_team not in expected_teams:
                db_mismatches.append({
                    "name": player.name,
                    "db_team": actual_team,
                    "expected_teams": sorted(list(expected_teams))
                })

    return {
        "duplicates": sorted(duplicates, key=lambda x: x["name"]),
        "db_mismatches": sorted(db_mismatches, key=lambda x: x["name"]),
        "summary": summary,
    }

async def seed_players(db=None):
    """Seed players for all Serie A teams"""
    if db:
        await _seed_players_internal(db)
    else:
        async with AsyncSessionLocal() as session:
            await _seed_players_internal(session)
            await session.commit()

async def _seed_players_internal(db):
    try:
        # Get all teams from database
        result = await db.execute(select(Team))
        teams = result.scalars().all()

        if not teams:
            logger.error("No teams found in database. Please run seed_teams.py first.")
            return

        # Create a mapping of team names to team objects
        team_map = {team.name: team for team in teams}

        total_players = 0

        for team_name, players_data in PLAYERS_DATA.items():
            team = team_map.get(team_name)

            if not team:
                logger.warning(f"Team '{team_name}' not found in database. Skipping players.")
                continue

            logger.info(f"Seeding players for {team_name}...")

            for player_data in players_data:
                # Check if player already exists (by name only, to handle transfers)
                result = await db.execute(
                    select(Player).where(
                        Player.name == player_data["name"]
                    )
                )
                existing_player = result.scalars().first()

                if existing_player:
                    if existing_player.team_id != team.id:
                        logger.info(f"Transferring {player_data['name']} from Team {existing_player.team_id} to {team.name} ({team.id})")
                        existing_player.team_id = team.id
                    
                    # Always update mutable fields
                    existing_player.jersey_number = player_data.get("number")
                    existing_player.nationality = player_data.get("nationality")
                    continue

                # Create new player
                player = Player(
                    team_id=team.id,
                    name=player_data["name"],
                    position=player_data["position"],
                    jersey_number=player_data.get("number"),
                    nationality=player_data.get("nationality")
                )
                db.add(player)
                total_players += 1
            
            # Flush after each team to avoid huge transaction if needed
            await db.flush()

        logger.info(f"Seeding completed. Added {total_players} new players.")
    except Exception as e:
        logger.error(f"Error seeding players: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_players())
