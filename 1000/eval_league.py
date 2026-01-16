# eval_league.py
import os
import random
from sb3_contrib import MaskablePPO

from envs.thousand_env import ThousandEnv
from league_manager import LeagueManager


MODEL_PATH = "models/stage7_5_final.zip"
LEAGUE_DIR = "league"
N_EPISODES = 200


def play_match(challenger, opponent_path):
    env = ThousandEnv(opponent_paths=[opponent_path])
    wins = 0

    for _ in range(N_EPISODES):
        obs, _ = env.reset()
        done = False
        total_reward = 0

        while not done:
            mask = env.get_action_mask()
            action, _ = challenger.predict(obs, action_masks=mask, deterministic=True)
            obs, reward, done, _, _ = env.step(action)
            total_reward += reward

        if total_reward > 0:
            wins += 1

    winrate = wins / N_EPISODES

    if winrate > 0.55:
        return 1
    elif winrate < 0.45:
        return 0
    else:
        return 0.5


def main():
    league = LeagueManager()

    challenger = MaskablePPO.load(MODEL_PATH)

    opponents = [
        os.path.join(LEAGUE_DIR, f)
        for f in os.listdir(LEAGUE_DIR)
        if f.endswith(".zip")
    ]

    sampled = random.sample(opponents, k=min(3, len(opponents)))

    for opp in sampled:
        result = play_match(challenger, opp)
        league.update(MODEL_PATH, opp, result)
        print(f"Match vs {opp}: result={result}")

    print("League updated.")


if __name__ == "__main__":
    main()
