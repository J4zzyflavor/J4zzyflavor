# play.py
from cards import Rank
from game_state import Phase


# ---------- КОНСТАНТЫ ----------

RANK_STRENGTH = {
    Rank.NINE: 0,
    Rank.JACK: 1,
    Rank.QUEEN: 2,
    Rank.KING: 3,
    Rank.TEN: 4,
    Rank.ACE: 5,
}

CARD_POINTS = {
    Rank.NINE: 0,
    Rank.JACK: 2,
    Rank.QUEEN: 3,
    Rank.KING: 4,
    Rank.TEN: 10,
    Rank.ACE: 11,
}


# ---------- ЛОГИКА ----------

def get_legal_cards(state, player_id):
    hand = state.hands[player_id]

    if not state.current_trick:
        return list(hand)

    lead_suit = state.current_trick[0][1].suit
    same_suit = [c for c in hand if c.suit == lead_suit]

    return same_suit if same_suit else list(hand)


def play_card(state, player_id, card):
    assert state.phase == Phase.PLAY
    assert player_id == state.current_player
    assert card in state.hands[player_id]

    legal_cards = get_legal_cards(state, player_id)
    assert card in legal_cards

    state.hands[player_id].remove(card)
    state.current_trick.append((player_id, card))
    state.played_cards.add(card)

    if len(state.current_trick) == 3:
        finish_trick(state)
    else:
        state.current_player = (state.current_player + 1) % 3


def card_strength(card, lead_suit, trump):
    strength = RANK_STRENGTH[card.rank]

    if trump is not None and card.suit == trump:
        return 100 + strength

    if card.suit == lead_suit:
        return 10 + strength

    return strength


def finish_trick(state):
    trick = state.current_trick
    trump = state.trump
    lead_suit = trick[0][1].suit

    winner_id, _ = max(
        trick,
        key=lambda item: card_strength(
            item[1],
            lead_suit,
            trump
        )
    )

    # --- очки взятки ---
    points = sum(CARD_POINTS[card.rank] for _, card in trick)
    points = state.rules.apply_golden_kon(points)

    state.scores[winner_id] += points

    # --- подготовка следующей ---
    state.current_trick = []
    state.current_player = winner_id
    state.trick_number += 1

    if state.is_round_finished():
        state.phase = Phase.ROUND_END

    state.validate()
