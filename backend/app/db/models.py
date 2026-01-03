"""
Database Models
All SQLAlchemy ORM models for the application
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    ForeignKey, Text, Date, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.db.base import Base


# Enums
class FixtureStatus(str, enum.Enum):
    """Fixture status enum"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class InjuryStatus(str, enum.Enum):
    """Injury status enum"""
    ACTIVE = "active"
    RECOVERED = "recovered"


class SuspensionStatus(str, enum.Enum):
    """Suspension status enum"""
    ACTIVE = "active"
    SERVED = "served"


# Models
class Competition(Base):
    """Football competition (e.g., Serie A)"""
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    season = Column(String(20), nullable=False)
    external_id = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fixtures = relationship("Fixture", back_populates="competition")

    __table_args__ = (
        Index('ix_competition_season', 'season'),
    )


class Team(Base):
    """Football team"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    short_name = Column(String(50))
    code = Column(String(10))
    logo_url = Column(String(255))
    founded = Column(Integer)
    venue_name = Column(String(100))
    venue_capacity = Column(Integer)
    external_id = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    home_fixtures = relationship("Fixture", foreign_keys="Fixture.home_team_id", back_populates="home_team")
    away_fixtures = relationship("Fixture", foreign_keys="Fixture.away_team_id", back_populates="away_team")
    players = relationship("Player", back_populates="team")
    team_stats = relationship("TeamStats", back_populates="team")
    injuries = relationship("Injury", back_populates="team")
    suspensions = relationship("Suspension", back_populates="team")


class Fixture(Base):
    """Match fixture"""
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    season = Column(String(20), nullable=False)
    round = Column(String(50))
    match_date = Column(DateTime(timezone=True), nullable=False, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    status = Column(SQLEnum(FixtureStatus), default=FixtureStatus.SCHEDULED, index=True)
    home_score = Column(Integer)
    away_score = Column(Integer)
    external_id = Column(Integer, unique=True, index=True)
    last_synced_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    competition = relationship("Competition", back_populates="fixtures")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_fixtures")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_fixtures")
    predictions = relationship("Prediction", back_populates="fixture")
    match_stats = relationship("MatchStats", back_populates="fixture", uselist=False)

    __table_args__ = (
        Index('ix_fixture_date_status', 'match_date', 'status'),
        Index('ix_fixture_teams', 'home_team_id', 'away_team_id'),
    )


class Player(Base):
    """Football player"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    position = Column(String(50))
    jersey_number = Column(Integer)
    nationality = Column(String(50))
    birth_date = Column(Date)
    external_id = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="players")
    injuries = relationship("Injury", back_populates="player")
    suspensions = relationship("Suspension", back_populates="player")


class TeamStats(Base):
    """Team statistics for a season"""
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    season = Column(String(20), nullable=False)
    matches_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    goals_scored = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    elo_rating = Column(Float, default=1500.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="team_stats")

    __table_args__ = (
        Index('ix_team_stats_season', 'team_id', 'season', unique=True),
    )


class MatchStats(Base):
    """Detailed match statistics"""
    __tablename__ = "match_stats"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, unique=True)
    home_possession = Column(Float)
    away_possession = Column(Float)
    home_shots = Column(Integer)
    away_shots = Column(Integer)
    home_shots_on_target = Column(Integer)
    away_shots_on_target = Column(Integer)
    home_corners = Column(Integer)
    away_corners = Column(Integer)
    home_fouls = Column(Integer)
    away_fouls = Column(Integer)
    home_yellow_cards = Column(Integer)
    away_yellow_cards = Column(Integer)
    home_red_cards = Column(Integer)
    away_red_cards = Column(Integer)
    home_xg = Column(Float)
    away_xg = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    fixture = relationship("Fixture", back_populates="match_stats")


class Injury(Base):
    """Player injury record"""
    __tablename__ = "injuries"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    injury_type = Column(String(100))
    severity = Column(String(50))
    expected_return_date = Column(Date)
    status = Column(SQLEnum(InjuryStatus), default=InjuryStatus.ACTIVE, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="injuries")
    team = relationship("Team", back_populates="injuries")

    __table_args__ = (
        Index('ix_injury_team_status', 'team_id', 'status'),
    )


class Suspension(Base):
    """Player suspension record"""
    __tablename__ = "suspensions"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    reason = Column(String(255))
    matches_remaining = Column(Integer, default=1)
    status = Column(SQLEnum(SuspensionStatus), default=SuspensionStatus.ACTIVE, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="suspensions")
    team = relationship("Team", back_populates="suspensions")


class Prediction(Base):
    """ML prediction for a fixture"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    prob_home_win = Column(Float, nullable=False)
    prob_draw = Column(Float, nullable=False)
    prob_away_win = Column(Float, nullable=False)
    prob_over_25 = Column(Float)
    prob_under_25 = Column(Float)
    prob_btts_yes = Column(Float)
    prob_btts_no = Column(Float)
    expected_home_goals = Column(Float)
    expected_away_goals = Column(Float)
    most_likely_score = Column(String(10))
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    fixture = relationship("Fixture", back_populates="predictions")
    evaluation = relationship("PredictionEvaluation", back_populates="prediction", uselist=False)
    feature_snapshot = relationship("FeatureSnapshot", back_populates="prediction", uselist=False)

    __table_args__ = (
        Index('ix_prediction_fixture_created', 'fixture_id', 'created_at'),
    )


class FeatureSnapshot(Base):
    """Snapshot of features used for prediction (for audit trail)"""
    __tablename__ = "feature_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, unique=True)
    home_elo_rating = Column(Float)
    away_elo_rating = Column(Float)
    home_form_last5 = Column(Float)
    away_form_last5 = Column(Float)
    home_goals_scored_avg = Column(Float)
    away_goals_scored_avg = Column(Float)
    home_goals_conceded_avg = Column(Float)
    away_goals_conceded_avg = Column(Float)
    home_injuries_count = Column(Integer)
    away_injuries_count = Column(Integer)
    home_suspensions_count = Column(Integer)
    away_suspensions_count = Column(Integer)
    h2h_home_wins = Column(Integer)
    h2h_draws = Column(Integer)
    h2h_away_wins = Column(Integer)
    snapshot_timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction = relationship("Prediction", back_populates="feature_snapshot")


class PredictionEvaluation(Base):
    """Evaluation of prediction after match completion"""
    __tablename__ = "prediction_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, unique=True)
    actual_outcome_1x2 = Column(String(10))
    predicted_outcome_1x2 = Column(String(10))
    is_correct_1x2 = Column(Boolean)
    is_correct_over_under = Column(Boolean)
    is_correct_btts = Column(Boolean)
    brier_score_1x2 = Column(Float)
    brier_score_over_under = Column(Float)
    brier_score_btts = Column(Float)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction = relationship("Prediction", back_populates="evaluation")


class DataSyncLog(Base):
    """Log of external data synchronization"""
    __tablename__ = "data_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, index=True)
    records_synced = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_sync_log_provider_resource', 'provider', 'resource_type'),
    )


class Stadium(Base):
    """Stadium information"""
    __tablename__ = "stadiums"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    city = Column(String(100))
    capacity = Column(Integer)
    surface = Column(String(50))
    external_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
