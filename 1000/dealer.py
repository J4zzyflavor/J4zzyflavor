# dealer.py
import random

from cards import ALL_CARDS
from game_state import GameState, Phase


def deal_cards(deck):
    """
    Раздаёт карты:
    - каждому игроку по 7 карт
    - 3 карты в прикуп
    """
    # ✅ СПИСОК, А НЕ СЛОВАРЬ
    hands = [set(), set(), set()]

    for _ in range(7):
        for pid in range(3):
            hands[pid].add(deck.pop())

    pickup_cards = [deck.pop(), deck.pop(), deck.pop()]
    return hands, pickup_cards


def init_game_state(rules=None):
    """
    Создаёт новое состояние игры (новую раздачу).
    """
    state = GameState(rules)

    # --- определяем сдающего ---
    if state.dealer_id is None:
        state.dealer_id = 0
    else:
        state.dealer_id = (state.dealer_id + 1) % 3

    # --- торговлю начинает игрок слева от сдающего ---
    state.current_player = (state.dealer_id + 1) % 3
    state.phase = Phase.BIDDING

    # --- готовим колоду ---
    deck = ALL_CARDS.copy()
    random.shuffle(deck)

    # --- раздача ---
    state.hands, state.pickup_cards = deal_cards(deck)

    # --- инициализация торгов ---
    state.current_bid = 0
    state.bid_winner = None
    state.passed_players = set()

    # 🔒 ПРОВЕРКА ИНВАРИАНТА
    assert all(isinstance(h, set) for h in state.hands), "Hands must be sets"

    return state
