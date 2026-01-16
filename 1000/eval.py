# eval.py
import os
import random
import numpy as np

from sb3_contrib import MaskablePPO

from envs.thousand_env import ThousandEnv


# =========================
# Config
# =========================

MODEL_PATH = "models/stage8_6_1768549415.zip"   # <-- путь к твоей финальной модели
LEAGUE_DIR = "league"                      # папка с league моделями
N_EPISODES = 500                           # 500–1000 достаточно
SEED = 42


# =========================
# Utils
# =========================

def run_eval(env: ThousandEnv, model: MaskablePPO, n_episodes: int) -> dict:
    wins = 0
    rewards = []

    for ep in range(n_episodes):
        obs, _ = env.reset(seed=SEED + ep)
        done = False
        ep_reward = 0.0

        while not done:
            mask = env.get_action_mask()
            action, _ = model.predict(
                obs,
                action_masks=mask,
                deterministic=True,
            )
            obs, reward, done, _, _ = env.step(action)
            ep_reward += reward

        rewards.append(ep_reward)

        # победа = положительный финальный reward
        if ep_reward > 0:
            wins += 1

    return {
        "episodes": n_episodes,
        "winrate": wins / n_episodes,
        "reward_mean": float(np.mean(rewards)),
        "reward_std": float(np.std(rewards)),
    }


def sample_league_models(league_dir: str, k: int = 3):
    if not os.path.exists(league_dir):
        return []

    files = []
    for f in os.listdir(league_dir):
        if not f.endswith(".zip"):
            continue
        if f.startswith("league_sp"):
            continue   # <-- КЛЮЧЕВО
        files.append(os.path.join(league_dir, f))

    if not files:
        return []

    files = sorted(files)
    return files[-k:]   # берём САМЫЕ СИЛЬНЫЕ



# =========================
# Main
# =========================

def main():
    random.seed(SEED)
    np.random.seed(SEED)

    print("\n=========================")
    print("Stage 5 — Evaluation")
    print("=========================\n")

    # ---------- Load agent ----------
    model = MaskablePPO.load(MODEL_PATH)
    print(f"Loaded model: {MODEL_PATH}")

    # =====================================================
    # Eval A — Random opponents
    # =====================================================
    print("\n[Eval A] Random opponents")

    env_random = ThousandEnv(opponent_paths=[])
    res_random = run_eval(env_random, model, N_EPISODES)

    print(
        f"Winrate: {res_random['winrate']:.3f} | "
        f"Reward mean: {res_random['reward_mean']:.3f} | "
        f"Std: {res_random['reward_std']:.3f}"
    )

    # =====================================================
    # Eval B — League opponents
    # =====================================================
    league_models = sample_league_models(LEAGUE_DIR, k=3)

    if not league_models:
        print("\n[Eval B] League — SKIPPED (no models found)")
        return

    print("\n[Eval B] League opponents")
    for path in league_models:
        print(" -", path)

    env_league = ThousandEnv(opponent_paths=league_models)
    res_league = run_eval(env_league, model, N_EPISODES)

    print(
        f"Winrate: {res_league['winrate']:.3f} | "
        f"Reward mean: {res_league['reward_mean']:.3f} | "
        f"Std: {res_league['reward_std']:.3f}"
    )

    # =====================================================
    # Summary
    # =====================================================
    print("\n=========================")
    print("Summary")
    print("=========================")

    print(
        f"Random  | winrate={res_random['winrate']:.3f}, "
        f"reward={res_random['reward_mean']:.3f}"
    )

    if league_models:
        print(
            f"League  | winrate={res_league['winrate']:.3f}, "
            f"reward={res_league['reward_mean']:.3f}"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
