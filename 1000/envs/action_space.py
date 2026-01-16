# envs/action_space.py
from cards import ALL_CARDS, Suit


# ----- Размер -----
ACTION_SIZE = 54


# ----- Индексы -----

# 0–23 : карты
CARD_OFFSET = 0
NUM_CARDS = 24

# 24–27 : марьяжи
MARRIAGE_OFFSET = CARD_OFFSET + NUM_CARDS
NUM_MARRIAGES = 4

# 28–48 : ставки
BID_OFFSET = MARRIAGE_OFFSET + NUM_MARRIAGES
BIDS = list(range(100, 301, 10))  # 100..300
NUM_BIDS = len(BIDS)

# 49 : pass
PASS_ACTION = BID_OFFSET + NUM_BIDS

# 50–53 : козырь
TRUMP_OFFSET = PASS_ACTION + 1
NUM_TRUMPS = 4


# ----- Декодеры -----

def decode_card(action):
    idx = action - CARD_OFFSET
    if 0 <= idx < NUM_CARDS:
        return ALL_CARDS[idx]
    return None


def decode_marriage(action):
    idx = action - MARRIAGE_OFFSET
    if 0 <= idx < NUM_MARRIAGES:
        return list(Suit)[idx]
    return None


def decode_bid(action):
    idx = action - BID_OFFSET
    if 0 <= idx < NUM_BIDS:
        return BIDS[idx]
    if action == PASS_ACTION:
        return "pass"
    return None


def decode_trump(action):
    idx = action - TRUMP_OFFSET
    if 0 <= idx < NUM_TRUMPS:
        return list(Suit)[idx]
    return None
