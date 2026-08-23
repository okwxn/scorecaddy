from fastapi import FastAPI, Request, HTTPException
from schemas import Match, Course, ScoringSystem, GameFormat
from collections import defaultdict

app = FastAPI()

app.state.current_match = Match()
app.state.current_course = Course()


def calculate_stableford(net_score_for_hole: int) -> int:
    """Stableford point system based on strokes relative to par."""
    # Example standard Stableford: Net Albatross=5, Eagle=4, Birdie=3, Par=2, Bogey=1, Double+=0
    match net_score_for_hole:
        case -3: return 5 # Albatross
        case -2: return 4
        case -1: return 3
        case 0: return 2 # Par
        case 1: return 1
        case _: return 0 # Double Bogey or worse

def calculate_split_sixes(stroke_counts: dict[str, int]) -> dict[str, int]:
    """Split Sixes (threesome game) points allocation logic."""
    # Split sixes splits 6 points per hole among 3 players based on scores.

    return {}

@app.get("/")
def read_root():
    return "Welcome to ScoreCaddy"

@app.post("/matches")
def create_match(match: Match, request: Request):
    request.app.state.current_match = match
    return match

@app.put("/matches")
def update_match(player_shots: dict[str, int], hole: int, request: Request):
    current_match: Match = request.app.state.current_match
    net_strokes_players = []

    match (current_match.scoring_system, current_match.game_format):
        case (ScoringSystem.stroke_play, GameFormat.match_play):
            for player_name, gross_strokes in player_shots.items(): # 2 iterations in every Match Play
                shots_given = current_match.shots_given[player_name][hole]
                net_stroke = gross_strokes - shots_given
                net_strokes_players.append([player_name, net_stroke])

            if net_strokes_players[0][1] > net_strokes_players[1][1]:
                current_match.scores[net_strokes_players[0][0]] = current_match.scores.get(net_strokes_players[0][0], 0) + 1
            elif net_strokes_players[0][1] < net_strokes_players[1][1]:
                current_match.scores[net_strokes_players[1][0]] = current_match.scores.get(net_strokes_players[1][0], 0) + 1
            else:
                pass

        case (ScoringSystem.stroke_play, GameFormat.split_sixes): # TODO next
            sixes_points = calculate_split_sixes(player_shots)
            for player_name, points in sixes_points.items():
                current_match.scores[player_name] = current_match.scores.get(player_name, 0) + points
                
        case _:
            raise HTTPException(status_code=400, detail="Game format not yet supported")

    return current_match

@app.get("/players/{name}")
def get_player(name: str, request: Request):
    current_match: Match = request.app.state.current_match

    for player in current_match.players:
        if name == player.name:
            return {
                "player_name": player.name, 
                "handicap": player.handicap
            }
    
    raise HTTPException(status_code=404, detail=f"Player {name} not found")
