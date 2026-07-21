from typing import Dict, List, Optional
from pydantic import BaseModel

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
    players: List[Player]
    course: Optional[Course] = None
    game_format: Optional[str] = None
    shots_given: Dict[str, List[int]] = {}
    scores: Dict[str, int] = {}