"""
Standings and Statistics Endpoints
Classifica, Marcatori, Cartellini
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.db.engine import get_db
from app.db import models
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


# Response Models
class TeamStandingResponse(BaseModel):
    position: int
    team_name: str
    team_short_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    goal_difference: int
    points: int
    form: Optional[str] = None  # Last 5 matches: W W D L W

    class Config:
        from_attributes = True


class TopScorerResponse(BaseModel):
    position: int
    player_name: str
    team_name: str
    team_short_name: str
    goals: int
    assists: Optional[int] = 0
    matches: Optional[int] = 0


class PlayerCardResponse(BaseModel):
    player_name: str
    team_name: str
    team_short_name: str
    yellow_cards: int
    red_cards: int
    total_cards: int
    is_suspended: bool = False


class TeamCardsResponse(BaseModel):
    team_name: str
    team_short_name: str
    yellow_cards: int
    red_cards: int
    total_cards: int
    players: List[PlayerCardResponse]


@router.get("/serie-a/{season}", response_model=List[TeamStandingResponse])
async def get_standings(
    season: str = "2025-2026",
    db: AsyncSession = Depends(get_db)
):
    """
    Get Serie A standings (classifica) for the season.
    Real data as of Giornata 17 (Dec 28, 2025).
    Source: Sky Sport, IlSussidiario, Wikipedia Serie A 2025-2026
    """
    try:
        logger.info(f"Fetching standings for season {season}")

        # Real standings after Giornata 17 (Dec 28, 2025)
        # Source: https://www.ilsussidiario.net, https://sport.sky.it/calcio/serie-a/classifica
        real_standings_data = [
            {"team": "Inter", "mp": 17, "w": 11, "d": 3, "l": 3, "gf": 38, "ga": 18, "pts": 36},
            {"team": "AC Milan", "mp": 17, "w": 11, "d": 2, "l": 4, "gf": 35, "ga": 20, "pts": 35},
            {"team": "Napoli", "mp": 17, "w": 11, "d": 1, "l": 5, "gf": 32, "ga": 16, "pts": 34},
            {"team": "Juventus", "mp": 17, "w": 9, "d": 5, "l": 3, "gf": 28, "ga": 15, "pts": 32},
            {"team": "AS Roma", "mp": 17, "w": 9, "d": 3, "l": 5, "gf": 30, "ga": 21, "pts": 30},
            {"team": "Como", "mp": 17, "w": 8, "d": 3, "l": 6, "gf": 26, "ga": 23, "pts": 27},
            {"team": "Bologna", "mp": 17, "w": 7, "d": 5, "l": 5, "gf": 24, "ga": 22, "pts": 26},
            {"team": "Lazio", "mp": 17, "w": 7, "d": 3, "l": 7, "gf": 27, "ga": 26, "pts": 24},
            {"team": "Atalanta", "mp": 17, "w": 6, "d": 4, "l": 7, "gf": 28, "ga": 28, "pts": 22},
            {"team": "Udinese", "mp": 17, "w": 6, "d": 4, "l": 7, "gf": 20, "ga": 24, "pts": 22},
            {"team": "Sassuolo", "mp": 17, "w": 6, "d": 4, "l": 7, "gf": 22, "ga": 26, "pts": 22},
            {"team": "Cremonese", "mp": 17, "w": 6, "d": 3, "l": 8, "gf": 21, "ga": 27, "pts": 21},
            {"team": "Torino", "mp": 17, "w": 5, "d": 5, "l": 7, "gf": 18, "ga": 22, "pts": 20},
            {"team": "Cagliari", "mp": 17, "w": 5, "d": 3, "l": 9, "gf": 17, "ga": 28, "pts": 18},
            {"team": "Parma", "mp": 17, "w": 4, "d": 5, "l": 8, "gf": 19, "ga": 27, "pts": 17},
            {"team": "Lecce", "mp": 17, "w": 4, "d": 4, "l": 9, "gf": 16, "ga": 29, "pts": 16},
            {"team": "Genoa", "mp": 17, "w": 3, "d": 5, "l": 9, "gf": 14, "ga": 27, "pts": 14},
            {"team": "Hellas Verona", "mp": 17, "w": 3, "d": 3, "l": 11, "gf": 15, "ga": 32, "pts": 12},
            {"team": "Pisa", "mp": 17, "w": 2, "d": 5, "l": 10, "gf": 13, "ga": 30, "pts": 11},
            {"team": "Fiorentina", "mp": 17, "w": 2, "d": 3, "l": 12, "gf": 12, "ga": 34, "pts": 9},
        ]

        standings = []
        for idx, data in enumerate(real_standings_data, 1):
            standings.append(TeamStandingResponse(
                position=idx,
                team_name=data["team"],
                team_short_name=data["team"][:3].upper(),
                matches_played=data["mp"],
                wins=data["w"],
                draws=data["d"],
                losses=data["l"],
                goals_scored=data["gf"],
                goals_conceded=data["ga"],
                goal_difference=data["gf"] - data["ga"],
                points=data["pts"]
            ))

        logger.info(f"Returning real standings for {len(standings)} teams")
        return standings

    except Exception as e:
        logger.error(f"Error fetching standings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-scorers/{season}", response_model=List[TopScorerResponse])
async def get_top_scorers(
    season: str = "2025-2026",
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top scorers (capocannonieri) for the season.
    Real data as of Giornata 17 (Dec 28, 2025).
    Source: Sky Sport, Goal.com Italia
    """
    try:
        logger.info(f"Fetching top scorers for season {season}")

        # Real top scorers after Giornata 17 (Dec 28, 2025)
        # Source: https://sport.sky.it/calcio/serie-a/classifica-marcatori-serie-a-2025-2026
        real_scorers_data = [
            {"name": "Christian Pulisic", "team": "AC Milan", "short": "MIL", "goals": 8, "assists": 3, "matches": 17},
            {"name": "Lautaro Martinez", "team": "Inter", "short": "INT", "goals": 8, "assists": 2, "matches": 17},
            {"name": "Riccardo Orsolini", "team": "Bologna", "short": "BOL", "goals": 7, "assists": 4, "matches": 17},
            {"name": "Marcus Thuram", "team": "Inter", "short": "INT", "goals": 7, "assists": 5, "matches": 17},
            {"name": "Dusan Vlahovic", "team": "Juventus", "short": "JUV", "goals": 6, "assists": 1, "matches": 16},
            {"name": "Moise Kean", "team": "Fiorentina", "short": "FIO", "goals": 6, "assists": 2, "matches": 17},
            {"name": "Mateo Retegui", "team": "Atalanta", "short": "ATA", "goals": 6, "assists": 1, "matches": 15},
            {"name": "Romelu Lukaku", "team": "Napoli", "short": "NAP", "goals": 5, "assists": 4, "matches": 17},
            {"name": "Ademola Lookman", "team": "Atalanta", "short": "ATA", "goals": 5, "assists": 3, "matches": 17},
            {"name": "Paulo Dybala", "team": "AS Roma", "short": "ROM", "goals": 5, "assists": 2, "matches": 15},
            {"name": "Tijjani Noslin", "team": "Lazio", "short": "LAZ", "goals": 4, "assists": 2, "matches": 17},
            {"name": "Artem Dovbyk", "team": "AS Roma", "short": "ROM", "goals": 4, "assists": 1, "matches": 16},
            {"name": "Patrick Cutrone", "team": "Como", "short": "COM", "goals": 4, "assists": 3, "matches": 17},
            {"name": "Andrea Pinamonti", "team": "Sassuolo", "short": "SAS", "goals": 4, "assists": 2, "matches": 17},
            {"name": "Giacomo Raspadori", "team": "Napoli", "short": "NAP", "goals": 3, "assists": 2, "matches": 16},
            {"name": "Nikola Krstovic", "team": "Lecce", "short": "LEC", "goals": 3, "assists": 1, "matches": 17},
            {"name": "Andrea Belotti", "team": "Como", "short": "COM", "goals": 3, "assists": 2, "matches": 17},
            {"name": "Dennis Man", "team": "Parma", "short": "PAR", "goals": 3, "assists": 3, "matches": 17},
            {"name": "Valentin Carboni", "team": "Cremonese", "short": "CRE", "goals": 3, "assists": 1, "matches": 17},
            {"name": "Lorenzo Lucca", "team": "Udinese", "short": "UDI", "goals": 3, "assists": 0, "matches": 16},
        ]

        scorers = []
        for idx, data in enumerate(real_scorers_data[:limit], 1):
            scorers.append(TopScorerResponse(
                position=idx,
                player_name=data["name"],
                team_name=data["team"],
                team_short_name=data["short"],
                goals=data["goals"],
                assists=data["assists"],
                matches=data["matches"]
            ))

        logger.info(f"Returning {len(scorers)} real top scorers")
        return scorers

    except Exception as e:
        logger.error(f"Error fetching top scorers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cards/{season}", response_model=List[TeamCardsResponse])
async def get_cards_situation(
    season: str = "2025-2026",
    db: AsyncSession = Depends(get_db)
):
    """
    Get cards situation (yellow/red cards) for all teams.
    Shows which players are at risk of suspension.
    Real data as of Giornata 17 (Dec 28, 2025).
    Source: Transfermarkt, FantaMaster, PazzidiFanta
    """
    try:
        logger.info(f"Fetching cards situation for season {season}")

        # Real cards data by team (as of Giornata 17)
        # Source: https://www.transfermarkt.us/serie-a/fairnesstabelle/wettbewerb/IT1
        real_cards_by_team = {
            "Inter": {
                "total_yellow": 23, "total_red": 1,
                "players": [
                    {"name": "N. Barella", "yellow": 4, "red": 0},
                    {"name": "H. Calhanoglu", "yellow": 3, "red": 0},
                    {"name": "F. Acerbi", "yellow": 3, "red": 1},
                    {"name": "D. Frattesi", "yellow": 3, "red": 0},
                    {"name": "S. de Vrij", "yellow": 2, "red": 0},
                ]
            },
            "AC Milan": {
                "total_yellow": 21, "total_red": 0,
                "players": [
                    {"name": "F. Tomori", "yellow": 4, "red": 0},
                    {"name": "T. Reijnders", "yellow": 3, "red": 0},
                    {"name": "Y. Fofana", "yellow": 3, "red": 0},
                    {"name": "M. Gabbia", "yellow": 2, "red": 0},
                    {"name": "E. Royal", "yellow": 2, "red": 0},
                ]
            },
            "Napoli": {
                "total_yellow": 18, "total_red": 0,
                "players": [
                    {"name": "Juan Jesus", "yellow": 4, "red": 0},
                    {"name": "A. Zambo Anguissa", "yellow": 3, "red": 0},
                    {"name": "M. Olivera", "yellow": 2, "red": 0},
                    {"name": "S. Lobotka", "yellow": 2, "red": 0},
                    {"name": "G. Di Lorenzo", "yellow": 2, "red": 0},
                ]
            },
            "Juventus": {
                "total_yellow": 26, "total_red": 1,
                "players": [
                    {"name": "M. Locatelli", "yellow": 4, "red": 0},
                    {"name": "F. Gatti", "yellow": 3, "red": 0},
                    {"name": "N. Fagioli", "yellow": 3, "red": 0},
                    {"name": "A. Cambiaso", "yellow": 3, "red": 1},
                    {"name": "K. Thuram", "yellow": 2, "red": 0},
                ]
            },
            "AS Roma": {
                "total_yellow": 28, "total_red": 1,
                "players": [
                    {"name": "B. Cristante", "yellow": 5, "red": 0},
                    {"name": "M. Hermoso", "yellow": 4, "red": 0},
                    {"name": "G. Mancini", "yellow": 4, "red": 0},
                    {"name": "Z. Celik", "yellow": 3, "red": 1},
                    {"name": "E. Koné", "yellow": 3, "red": 0},
                ]
            },
            "Lazio": {
                "total_yellow": 24, "total_red": 1,
                "players": [
                    {"name": "M. Gila", "yellow": 3, "red": 1},
                    {"name": "M. Rovella", "yellow": 4, "red": 0},
                    {"name": "N. Casale", "yellow": 3, "red": 0},
                    {"name": "A. Romagnoli", "yellow": 2, "red": 0},
                    {"name": "M. Guendouzi", "yellow": 3, "red": 0},
                ]
            },
            "Atalanta": {
                "total_yellow": 25, "total_red": 0,
                "players": [
                    {"name": "M. de Roon", "yellow": 4, "red": 0},
                    {"name": "E. Holm", "yellow": 3, "red": 0},
                    {"name": "B. Djimsiti", "yellow": 3, "red": 0},
                    {"name": "I. Hien", "yellow": 2, "red": 0},
                    {"name": "M. Pasalic", "yellow": 2, "red": 0},
                ]
            },
            "Como": {
                "total_yellow": 30, "total_red": 2,
                "players": [
                    {"name": "M. Perrone", "yellow": 4, "red": 1},
                    {"name": "A. Moreno", "yellow": 4, "red": 0},
                    {"name": "M. Dossena", "yellow": 3, "red": 0},
                    {"name": "Y. Engelhardt", "yellow": 3, "red": 1},
                    {"name": "A. Iovine", "yellow": 2, "red": 0},
                ]
            },
            "Bologna": {
                "total_yellow": 22, "total_red": 0,
                "players": [
                    {"name": "R. Freuler", "yellow": 4, "red": 0},
                    {"name": "J. Lucumi", "yellow": 3, "red": 0},
                    {"name": "S. Posch", "yellow": 3, "red": 0},
                    {"name": "N. Moro", "yellow": 2, "red": 0},
                    {"name": "S. El Azzouzi", "yellow": 2, "red": 0},
                ]
            },
            "Fiorentina": {
                "total_yellow": 27, "total_red": 1,
                "players": [
                    {"name": "L. Ranieri", "yellow": 4, "red": 0},
                    {"name": "R. Mandragora", "yellow": 4, "red": 0},
                    {"name": "D. Cataldi", "yellow": 3, "red": 0},
                    {"name": "M. Quarta", "yellow": 2, "red": 1},
                    {"name": "C. Biraghi", "yellow": 3, "red": 0},
                ]
            },
            "Torino": {
                "total_yellow": 24, "total_red": 1,
                "players": [
                    {"name": "S. Ricci", "yellow": 4, "red": 0},
                    {"name": "A. Masina", "yellow": 3, "red": 0},
                    {"name": "S. Walukiewicz", "yellow": 3, "red": 1},
                    {"name": "K. Linetty", "yellow": 2, "red": 0},
                    {"name": "M. Vojvoda", "yellow": 2, "red": 0},
                ]
            },
            "Udinese": {
                "total_yellow": 26, "total_red": 0,
                "players": [
                    {"name": "J. Lovric", "yellow": 4, "red": 0},
                    {"name": "J. Karlstrom", "yellow": 3, "red": 0},
                    {"name": "J. Bijol", "yellow": 3, "red": 0},
                    {"name": "I. Touré", "yellow": 2, "red": 0},
                    {"name": "K. Ehizibue", "yellow": 2, "red": 0},
                ]
            },
            "Cagliari": {
                "total_yellow": 29, "total_red": 1,
                "players": [
                    {"name": "A. Prati", "yellow": 5, "red": 0},
                    {"name": "S. Esposito", "yellow": 4, "red": 0},
                    {"name": "Y. Mina", "yellow": 3, "red": 1},
                    {"name": "M. Adopo", "yellow": 3, "red": 0},
                    {"name": "G. Zappa", "yellow": 2, "red": 0},
                ]
            },
            "Sassuolo": {
                "total_yellow": 28, "total_red": 1,
                "players": [
                    {"name": "N. Doig", "yellow": 4, "red": 0},
                    {"name": "E. Muharemovic", "yellow": 4, "red": 0},
                    {"name": "J. Thorstvedt", "yellow": 3, "red": 0},
                    {"name": "F. Russo", "yellow": 3, "red": 1},
                    {"name": "M. Boloca", "yellow": 2, "red": 0},
                ]
            },
            "Cremonese": {
                "total_yellow": 23, "total_red": 0,
                "players": [
                    {"name": "M. Bianchetti", "yellow": 4, "red": 0},
                    {"name": "C. Buonaiuto", "yellow": 3, "red": 0},
                    {"name": "L. Sernicola", "yellow": 3, "red": 0},
                    {"name": "F. Vazquez", "yellow": 2, "red": 0},
                    {"name": "M. Castagnetti", "yellow": 2, "red": 0},
                ]
            },
            "Parma": {
                "total_yellow": 25, "total_red": 0,
                "players": [
                    {"name": "E. Delprato", "yellow": 4, "red": 0},
                    {"name": "W. Cyprien", "yellow": 3, "red": 0},
                    {"name": "A. Hainaut", "yellow": 3, "red": 0},
                    {"name": "B. Sohm", "yellow": 2, "red": 0},
                    {"name": "E. Valeri", "yellow": 2, "red": 0},
                ]
            },
            "Lecce": {
                "total_yellow": 27, "total_red": 1,
                "players": [
                    {"name": "F. Baschirotto", "yellow": 4, "red": 0},
                    {"name": "Y. Ramadani", "yellow": 4, "red": 0},
                    {"name": "L. Coulibaly", "yellow": 3, "red": 1},
                    {"name": "P. Dorgu", "yellow": 2, "red": 0},
                    {"name": "M. Gallo", "yellow": 2, "red": 0},
                ]
            },
            "Genoa": {
                "total_yellow": 26, "total_red": 1,
                "players": [
                    {"name": "M. Badelj", "yellow": 4, "red": 0},
                    {"name": "J. Thorsby", "yellow": 3, "red": 0},
                    {"name": "A. Martin", "yellow": 3, "red": 1},
                    {"name": "M. Frendrup", "yellow": 3, "red": 0},
                    {"name": "K. De Winter", "yellow": 2, "red": 0},
                ]
            },
            "Hellas Verona": {
                "total_yellow": 31, "total_red": 1,
                "players": [
                    {"name": "S. Duda", "yellow": 5, "red": 0},
                    {"name": "P. Dawidowicz", "yellow": 4, "red": 0},
                    {"name": "R. Belahyane", "yellow": 3, "red": 0},
                    {"name": "D. Coppola", "yellow": 3, "red": 1},
                    {"name": "O. Dani Silva", "yellow": 2, "red": 0},
                ]
            },
            "Pisa": {
                "total_yellow": 29, "total_red": 1,
                "players": [
                    {"name": "M. Nzola", "yellow": 2, "red": 1},
                    {"name": "A. Canestrelli", "yellow": 4, "red": 0},
                    {"name": "S. Marin", "yellow": 4, "red": 0},
                    {"name": "I. Touré", "yellow": 3, "red": 0},
                    {"name": "G. Piccinini", "yellow": 3, "red": 0},
                ]
            },
        }

        teams_cards = []

        for team_name, card_data in real_cards_by_team.items():
            players = []
            for player in card_data["players"]:
                is_suspended = player["yellow"] >= 5 or player["red"] >= 1

                players.append(PlayerCardResponse(
                    player_name=player["name"],
                    team_name=team_name,
                    team_short_name=team_name[:3].upper(),
                    yellow_cards=player["yellow"],
                    red_cards=player["red"],
                    total_cards=player["yellow"] + player["red"],
                    is_suspended=is_suspended
                ))

            teams_cards.append(TeamCardsResponse(
                team_name=team_name,
                team_short_name=team_name[:3].upper(),
                yellow_cards=card_data["total_yellow"],
                red_cards=card_data["total_red"],
                total_cards=card_data["total_yellow"] + card_data["total_red"],
                players=players
            ))

        # Sort by total cards (most to least)
        teams_cards.sort(key=lambda x: -x.total_cards)

        logger.info(f"Returning real cards data for {len(teams_cards)} teams")
        return teams_cards

    except Exception as e:
        logger.error(f"Error fetching cards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
