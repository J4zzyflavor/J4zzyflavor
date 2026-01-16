# train_stage9_3.py
import time
import random
from sb3_contrib import MaskablePPO
from envs.thousand_env import ThousandEnv
from league_manager import LeagueManager

TOTAL_TIMESTEPS = 900_000
SURVIVAL_WINRATE = 0.58
SEEDS = [random.randint(0, 10_000_000) for _ in range(3)]


def run(seed: int):
    print(f"\n--- Stage 9.3 | seed={seed} ---")

    league = LeagueManager()
    opponents = league.top_models(k=5)

    env = ThousandEnv(
        opponent_paths=opponents,
        force_agent_first=False,
        anti_draw_reward=True,
    )

    model = MaskablePPO(
        "MlpPolicy",
        env,
        learning_rate=5e-6,
        clip_range=0.025,
        ent_coef=0.005,
        n_steps=2048,
        batch_size=256,
        verbose=1,
        seed=seed,
    )

    model.learn(total_timesteps=TOTAL_TIMESTEPS)

    name = f"models/stage9_3_{int(time.time())}_{seed}.zip"
    model.save(name)

    wins, games = env.eval_vs(opponents, episodes=300)
    winrate = wins / games
    print(f"Survival winrate = {winrate:.3f}")

    if winrate >= SURVIVAL_WINRATE:
        for opp in opponents:
            league.update(name, opp, 1.0)
        print("✔ Survived → added to league")
    else:
        print("✘ Discarded")


if __name__ == "__main__":
    for s in SEEDS:
        run(s)
