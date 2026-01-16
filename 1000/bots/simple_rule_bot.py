# bots/simple_rule_bot.py
from bots.base_bot import BaseBot
from cards import Rank


class SimpleRuleBot(BaseBot):
    def select_bid(self, state, available_bids):
        # всегда минимальная ставка, если не пас
        numeric_bids = [b for b in available_bids if b != "pass"]
        if not numeric_bids:
            return "pass"
        return numeric_bids[0]

    def select_trump(self, state):
        # выбираем масть, где больше всего карт
        suit_count = {}
        for card in state.hands[state.current_player]:
            suit_count[card.suit] = suit_count.get(card.suit, 0) + 1
        return max(suit_count, key=suit_count.get)

    def select_card(self, state, legal_cards):
        # если можно взять взятку — берём старшей
        def strength(card):
            return card.strength

        return max(legal_cards, key=strength)

    def select_marriage(self, _state, possible_marriages):
        # объявляем марьяж сразу, если есть
        if possible_marriages:
            return possible_marriages[0]
        return None
