from fastapi import FastAPI, Request
from schemas import Match

app = FastAPI()
app.state.current_match = Match() # TODO: replace with persistence

@app.get("/")
def read_root():
    return "Welcome to ScoreCaddy"

@app.put("/matches")
def create_match(match: Match, request: Request):
    request.app.state.current_match = match
    return match

@app.get("/players/{name}")
def get_player(name: str, request: Request):
    current_match: Match = request.app.state.current_match

    for player in current_match.players:
        if name == player.name:
            return {
                "player_name": player.name, 
                "handicap": player.handicap
            }
    return f"player {name} not found"
