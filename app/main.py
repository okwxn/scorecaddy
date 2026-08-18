from fastapi import FastAPI, Request, HTTPException
from schemas import Match, Course, ScoringSystem, GameFormat
from collections import defaultdict

app = FastAPI()

app.state.current_match = Match()
app.state.current_course = Course()

# TODO: implement function to dynamically calculate the shots_given list using the player's handicap, course slope, and rating
# TODO: Persist matches in a lightweight database (like SQLite) instead of keeping them in volatile application state


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
    # TODO: implement 3-player ties/win distribution logic here

    return {}

@app.get("/")
def read_root():
    return "Welcome to ScoreCaddy"

@app.post("/matches")
def create_match(match: Match, request: Request):
    request.app.state.current_match = match
    return match

@app.put("/matches")
def update_match(stroke_counts: dict[str, int], hole: int, request: Request):
    current_match: Match = request.app.state.current_match
    current_course: Course = request.app.state.current_course

    # Guard rail: Ensure course data exists before running math
    if not current_course.par_by_hole or hole >= len(current_course.par_by_hole):
        raise HTTPException(status_code=400, detail="Invalid hole or course data not loaded")

    par = current_course.par_by_hole[hole]
    net_strokes = defaultdict(lambda: [0] * 18)

    match (current_match.game_format, current_match.scoring_system):

        # TODO: cover all cases below

        case (GameFormat.match_play, ScoringSystem.stroke_play):
            for player_name, gross_strokes in stroke_counts.items():
                # Safely get shots given for this specific player (default to 0 if missing)
                player_shots = current_match.shots_given.get(player_name, [0] * 18)
                shots_on_hole = player_shots[hole] if hole < len(player_shots) else 0
                
                # Calculate net strokes relative to par for Stableford
                net_strokes = gross_strokes - shots_on_hole
                net_relative_to_par = net_strokes - par
                
                # Calculate points and update running score total
                hole_points = calculate_stableford(net_relative_to_par)
                current_match.scores[player_name] = current_match.scores.get(player_name, 0) + hole_points

        case (GameFormat.split_sixes, ScoringSystem.stroke_play):
            # Split Sixes requires analyzing all player scores on the hole together
            sixes_points = calculate_split_sixes(stroke_counts)
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
