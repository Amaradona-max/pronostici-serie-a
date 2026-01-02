"""
Pydantic Schemas for API Request/Response Models
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal


# ============= BASE MODELS =============

class TeamBase(BaseModel):
    id: int
    name: str
    short_name: Optional[str] = None
    logo_url: Optional[str] = None

    model_config = {"from_attributes": True}

# ============= PREDICTION STATS MODELS =============

class PredictionStatsResponse(BaseModel):
    total_predictions: int
    accuracy_1x2: float
    accuracy_over_under: float
    accuracy_btts: float
    best_team_predicted: str
    worst_team_predicted: str
    last_week_accuracy: float
    model_version: str
    last_update: datetime
    avg_confidence: float
    high_confidence_wins: int
    high_confidence_accuracy: float
    medium_confidence_wins: int
    medium_confidence_accuracy: float
    low_confidence_wins: int
    low_confidence_accuracy: float

    # Detailed Team Stats
    best_team_accuracy: float
    best_team_correct: int
    best_team_total: int
    worst_team_accuracy: float
    worst_team_correct: int
    worst_team_total: int

    model_config = {"from_attributes": True, "protected_namespaces": ()}



class StadiumInfo(BaseModel):
    name: str
    city: Optional[str] = None
    capacity: Optional[int] = None
    home_advantage_factor: float

    model_config = {"from_attributes": True}


# ============= FIXTURE MODELS =============

class FixtureBase(BaseModel):
    id: int
    home_team: TeamBase
    away_team: TeamBase
    match_date: datetime
    round: Optional[str] = None
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    prediction: Optional['PredictionResponse'] = None

    model_config = {"from_attributes": True}


class FixtureListResponse(BaseModel):
    fixtures: List[FixtureBase]
    total: int
    page: int
    page_size: int


# ============= PREDICTION MODELS =============

class PredictionResponse(BaseModel):
    id: int
    fixture_id: int

    # 1X2 Probabilities
    prob_home_win: float = Field(..., ge=0, le=1, description="P(1)")
    prob_draw: float = Field(..., ge=0, le=1, description="P(X)")
    prob_away_win: float = Field(..., ge=0, le=1, description="P(2)")

    # Over/Under
    prob_over_25: Optional[float] = Field(None, ge=0, le=1)
    prob_under_25: Optional[float] = Field(None, ge=0, le=1)

    # BTTS
    prob_btts_yes: Optional[float] = Field(None, ge=0, le=1)
    prob_btts_no: Optional[float] = Field(None, ge=0, le=1)

    # Scoreline
    most_likely_score: Optional[str] = Field(None, examples=["2-1"])

    # Expected Goals
    expected_home_goals: Optional[float] = Field(None, ge=0, description="xG casa")
    expected_away_goals: Optional[float] = Field(None, ge=0, description="xG trasferta")

    # Metadata
    confidence_score: float = Field(..., ge=0, le=1)
    computed_at: datetime = Field(validation_alias="created_at")

    model_config = {"from_attributes": True, "populate_by_name": True}


# ============= TEAM STATS MODELS =============

class TeamStatsResponse(BaseModel):
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    form_last5: Optional[str] = None
    xg_for: float = 0.0
    xg_against: float = 0.0

    model_config = {"from_attributes": True}


class InjuryResponse(BaseModel):
    player_name: str
    injury_type: str
    severity: str
    expected_return: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SuspensionResponse(BaseModel):
    player_name: str
    reason: Optional[str] = None
    matches_remaining: int

    model_config = {"from_attributes": True}


# ============= MATCH DETAIL MODEL =============

class MatchDetailResponse(BaseModel):
    fixture: FixtureBase
    prediction: Optional[PredictionResponse] = None

    # Team stats
    home_team_stats: Optional[TeamStatsResponse] = None
    away_team_stats: Optional[TeamStatsResponse] = None

    # Injuries & Suspensions
    home_injuries: List[InjuryResponse] = []
    away_injuries: List[InjuryResponse] = []
    home_suspensions: List[SuspensionResponse] = []
    away_suspensions: List[SuspensionResponse] = []

    # Form
    home_last_5_results: List[str] = []
    away_last_5_results: List[str] = []

    # H2H
    h2h_summary: Optional[Dict] = None


# ============= EVALUATION MODELS =============

class ModelPerformanceResponse(BaseModel):
    model_version: str
    evaluation_period: str
    matches_evaluated: int

    # Overall metrics
    accuracy_1x2: float
    log_loss: float
    brier_score: float
    expected_calibration_error: float

    # Breakdown
    breakdown_by_outcome: Dict[str, Dict]

    # Optional
    roi_if_betting: Optional[float] = None
    
    model_config = {"protected_namespaces": ()}


# ============= SCORER PROBABILITY MODELS =============

class ScorerProbability(BaseModel):
    """Probabilità che un giocatore segni in una partita"""
    player_name: str
    position: str  # "Attaccante", "Centrocampista", "Difensore"
    probability: float = Field(..., ge=0, le=1, description="P(gol)")

    model_config = {"from_attributes": True}


class FixtureScorersResponse(BaseModel):
    """Probabilità marcatori per una partita"""
    fixture_id: int
    home_team_scorers: List[ScorerProbability]
    away_team_scorers: List[ScorerProbability]


# ============= LINEUP MODELS =============

class LineupPlayer(BaseModel):
    """Giocatore in formazione"""
    name: str
    position: str  # "GK", "DF", "MF", "FW"
    jersey_number: int
    is_starter: bool  # True = titolare, False = panchina

    model_config = {"from_attributes": True}


class TeamLineup(BaseModel):
    """Formazione squadra (11 titolari + 7 panchina)"""
    team_name: str
    formation: str  # Es: "4-3-3", "3-5-2"
    starters: List[LineupPlayer]  # 11 giocatori
    bench: List[LineupPlayer]  # 7 giocatori

    model_config = {"from_attributes": True}


class FixtureLineupsResponse(BaseModel):
    """Formazioni probabili per una partita - sempre disponibili"""
    fixture_id: int
    home_lineup: Optional[TeamLineup] = None
    away_lineup: Optional[TeamLineup] = None


# ============= BIORHYTHM MODELS =============

class PlayerBiorhythm(BaseModel):
    """Bioritmi di un singolo calciatore"""
    player_name: str
    position: str
    physical: float = Field(..., ge=-100, le=100, description="Bioritmo fisico")
    emotional: float = Field(..., ge=-100, le=100, description="Bioritmo emotivo")
    intellectual: float = Field(..., ge=-100, le=100, description="Bioritmo intellettuale")
    overall: float = Field(..., ge=-100, le=100, description="Media ponderata")
    status: str = Field(..., description="excellent, good, low, critical")

    model_config = {"from_attributes": True}


class TeamBiorhythm(BaseModel):
    """Bioritmi aggregati di una squadra"""
    team_name: str
    avg_physical: float
    avg_emotional: float
    avg_intellectual: float
    avg_overall: float
    players_excellent: int  # Numero giocatori in forma eccellente
    players_good: int
    players_low: int
    players_critical: int
    total_players: int
    top_performers: List[PlayerBiorhythm] = Field(default_factory=list, description="Top 3 giocatori per bioritmo")

    model_config = {"from_attributes": True}


class FixtureBiorhythmsResponse(BaseModel):
    """Bioritmi completi per una partita"""
    fixture_id: int
    match_date: datetime
    home_team_biorhythm: TeamBiorhythm
    away_team_biorhythm: TeamBiorhythm
    biorhythm_advantage: str = Field(..., description="home, away, neutral")

    model_config = {"from_attributes": True}
