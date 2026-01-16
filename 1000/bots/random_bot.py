# bots/random_bot.py
import random
from bots.base_bot import BaseBot
from cards import Suit


class RandomBot(BaseBot):
    def select_bid(self, state, available_bids):
        return random.choice(available_bids)

    def select_trump(self, state):
        return random.choice(list(Suit))

    def select_card(self, state, legal_cards):
        return random.choice(legal_cards)

    def select_marriage(self, _state, possible_marriages):
        if not possible_marriages:
            return None
        return random.choice(possible_marriages)
