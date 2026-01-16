# train.py — Stage 8.6 ELO-Gated Population Self-Play

import os
import time

from sb3_contrib import MaskablePPO
from stable_baselines3.common.monitor import Monitor

from envs.thousand_env import ThousandEnv
from league_manager import LeagueManager


BASE_MODEL = "models/stage8_5_1768548437.zip"
TOTAL_TIMESTEPS = 900_000

LR = 5e-06
CLIP_RANGE = 0.035
ELO_WINDOW = 120   # насколько сильнее себя берём оппонентов

SAVE_DIR = "models"


def select_elo_opponents(league: LeagueManager, self_model: str, k=3):
    if self_model not in league.state:
        return []

    self_elo = league.state[self_model]["elo"]

    candidates = [
        m for m, s in league.state.items()
        if s["elo"] >= self_elo and s["elo"] <= self_elo + ELO_WINDOW
        and os.path.exists(m)
    ]

    candidates = sorted(
        candidates,
        key=lambda m: league.state[m]["elo"]
    )

    return candidates[:k]


def main():
    print("\n==============================")
    print("Stage 8.6 — ELO-Gated Self-Play")
    print("==============================\n")

    os.makedirs(SAVE_DIR, exist_ok=True)
    league = LeagueManager()

    league.register(BASE_MODEL)

    opponents = select_elo_opponents(league, BASE_MODEL, k=3)

    if not opponents:
        opponents = [BASE_MODEL]

    print("[Stage 8.6] Opponents:")
    for o in opponents:
        print(" -", o)

    env = ThousandEnv(opponent_paths=opponents)
    env = Monitor(env)

    model = MaskablePPO.load(
        BASE_MODEL,
        env=env,
        device="cpu",
        learning_rate=LR,
        clip_range=CLIP_RANGE,
        n_steps=4096,
        batch_size=256,
        ent_coef=0.006,
        vf_coef=0.5,
        verbose=1,
    )

    model.learn(
        total_timesteps=TOTAL_TIMESTEPS,
        progress_bar=True,
    )

    save_path = f"{SAVE_DIR}/stage8_6_{int(time.time())}.zip"
    model.save(save_path)
    league.register(save_path)

    print("\n==============================")
    print(f"Stage 8.6 finished. Saved to {save_path}")
    print("==============================\n")


if __name__ == "__main__":
    main()
