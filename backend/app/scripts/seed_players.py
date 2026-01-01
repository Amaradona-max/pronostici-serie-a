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

# Complete Serie A 2025/2026 players data (Updated Matchday 17)
PLAYERS_DATA = {
    "Inter": [
        {"name": "Yann Sommer", "position": "GK", "number": 1, "nationality": "Switzerland"},
        {"name": "Denzel Dumfries", "position": "DF", "number": 2, "nationality": "Netherlands"},
        {"name": "Stefan de Vrij", "position": "DF", "number": 6, "nationality": "Netherlands"},
        {"name": "Carlos Augusto", "position": "DF", "number": 30, "nationality": "Brazil"},
        {"name": "Benjamin Pavard", "position": "DF", "number": 28, "nationality": "France"},
        {"name": "Alessandro Bastoni", "position": "DF", "number": 95, "nationality": "Italy"},
        {"name": "Francesco Acerbi", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Yann Bisseck", "position": "DF", "number": 31, "nationality": "Germany"},
        {"name": "Matteo Darmian", "position": "DF", "number": 36, "nationality": "Italy"},
        {"name": "Hakan Calhanoglu", "position": "MF", "number": 20, "nationality": "Turkey"},
        {"name": "Henrikh Mkhitaryan", "position": "MF", "number": 22, "nationality": "Armenia"},
        {"name": "Nicolò Barella", "position": "MF", "number": 23, "nationality": "Italy"},
        {"name": "Kristjan Asllani", "position": "MF", "number": 21, "nationality": "Albania"},
        {"name": "Davide Frattesi", "position": "MF", "number": 16, "nationality": "Italy"},
        {"name": "Piotr Zielinski", "position": "MF", "number": 7, "nationality": "Poland"},
        {"name": "Lautaro Martinez", "position": "FW", "number": 10, "nationality": "Argentina"},
        {"name": "Marcus Thuram", "position": "FW", "number": 9, "nationality": "France"},
        {"name": "Mehdi Taremi", "position": "FW", "number": 99, "nationality": "Iran"},
        {"name": "Marko Arnautovic", "position": "FW", "number": 8, "nationality": "Austria"},
        {"name": "Joaquin Correa", "position": "FW", "number": 11, "nationality": "Argentina"},
        {"name": "Josep Martinez", "position": "GK", "number": 13, "nationality": "Spain"},
        {"name": "Raffaele Di Gennaro", "position": "GK", "number": 12, "nationality": "Italy"},
    ],
    "AC Milan": [
        {"name": "Mike Maignan", "position": "GK", "number": 16, "nationality": "France"},
        {"name": "Pietro Terracciano", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Lorenzo Torriani", "position": "GK", "number": 96, "nationality": "Italy"},
        {"name": "Fikayo Tomori", "position": "DF", "number": 23, "nationality": "England"},
        {"name": "Malick Thiaw", "position": "DF", "number": 28, "nationality": "Germany"},
        {"name": "Strahinja Pavlovic", "position": "DF", "number": 31, "nationality": "Serbia"},
        {"name": "Matteo Gabbia", "position": "DF", "number": 46, "nationality": "Italy"},
        {"name": "Koni De Winter", "position": "DF", "number": 4, "nationality": "Belgium"},
        {"name": "Pervis Estupinan", "position": "DF", "number": 19, "nationality": "Ecuador"},
        {"name": "Youssouf Fofana", "position": "MF", "number": 29, "nationality": "France"},
        {"name": "Ruben Loftus-Cheek", "position": "MF", "number": 8, "nationality": "England"},
        {"name": "Yunus Musah", "position": "MF", "number": 80, "nationality": "USA"},
        {"name": "Samuele Ricci", "position": "MF", "number": 28, "nationality": "Italy"},
        {"name": "Luka Modric", "position": "MF", "number": 14, "nationality": "Croatia"},
        {"name": "Christian Pulisic", "position": "FW", "number": 11, "nationality": "USA"},
        {"name": "Rafael Leao", "position": "FW", "number": 10, "nationality": "Portugal"},
        {"name": "Tammy Abraham", "position": "FW", "number": 90, "nationality": "England"},
        {"name": "Samuel Chukwueze", "position": "FW", "number": 21, "nationality": "Nigeria"},
        {"name": "Noah Okafor", "position": "FW", "number": 17, "nationality": "Switzerland"},
        {"name": "Kevin Zeroli", "position": "MF", "number": 43, "nationality": "Italy"},
    ],
    "Juventus": [
        {"name": "Michele Di Gregorio", "position": "GK", "number": 29, "nationality": "Italy"},
        {"name": "Andrea Cambiaso", "position": "DF", "number": 27, "nationality": "Italy"},
        {"name": "Federico Gatti", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Bremer", "position": "DF", "number": 3, "nationality": "Brazil"},
        {"name": "Pierre Kalulu", "position": "DF", "number": 15, "nationality": "France"},
        {"name": "Danilo", "position": "DF", "number": 6, "nationality": "Brazil"},
        {"name": "Juan Cabal", "position": "DF", "number": 32, "nationality": "Colombia"},
        {"name": "Nicolo Savona", "position": "DF", "number": 37, "nationality": "Italy"},
        {"name": "Manuel Locatelli", "position": "MF", "number": 5, "nationality": "Italy"},
        {"name": "Khephren Thuram", "position": "MF", "number": 19, "nationality": "France"},
        {"name": "Douglas Luiz", "position": "MF", "number": 26, "nationality": "Brazil"},
        {"name": "Weston McKennie", "position": "MF", "number": 16, "nationality": "USA"},
        {"name": "Nicolo Fagioli", "position": "MF", "number": 21, "nationality": "Italy"},
        {"name": "Kenan Yildiz", "position": "FW", "number": 10, "nationality": "Turkey"},
        {"name": "Dusan Vlahovic", "position": "FW", "number": 9, "nationality": "Serbia"},
        {"name": "Timothy Weah", "position": "FW", "number": 22, "nationality": "USA"},
        {"name": "Francisco Conceicao", "position": "FW", "number": 7, "nationality": "Portugal"},
        {"name": "Teun Koopmeiners", "position": "MF", "number": 8, "nationality": "Netherlands"},
        {"name": "Mattia Perin", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Carlo Pinsoglio", "position": "GK", "number": 23, "nationality": "Italy"},
        {"name": "Jonas Rouhi", "position": "DF", "number": 40, "nationality": "Sweden"},
        {"name": "Samuel Mbangula", "position": "FW", "number": 51, "nationality": "Belgium"},
    ],
    "Atalanta": [
        {"name": "Marco Carnesecchi", "position": "GK", "number": 29, "nationality": "Italy"},
        {"name": "Marco Sportiello", "position": "GK", "number": 57, "nationality": "Italy"},
        {"name": "Francesco Rossi", "position": "GK", "number": 31, "nationality": "Italy"},
        {"name": "Berat Djimsiti", "position": "DF", "number": 19, "nationality": "Albania"},
        {"name": "Sead Kolasinac", "position": "DF", "number": 23, "nationality": "Bosnia"},
        {"name": "Isak Hien", "position": "DF", "number": 4, "nationality": "Sweden"},
        {"name": "Odilon Kossounou", "position": "DF", "number": 3, "nationality": "Ivory Coast"},
        {"name": "Ben Godfrey", "position": "DF", "number": 5, "nationality": "England"},
        {"name": "Honest Ahanor", "position": "DF", "number": 33, "nationality": "Italy"},
        {"name": "Marten de Roon", "position": "MF", "number": 15, "nationality": "Netherlands"},
        {"name": "Ederson", "position": "MF", "number": 13, "nationality": "Brazil"},
        {"name": "Mario Pasalic", "position": "MF", "number": 8, "nationality": "Croatia"},
        {"name": "Davide Zappacosta", "position": "DF", "number": 77, "nationality": "Italy"},
        {"name": "Raoul Bellanova", "position": "DF", "number": 16, "nationality": "Italy"},
        {"name": "Marco Brescianini", "position": "MF", "number": 44, "nationality": "Italy"},
        {"name": "Lazar Samardzic", "position": "MF", "number": 24, "nationality": "Serbia"},
        {"name": "Nicola Zalewski", "position": "MF", "number": 59, "nationality": "Poland"},
        {"name": "Kamaldeen Sulemana", "position": "MF", "number": 7, "nationality": "Ghana"},
        {"name": "Charles De Ketelaere", "position": "FW", "number": 17, "nationality": "Belgium"},
        {"name": "Ademola Lookman", "position": "FW", "number": 11, "nationality": "Nigeria"},
        {"name": "Nikola Krstovic", "position": "FW", "number": 9, "nationality": "Montenegro"},
        {"name": "Nicolo Zaniolo", "position": "FW", "number": 10, "nationality": "Italy"},
    ],
    "Napoli": [
        {"name": "Alex Meret", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Vanja Milinkovic-Savic", "position": "GK", "number": 32, "nationality": "Serbia"},
        {"name": "Nikita Contini", "position": "GK", "number": 12, "nationality": "Italy"},
        {"name": "Giovanni Di Lorenzo", "position": "DF", "number": 22, "nationality": "Italy"},
        {"name": "Amir Rrahmani", "position": "DF", "number": 13, "nationality": "Kosovo"},
        {"name": "Alessandro Buongiorno", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Mathias Olivera", "position": "DF", "number": 17, "nationality": "Uruguay"},
        {"name": "Juan Jesus", "position": "DF", "number": 5, "nationality": "Brazil"},
        {"name": "Pasquale Mazzocchi", "position": "DF", "number": 30, "nationality": "Italy"},
        {"name": "Leonardo Spinazzola", "position": "DF", "number": 37, "nationality": "Italy"},
        {"name": "Sam Beukema", "position": "DF", "number": 31, "nationality": "Netherlands"},
        {"name": "Stanislav Lobotka", "position": "MF", "number": 68, "nationality": "Slovakia"},
        {"name": "Frank Anguissa", "position": "MF", "number": 99, "nationality": "Cameroon"},
        {"name": "Scott McTominay", "position": "MF", "number": 8, "nationality": "Scotland"},
        {"name": "Billy Gilmour", "position": "MF", "number": 6, "nationality": "Scotland"},
        {"name": "Kevin De Bruyne", "position": "MF", "number": 17, "nationality": "Belgium"},
        {"name": "Khvicha Kvaratskhelia", "position": "FW", "number": 77, "nationality": "Georgia"},
        {"name": "Romelu Lukaku", "position": "FW", "number": 11, "nationality": "Belgium"},
        {"name": "Matteo Politano", "position": "FW", "number": 21, "nationality": "Italy"},
        {"name": "David Neres", "position": "FW", "number": 7, "nationality": "Brazil"},
        {"name": "Giovanni Simeone", "position": "FW", "number": 18, "nationality": "Argentina"},
        {"name": "Giacomo Raspadori", "position": "FW", "number": 81, "nationality": "Italy"},
        {"name": "Cyril Ngonge", "position": "FW", "number": 26, "nationality": "Belgium"},
    ],
    "Lazio": [
        {"name": "Ivan Provedel", "position": "GK", "number": 94, "nationality": "Italy"},
        {"name": "Christos Mandas", "position": "GK", "number": 35, "nationality": "Greece"},
        {"name": "Luigi Sepe", "position": "GK", "number": 55, "nationality": "Italy"},
        {"name": "Adam Marusic", "position": "DF", "number": 77, "nationality": "Montenegro"},
        {"name": "Alessio Romagnoli", "position": "DF", "number": 13, "nationality": "Italy"},
        {"name": "Patric", "position": "DF", "number": 4, "nationality": "Spain"},
        {"name": "Nuno Tavares", "position": "DF", "number": 30, "nationality": "Portugal"},
        {"name": "Manuel Lazzari", "position": "DF", "number": 29, "nationality": "Italy"},
        {"name": "Mario Gila", "position": "DF", "number": 34, "nationality": "Spain"},
        {"name": "Luca Pellegrini", "position": "DF", "number": 3, "nationality": "Italy"},
        {"name": "Samuel Gigot", "position": "DF", "number": 2, "nationality": "France"},
        {"name": "Matteo Guendouzi", "position": "MF", "number": 8, "nationality": "France"},
        {"name": "Nicolo Rovella", "position": "MF", "number": 6, "nationality": "Italy"},
        {"name": "Matias Vecino", "position": "MF", "number": 5, "nationality": "Uruguay"},
        {"name": "Fisayo Dele-Bashiru", "position": "MF", "number": 7, "nationality": "Nigeria"},
        {"name": "Gaetano Castrovilli", "position": "MF", "number": 22, "nationality": "Italy"},
        {"name": "Gustav Isaksen", "position": "FW", "number": 18, "nationality": "Denmark"},
        {"name": "Mattia Zaccagni", "position": "FW", "number": 10, "nationality": "Italy"},
        {"name": "Boulaye Dia", "position": "FW", "number": 19, "nationality": "Senegal"},
        {"name": "Taty Castellanos", "position": "FW", "number": 11, "nationality": "Argentina"},
        {"name": "Pedro", "position": "FW", "number": 9, "nationality": "Spain"},
        {"name": "Tijjani Noslin", "position": "FW", "number": 14, "nationality": "Netherlands"},
    ],
    "AS Roma": [
        {"name": "Mile Svilar", "position": "GK", "number": 99, "nationality": "Belgium"},
        {"name": "Mathew Ryan", "position": "GK", "number": 89, "nationality": "Australia"},
        {"name": "Renato Marin", "position": "GK", "number": 98, "nationality": "Romania"},
        {"name": "Evan Ndicka", "position": "DF", "number": 5, "nationality": "France"},
        {"name": "Gianluca Mancini", "position": "DF", "number": 23, "nationality": "Italy"},
        {"name": "Angelino", "position": "DF", "number": 3, "nationality": "Spain"},
        {"name": "Zeki Celik", "position": "DF", "number": 19, "nationality": "Turkey"},
        {"name": "Mario Hermoso", "position": "DF", "number": 22, "nationality": "Spain"},
        {"name": "Wesley Franca", "position": "DF", "number": 2, "nationality": "Brazil"},
        {"name": "Leandro Paredes", "position": "MF", "number": 16, "nationality": "Argentina"},
        {"name": "Bryan Cristante", "position": "MF", "number": 4, "nationality": "Italy"},
        {"name": "Manu Kone", "position": "MF", "number": 17, "nationality": "France"},
        {"name": "Lorenzo Pellegrini", "position": "MF", "number": 7, "nationality": "Italy"},
        {"name": "Niccolo Pisilli", "position": "MF", "number": 61, "nationality": "Italy"},
        {"name": "Enzo Le Fee", "position": "MF", "number": 28, "nationality": "France"},
        {"name": "Paulo Dybala", "position": "FW", "number": 21, "nationality": "Argentina"},
        {"name": "Artem Dovbyk", "position": "FW", "number": 11, "nationality": "Ukraine"},
        {"name": "Stephan El Shaarawy", "position": "FW", "number": 92, "nationality": "Italy"},
        {"name": "Matias Soule", "position": "FW", "number": 18, "nationality": "Argentina"},
        {"name": "Eldor Shomurodov", "position": "FW", "number": 14, "nationality": "Uzbekistan"},
        {"name": "Alexis Saelemaekers", "position": "FW", "number": 56, "nationality": "Belgium"},
    ],
    "Fiorentina": [
        {"name": "David de Gea", "position": "GK", "number": 43, "nationality": "Spain"},
        {"name": "Tommaso Martinelli", "position": "GK", "number": 30, "nationality": "Italy"},
        {"name": "Dodô", "position": "DF", "number": 2, "nationality": "Brazil"},
        {"name": "Luca Ranieri", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Pietro Comuzzo", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Robin Gosens", "position": "DF", "number": 21, "nationality": "Germany"},
        {"name": "Michael Kayode", "position": "DF", "number": 33, "nationality": "Italy"},
        {"name": "Marin Pongracic", "position": "DF", "number": 5, "nationality": "Croatia"},
        {"name": "Fabiano Parisi", "position": "DF", "number": 65, "nationality": "Italy"},
        {"name": "Lucas Martinez Quarta", "position": "DF", "number": 28, "nationality": "Argentina"},
        {"name": "Danilo Cataldi", "position": "MF", "number": 32, "nationality": "Italy"},
        {"name": "Rolando Mandragora", "position": "MF", "number": 8, "nationality": "Italy"},
        {"name": "Yacine Adli", "position": "MF", "number": 29, "nationality": "France"},
        {"name": "Edoardo Bove", "position": "MF", "number": 4, "nationality": "Italy"},
        {"name": "Andrea Colpani", "position": "MF", "number": 23, "nationality": "Italy"},
        {"name": "Amir Richardson", "position": "MF", "number": 24, "nationality": "Morocco"},
        {"name": "Riccardo Sottil", "position": "FW", "number": 7, "nationality": "Italy"},
        {"name": "Moise Kean", "position": "FW", "number": 20, "nationality": "Italy"},
        {"name": "Roberto Piccoli", "position": "FW", "number": 91, "nationality": "Italy"},
        {"name": "Edin Dzeko", "position": "FW", "number": 9, "nationality": "Bosnia"},
        {"name": "Manor Solomon", "position": "FW", "number": 14, "nationality": "Israel"},
        {"name": "Albert Gudmundsson", "position": "FW", "number": 10, "nationality": "Iceland"},
        {"name": "Jonathan Ikone", "position": "FW", "number": 11, "nationality": "France"},
        {"name": "Christian Kouame", "position": "FW", "number": 99, "nationality": "Ivory Coast"},
    ],
    "Bologna": [
        {"name": "Lukasz Skorupski", "position": "GK", "number": 28, "nationality": "Poland"},
        {"name": "Federico Ravaglia", "position": "GK", "number": 34, "nationality": "Italy"},
        {"name": "Stefan Posch", "position": "DF", "number": 3, "nationality": "Austria"},
        {"name": "Sam Beukema", "position": "DF", "number": 31, "nationality": "Netherlands"},
        {"name": "Jhon Lucumi", "position": "DF", "number": 26, "nationality": "Colombia"},
        {"name": "Charalampos Lykogiannis", "position": "DF", "number": 22, "nationality": "Greece"},
        {"name": "Lorenzo De Silvestri", "position": "DF", "number": 29, "nationality": "Italy"},
        {"name": "Juan Miranda", "position": "DF", "number": 33, "nationality": "Spain"},
        {"name": "Martin Erlic", "position": "DF", "number": 5, "nationality": "Croatia"},
        {"name": "Remo Freuler", "position": "MF", "number": 8, "nationality": "Switzerland"},
        {"name": "Michel Aebischer", "position": "MF", "number": 20, "nationality": "Switzerland"},
        {"name": "Lewis Ferguson", "position": "MF", "number": 19, "nationality": "Scotland"},
        {"name": "Giovanni Fabbian", "position": "MF", "number": 80, "nationality": "Italy"},
        {"name": "Kacper Urbanski", "position": "MF", "number": 82, "nationality": "Poland"},
        {"name": "Nikola Moro", "position": "MF", "number": 6, "nationality": "Croatia"},
        {"name": "Riccardo Orsolini", "position": "FW", "number": 7, "nationality": "Italy"},
        {"name": "Dan Ndoye", "position": "FW", "number": 11, "nationality": "Switzerland"},
        {"name": "Santiago Castro", "position": "FW", "number": 9, "nationality": "Argentina"},
        {"name": "Jens Odgaard", "position": "FW", "number": 21, "nationality": "Denmark"},
        {"name": "Ciro Immobile", "position": "FW", "number": 17, "nationality": "Italy"},
    ],
    "Torino": [
        {"name": "Alberto Paleari", "position": "GK", "number": 89, "nationality": "Italy"},
        {"name": "Antonio Donnarumma", "position": "GK", "number": 71, "nationality": "Italy"},
        {"name": "Saul Coco", "position": "DF", "number": 23, "nationality": "Equatorial Guinea"},
        {"name": "Adam Masina", "position": "DF", "number": 5, "nationality": "Morocco"},
        {"name": "Valentino Lazaro", "position": "DF", "number": 20, "nationality": "Austria"},
        {"name": "Marcus Pedersen", "position": "DF", "number": 16, "nationality": "Norway"},
        {"name": "Mergim Vojvoda", "position": "DF", "number": 27, "nationality": "Kosovo"},
        {"name": "Guillermo Maripan", "position": "DF", "number": 13, "nationality": "Chile"},
        {"name": "Karol Linetty", "position": "MF", "number": 77, "nationality": "Poland"},
        {"name": "Gvidas Gineitis", "position": "MF", "number": 66, "nationality": "Lithuania"},
        {"name": "Ivan Ilic", "position": "MF", "number": 8, "nationality": "Serbia"},
        {"name": "Adrien Tameze", "position": "MF", "number": 61, "nationality": "France"},
        {"name": "Nikola Vlasic", "position": "FW", "number": 10, "nationality": "Croatia"},
        {"name": "Duvan Zapata", "position": "FW", "number": 91, "nationality": "Colombia"},
        {"name": "Ché Adams", "position": "FW", "number": 18, "nationality": "Scotland"},
        {"name": "Yann Karamoh", "position": "FW", "number": 7, "nationality": "France"},
        {"name": "Ali Dembele", "position": "FW", "number": 21, "nationality": "France"},
        {"name": "Alieu Njie", "position": "FW", "number": 14, "nationality": "Sweden"},
    ],
    "Udinese": [
        {"name": "Maduka Okoye", "position": "GK", "number": 40, "nationality": "Nigeria"},
        {"name": "Daniele Padelli", "position": "GK", "number": 93, "nationality": "Italy"},
        {"name": "Razvan Sava", "position": "GK", "number": 77, "nationality": "Romania"},
        {"name": "Jaka Bijol", "position": "DF", "number": 29, "nationality": "Slovenia"},
        {"name": "Thomas Kristensen", "position": "DF", "number": 31, "nationality": "Denmark"},
        {"name": "Lautaro Giannetti", "position": "DF", "number": 30, "nationality": "Argentina"},
        {"name": "Kingsley Ehizibue", "position": "DF", "number": 19, "nationality": "Netherlands"},
        {"name": "Jordan Zemura", "position": "DF", "number": 33, "nationality": "Zimbabwe"},
        {"name": "Christian Kabasele", "position": "DF", "number": 27, "nationality": "Belgium"},
        {"name": "Hassane Kamara", "position": "DF", "number": 12, "nationality": "France"},
        {"name": "Rui Modesto", "position": "DF", "number": 18, "nationality": "Portugal"},
        {"name": "Enzo Ebosse", "position": "DF", "number": 95, "nationality": "Cameroon"},
        {"name": "Jesper Karlstrom", "position": "MF", "number": 25, "nationality": "Sweden"},
        {"name": "Sandi Lovric", "position": "MF", "number": 8, "nationality": "Slovenia"},
        {"name": "Jurgen Ekkelenkamp", "position": "MF", "number": 32, "nationality": "Netherlands"},
        {"name": "Oier Zarraga", "position": "MF", "number": 6, "nationality": "Spain"},
        {"name": "Florian Thauvin", "position": "FW", "number": 10, "nationality": "France"},
        {"name": "Lorenzo Lucca", "position": "FW", "number": 17, "nationality": "Italy"},
        {"name": "Keinan Davis", "position": "FW", "number": 9, "nationality": "England"},
        {"name": "Iker Bravo", "position": "FW", "number": 21, "nationality": "Spain"},
        {"name": "Brenner", "position": "FW", "number": 22, "nationality": "Brazil"},
    ],
    "Sassuolo": [
        {"name": "Arijanet Muric", "position": "GK", "number": 12, "nationality": "Kosovo"},
        {"name": "Giacomo Satalino", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Stefano Turati", "position": "GK", "number": 13, "nationality": "Italy"},
        {"name": "Josh Doig", "position": "DF", "number": 3, "nationality": "Scotland"},
        {"name": "Fali Candè", "position": "DF", "number": 5, "nationality": "Guinea-Bissau"},
        {"name": "Sebastian Walukiewicz", "position": "DF", "number": 6, "nationality": "Poland"},
        {"name": "Edoardo Pieragnolo", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Yeferson Paz", "position": "DF", "number": 17, "nationality": "Colombia"},
        {"name": "Filippo Romagna", "position": "DF", "number": 19, "nationality": "Italy"},
        {"name": "Jay Idzes", "position": "DF", "number": 21, "nationality": "Indonesia"},
        {"name": "Woyo Coulibaly", "position": "DF", "number": 25, "nationality": "Mali"},
        {"name": "Cas Odenthal", "position": "DF", "number": 26, "nationality": "Netherlands"},
        {"name": "Tarik Muharemovic", "position": "DF", "number": 80, "nationality": "Bosnia"},
        {"name": "Daniel Boloca", "position": "MF", "number": 11, "nationality": "Romania"},
        {"name": "Alieu Fadera", "position": "MF", "number": 20, "nationality": "Gambia"},
        {"name": "Edoardo Iannoni", "position": "MF", "number": 44, "nationality": "Italy"},
        {"name": "Ismael Konè", "position": "MF", "number": 90, "nationality": "Canada"},
        {"name": "Luca Lipani", "position": "MF", "number": 35, "nationality": "Italy"},
        {"name": "Nemanja Matic", "position": "MF", "number": 18, "nationality": "Serbia"},
        {"name": "Kristian Thorstvedt", "position": "MF", "number": 42, "nationality": "Norway"},
        {"name": "Cristian Volpato", "position": "MF", "number": 7, "nationality": "Italy"},
        {"name": "Aster Vranckx", "position": "MF", "number": 40, "nationality": "Belgium"},
        {"name": "Domenico Berardi", "position": "FW", "number": 10, "nationality": "Italy"},
        {"name": "Walid Cheddira", "position": "FW", "number": 9, "nationality": "Morocco"},
        {"name": "Armand Laurienté", "position": "FW", "number": 45, "nationality": "France"},
        {"name": "Luca Moro", "position": "FW", "number": 24, "nationality": "Italy"},
        {"name": "Nicholas Pierini", "position": "FW", "number": 77, "nationality": "Italy"},
        {"name": "Andrea Pinamonti", "position": "FW", "number": 99, "nationality": "Italy"},
        {"name": "Laurs Skjellerup", "position": "FW", "number": 14, "nationality": "Denmark"},
    ],
    "Parma": [
        {"name": "Zion Suzuki", "position": "GK", "number": 31, "nationality": "Japan"},
        {"name": "Leandro Chichizola", "position": "GK", "number": 1, "nationality": "Argentina"},
        {"name": "Edoardo Corvi", "position": "GK", "number": 40, "nationality": "Italy"},
        {"name": "Enrico Delprato", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Botond Balogh", "position": "DF", "number": 4, "nationality": "Hungary"},
        {"name": "Emanuele Valeri", "position": "DF", "number": 14, "nationality": "Italy"},
        {"name": "Woyo Couibaly", "position": "DF", "number": 26, "nationality": "Ivory Coast"},
        {"name": "Antoine Hainaut", "position": "DF", "number": 20, "nationality": "France"},
        {"name": "Gianluca Di Chiara", "position": "DF", "number": 3, "nationality": "Italy"},
        {"name": "Alessandro Circati", "position": "DF", "number": 39, "nationality": "Australia"},
        {"name": "Nahuel Estevez", "position": "MF", "number": 8, "nationality": "Argentina"},
        {"name": "Adrian Bernabe", "position": "MF", "number": 10, "nationality": "Spain"},
        {"name": "Simon Sohm", "position": "MF", "number": 19, "nationality": "Switzerland"},
        {"name": "Mandela Keita", "position": "MF", "number": 16, "nationality": "Mali"},
        {"name": "Hernani", "position": "MF", "number": 27, "nationality": "Portugal"},
        {"name": "Drissa Camara", "position": "MF", "number": 6, "nationality": "Mali"},
        {"name": "Ange-Yoan Bonny", "position": "FW", "number": 13, "nationality": "Ivory Coast"},
        {"name": "Dennis Man", "position": "FW", "number": 98, "nationality": "Romania"},
        {"name": "Valentin Mihaila", "position": "FW", "number": 28, "nationality": "Romania"},
        {"name": "Gabriel Charpentier", "position": "FW", "number": 30, "nationality": "France"},
        {"name": "Matteo Cancellieri", "position": "FW", "number": 22, "nationality": "Italy"},
        {"name": "Pontus Almqvist", "position": "FW", "number": 11, "nationality": "Sweden"},
    ],
    "Cagliari": [
        {"name": "Alen Sherri", "position": "GK", "number": 1, "nationality": "Albania"},
        {"name": "Giuseppe Ciocci", "position": "GK", "number": 31, "nationality": "Italy"},
        {"name": "Elia Caprile", "position": "GK", "number": 25, "nationality": "Italy"},
        {"name": "Gabriele Zappa", "position": "DF", "number": 28, "nationality": "Italy"},
        {"name": "Yerry Mina", "position": "DF", "number": 26, "nationality": "Colombia"},
        {"name": "Sebastiano Luperto", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Adam Obert", "position": "DF", "number": 33, "nationality": "Slovakia"},
        {"name": "Tommaso Augello", "position": "DF", "number": 3, "nationality": "Italy"},
        {"name": "Paulo Azzi", "position": "DF", "number": 37, "nationality": "Italy"},
        {"name": "Jose Luis Palomino", "position": "DF", "number": 5, "nationality": "Argentina"},
        {"name": "Mateusz Wieteska", "position": "DF", "number": 24, "nationality": "Poland"},
        {"name": "Razvan Marin", "position": "MF", "number": 18, "nationality": "Romania"},
        {"name": "Alessandro Deiola", "position": "MF", "number": 14, "nationality": "Italy"},
        {"name": "Michel Adopo", "position": "MF", "number": 8, "nationality": "Ivory Coast"},
        {"name": "Matteo Prati", "position": "MF", "number": 16, "nationality": "Italy"},
        {"name": "Nicolas Viola", "position": "MF", "number": 10, "nationality": "Italy"},
        {"name": "Gianluca Gaetano", "position": "MF", "number": 70, "nationality": "Italy"},
        {"name": "Michael Folorunsho", "position": "MF", "number": 90, "nationality": "Italy"},
        {"name": "Luca Mazzitelli", "position": "MF", "number": 36, "nationality": "Italy"},
        {"name": "Zito Luvumbo", "position": "FW", "number": 77, "nationality": "Angola"},
        {"name": "Leonardo Pavoletti", "position": "FW", "number": 30, "nationality": "Italy"},
        {"name": "Kingstone Mutandwa", "position": "FW", "number": 61, "nationality": "Zimbabwe"},
        {"name": "Andrea Belotti", "position": "FW", "number": 19, "nationality": "Italy"},
        {"name": "Sebastiano Esposito", "position": "FW", "number": 99, "nationality": "Italy"},
        {"name": "Semih Kilicsoy", "position": "FW", "number": 9, "nationality": "Turkey"},
        {"name": "Gennaro Borrelli", "position": "FW", "number": 29, "nationality": "Italy"},
    ],
    "Lecce": [
        {"name": "Wladimiro Falcone", "position": "GK", "number": 30, "nationality": "Italy"},
        {"name": "Jasper Samooja", "position": "GK", "number": 1, "nationality": "Finland"},
        {"name": "Christian Fruchtl", "position": "GK", "number": 32, "nationality": "Germany"},
        {"name": "Antonino Gallo", "position": "DF", "number": 25, "nationality": "Italy"},
        {"name": "Kialonda Gaspar", "position": "DF", "number": 4, "nationality": "Angola"},
        {"name": "Patrick Dorgu", "position": "DF", "number": 13, "nationality": "Denmark"},
        {"name": "Frederic Guilbert", "position": "DF", "number": 12, "nationality": "France"},
        {"name": "Andy Pelmard", "position": "DF", "number": 5, "nationality": "France"},
        {"name": "Balthazar Pierret", "position": "MF", "number": 20, "nationality": "France"},
        {"name": "Ylber Ramadani", "position": "MF", "number": 16, "nationality": "Albania"},
        {"name": "Hamza Rafia", "position": "MF", "number": 8, "nationality": "Tunisia"},
        {"name": "Lassana Coulibaly", "position": "MF", "number": 29, "nationality": "Mali"},
        {"name": "Medon Berisha", "position": "MF", "number": 3, "nationality": "Kosovo"},
        {"name": "Luis Hasa", "position": "MF", "number": 27, "nationality": "Italy"},
        {"name": "Lameck Banda", "position": "FW", "number": 22, "nationality": "Zambia"},
        {"name": "Santiago Pierotti", "position": "FW", "number": 50, "nationality": "Argentina"},
        {"name": "Tete Morente", "position": "FW", "number": 7, "nationality": "Spain"},
        {"name": "Remi Oudin", "position": "FW", "number": 10, "nationality": "France"},
        {"name": "Nicola Sansone", "position": "FW", "number": 19, "nationality": "Italy"},
        {"name": "Filip Marchwinski", "position": "FW", "number": 18, "nationality": "Poland"},
    ],
    "Como": [
        {"name": "Pepe Reina", "position": "GK", "number": 25, "nationality": "Spain"},
        {"name": "Jean Butez", "position": "GK", "number": 12, "nationality": "France"},
        {"name": "Alberto Dossena", "position": "DF", "number": 13, "nationality": "Italy"},
        {"name": "Marc-Oliver Kempf", "position": "DF", "number": 2, "nationality": "Germany"},
        {"name": "Edoardo Goldaniga", "position": "DF", "number": 5, "nationality": "Italy"},
        {"name": "Ignace Van der Brempt", "position": "DF", "number": 77, "nationality": "Belgium"},
        {"name": "Alberto Moreno", "position": "DF", "number": 18, "nationality": "Spain"},
        {"name": "Federico Barba", "position": "DF", "number": 93, "nationality": "Italy"},
        {"name": "Fellipe Jack", "position": "DF", "number": 4, "nationality": "Brazil"},
        {"name": "Alex Valle", "position": "DF", "number": 3, "nationality": "Spain"},
        {"name": "Matthias Braunoder", "position": "MF", "number": 23, "nationality": "Austria"},
        {"name": "Sergi Roberto", "position": "MF", "number": 20, "nationality": "Spain"},
        {"name": "Nico Paz", "position": "MF", "number": 10, "nationality": "Argentina"},
        {"name": "Yannik Engelhardt", "position": "MF", "number": 6, "nationality": "Germany"},
        {"name": "Lucas Da Cunha", "position": "MF", "number": 33, "nationality": "France"},
        {"name": "Maximo Perrone", "position": "MF", "number": 23, "nationality": "Argentina"},
        {"name": "Nicolas Kuhn", "position": "MF", "number": 11, "nationality": "Germany"},
        {"name": "Jayden Addai", "position": "MF", "number": 17, "nationality": "Ghana"},
        {"name": "Martin Baturina", "position": "MF", "number": 10, "nationality": "Croatia"},
        {"name": "Jesus Rodriguez", "position": "MF", "number": 14, "nationality": "Spain"},
        {"name": "Patrick Cutrone", "position": "FW", "number": 63, "nationality": "Italy"},
        {"name": "Alessio Iovine", "position": "FW", "number": 21, "nationality": "Italy"},
        {"name": "Gabriel Strefezza", "position": "FW", "number": 7, "nationality": "Brazil"},
        {"name": "Alessandro Gabrielloni", "position": "FW", "number": 9, "nationality": "Italy"},
        {"name": "Alvaro Morata", "position": "FW", "number": 9, "nationality": "Spain"},
    ],
    "Hellas Verona": [
        {"name": "Lorenzo Montipo", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Simone Perilli", "position": "GK", "number": 22, "nationality": "Italy"},
        {"name": "Alessandro Berardi", "position": "GK", "number": 34, "nationality": "Italy"},
        {"name": "Jackson Tchatchoua", "position": "DF", "number": 38, "nationality": "Cameroon"},
        {"name": "Pawel Dawidowicz", "position": "DF", "number": 27, "nationality": "Poland"},
        {"name": "Giangiacomo Magnani", "position": "DF", "number": 23, "nationality": "Italy"},
        {"name": "Diego Coppola", "position": "DF", "number": 42, "nationality": "Italy"},
        {"name": "Domagoj Bradaric", "position": "DF", "number": 12, "nationality": "Croatia"},
        {"name": "Flavius Daniliuc", "position": "DF", "number": 4, "nationality": "Austria"},
        {"name": "Mathis Lambourde", "position": "DF", "number": 18, "nationality": "France"},
        {"name": "Darko Lazovic", "position": "MF", "number": 8, "nationality": "Serbia"},
        {"name": "Ondrej Duda", "position": "MF", "number": 33, "nationality": "Slovakia"},
        {"name": "Reda Belahyane", "position": "MF", "number": 6, "nationality": "Morocco"},
        {"name": "Suat Serdar", "position": "MF", "number": 25, "nationality": "Germany"},
        {"name": "Tomas Suslov", "position": "MF", "number": 31, "nationality": "Slovakia"},
        {"name": "Abdou Harroui", "position": "MF", "number": 21, "nationality": "Morocco"},
        {"name": "Grigoris Kastanos", "position": "MF", "number": 20, "nationality": "Cyprus"},
        {"name": "Ayanda Sishuba", "position": "MF", "number": 35, "nationality": "South Africa"},
        {"name": "Casper Tengstedt", "position": "FW", "number": 11, "nationality": "Denmark"},
        {"name": "Daniel Mosquera", "position": "FW", "number": 9, "nationality": "Colombia"},
        {"name": "Amin Sarr", "position": "FW", "number": 14, "nationality": "Sweden"},
        {"name": "Dailon Livramento", "position": "FW", "number": 77, "nationality": "Cape Verde"},
    ],
    "Genoa": [
        {"name": "Pierluigi Gollini", "position": "GK", "number": 95, "nationality": "Italy"},
        {"name": "Nicola Leali", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Daniele Sommariva", "position": "GK", "number": 39, "nationality": "Italy"},
        {"name": "Alessandro Vogliacco", "position": "DF", "number": 14, "nationality": "Italy"},
        {"name": "Johan Vasquez", "position": "DF", "number": 22, "nationality": "Mexico"},
        {"name": "Mattia Bani", "position": "DF", "number": 13, "nationality": "Italy"},
        {"name": "Aaron Martin", "position": "DF", "number": 3, "nationality": "Spain"},
        {"name": "Stefano Sabelli", "position": "DF", "number": 20, "nationality": "Italy"},
        {"name": "Brooke Norton-Cuffy", "position": "DF", "number": 59, "nationality": "England"},
        {"name": "Alan Matturro", "position": "DF", "number": 33, "nationality": "Uruguay"},
        {"name": "Alessandro Zanoli", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Morten Frendrup", "position": "MF", "number": 32, "nationality": "Denmark"},
        {"name": "Milan Badelj", "position": "MF", "number": 47, "nationality": "Croatia"},
        {"name": "Morten Thorsby", "position": "MF", "number": 2, "nationality": "Norway"},
        {"name": "Ruslan Malinovskyi", "position": "MF", "number": 17, "nationality": "Ukraine"},
        {"name": "Fabio Miretti", "position": "MF", "number": 23, "nationality": "Italy"},
        {"name": "Patrizio Masini", "position": "MF", "number": 8, "nationality": "Italy"},
        {"name": "Vitinha", "position": "FW", "number": 9, "nationality": "Portugal"},
        {"name": "Jeff Ekhator", "position": "FW", "number": 18, "nationality": "Nigeria"},
        {"name": "Caleb Ekuban", "position": "FW", "number": 10, "nationality": "Ghana"},
        {"name": "Mario Balotelli", "position": "FW", "number": 45, "nationality": "Italy"},
    ],
    "Cremonese": [
        {"name": "Emil Audero", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Marco Silvestri", "position": "GK", "number": 16, "nationality": "Italy"},
        {"name": "Lapo Nava", "position": "GK", "number": 69, "nationality": "Italy"},
        {"name": "Mikayil Faye", "position": "DF", "number": 30, "nationality": "Senegal"},
        {"name": "Federico Baschirotto", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Matteo Bianchetti", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Federico Ceccherini", "position": "DF", "number": 23, "nationality": "Italy"},
        {"name": "Giuseppe Pezzella", "position": "DF", "number": 3, "nationality": "Italy"},
        {"name": "Leonardo Sernicola", "position": "DF", "number": 17, "nationality": "Italy"},
        {"name": "Filippo Terracciano", "position": "DF", "number": 24, "nationality": "Italy"},
        {"name": "Tommaso Barbieri", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Romano Floriani Mussolini", "position": "DF", "number": 22, "nationality": "Italy"},
        {"name": "Alberto Grassi", "position": "MF", "number": 33, "nationality": "Italy"},
        {"name": "Warren Bondo", "position": "MF", "number": 38, "nationality": "France"},
        {"name": "Martin Payero", "position": "MF", "number": 32, "nationality": "Argentina"},
        {"name": "Jari Vandeputte", "position": "MF", "number": 27, "nationality": "Belgium"},
        {"name": "Michele Collocolo", "position": "MF", "number": 18, "nationality": "Italy"},
        {"name": "Mattia Valoti", "position": "MF", "number": 8, "nationality": "Italy"},
        {"name": "Franco Vazquez", "position": "MF", "number": 20, "nationality": "Argentina"},
        {"name": "Jamie Vardy", "position": "FW", "number": 9, "nationality": "England"},
        {"name": "Federico Bonazzoli", "position": "FW", "number": 99, "nationality": "Italy"},
        {"name": "Antonio Sanabria", "position": "FW", "number": 19, "nationality": "Paraguay"},
        {"name": "Felix Afena-Gyan", "position": "FW", "number": 7, "nationality": "Ghana"},
        {"name": "Marco Nasti", "position": "FW", "number": 11, "nationality": "Italy"},
        {"name": "Frank Tsadjout", "position": "FW", "number": 74, "nationality": "Italy"},
    ],
    "Pisa": [
        {"name": "Nicolas", "position": "GK", "number": 1, "nationality": "Brazil"},
        {"name": "Adrian Semper", "position": "GK", "number": 47, "nationality": "Croatia"},
        {"name": "Simone Scuffet", "position": "GK", "number": 22, "nationality": "Italy"},
        {"name": "Raul Albiol", "position": "DF", "number": 33, "nationality": "Spain"},
        {"name": "Samuele Angori", "position": "DF", "number": 3, "nationality": "Italy"},
        {"name": "Giovanni Bonfanti", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Arturo Calabresi", "position": "DF", "number": 5, "nationality": "Italy"},
        {"name": "Simone Canestrelli", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Antonio Caracciolo", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Daniel Denoon", "position": "DF", "number": 12, "nationality": "USA"},
        {"name": "Tomas Esteves", "position": "DF", "number": 19, "nationality": "Portugal"},
        {"name": "Mateus Lusuardi", "position": "DF", "number": 30, "nationality": "Brazil"},
        {"name": "Jeremy Kandje Mbambi", "position": "DF", "number": 31, "nationality": "Switzerland"},
        {"name": "Juan Cuadrado", "position": "MF", "number": 11, "nationality": "Colombia"},
        {"name": "Michel Aebischer", "position": "MF", "number": 20, "nationality": "Switzerland"},
        {"name": "Ebenezer Akinsanmiro", "position": "MF", "number": 21, "nationality": "Nigeria"},
        {"name": "Malthe Hojholt", "position": "MF", "number": 8, "nationality": "Denmark"},
        {"name": "Mehdi Leris", "position": "MF", "number": 11, "nationality": "Algeria"},
        {"name": "Lorran", "position": "MF", "number": 10, "nationality": "Brazil"},
        {"name": "Marius Marin", "position": "MF", "number": 18, "nationality": "Romania"},
        {"name": "Gabriele Piccinini", "position": "MF", "number": 36, "nationality": "Italy"},
        {"name": "Idrissa Touré", "position": "MF", "number": 27, "nationality": "Germany"},
        {"name": "Matteo Tramoni", "position": "MF", "number": 17, "nationality": "France"},
        {"name": "Isak Vural", "position": "MF", "number": 25, "nationality": "Turkey"},
        {"name": "Calvin Stengs", "position": "FW", "number": 7, "nationality": "Netherlands"},
        {"name": "Louis Buffon", "position": "FW", "number": 28, "nationality": "France"},
        {"name": "Henrik Meister", "position": "FW", "number": 9, "nationality": "Denmark"},
        {"name": "Stefano Moreo", "position": "FW", "number": 32, "nationality": "Italy"},
        {"name": "M'Bala Nzola", "position": "FW", "number": 14, "nationality": "Angola"},
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
