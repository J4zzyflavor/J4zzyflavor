# train_stage9.py
import time
from sb3_contrib import MaskablePPO
from envs.thousand_env import ThousandEnv
from league_manager import LeagueManager


TOTAL_TIMESTEPS = 800_000
SURVIVAL_WINRATE = 0.55


def main():
    print("\n==============================")
    print("Stage 9 — Population Collapse")
    print("==============================\n")

    league = LeagueManager()
    opponents = league.top_models(k=3)

    env = ThousandEnv(
        opponent_paths=opponents,
        force_agent_first=True,
        anti_draw_reward=True
    )

    model = MaskablePPO(
        "MlpPolicy",
        env,
        learning_rate=5e-6,
        clip_range=0.03,
        ent_coef=0.01,
        verbose=1,
    )

    model.learn(total_timesteps=TOTAL_TIMESTEPS)

    name = f"models/stage9_{int(time.time())}.zip"
    model.save(name)

    # survival test
    wins, games = env.eval_vs(opponents, episodes=200)
    winrate = wins / games

    print(f"\nSurvival winrate: {winrate:.3f}")

    if winrate >= SURVIVAL_WINRATE:
        for opp in opponents:
            league.update(name, opp, 1.0)
        print("✔ Model survived and added to league")
    else:
        print("✘ Model discarded")


if __name__ == "__main__":
    main()
