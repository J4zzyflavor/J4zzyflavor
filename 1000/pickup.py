# pickup.py
from game_state import Phase


def apply_pickup(state, trump):
    assert state.bid_winner is not None, "No bidding winner"

    winner = state.bid_winner

    # 1️⃣ Добавляем прикуп победителю
    for card in state.pickup_cards:
        state.hands[winner].add(card)

    state.pickup_cards.clear()

    # 2️⃣ Победитель выбирает 2 карты для раздачи
    # (ПОКА: простая заглушка — первые 2)
    cards_to_give = list(state.hands[winner])[:2]

    next_player = (winner + 1) % 3
    next_next_player = (winner + 2) % 3

    state.hands[winner].remove(cards_to_give[0])
    state.hands[winner].remove(cards_to_give[1])

    state.hands[next_player].add(cards_to_give[0])
    state.hands[next_next_player].add(cards_to_give[1])

    # 3️⃣ Устанавливаем козырь
    state.trump = trump

    # 4️⃣ Переход к игре
    state.phase = Phase.PLAY
    state.current_player = winner

    # 5️⃣ Проверка целостности
    state.validate()
