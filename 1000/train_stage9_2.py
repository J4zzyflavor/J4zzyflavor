# train_stage9_2.py
import time
import random
from sb3_contrib import MaskablePPO

from envs.thousand_env import ThousandEnv
from league_manager import LeagueManager


# =========================
# CONFIG
# =========================

POPULATION_SIZE = 4          # сколько агентов в волне
TOTAL_TIMESTEPS = 600_000
SURVIVAL_WINRATE = 0.52
EVAL_EPISODES = 200

LR = 5e-6
CLIP_RANGE = 0.03
ENT_COEF = 0.015


# =========================
# Main
# =========================

def train_one(seed: int, opponents: list, league: LeagueManager):
    print(f"\n--- Training agent seed={seed} ---")

    env = ThousandEnv(
        opponent_paths=opponents,
        force_agent_first=True,
        anti_draw_reward=True,
    )

    model = MaskablePPO(
        "MlpPolicy",
        env,
        learning_rate=LR,
        clip_range=CLIP_RANGE,
        ent_coef=ENT_COEF,
        seed=seed,
        verbose=1,
    )

    model.learn(total_timesteps=TOTAL_TIMESTEPS)

    name = f"models/stage9_2_{int(time.time())}_{seed}.zip"
    model.save(name)

    # ---- survival test ----
    wins = 0
    for ep in range(EVAL_EPISODES):
        env.opponent_paths = opponents
        obs, _ = env.reset(seed=ep)
        done = False
        ep_reward = 0.0

        while not done:
            mask = env.get_action_mask()
            action, _ = model.predict(
                obs, action_masks=mask, deterministic=True
            )
            obs, reward, done, _, _ = env.step(action)
            ep_reward += reward

        if ep_reward > 0:
            wins += 1

    winrate = wins / EVAL_EPISODES
    print(f"Survival winrate = {winrate:.3f}")

    if winrate >= SURVIVAL_WINRATE:
        print("✔ Survived → added to league")
        for opp in opponents:
            league.update(name, opp, 1.0)
    else:
        print("✘ Discarded")


def main():
    print("\n==============================")
    print("Stage 9.2 — Population Growth")
    print("==============================\n")

    league = LeagueManager()
    opponents = league.top_models(k=3)

    for i in range(POPULATION_SIZE):
        seed = random.randint(0, 10_000_000)
        train_one(seed, opponents, league)

    print("\nStage 9.2 finished.")


if __name__ == "__main__":
    main()
