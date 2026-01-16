# cards.py
from dataclasses import dataclass
from enum import Enum, IntEnum


class Suit(Enum):
    SPADES = 0
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3


class Rank(IntEnum):
    NINE = 0
    TEN = 1
    JACK = 2
    QUEEN = 3
    KING = 4
    ACE = 5


@dataclass(frozen=True)
class Card:
    suit: Suit
    rank: Rank

    def __str__(self):
        return f"{self.rank.name}_OF_{self.suit.name}"


# Фиксированный порядок карт (24 штуки)
ALL_CARDS = [
    Card(suit, rank)
    for suit in Suit
    for rank in Rank
]
