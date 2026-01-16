# marriage.py
from cards import Rank
from game_state import Phase


def can_declare_marriage(state, player_id, suit):
    """
    Проверяет, может ли игрок объявить марьяж данной масти
    """
    if state.phase != Phase.PLAY:
        return False
    
    if state.trick_number == 0:
        return False

    if (player_id, suit) in state.marriages_declared:
        return False

    hand = state.hands[player_id]

    has_king = any(c.rank == Rank.KING and c.suit == suit for c in hand)
    has_queen = any(c.rank == Rank.QUEEN and c.suit == suit for c in hand)

    return has_king and has_queen


def declare_marriage(state, player_id, suit):
    """
    Объявляет марьяж:
    - начисляет очки
    - делает масть козырем
    """
    assert can_declare_marriage(state, player_id, suit), "Cannot declare marriage"

    points = state.rules.marriage_points[suit.name]
    points = state.rules.apply_golden_kon(points)

    state.scores[player_id] += points
    state.trump = suit

    state.marriages_declared.add((player_id, suit))
