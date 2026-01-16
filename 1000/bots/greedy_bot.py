# bots/greedy_bot.py
from bots.base_bot import BaseBot


class GreedyBot(BaseBot):
    def select_bid(self, state, available_bids):
        numeric_bids = [b for b in available_bids if b != "pass"]
        if not numeric_bids:
            return "pass"
        return max(numeric_bids)

    def select_trump(self, state):
        # козырь = масть с максимальными очками
        suit_points = {}
        for card in state.hands[state.current_player]:
            suit_points[card.suit] = suit_points.get(card.suit, 0) + card.points
        return max(suit_points, key=suit_points.get)

    def select_card(self, state, legal_cards):
        # всегда карта с максимальными очками
        return max(legal_cards, key=lambda c: c.points)

    def select_marriage(self, _state, possible_marriages):
        if possible_marriages:
            return possible_marriages[0]
        return None
