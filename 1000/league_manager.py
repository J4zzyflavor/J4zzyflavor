# league_manager.py
import json
import os
from typing import Dict

LEAGUE_FILE = "league/league_state.json"
K_FACTOR = 32
MAX_POPULATION = 5
MIN_SURVIVAL_ELO = 950


def expected_score(r_a, r_b):
    return 1 / (1 + 10 ** ((r_b - r_a) / 400))


class LeagueManager:
    def __init__(self, path=LEAGUE_FILE):
        self.path = path
        self.state: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.state = json.load(f)
        else:
            self.state = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.state, f, indent=2)

    def register(self, model_path: str):
        if model_path not in self.state:
            self.state[model_path] = {"elo": 1000, "games": 0}

    def update(self, model_a, model_b, result_a):
        self.register(model_a)
        self.register(model_b)

        ra, rb = self.state[model_a]["elo"], self.state[model_b]["elo"]
        ea = expected_score(ra, rb)

        self.state[model_a]["elo"] = ra + K_FACTOR * (result_a - ea)
        self.state[model_b]["elo"] = rb + K_FACTOR * ((1 - result_a) - (1 - ea))

        self.state[model_a]["games"] += 1
        self.state[model_b]["games"] += 1

        self._prune()
        self._save()

    def top_models(self, k=3):
        return sorted(
            self.state.keys(),
            key=lambda m: self.state[m]["elo"],
            reverse=True
        )[:k]

    def _prune(self):
        # remove weak
        self.state = {
            m: v for m, v in self.state.items()
            if v["elo"] >= MIN_SURVIVAL_ELO
        }

        # keep only top-K
        if len(self.state) > MAX_POPULATION:
            top = self.top_models(MAX_POPULATION)
            self.state = {m: self.state[m] for m in top}
