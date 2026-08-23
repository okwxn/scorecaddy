from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ScoringSystem(str, Enum):
    stroke_play = "stroke_play"
    stableford = "stableford"

class GameFormat(str, Enum): # dictates how the scores are matched against playing partners
    match_play = "match_play"
    split_sixes = "split_sixes"
    skins = "skins"

class Player(BaseModel):
    name: str
    handicap: int

class Course(BaseModel):
    name: str = ""
    par_by_hole: List[int] = Field(default_factory=list)
    stroke_indexes: List[int] = Field(default_factory=list)
    course_rating: int = 0 # there might be a better default value to set 
    slope_rating: int = 0 # there might be a better default value to set

class Match(BaseModel):
    players: List[Player] = Field(default_factory=list)
    course: Optional[Course] = None
    shots_given: Dict[str, List[int]] = Field(default_factory=dict)
    scores: Dict[str, int] = Field(default_factory=dict)
    game_format: GameFormat = GameFormat.match_play
    scoring_system: ScoringSystem = ScoringSystem.stroke_play