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
        case -2: return 4 # Eagle
        case -1: return 3 # Birdie
        case 0: return 2 # Par
        case 1: return 1 # Bogey
        case _: return 0 # Double Bogey or worse

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
            for player_name, gross_strokes in player_shots.items(): # 2 iterations in Match Play
                shots_given = current_match.shots_given[player_name][hole]
                net_stroke = gross_strokes - shots_given
                net_strokes_players.append([player_name, net_stroke])

            if net_strokes_players[0][1] > net_strokes_players[1][1]:
                current_match.scores[net_strokes_players[0][0]] = current_match.scores.get(net_strokes_players[0][0], 0) + 1
            elif net_strokes_players[0][1] < net_strokes_players[1][1]:
                current_match.scores[net_strokes_players[1][0]] = current_match.scores.get(net_strokes_players[1][0], 0) + 1
            else:
                return current_match

        case (ScoringSystem.stroke_play, GameFormat.split_sixes): # TODO next
            for player_name, gross_strokes in player_shots.items(): # 3 iterations in Split Sixes
                shots_given = current_match.shots_given[player_name][hole]
                net_stroke = gross_strokes - shots_given
                net_strokes_players.append([player_name, net_stroke])

            sixes_points: dict[str, int] = calculate_split_sixes(net_strokes_players)
            for player, score in sixes_points.items():
                current_match.scores[player] += score

            lowest_score = min(current_match.scores.values())
            current_match.scores = {player: score - lowest_score for player, score in current_match.scores.items()}

            return current_match    

        case _:
            raise HTTPException(status_code=400, detail="Game format not yet supported")

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
