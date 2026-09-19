from typing import Dict, List
from pydantic import BaseModel, Field, model_validator

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
    def set_default_course_rating(cls, data):
        if isinstance(data, dict) and "par_by_hole" in data:
            data["course_rating"] = float(sum(data["par_by_hole"]))
        return data

class Match(BaseModel):
    players: List[Player]
    course: Course
    shots_given: Dict[str, List[int]] = Field(default_factory=dict)
    scores: Dict[str, int] = Field(default_factory=dict)