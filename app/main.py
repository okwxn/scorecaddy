from fastapi import FastAPI
from schemas import Player, Match


app = FastAPI()

matches = []

@app.get("/")
def read_root():
    return "Welcome to ScoreCaddy."


@app.get("/players/{name}")
def get_player(name: str):
    for match in matches:
        for player in match.players:
            if name == player.name:
                return {"player_name": player.name, "handicap": player.handicap}
    return f"player {name} not found"


@app.put("/matches")
def create_match(match: Match):
    matches.append(match)
    return match