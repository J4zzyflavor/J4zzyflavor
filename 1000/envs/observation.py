# envs/observation.py
import numpy as np

from cards import ALL_CARDS


# ---------- Вспомогательные ----------

def card_index(card):
    return ALL_CARDS.index(card)


# ---------- Encoder'ы компонентов ----------

def encode_hand(hand):
    vec = np.zeros(24, dtype=np.float32)
    for card in hand:
        vec[card_index(card)] = 1.0
    return vec


def encode_played_cards(_state):
    """
    Истории взяток пока нет в GameState.
    Оставляем заглушку из нулей (forward-compatible).
    """
    return np.zeros(24, dtype=np.float32)


def encode_current_trick(state):
    vec = np.zeros((3, 24), dtype=np.float32)
    for i, (_, card) in enumerate(state.current_trick):
        vec[i, card_index(card)] = 1.0
    return vec.flatten()


def encode_trump(trump):
    vec = np.zeros(4, dtype=np.float32)
    if trump is not None:
        vec[trump.value] = 1.0
    return vec


def encode_scores(state, pid):
    vec = np.zeros(3, dtype=np.float32)
    vec[0] = state.scores[pid]

    opp = [i for i in range(3) if i != pid]
    vec[1] = state.scores[opp[0]]
    vec[2] = state.scores[opp[1]]

    # нормализация
    return vec / 1000.0


def encode_phase(state):
    phases = ["BIDDING", "PICKUP", "PLAY"]
    vec = np.zeros(3, dtype=np.float32)
    if state.phase.name in phases:
        vec[phases.index(state.phase.name)] = 1.0
    return vec


# ---------- Главная функция ----------

def encode_observation(state, pid):
    """
    GameState + current player id -> np.ndarray (133,)
    """
    obs = np.concatenate([
        encode_hand(state.hands[pid]),
        encode_played_cards(state),
        encode_current_trick(state),
        encode_trump(state.trump),
        encode_scores(state, pid),
        encode_phase(state),
    ])
    return obs
