from dealer import init_game_state
from bidding import get_available_bids, apply_bid
from pickup import apply_pickup
from play import play_card, get_legal_cards
from marriage import can_declare_marriage, declare_marriage
from round_end import finish_round
from bots.random_bot import RandomBot
from bots.simple_rule_bot import SimpleRuleBot
from bots.greedy_bot import GreedyBot

bots = [
    SimpleRuleBot(),
    GreedyBot(),
    RandomBot()
]

state = init_game_state()

# Торги
while state.phase.name == "BIDDING":
    pid = state.current_player
    bot = bots[pid]
    bids = get_available_bids(state, pid)
    bid = bot.select_bid(state, bids)
    apply_bid(state, pid, bid)

# Прикуп
trump = bots[state.bid_winner].select_trump(state)
apply_pickup(state, trump)

# Игра
while state.phase.name == "PLAY":
    pid = state.current_player
    bot = bots[pid]

    # Марьяж
    possible = []
    from cards import Suit
    for suit in Suit:
        if can_declare_marriage(state, pid, suit):
            possible.append(suit)

    marriage = bot.select_marriage(state, possible)
    if marriage:
        declare_marriage(state, pid, marriage)

    legal = get_legal_cards(state, pid)
    card = bot.select_card(state, legal)
    play_card(state, pid, card)

# Конец кона
winners = finish_round(state)

print("Final scores:", state.scores)
print("Game winners:", winners)
