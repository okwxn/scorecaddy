from typing import Dict, List
from pydantic import BaseModel, Field, model_validator
from enum import Enum

class ScoringSystem(str, Enum):
    stroke_play = "stroke_play"
    stableford = "stableford"

class GameFormat(str, Enum):
    match_play = "match_play"
    split_sixes = "split_sixes"
    skins = "skins"

class Player(BaseModel):
    name: str
    handicap: float

class Course(BaseModel):
    name: str
    par_by_hole: List[int]
    stroke_indexes: List[int]
    course_rating: float
    slope_rating: int = 113

    @model_validator(mode="before")
    def set_default_course_rating(self) -> "Course":
        self.course_rating = float(sum(self.par_by_hole))
        return self

class Match(BaseModel):
    players: List[Player]
    course: Course
    shots_given: Dict[str, List[int]] = Field(default_factory=dict)
    scores: Dict[str, int] = Field(default_factory=dict)
    game_format: GameFormat = GameFormat.match_play
    scoring_system: ScoringSystem = ScoringSystem.stroke_play