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

    model_config = {"from_attributes": True}


class FixtureListResponse(BaseModel):
    fixtures: List[FixtureBase]
    total: int
    page: int
    page_size: int


# ============= PREDICTION MODELS =============

class PredictionResponse(BaseModel):
    fixture_id: int
    model_version: str

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
    most_likely_score_prob: Optional[float] = None

    # Metadata
    confidence_score: float = Field(..., ge=0, le=1)
    data_completeness: float = Field(..., ge=0, le=1)
    computed_at: datetime

    @field_validator('prob_draw')
    @classmethod
    def validate_probabilities_sum(cls, v, info):
        """Validate that P(1) + P(X) + P(2) ≈ 1"""
        total = info.data.get('prob_home_win', 0) + v + info.data.get('prob_away_win', 0)
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Probabilities must sum to 1, got {total}")
        return v

    model_config = {"from_attributes": True}


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
