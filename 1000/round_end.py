# round_end.py
from game_state import Phase


def finish_round(state):
    """
    Завершает кон:
    - проверяет выполнение ставки
    - начисляет штраф при провале
    - применяет самосвал / бочку
    - проверяет победу
    - подготавливает следующий кон
    """

    assert state.phase == Phase.ROUND_END, "Round is not finished yet"
    assert state.bid_winner is not None, "No bidding winner"

    winner = state.bid_winner
    bid = state.current_bid

    # Очки, набранные победителем торгов за кон
    scored_points = state.scores[winner]

    # Проверка выполнения ставки
    if scored_points < bid:
        penalty = bid

        # Золотой кон удваивает штраф
        penalty = state.rules.apply_golden_kon(penalty)

        state.scores[winner] -= penalty

    # Применяем специальные правила ко всем игрокам
    for pid in range(3):
        state.scores[pid] = state.rules.apply_special_rules(
            state.scores[pid]
        )

    # Проверка победы
    winners = []
    for pid, score in enumerate(state.scores):
        if score >= state.rules.WIN_SCORE:
            winners.append(pid)

    # Подготовка к следующему кону
    state.phase = Phase.BIDDING
    state.current_bid = 0
    state.bid_winner = None
    state.bidding_history = []
    state.passed_players = set()
    state.pickup_cards = []
    state.current_trick = []
    state.played_cards = set()
    state.trick_number = 0
    state.trump = None
    state.marriages_declared = set()

    # Сдающий переходит по кругу
    state.dealer_id = (state.dealer_id + 1) % 3
    state.current_player = (state.dealer_id + 1) % 3

    return winners
