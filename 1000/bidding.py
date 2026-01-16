# bidding.py
from game_state import Phase


def get_available_bids(state, player_id):
    bids = []

    rules = state.rules
    current_bid = state.current_bid
    score = state.scores[player_id]

    on_barrel = rules.allow_barrel and score >= rules.BARREL_SCORE

    # минимальная ставка
    if current_bid == 0:
        min_bid = rules.MIN_BID
        if on_barrel:
            min_bid = max(min_bid, 120)
    else:
        min_bid = current_bid + rules.BID_STEP
        if on_barrel:
            min_bid = max(min_bid, 120)

    bid = min_bid
    while bid <= rules.MAX_BID:
        bids.append(bid)
        bid += rules.BID_STEP

    # pass
    if not (on_barrel and current_bid == 0):
        bids.append("pass")

    return bids


def apply_bid(state, player_id, bid):
    # игрок пасует
    if bid == "pass":
        state.passed_players.add(player_id)
    else:
        # игрок делает ставку
        state.current_bid = bid
        state.bid_winner = player_id

    # если двое спасовали — торги закончены
    if len(state.passed_players) >= 2 and state.bid_winner is not None:
        finish_bidding(state)
        return

    # следующий игрок по часовой стрелке
    state.current_player = (state.current_player + 1) % 3

def finish_bidding(state):
    state.current_player = state.bid_winner
    state.phase = Phase.PICKUP

