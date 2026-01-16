from dataclasses import dataclass, field
from enum import Enum
from rules import Rules


class Phase(Enum):
    BIDDING = 0
    PICKUP = 1
    REDISTRIBUTION = 2
    PLAY = 3
    ROUND_END = 4


@dataclass
class GameState:
    rules: Rules
    phase: Phase = Phase.BIDDING

    hands: object = field(default_factory=lambda: {
        0: set(),
        1: set(),
        2: set(),
    })
    scores: object = field(default_factory=lambda: [0, 0, 0])

    dealer_id: object = None
    current_player: int = 0

    current_bid: int = 0
    bid_winner: object = None
    bidding_history: object = field(default_factory=list)
    passed_players: object = field(default_factory=set)

    pickup_cards: object = field(default_factory=list)

    trump: object = None
    marriages_declared: object = field(default_factory=set)

    current_trick: object = field(default_factory=list)
    played_cards: object = field(default_factory=set)

    trick_number: int = 0



    # ================== ПРОВЕРКИ ==================

    def validate(self):
        """
        Проверяет целостность состояния игры.
        Использовать для отладки и тестов.
        """

        total_cards = 0
        for hand in self.hands:
            total_cards += len(hand)

        total_cards += len(self.played_cards)
        total_cards += len(self.pickup_cards)
        total_cards += len(self.current_trick)

        assert total_cards <= 24, f"Too many cards in game: {total_cards}"

        all_cards = []

        for hand in self.hands:
            all_cards.extend(hand)

        all_cards.extend(self.played_cards)
        all_cards.extend(self.pickup_cards)
        all_cards.extend([card for _, card in self.current_trick])

        assert len(all_cards) == len(set(all_cards)), "Duplicate card detected"

        assert 0 <= self.current_player < 3, "Invalid current_player index"

    # ================== УТИЛИТЫ ==================

    def next_player(self):
        return (self.current_player + 1) % 3

    def advance_player(self):
        self.current_player = self.next_player()

    def reset_trick(self):
        self.current_trick.clear()

    def is_round_finished(self):
        return all(len(hand) == 0 for hand in self.hands)

    def debug_state(self):
        """
        Удобный вывод состояния для ручной отладки
        """
        print("\n--- GAME STATE ---")
        print(f"Phase: {self.phase.name}")
        print(f"Current player: {self.current_player}")
        print(f"Dealer: {self.dealer_id}")
        print(f"Scores: {self.scores}")
        print(f"Trump: {self.trump}")
        print(f"Current bid: {self.current_bid}")
        print(f"Bid winner: {self.bid_winner}")
        print(f"Passed players: {self.passed_players}")
        print(f"Pickup cards: {[str(c) for c in self.pickup_cards]}")
        print(f"Current trick: {[(pid, str(c)) for pid, c in self.current_trick]}")

        for i, hand in enumerate(self.hands):
            print(f"Hand {i}: {[str(c) for c in hand]}")
