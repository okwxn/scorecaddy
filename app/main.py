from fastapi import FastAPI, Request, HTTPException
from schemas import Match, Course, Player
from collections import defaultdict
from typing import Dict, List
from math import floor

app = FastAPI()

app.state.current_match = None

def set_shots_given(
        course: Course, 
        players: List[Player]
    ) -> Dict[str, List[int]]:

    slope_rating, course_rating, course_par = course.slope_rating, course.course_rating, sum(course.par_by_hole)
    handicaps = defaultdict(int)
    min_handicap = 54
    for player in players:
        player_name = player.name
        course_handicap = floor(0.5 + (player.handicap * (slope_rating / 113) + (course_rating - course_par)))
        handicaps[player_name] = course_handicap
        min_handicap = min(min_handicap, course_handicap)

    max_net_handicap = 0
    for player_name, course_handicap in handicaps.items():
        net_handicap = course_handicap - min_handicap
        handicaps[player_name] = net_handicap
        max_net_handicap = max(max_net_handicap, net_handicap)

    stroke_indexes = course.stroke_indexes
    shots_given = {player.name: [0] * 18 for player in players}

    for hole in range(18):
        stroke_index = stroke_indexes[hole]

        for player in players:
            player_name = player.name
            handicap = handicaps[player_name]

            base_shots = handicap // 18
            extra_stroke_cutoff = handicap % 18

            if stroke_index <= extra_stroke_cutoff:
                shots_given[player_name][hole] = 1 + base_shots
            else:
                shots_given[player_name][hole] = base_shots

    return shots_given

def calculate_split_sixes(net_stroke_players: list[list[int]]) -> dict[str, int]:
    """Allocate six points by net score, splitting tied positions equally."""
    sorted_players = sorted(net_stroke_players, key=lambda player: player[1])
    position_points = (4, 2, 0)
    net_score_players = defaultdict(int)
    position = 0

    while position < len(sorted_players):
        tie_end = position + 1
        while (tie_end < len(sorted_players)
               and sorted_players[tie_end][1] == sorted_players[position][1]):
            tie_end += 1

        points = sum(position_points[position:tie_end]) / (tie_end - position)
        for player_name, _ in sorted_players[position:tie_end]:
            net_score_players[player_name] = int(points)
        position = tie_end

    return dict(net_score_players)

@app.get("/")
def read_root():
    return "Welcome to ScoreCaddy"

@app.get("/match")
def get_match():
    return app.state.current_match

@app.post("/match")
def create_match(match: Match, request: Request):
    match.shots_given = set_shots_given(match.course, match.players)
    request.app.state.current_match = match
    return match

@app.put("/match")
def update_match(
    player_shots: dict[str, int], 
    hole: int, 
    request: Request
):
    current_match = request.app.state.current_match
    net_strokes_players = []

    match (len(current_match.players)):
        case (2): # 1 vs 1, net strokes match play 
            for player_name, gross_strokes in player_shots.items():
                shots_given = current_match.shots_given[player_name][hole]
                net_stroke = gross_strokes - shots_given
                net_strokes_players.append([player_name, net_stroke])

            if net_strokes_players[0][1] > net_strokes_players[1][1]:
                current_match.scores[net_strokes_players[0][0]] = current_match.scores.get(net_strokes_players[0][0], 0) + 1
            elif net_strokes_players[0][1] < net_strokes_players[1][1]:
                current_match.scores[net_strokes_players[1][0]] = current_match.scores.get(net_strokes_players[1][0], 0) + 1
            else:
                return current_match

        case (3): # 1 vs 1 vs 1, net strokes split sixes
            for player_name, gross_strokes in player_shots.items():
                shots_given = current_match.shots_given[player_name][hole]
                net_stroke = gross_strokes - shots_given
                net_strokes_players.append([player_name, net_stroke])

            sixes_points: dict[str, int] = calculate_split_sixes(net_strokes_players)
            for player_name, score in sixes_points.items():
                current_match.scores[player_name] += score

            lowest_score = min(current_match.scores.values())
            current_match.scores = {player: score - lowest_score for player, score in current_match.scores.items()}

            return current_match    

        case _:
            raise HTTPException(status_code=400, detail="4 player games not yet supported")
