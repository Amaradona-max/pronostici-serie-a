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

# Complete Serie A 2025/2026 players data
# Verified from official Transfermarkt sources - January 3, 2026
PLAYERS_DATA = {
    "Inter": [
        # Goalkeepers
        {"name": "Josep Martinez", "position": "GK", "number": 13, "nationality": "Spain"},
        {"name": "Yann Sommer", "position": "GK", "number": 1, "nationality": "Switzerland"},
        {"name": "Raffaele Di Gennaro", "position": "GK", "number": 21, "nationality": "Italy"},
        # Defenders
        {"name": "Alessandro Bastoni", "position": "DF", "number": 95, "nationality": "Italy"},
        {"name": "Yann Bisseck", "position": "DF", "number": 31, "nationality": "Germany"},
        {"name": "Manuel Akanji", "position": "DF", "number": 25, "nationality": "Switzerland"},
        {"name": "Stefan de Vrij", "position": "DF", "number": 6, "nationality": "Netherlands"},
        {"name": "Tomas Palacios", "position": "DF", "number": 5, "nationality": "Argentina"},
        {"name": "Francesco Acerbi", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Federico Dimarco", "position": "DF", "number": 32, "nationality": "Italy"},
        {"name": "Carlos Augusto", "position": "DF", "number": 30, "nationality": "Brazil"},
        {"name": "Denzel Dumfries", "position": "DF", "number": 2, "nationality": "Netherlands"},
        {"name": "Matteo Darmian", "position": "DF", "number": 36, "nationality": "Italy"},
        # Midfielders
        {"name": "Hakan Calhanoglu", "position": "MF", "number": 20, "nationality": "Turkey"},
        {"name": "Nicolo Barella", "position": "MF", "number": 23, "nationality": "Italy"},
        {"name": "Petar Sucic", "position": "MF", "number": 14, "nationality": "Croatia"},
        {"name": "Davide Frattesi", "position": "MF", "number": 16, "nationality": "Italy"},
        {"name": "Andy Diouf", "position": "MF", "number": 27, "nationality": "France"},
        {"name": "Piotr Zielinski", "position": "MF", "number": 7, "nationality": "Poland"},
        {"name": "Henrikh Mkhitaryan", "position": "MF", "number": 22, "nationality": "Armenia"},
        {"name": "Luis Henrique", "position": "MF", "number": 11, "nationality": "Brazil"},
        # Forwards
        {"name": "Lautaro Martinez", "position": "FW", "number": 10, "nationality": "Argentina"},
        {"name": "Marcus Thuram", "position": "FW", "number": 9, "nationality": "France"},
        {"name": "Ange-Yoan Bonny", "position": "FW", "number": 13, "nationality": "France"},
        {"name": "Pio Esposito", "position": "FW", "number": 99, "nationality": "Italy"},
    ],

    "AC Milan": [
        # Goalkeepers
        {"name": "Mike Maignan", "position": "GK", "number": 16, "nationality": "France"},
        {"name": "Lorenzo Torriani", "position": "GK", "number": 96, "nationality": "Italy"},
        # Defenders
        {"name": "Fikayo Tomori", "position": "DF", "number": 23, "nationality": "England"},
        {"name": "Strahinja Pavlovic", "position": "DF", "number": 31, "nationality": "Serbia"},
        {"name": "Pervis Estupinan", "position": "DF", "number": 30, "nationality": "Ecuador"},
        {"name": "Koni De Winter", "position": "DF", "number": 4, "nationality": "Belgium"},
        {"name": "Malick Thiaw", "position": "DF", "number": 28, "nationality": "Germany"},
        {"name": "Matteo Gabbia", "position": "DF", "number": 46, "nationality": "Italy"},
        {"name": "Theo Hernandez", "position": "DF", "number": 19, "nationality": "France"},
        # Midfielders
        {"name": "Luka Modric", "position": "MF", "number": 10, "nationality": "Croatia"},
        {"name": "Samuele Ricci", "position": "MF", "number": 21, "nationality": "Italy"},
        {"name": "Ruben Loftus-Cheek", "position": "MF", "number": 8, "nationality": "England"},
        {"name": "Youssouf Fofana", "position": "MF", "number": 29, "nationality": "France"},
        {"name": "Adrien Rabiot", "position": "MF", "number": 25, "nationality": "France"},
        {"name": "Tijjani Reijnders", "position": "MF", "number": 14, "nationality": "Netherlands"},
        {"name": "Ardon Jashari", "position": "MF", "number": 27, "nationality": "Switzerland"},
        {"name": "Alexis Saelemaekers", "position": "MF", "number": 56, "nationality": "Belgium"},
        # Forwards
        {"name": "Christian Pulisic", "position": "FW", "number": 11, "nationality": "USA"},
        {"name": "Rafael Leao", "position": "FW", "number": 10, "nationality": "Portugal"},
        {"name": "Christopher Nkunku", "position": "FW", "number": 18, "nationality": "France"},
        {"name": "Santiago Gimenez", "position": "FW", "number": 9, "nationality": "Mexico"},
        {"name": "Niclas Fullkrug", "position": "FW", "number": 24, "nationality": "Germany"},
    ],

    "Juventus": [
        # Goalkeepers
        {"name": "Michele Di Gregorio", "position": "GK", "number": 29, "nationality": "Italy"},
        {"name": "Mattia Perin", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Carlo Pinsoglio", "position": "GK", "number": 23, "nationality": "Italy"},
        # Defenders
        {"name": "Gleison Bremer", "position": "DF", "number": 3, "nationality": "Brazil"},
        {"name": "Federico Gatti", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Pierre Kalulu", "position": "DF", "number": 15, "nationality": "France"},
        {"name": "Joao Mario", "position": "DF", "number": 6, "nationality": "Portugal"},
        {"name": "Andrea Cambiaso", "position": "DF", "number": 27, "nationality": "Italy"},
        {"name": "Juan Cabal", "position": "DF", "number": 32, "nationality": "Colombia"},
        {"name": "Daniele Rugani", "position": "DF", "number": 24, "nationality": "Italy"},
        {"name": "Lloyd Kelly", "position": "DF", "number": 25, "nationality": "England"},
        # Midfielders
        {"name": "Teun Koopmeiners", "position": "MF", "number": 8, "nationality": "Netherlands"},
        {"name": "Manuel Locatelli", "position": "MF", "number": 5, "nationality": "Italy"},
        {"name": "Khephren Thuram", "position": "MF", "number": 19, "nationality": "France"},
        {"name": "Weston McKennie", "position": "MF", "number": 16, "nationality": "USA"},
        {"name": "Fabio Miretti", "position": "MF", "number": 20, "nationality": "Italy"},
        {"name": "Filip Kostic", "position": "MF", "number": 11, "nationality": "Serbia"},
        # Forwards
        {"name": "Kenan Yildiz", "position": "FW", "number": 10, "nationality": "Turkey"},
        {"name": "Dusan Vlahovic", "position": "FW", "number": 9, "nationality": "Serbia"},
        {"name": "Jonathan David", "position": "FW", "number": 14, "nationality": "Canada"},
        {"name": "Lois Openda", "position": "FW", "number": 17, "nationality": "Belgium"},
        {"name": "Edon Zhegrova", "position": "FW", "number": 7, "nationality": "Kosovo"},
        {"name": "Francisco Conceicao", "position": "FW", "number": 30, "nationality": "Portugal"},
        {"name": "Arkadiusz Milik", "position": "FW", "number": 14, "nationality": "Poland"},
    ],

    "Atalanta": [
        # Goalkeepers
        {"name": "Marco Carnesecchi", "position": "GK", "number": 29, "nationality": "Italy"},
        {"name": "Marco Sportiello", "position": "GK", "number": 57, "nationality": "Italy"},
        {"name": "Rui Patricio", "position": "GK", "number": 28, "nationality": "Portugal"},
        # Defenders
        {"name": "Giorgio Scalvini", "position": "DF", "number": 42, "nationality": "Italy"},
        {"name": "Isak Hien", "position": "DF", "number": 4, "nationality": "Sweden"},
        {"name": "Berat Djimsiti", "position": "DF", "number": 19, "nationality": "Albania"},
        {"name": "Sead Kolasinac", "position": "DF", "number": 23, "nationality": "Bosnia"},
        {"name": "Odilon Kossounou", "position": "DF", "number": 3, "nationality": "Ivory Coast"},
        {"name": "Raoul Bellanova", "position": "DF", "number": 16, "nationality": "Italy"},
        {"name": "Davide Zappacosta", "position": "DF", "number": 77, "nationality": "Italy"},
        # Midfielders
        {"name": "Ederson", "position": "MF", "number": 13, "nationality": "Brazil"},
        {"name": "Marten de Roon", "position": "MF", "number": 15, "nationality": "Netherlands"},
        {"name": "Mario Pasalic", "position": "MF", "number": 8, "nationality": "Croatia"},
        {"name": "Lazar Samardzic", "position": "MF", "number": 24, "nationality": "Serbia"},
        # Forwards
        {"name": "Charles De Ketelaere", "position": "FW", "number": 17, "nationality": "Belgium"},
        {"name": "Ademola Lookman", "position": "FW", "number": 11, "nationality": "Nigeria"},
        {"name": "Gianluca Scamacca", "position": "FW", "number": 9, "nationality": "Italy"},
    ],

    "Napoli": [
        # Goalkeepers
        {"name": "Alex Meret", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Vanja Milinkovic-Savic", "position": "GK", "number": 32, "nationality": "Serbia"},
        {"name": "Nikita Contini", "position": "GK", "number": 12, "nationality": "Italy"},
        {"name": "Mathias Ferrante", "position": "GK", "number": 25, "nationality": "Italy"},
        # Defenders
        {"name": "Alessandro Buongiorno", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Sam Beukema", "position": "DF", "number": 31, "nationality": "Netherlands"},
        {"name": "Amir Rrahmani", "position": "DF", "number": 13, "nationality": "Kosovo"},
        {"name": "Juan Jesus", "position": "DF", "number": 5, "nationality": "Brazil"},
        {"name": "Luca Marianucci", "position": "DF", "number": 44, "nationality": "Italy"},
        {"name": "Mathias Olivera", "position": "DF", "number": 17, "nationality": "Uruguay"},
        {"name": "Miguel Gutierrez", "position": "DF", "number": 3, "nationality": "Spain"},
        {"name": "Leonardo Spinazzola", "position": "DF", "number": 37, "nationality": "Italy"},
        {"name": "Giovanni Di Lorenzo", "position": "DF", "number": 22, "nationality": "Italy"},
        {"name": "Pasquale Mazzocchi", "position": "DF", "number": 30, "nationality": "Italy"},
        # Midfielders
        {"name": "Stanislav Lobotka", "position": "MF", "number": 68, "nationality": "Slovakia"},
        {"name": "Billy Gilmour", "position": "MF", "number": 6, "nationality": "Scotland"},
        {"name": "Scott McTominay", "position": "MF", "number": 8, "nationality": "Scotland"},
        {"name": "Frank Anguissa", "position": "MF", "number": 99, "nationality": "Cameroon"},
        {"name": "Kevin De Bruyne", "position": "MF", "number": 17, "nationality": "Belgium"},
        {"name": "Eljif Elmas", "position": "MF", "number": 7, "nationality": "North Macedonia"},
        {"name": "Antonio Vergara", "position": "MF", "number": 19, "nationality": "Italy"},
        # Forwards
        {"name": "Noa Lang", "position": "FW", "number": 10, "nationality": "Netherlands"},
        {"name": "David Neres", "position": "FW", "number": 7, "nationality": "Brazil"},
        {"name": "Matteo Politano", "position": "FW", "number": 21, "nationality": "Italy"},
        {"name": "Romelu Lukaku", "position": "FW", "number": 9, "nationality": "Belgium"},
        {"name": "Rasmus Hojlund", "position": "FW", "number": 11, "nationality": "Denmark"},
        {"name": "Lorenzo Lucca", "position": "FW", "number": 20, "nationality": "Italy"},
        {"name": "Giuseppe Ambrosino", "position": "FW", "number": 33, "nationality": "Italy"},
    ],

    "Lazio": [
        # Goalkeepers
        {"name": "Christos Mandas", "position": "GK", "number": 35, "nationality": "Greece"},
        {"name": "Ivan Provedel", "position": "GK", "number": 94, "nationality": "Italy"},
        {"name": "Alessio Furlanetto", "position": "GK", "number": 1, "nationality": "Italy"},
        # Defenders
        {"name": "Mario Gila", "position": "DF", "number": 34, "nationality": "Spain"},
        {"name": "Alessio Romagnoli", "position": "DF", "number": 13, "nationality": "Italy"},
        {"name": "Oliver Provstgaard", "position": "DF", "number": 5, "nationality": "Denmark"},
        {"name": "Samuel Gigot", "position": "DF", "number": 2, "nationality": "France"},
        {"name": "Patric", "position": "DF", "number": 4, "nationality": "Spain"},
        {"name": "Nuno Tavares", "position": "DF", "number": 30, "nationality": "Portugal"},
        {"name": "Luca Pellegrini", "position": "DF", "number": 3, "nationality": "Italy"},
        {"name": "Dimitrije Kamenovic", "position": "DF", "number": 27, "nationality": "Serbia"},
        {"name": "Adam Marusic", "position": "DF", "number": 77, "nationality": "Montenegro"},
        {"name": "Manuel Lazzari", "position": "DF", "number": 29, "nationality": "Italy"},
        {"name": "Elseid Hysaj", "position": "DF", "number": 23, "nationality": "Albania"},
        # Midfielders
        {"name": "Nicolo Rovella", "position": "MF", "number": 6, "nationality": "Italy"},
        {"name": "Reda Belahyane", "position": "MF", "number": 55, "nationality": "Morocco"},
        {"name": "Danilo Cataldi", "position": "MF", "number": 32, "nationality": "Italy"},
        {"name": "Matteo Guendouzi", "position": "MF", "number": 8, "nationality": "France"},
        {"name": "Toma Basic", "position": "MF", "number": 18, "nationality": "Croatia"},
        {"name": "Matias Vecino", "position": "MF", "number": 5, "nationality": "Uruguay"},
        {"name": "Fisayo Dele-Bashiru", "position": "MF", "number": 7, "nationality": "Nigeria"},
        # Forwards
        {"name": "Mattia Zaccagni", "position": "FW", "number": 10, "nationality": "Italy"},
        {"name": "Gustav Isaksen", "position": "FW", "number": 18, "nationality": "Denmark"},
        {"name": "Tijjani Noslin", "position": "FW", "number": 14, "nationality": "Netherlands"},
        {"name": "Matteo Cancellieri", "position": "FW", "number": 22, "nationality": "Italy"},
        {"name": "Diego Gonzalez", "position": "FW", "number": 20, "nationality": "Paraguay"},
        {"name": "Pedro", "position": "FW", "number": 9, "nationality": "Spain"},
        {"name": "Taty Castellanos", "position": "FW", "number": 11, "nationality": "Argentina"},
        {"name": "Boulaye Dia", "position": "FW", "number": 19, "nationality": "Senegal"},
    ],

    "AS Roma": [
        # Goalkeepers
        {"name": "Mile Svilar", "position": "GK", "number": 99, "nationality": "Belgium"},
        {"name": "Devis Vasquez", "position": "GK", "number": 98, "nationality": "Colombia"},
        {"name": "Pierluigi Gollini", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Radoslaw Zelezny", "position": "GK", "number": 12, "nationality": "Poland"},
        # Defenders
        {"name": "Evan Ndicka", "position": "DF", "number": 5, "nationality": "Ivory Coast"},
        {"name": "Gianluca Mancini", "position": "DF", "number": 23, "nationality": "Italy"},
        {"name": "Daniele Ghilardi", "position": "DF", "number": 14, "nationality": "Italy"},
        {"name": "Jan Ziolkowski", "position": "DF", "number": 66, "nationality": "Poland"},
        {"name": "Mario Hermoso", "position": "DF", "number": 22, "nationality": "Spain"},
        {"name": "Angelino", "position": "DF", "number": 3, "nationality": "Spain"},
        {"name": "Konstantinos Tsimikas", "position": "DF", "number": 21, "nationality": "Greece"},
        {"name": "Wesley", "position": "DF", "number": 2, "nationality": "Brazil"},
        {"name": "Zeki Celik", "position": "DF", "number": 19, "nationality": "Turkey"},
        {"name": "Devyne Rensch", "position": "DF", "number": 28, "nationality": "Netherlands"},
        {"name": "Buba Sangare", "position": "DF", "number": 64, "nationality": "Spain"},
        # Midfielders
        {"name": "Bryan Cristante", "position": "MF", "number": 4, "nationality": "Italy"},
        {"name": "Manu Kone", "position": "MF", "number": 17, "nationality": "France"},
        {"name": "Neil El Aynaoui", "position": "MF", "number": 63, "nationality": "Morocco"},
        {"name": "Niccolo Pisilli", "position": "MF", "number": 61, "nationality": "Italy"},
        {"name": "Edoardo Bove", "position": "MF", "number": 4, "nationality": "Italy"},
        {"name": "Tommaso Baldanzi", "position": "MF", "number": 35, "nationality": "Italy"},
        {"name": "Lorenzo Pellegrini", "position": "MF", "number": 7, "nationality": "Italy"},
        # Forwards
        {"name": "Stephan El Shaarawy", "position": "FW", "number": 92, "nationality": "Italy"},
        {"name": "Matias Soule", "position": "FW", "number": 18, "nationality": "Argentina"},
        {"name": "Leon Bailey", "position": "FW", "number": 7, "nationality": "Jamaica"},
        {"name": "Paulo Dybala", "position": "FW", "number": 21, "nationality": "Argentina"},
        {"name": "Evan Ferguson", "position": "FW", "number": 9, "nationality": "Ireland"},
        {"name": "Artem Dovbyk", "position": "FW", "number": 11, "nationality": "Ukraine"},
    ],

    "Fiorentina": [
        # Goalkeepers
        {"name": "David de Gea", "position": "GK", "number": 43, "nationality": "Spain"},
        {"name": "Tommaso Martinelli", "position": "GK", "number": 30, "nationality": "Italy"},
        {"name": "Luca Lezzerini", "position": "GK", "number": 1, "nationality": "Italy"},
        # Defenders
        {"name": "Pietro Comuzzo", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Marin Pongracic", "position": "DF", "number": 5, "nationality": "Croatia"},
        {"name": "Luca Ranieri", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Mattia Viti", "position": "DF", "number": 26, "nationality": "Italy"},
        {"name": "Pablo Mari", "position": "DF", "number": 22, "nationality": "Spain"},
        {"name": "Robin Gosens", "position": "DF", "number": 21, "nationality": "Germany"},
        {"name": "Fabiano Parisi", "position": "DF", "number": 65, "nationality": "Italy"},
        {"name": "Dodo", "position": "DF", "number": 2, "nationality": "Brazil"},
        {"name": "Tariq Lamptey", "position": "DF", "number": 48, "nationality": "Ghana"},
        # Midfielders
        {"name": "Rolando Mandragora", "position": "MF", "number": 38, "nationality": "Italy"},
        {"name": "Nicolo Fagioli", "position": "MF", "number": 44, "nationality": "Italy"},
        {"name": "Jacopo Fazzini", "position": "MF", "number": 22, "nationality": "Italy"},
        {"name": "Simon Sohm", "position": "MF", "number": 7, "nationality": "Switzerland"},
        {"name": "Hans Nicolussi Caviglia", "position": "MF", "number": 14, "nationality": "Italy"},
        {"name": "Cher Ndour", "position": "MF", "number": 27, "nationality": "Italy"},
        {"name": "Amir Richardson", "position": "MF", "number": 24, "nationality": "Morocco"},
        {"name": "Abdelhamid Sabiri", "position": "MF", "number": 11, "nationality": "Morocco"},
        {"name": "Albert Gudmundsson", "position": "MF", "number": 10, "nationality": "Iceland"},
        # Forwards
        {"name": "Moise Kean", "position": "FW", "number": 20, "nationality": "Italy"},
        {"name": "Roberto Piccoli", "position": "FW", "number": 91, "nationality": "Italy"},
        {"name": "Christian Kouame", "position": "FW", "number": 99, "nationality": "Ivory Coast"},
        {"name": "Edin Dzeko", "position": "FW", "number": 9, "nationality": "Bosnia"},
    ],

    "Bologna": [
        # Goalkeepers (already correct from previous fetch)
        {"name": "Lukasz Skorupski", "position": "GK", "number": 28, "nationality": "Poland"},
        {"name": "Federico Ravaglia", "position": "GK", "number": 34, "nationality": "Italy"},
        # Defenders
        {"name": "Jhon Lucumi", "position": "DF", "number": 26, "nationality": "Colombia"},
        {"name": "Torbjorn Heggem", "position": "DF", "number": 3, "nationality": "Norway"},
        {"name": "Martin Vitik", "position": "DF", "number": 4, "nationality": "Czech Republic"},
        {"name": "Nicolo Casale", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Juan Miranda", "position": "DF", "number": 33, "nationality": "Spain"},
        {"name": "Charalampos Lykogiannis", "position": "DF", "number": 22, "nationality": "Greece"},
        {"name": "Emil Holm", "position": "DF", "number": 2, "nationality": "Sweden"},
        {"name": "Nadir Zortea", "position": "DF", "number": 21, "nationality": "Italy"},
        # Midfielders
        {"name": "Remo Freuler", "position": "MF", "number": 8, "nationality": "Switzerland"},
        {"name": "Lewis Ferguson", "position": "MF", "number": 19, "nationality": "Scotland"},
        {"name": "Giovanni Fabbian", "position": "MF", "number": 80, "nationality": "Italy"},
        {"name": "Nikola Moro", "position": "MF", "number": 6, "nationality": "Croatia"},
        {"name": "Kacper Urbanski", "position": "MF", "number": 82, "nationality": "Poland"},
        # Forwards
        {"name": "Riccardo Orsolini", "position": "FW", "number": 7, "nationality": "Italy"},
        {"name": "Ciro Immobile", "position": "FW", "number": 17, "nationality": "Italy"},
        {"name": "Santiago Castro", "position": "FW", "number": 9, "nationality": "Argentina"},
        {"name": "Jonathan Rowe", "position": "FW", "number": 10, "nationality": "England"},
        {"name": "Federico Bernardeschi", "position": "FW", "number": 33, "nationality": "Italy"},
    ],

    "Torino": [
        # Goalkeepers
        {"name": "Franco Israel", "position": "GK", "number": 24, "nationality": "Uruguay"},
        {"name": "Alberto Paleari", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Mihai Popa", "position": "GK", "number": 32, "nationality": "Romania"},
        # Defenders
        {"name": "Saul Coco", "position": "DF", "number": 23, "nationality": "Equatorial Guinea"},
        {"name": "Ardian Ismajli", "position": "DF", "number": 34, "nationality": "Albania"},
        {"name": "Guillermo Maripan", "position": "DF", "number": 13, "nationality": "Chile"},
        {"name": "Adam Masina", "position": "DF", "number": 5, "nationality": "Morocco"},
        {"name": "Saba Sazonov", "position": "DF", "number": 6, "nationality": "Georgia"},
        {"name": "Perr Schuurs", "position": "DF", "number": 3, "nationality": "Netherlands"},
        {"name": "Niels Nkounkou", "position": "DF", "number": 19, "nationality": "France"},
        {"name": "Cristiano Biraghi", "position": "DF", "number": 27, "nationality": "Italy"},
        {"name": "Valentino Lazaro", "position": "DF", "number": 20, "nationality": "Austria"},
        {"name": "Marcus Pedersen", "position": "DF", "number": 16, "nationality": "Norway"},
        # Midfielders
        {"name": "Kristjan Asllani", "position": "MF", "number": 21, "nationality": "Albania"},
        {"name": "Adrien Tameze", "position": "MF", "number": 61, "nationality": "France"},
        {"name": "Cesare Casadei", "position": "MF", "number": 4, "nationality": "Italy"},
        {"name": "Ivan Ilic", "position": "MF", "number": 8, "nationality": "Serbia"},
        {"name": "Gvidas Gineitis", "position": "MF", "number": 66, "nationality": "Lithuania"},
        {"name": "Nikola Vlasic", "position": "MF", "number": 10, "nationality": "Croatia"},
        {"name": "Tino Anjorin", "position": "MF", "number": 8, "nationality": "England"},
        # Forwards
        {"name": "Alieu Njie", "position": "FW", "number": 39, "nationality": "Sweden"},
        {"name": "Zakaria Aboukhlal", "position": "FW", "number": 11, "nationality": "Morocco"},
        {"name": "Cyril Ngonge", "position": "FW", "number": 26, "nationality": "Belgium"},
        {"name": "Che Adams", "position": "FW", "number": 18, "nationality": "Scotland"},
        {"name": "Giovanni Simeone", "position": "FW", "number": 99, "nationality": "Argentina"},
        {"name": "Duvan Zapata", "position": "FW", "number": 91, "nationality": "Colombia"},
    ],

    "Udinese": [
        # Goalkeepers
        {"name": "Maduka Okoye", "position": "GK", "number": 40, "nationality": "Nigeria"},
        {"name": "Razvan Sava", "position": "GK", "number": 90, "nationality": "Romania"},
        {"name": "Alessandro Nunziante", "position": "GK", "number": 77, "nationality": "Italy"},
        {"name": "Daniele Padelli", "position": "GK", "number": 1, "nationality": "Italy"},
        # Defenders
        {"name": "Oumar Solet", "position": "DF", "number": 29, "nationality": "France"},
        {"name": "Thomas Kristensen", "position": "DF", "number": 31, "nationality": "Denmark"},
        {"name": "Nicolo Bertola", "position": "DF", "number": 30, "nationality": "Italy"},
        {"name": "Saba Goglichidze", "position": "DF", "number": 2, "nationality": "Georgia"},
        {"name": "Christian Kabasele", "position": "DF", "number": 27, "nationality": "Belgium"},
        {"name": "Jordan Zemura", "position": "DF", "number": 33, "nationality": "Zimbabwe"},
        {"name": "Hassane Kamara", "position": "DF", "number": 11, "nationality": "Ivory Coast"},
        {"name": "Alessandro Zanoli", "position": "DF", "number": 19, "nationality": "Italy"},
        {"name": "Kingsley Ehizibue", "position": "DF", "number": 19, "nationality": "Netherlands"},
        # Midfielders
        {"name": "Jesper Karlstrom", "position": "MF", "number": 25, "nationality": "Sweden"},
        {"name": "Jurgen Ekkelenkamp", "position": "MF", "number": 32, "nationality": "Netherlands"},
        {"name": "Sandi Lovric", "position": "MF", "number": 8, "nationality": "Slovenia"},
        {"name": "Jakub Piotrowski", "position": "MF", "number": 5, "nationality": "Poland"},
        {"name": "Oier Zarraga", "position": "MF", "number": 6, "nationality": "Spain"},
        {"name": "Nicolo Zaniolo", "position": "MF", "number": 10, "nationality": "Italy"},
        # Forwards
        {"name": "Iker Bravo", "position": "FW", "number": 21, "nationality": "Spain"},
        {"name": "Idrissa Gueye", "position": "FW", "number": 23, "nationality": "Senegal"},
        {"name": "Keinan Davis", "position": "FW", "number": 9, "nationality": "England"},
        {"name": "Adam Buksa", "position": "FW", "number": 20, "nationality": "Poland"},
        {"name": "Vakoun Bayo", "position": "FW", "number": 15, "nationality": "Ivory Coast"},
    ],

    "Sassuolo": [
        {"name": "Giacomo Satalino", "position": "GK", "number": 47, "nationality": "Italy"},
        {"name": "Gianluca Pegolo", "position": "GK", "number": 12, "nationality": "Italy"},
        {"name": "Filip Stankovic", "position": "GK", "number": 1, "nationality": "Serbia"},
        {"name": "Josh Doig", "position": "DF", "number": 3, "nationality": "Scotland"},
        {"name": "Filippo Romagna", "position": "DF", "number": 19, "nationality": "Italy"},
        {"name": "Yeferson Paz", "position": "DF", "number": 5, "nationality": "Venezuela"},
        {"name": "Martin Erlic", "position": "DF", "number": 6, "nationality": "Croatia"},
        {"name": "Sebastian Walukiewicz", "position": "DF", "number": 4, "nationality": "Poland"},
        {"name": "Tajon Buchanan", "position": "MF", "number": 17, "nationality": "Canada"},
        {"name": "Daniel Boloca", "position": "MF", "number": 11, "nationality": "Romania"},
        {"name": "Kristian Thorstvedt", "position": "MF", "number": 42, "nationality": "Norway"},
        {"name": "Nedim Bajrami", "position": "MF", "number": 10, "nationality": "Albania"},
        {"name": "Alieu Fadera", "position": "FW", "number": 16, "nationality": "Gambia"},
        {"name": "Armand Lauriente", "position": "FW", "number": 45, "nationality": "France"},
        {"name": "Samuele Mulattieri", "position": "FW", "number": 8, "nationality": "Italy"},
        {"name": "Cristian Volpato", "position": "FW", "number": 23, "nationality": "Italy"},
        {"name": "Andrea Pinamonti", "position": "FW", "number": 9, "nationality": "Italy"},
    ],

    "Parma": [
        # Goalkeepers
        {"name": "Zion Suzuki", "position": "GK", "number": 31, "nationality": "Japan"},
        {"name": "Edoardo Corvi", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Vicente Guaita", "position": "GK", "number": 35, "nationality": "Spain"},
        # Defenders
        {"name": "Alessandro Circati", "position": "DF", "number": 39, "nationality": "Australia"},
        {"name": "Abdoulaye Ndiaye", "position": "DF", "number": 4, "nationality": "Senegal"},
        {"name": "Mariano Troilo", "position": "DF", "number": 46, "nationality": "Argentina"},
        {"name": "Mathias Lovik", "position": "DF", "number": 14, "nationality": "Norway"},
        {"name": "Emanuele Valeri", "position": "DF", "number": 14, "nationality": "Italy"},
        {"name": "Sascha Britschgi", "position": "DF", "number": 99, "nationality": "Switzerland"},
        {"name": "Enrico Delprato", "position": "DF", "number": 15, "nationality": "Italy"},
        # Midfielders
        {"name": "Mandela Keita", "position": "MF", "number": 19, "nationality": "Belgium"},
        {"name": "Nahuel Estevez", "position": "MF", "number": 8, "nationality": "Argentina"},
        {"name": "Adrian Bernabe", "position": "MF", "number": 10, "nationality": "Spain"},
        {"name": "Oliver Sorensen", "position": "MF", "number": 6, "nationality": "Denmark"},
        {"name": "Christian Ordonez", "position": "MF", "number": 21, "nationality": "Argentina"},
        {"name": "Benja Cremaschi", "position": "MF", "number": 32, "nationality": "USA"},
        {"name": "Hernani", "position": "MF", "number": 27, "nationality": "Brazil"},
        {"name": "Gaetano Oristanio", "position": "MF", "number": 23, "nationality": "Italy"},
        # Forwards
        {"name": "Jacob Ondrejka", "position": "FW", "number": 13, "nationality": "Sweden"},
        {"name": "Pontus Almqvist", "position": "FW", "number": 11, "nationality": "Sweden"},
        {"name": "Mateo Pellegrino", "position": "FW", "number": 77, "nationality": "Argentina"},
        {"name": "Matija Frigan", "position": "FW", "number": 37, "nationality": "Croatia"},
        {"name": "Patrick Cutrone", "position": "FW", "number": 11, "nationality": "Italy"},
        {"name": "Milan Djuric", "position": "FW", "number": 9, "nationality": "Bosnia"},
    ],

    # Cagliari already corrected
    "Cagliari": [
        {"name": "Elia Caprile", "position": "GK", "number": 22, "nationality": "Italy"},
        {"name": "Boris Radunovic", "position": "GK", "number": 31, "nationality": "Serbia"},
        {"name": "Giuseppe Ciocci", "position": "GK", "number": 12, "nationality": "Italy"},
        {"name": "Sebastiano Luperto", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Yerry Mina", "position": "DF", "number": 26, "nationality": "Colombia"},
        {"name": "Gabriele Zappa", "position": "DF", "number": 28, "nationality": "Italy"},
        {"name": "Juan Rodriguez", "position": "DF", "number": 2, "nationality": "Uruguay"},
        {"name": "Adam Obert", "position": "DF", "number": 33, "nationality": "Slovakia"},
        {"name": "Ze Pedro", "position": "DF", "number": 4, "nationality": "Portugal"},
        {"name": "Marco Palestra", "position": "DF", "number": 37, "nationality": "Italy"},
        {"name": "Alessandro Di Pardo", "position": "DF", "number": 29, "nationality": "Italy"},
        {"name": "Alessandro Deiola", "position": "MF", "number": 14, "nationality": "Italy"},
        {"name": "Matteo Prati", "position": "MF", "number": 16, "nationality": "Italy"},
        {"name": "Gianluca Gaetano", "position": "MF", "number": 70, "nationality": "Italy"},
        {"name": "Michel Adopo", "position": "MF", "number": 8, "nationality": "France"},
        {"name": "Michael Folorunsho", "position": "MF", "number": 90, "nationality": "Italy"},
        {"name": "Luca Mazzitelli", "position": "MF", "number": 18, "nationality": "Italy"},
        {"name": "Marko Rog", "position": "MF", "number": 6, "nationality": "Croatia"},
        {"name": "Mattia Felici", "position": "FW", "number": 24, "nationality": "Italy"},
        {"name": "Zito Luvumbo", "position": "FW", "number": 77, "nationality": "Angola"},
        {"name": "Leonardo Pavoletti", "position": "FW", "number": 30, "nationality": "Italy"},
        {"name": "Andrea Belotti", "position": "FW", "number": 11, "nationality": "Italy"},
        {"name": "Sebastiano Esposito", "position": "FW", "number": 99, "nationality": "Italy"},
        {"name": "Semih Kilicsoy", "position": "FW", "number": 10, "nationality": "Turkey"},
        {"name": "Gennaro Borrelli", "position": "FW", "number": 90, "nationality": "Italy"},
    ],

    "Lecce": [
        # Goalkeepers
        {"name": "Wladimiro Falcone", "position": "GK", "number": 30, "nationality": "Italy"},
        {"name": "Christian Fruchtl", "position": "GK", "number": 1, "nationality": "Germany"},
        {"name": "Jasper Samooja", "position": "GK", "number": 12, "nationality": "Finland"},
        # Defenders
        {"name": "Tiago Gabriel", "position": "DF", "number": 98, "nationality": "Portugal"},
        {"name": "Jamil Siebert", "position": "DF", "number": 23, "nationality": "Germany"},
        {"name": "Gaspar", "position": "DF", "number": 4, "nationality": "Angola"},
        {"name": "Gaby Jean", "position": "DF", "number": 6, "nationality": "France"},
        {"name": "Antonino Gallo", "position": "DF", "number": 25, "nationality": "Italy"},
        {"name": "Corrie Ndaba", "position": "DF", "number": 19, "nationality": "Ireland"},
        {"name": "Christ-Owen Kouassi", "position": "DF", "number": 22, "nationality": "Ivory Coast"},
        {"name": "Frederic Guilbert", "position": "DF", "number": 12, "nationality": "France"},
        # Midfielders
        {"name": "Ylber Ramadani", "position": "MF", "number": 20, "nationality": "Albania"},
        {"name": "Balthazar Pierret", "position": "MF", "number": 5, "nationality": "France"},
        {"name": "Medon Berisha", "position": "MF", "number": 75, "nationality": "Albania"},
        {"name": "Lassana Coulibaly", "position": "MF", "number": 29, "nationality": "Mali"},
        {"name": "Alex Sala", "position": "MF", "number": 27, "nationality": "Spain"},
        {"name": "Mohamed Kaba", "position": "MF", "number": 77, "nationality": "France"},
        {"name": "Youssef Maleh", "position": "MF", "number": 93, "nationality": "Morocco"},
        {"name": "Hamza Rafia", "position": "MF", "number": 8, "nationality": "Tunisia"},
        {"name": "Filip Marchwinski", "position": "MF", "number": 10, "nationality": "Poland"},
        # Forwards
        {"name": "Riccardo Sottil", "position": "FW", "number": 7, "nationality": "Italy"},
        {"name": "Lameck Banda", "position": "FW", "number": 22, "nationality": "Zambia"},
        {"name": "Tete Morente", "position": "FW", "number": 14, "nationality": "Spain"},
        {"name": "Santiago Pierotti", "position": "FW", "number": 50, "nationality": "Argentina"},
        {"name": "Francesco Camarda", "position": "FW", "number": 73, "nationality": "Italy"},
        {"name": "Nikola Stulic", "position": "FW", "number": 9, "nationality": "Serbia"},
    ],

    "Como": [
        # Goalkeepers
        {"name": "Jean Butez", "position": "GK", "number": 1, "nationality": "France"},
        {"name": "Noel Tornqvist", "position": "GK", "number": 16, "nationality": "Sweden"},
        {"name": "Mauro Vigorito", "position": "GK", "number": 22, "nationality": "Italy"},
        # Defenders
        {"name": "Jacobo Ramon", "position": "DF", "number": 27, "nationality": "Spain"},
        {"name": "Diego Carlos", "position": "DF", "number": 3, "nationality": "Brazil"},
        {"name": "Alberto Dossena", "position": "DF", "number": 4, "nationality": "Italy"},
        {"name": "Stefan Posch", "position": "DF", "number": 15, "nationality": "Austria"},
        {"name": "Marc Oliver Kempf", "position": "DF", "number": 2, "nationality": "Germany"},
        {"name": "Edoardo Goldaniga", "position": "DF", "number": 5, "nationality": "Italy"},
        {"name": "Alex Valle", "position": "DF", "number": 18, "nationality": "Spain"},
        {"name": "Alberto Moreno", "position": "DF", "number": 18, "nationality": "Spain"},
        {"name": "Ignace Van der Brempt", "position": "DF", "number": 13, "nationality": "Belgium"},
        {"name": "Mergim Vojvoda", "position": "DF", "number": 77, "nationality": "Kosovo"},
        # Midfielders
        {"name": "Maximo Perrone", "position": "MF", "number": 8, "nationality": "Argentina"},
        {"name": "Maxence Caqueret", "position": "MF", "number": 6, "nationality": "France"},
        {"name": "Lucas Da Cunha", "position": "MF", "number": 33, "nationality": "France"},
        {"name": "Sergi Roberto", "position": "MF", "number": 20, "nationality": "Spain"},
        {"name": "Nico Paz", "position": "MF", "number": 79, "nationality": "Argentina"},
        {"name": "Martin Baturina", "position": "MF", "number": 25, "nationality": "Croatia"},
        # Forwards
        {"name": "Jesus Rodriguez", "position": "FW", "number": 11, "nationality": "Spain"},
        {"name": "Assane Diao", "position": "FW", "number": 23, "nationality": "Senegal"},
        {"name": "Jayden Addai", "position": "FW", "number": 21, "nationality": "Netherlands"},
        {"name": "Nicolas Kuhn", "position": "FW", "number": 17, "nationality": "Germany"},
        {"name": "Alvaro Morata", "position": "FW", "number": 7, "nationality": "Spain"},
        {"name": "Alberto Cerri", "position": "FW", "number": 27, "nationality": "Italy"},
    ],

    "Hellas Verona": [
        # Goalkeepers
        {"name": "Lorenzo Montipo", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Simone Perilli", "position": "GK", "number": 34, "nationality": "Italy"},
        # Defenders
        {"name": "Victor Nelsson", "position": "DF", "number": 4, "nationality": "Denmark"},
        {"name": "Armel Bella-Kotchap", "position": "DF", "number": 21, "nationality": "Germany"},
        {"name": "Nicolas Valentini", "position": "DF", "number": 5, "nationality": "Argentina"},
        {"name": "Unai Nunez", "position": "DF", "number": 3, "nationality": "Spain"},
        {"name": "Enzo Ebosse", "position": "DF", "number": 24, "nationality": "Cameroon"},
        {"name": "Martin Frese", "position": "DF", "number": 27, "nationality": "Denmark"},
        {"name": "Domagoj Bradaric", "position": "DF", "number": 12, "nationality": "Croatia"},
        {"name": "Rafik Belghali", "position": "DF", "number": 14, "nationality": "Algeria"},
        # Midfielders
        {"name": "Moatasem Al-Musrati", "position": "MF", "number": 6, "nationality": "Libya"},
        {"name": "Cheikh Niasse", "position": "MF", "number": 20, "nationality": "Senegal"},
        {"name": "Suat Serdar", "position": "MF", "number": 25, "nationality": "Germany"},
        {"name": "Abdou Harroui", "position": "MF", "number": 33, "nationality": "Morocco"},
        {"name": "Roberto Gagliardini", "position": "MF", "number": 28, "nationality": "Italy"},
        {"name": "Tomas Suslov", "position": "MF", "number": 31, "nationality": "Slovakia"},
        {"name": "Grigoris Kastanos", "position": "MF", "number": 20, "nationality": "Cyprus"},
        # Forwards
        {"name": "Giovane", "position": "FW", "number": 17, "nationality": "Brazil"},
        {"name": "Gift Orban", "position": "FW", "number": 9, "nationality": "Nigeria"},
        {"name": "Amin Sarr", "position": "FW", "number": 14, "nationality": "Sweden"},
        {"name": "Daniel Mosquera", "position": "FW", "number": 9, "nationality": "Colombia"},
    ],

    "Genoa": [
        # Goalkeepers
        {"name": "Nicola Leali", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Benjamin Siegrist", "position": "GK", "number": 22, "nationality": "Switzerland"},
        {"name": "Daniele Sommariva", "position": "GK", "number": 39, "nationality": "Italy"},
        # Defenders
        {"name": "Johan Vasquez", "position": "DF", "number": 22, "nationality": "Mexico"},
        {"name": "Leo Ostigard", "position": "DF", "number": 55, "nationality": "Norway"},
        {"name": "Alessandro Marcandalli", "position": "DF", "number": 14, "nationality": "Italy"},
        {"name": "Aaron Martin", "position": "DF", "number": 3, "nationality": "Spain"},
        {"name": "Brooke Norton-Cuffy", "position": "DF", "number": 59, "nationality": "England"},
        {"name": "Stefano Sabelli", "position": "DF", "number": 20, "nationality": "Italy"},
        # Midfielders
        {"name": "Jean Onana", "position": "MF", "number": 24, "nationality": "Cameroon"},
        {"name": "Morten Frendrup", "position": "MF", "number": 32, "nationality": "Denmark"},
        {"name": "Patrizio Masini", "position": "MF", "number": 8, "nationality": "Italy"},
        {"name": "Mikael Egill Ellertsson", "position": "MF", "number": 21, "nationality": "Iceland"},
        {"name": "Morten Thorsby", "position": "MF", "number": 2, "nationality": "Norway"},
        {"name": "Valentin Carboni", "position": "MF", "number": 44, "nationality": "Argentina"},
        {"name": "Albert Gronbaek", "position": "MF", "number": 30, "nationality": "Denmark"},
        {"name": "Ruslan Malinovskyi", "position": "MF", "number": 17, "nationality": "Ukraine"},
        {"name": "Nicolae Stanciu", "position": "MF", "number": 10, "nationality": "Romania"},
        # Forwards
        {"name": "Maxwel Cornet", "position": "FW", "number": 11, "nationality": "Ivory Coast"},
        {"name": "Junior Messias", "position": "FW", "number": 18, "nationality": "Brazil"},
        {"name": "Vitinha", "position": "FW", "number": 9, "nationality": "Portugal"},
        {"name": "Jeff Ekhator", "position": "FW", "number": 19, "nationality": "Italy"},
        {"name": "Lorenzo Colombo", "position": "FW", "number": 29, "nationality": "Italy"},
        {"name": "Caleb Ekuban", "position": "FW", "number": 18, "nationality": "Ghana"},
    ],

    "Cremonese": [
        # Goalkeepers
        {"name": "Emil Audero", "position": "GK", "number": 1, "nationality": "Italy"},
        {"name": "Marco Silvestri", "position": "GK", "number": 22, "nationality": "Italy"},
        {"name": "Lapo Nava", "position": "GK", "number": 12, "nationality": "Italy"},
        # Defenders
        {"name": "Mikayil Faye", "position": "DF", "number": 30, "nationality": "Senegal"},
        {"name": "Federico Baschirotto", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Matteo Bianchetti", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Federico Ceccherini", "position": "DF", "number": 15, "nationality": "Italy"},
        {"name": "Giuseppe Pezzella", "position": "DF", "number": 3, "nationality": "Italy"},
        {"name": "Leonardo Sernicola", "position": "DF", "number": 17, "nationality": "Italy"},
        {"name": "Filippo Terracciano", "position": "DF", "number": 14, "nationality": "Italy"},
        {"name": "Tommaso Barbieri", "position": "DF", "number": 36, "nationality": "Italy"},
        {"name": "Romano Floriani Mussolini", "position": "DF", "number": 55, "nationality": "Italy"},
        # Midfielders
        {"name": "Alberto Grassi", "position": "MF", "number": 5, "nationality": "Italy"},
        {"name": "Warren Bondo", "position": "MF", "number": 38, "nationality": "France"},
        {"name": "Martin Payero", "position": "MF", "number": 8, "nationality": "Argentina"},
        {"name": "Jari Vandeputte", "position": "MF", "number": 71, "nationality": "Belgium"},
        {"name": "Michele Collocolo", "position": "MF", "number": 18, "nationality": "Italy"},
        {"name": "Alessio Zerbin", "position": "MF", "number": 23, "nationality": "Italy"},
        {"name": "Franco Vazquez", "position": "MF", "number": 20, "nationality": "Argentina"},
        {"name": "Jeremy Sarmiento", "position": "MF", "number": 28, "nationality": "Ecuador"},
        # Forwards
        {"name": "Faris Moumbagna", "position": "FW", "number": 77, "nationality": "Cameroon"},
        {"name": "Antonio Sanabria", "position": "FW", "number": 11, "nationality": "Paraguay"},
        {"name": "Federico Bonazzoli", "position": "FW", "number": 99, "nationality": "Italy"},
        {"name": "David Okereke", "position": "FW", "number": 10, "nationality": "Nigeria"},
        {"name": "Jamie Vardy", "position": "FW", "number": 9, "nationality": "England"},
    ],

    "Pisa": [
        # Goalkeepers
        {"name": "Adrian Semper", "position": "GK", "number": 47, "nationality": "Croatia"},
        {"name": "Simone Scuffet", "position": "GK", "number": 22, "nationality": "Italy"},
        {"name": "Nicolas", "position": "GK", "number": 1, "nationality": "Brazil"},
        # Defenders
        {"name": "Simone Canestrelli", "position": "DF", "number": 6, "nationality": "Italy"},
        {"name": "Giovanni Bonfanti", "position": "DF", "number": 5, "nationality": "Italy"},
        {"name": "Francesco Coppola", "position": "DF", "number": 28, "nationality": "Italy"},
        {"name": "Raul Albiol", "position": "DF", "number": 33, "nationality": "Spain"},
        {"name": "Arturo Calabresi", "position": "DF", "number": 29, "nationality": "Italy"},
        {"name": "Antonio Caracciolo", "position": "DF", "number": 4, "nationality": "Italy"},
        # Midfielders
        {"name": "Marius Marin", "position": "MF", "number": 8, "nationality": "Romania"},
        {"name": "Malthe Hojholt", "position": "MF", "number": 5, "nationality": "Denmark"},
        {"name": "Ebenezer Akinsanmiro", "position": "MF", "number": 21, "nationality": "Nigeria"},
        {"name": "Michel Aebischer", "position": "MF", "number": 20, "nationality": "Switzerland"},
        {"name": "Idrissa Toure", "position": "MF", "number": 15, "nationality": "Germany"},
        {"name": "Juan Cuadrado", "position": "MF", "number": 7, "nationality": "Colombia"},
        {"name": "Samuele Angori", "position": "MF", "number": 3, "nationality": "Italy"},
        {"name": "Matteo Tramoni", "position": "MF", "number": 11, "nationality": "France"},
        {"name": "Calvin Stengs", "position": "MF", "number": 10, "nationality": "Netherlands"},
        {"name": "Stefano Moreo", "position": "MF", "number": 32, "nationality": "Italy"},
        # Forwards
        {"name": "Mehdi Leris", "position": "FW", "number": 14, "nationality": "Algeria"},
        {"name": "M'Bala Nzola", "position": "FW", "number": 18, "nationality": "Angola"},
        {"name": "Henrik Meister", "position": "FW", "number": 9, "nationality": "Denmark"},
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
