from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Player(BaseModel):
    name: str
    handicap: float

class Hole(BaseModel):
    number: int
    par: int
    stroke_index: int

class Course(BaseModel):
    name: str
    par: int
    stroke_indexes: List[int]
    course_rating: int
    slope_rating: int

class Match(BaseModel):
    players: list[Player] = Field(default_factory=list)
    course: Optional[Course] = None
    game_format: Optional[str] = None
    shots_given: Dict[str, List[int]] = Field(default_factory=dict)
    scores: Dict[str, int] = Field(default_factory=dict)