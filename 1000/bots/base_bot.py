# bots/base_bot.py

class BaseBot:
    def select_bid(self, state, available_bids):
        """
        Выбор ставки в фазе BIDDING
        """
        raise NotImplementedError

    def select_trump(self, state):
        """
        Выбор козыря после прикупа
        """
        raise NotImplementedError

    def select_card(self, state, legal_cards):
        """
        Выбор карты в фазе PLAY
        """
        raise NotImplementedError

    def select_marriage(self, _state, _possible_marriages):
        """
        Выбор марьяжа (или None)
        """
        return None