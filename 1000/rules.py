# rules.py
from dataclasses import dataclass


@dataclass
class Rules:
    # Базовые правила
    allow_samosval: bool = True          # самосвал на 555
    allow_barrel: bool = True            # бочка (760)
    golden_kon: bool = False             # золотой кон (x2 очки)
    forbid_bidding_if_negative: bool = False

    # Очки за марьяжи
    marriage_points = {
        "SPADES": 40,
        "CLUBS": 60,
        "DIAMONDS": 80,
        "HEARTS": 100,
    }

    # Ключевые пороги
    SAMOSVAL_SCORE: int = 555
    BARREL_SCORE: int = 760
    WIN_SCORE: int = 1000

    # Торги
    MIN_BID: int = 100
    BID_STEP: int = 10
    MAX_BID: int = 300

    def apply_special_rules(self, score: int) -> int:
        """
        Применяет самосвал / бочку к очкам игрока
        """
        if self.allow_samosval and score == self.SAMOSVAL_SCORE:
            return 0

        if self.allow_barrel and score > self.BARREL_SCORE:
            return self.BARREL_SCORE

        return score

    def apply_golden_kon(self, value: int) -> int:
        """
        Умножение очков при золотом коне
        """
        if self.golden_kon:
            return value * 2
        return value
