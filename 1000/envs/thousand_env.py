# envs/thousand_env.py

import random
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from enum import Enum
from typing import List, Dict, Tuple, Optional

from stable_baselines3.common.base_class import BaseAlgorithm
from sb3_contrib import MaskablePPO


# =========================
# Enums
# =========================

class Suit(Enum):
    HEARTS = 0
    DIAMONDS = 1
    CLUBS = 2
    SPADES = 3
    NO_TRUMP = 4


class Phase(Enum):
    BIDDING = 0
    TRUMP_SELECTION = 1
    PLAY = 2
    DONE = 3


# =========================
# Card helpers
# =========================

def card_suit(card: int) -> Suit:
    return Suit(card // 8)


def card_rank(card: int) -> int:
    return card % 8


# =========================
# Environment
# =========================

class ThousandEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(
        self,
        opponent_paths: Optional[List[str]] = None,
        force_agent_first: bool = False,
        anti_draw_reward: bool = False,
    ):
        super().__init__()

        # ---------- CONFIG ----------
        self.num_players = 3
        self.learning_player = 0

        self.force_agent_first = force_agent_first
        self.anti_draw_reward = anti_draw_reward

        # ---------- OPPONENTS ----------
        self.opponent_paths = opponent_paths or []
        self.opponents: Dict[int, BaseAlgorithm] = {}

        # ---------- GAME STATE ----------
        self.phase = Phase.BIDDING
        self.trump: Suit | None = None

        self.hands: List[List[int]] = [[] for _ in range(self.num_players)]
        self.bids: Dict[int, int] = {}
        self.contract_player: int | None = None

        self.trick_cards: List[Tuple[int, int]] = []
        self.tricks_won = [0, 0, 0]

        self.current_player = 0
        self.lead_player = 0

        self.step_count = 0
        self.max_steps = 60
        self.done = False

        # ---------- ACTION SPACE ----------
        self.ACTION_BID_START = 0
        self.ACTION_TRUMP_START = 20
        self.ACTION_CARD_START = 25

        self.action_space = spaces.Discrete(57)

        # ---------- OBS ----------
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(12,), dtype=np.float32
        )

        self.reset()

    # =========================
    # Reset
    # =========================

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        self._sample_opponents()

        self.phase = Phase.BIDDING
        self.done = False
        self.step_count = 0

        if self.force_agent_first:
            self.current_player = self.learning_player
            self.lead_player = self.learning_player
        else:
            self.current_player = 0
            self.lead_player = 0

        self.bids.clear()
        self.tricks_won = [0, 0, 0]
        self.trick_cards.clear()

        self.trump = None
        self.contract_player = None

        deck = list(range(32))
        random.shuffle(deck)

        for i in range(self.num_players):
            self.hands[i] = deck[i * 10:(i + 1) * 10]

        return self._get_obs(), {}

    # =========================
    # Step
    # =========================

    def step(self, action: int):
        reward = 0.0
        self.step_count += 1

        if not self.get_action_mask()[action]:
            if self.current_player == self.learning_player:
                reward -= 0.2
            action = random.choice(self.get_legal_actions())

        # ---------- BIDDING ----------
        if self.phase == Phase.BIDDING:
            bid = 80 + (action - self.ACTION_BID_START) * 5
            self.bids[self.current_player] = bid

            if len(self.bids) == self.num_players:
                self.contract_player = max(self.bids, key=self.bids.get)
                self.current_player = self.contract_player
                self.phase = Phase.TRUMP_SELECTION
            else:
                self._next_player()

        # ---------- TRUMP ----------
        elif self.phase == Phase.TRUMP_SELECTION:
            self.trump = Suit(action - self.ACTION_TRUMP_START)
            self.phase = Phase.PLAY
            self.current_player = self.contract_player
            self.lead_player = self.contract_player

        # ---------- PLAY ----------
        elif self.phase == Phase.PLAY:
            card = action - self.ACTION_CARD_START
            self.hands[self.current_player].remove(card)
            self.trick_cards.append((self.current_player, card))

            if len(self.trick_cards) == self.num_players:
                winner = self._resolve_trick()
                self.tricks_won[winner] += 1

                reward += 0.25 if winner == self.learning_player else -0.05

                self.trick_cards.clear()
                self.current_player = winner
                self.lead_player = winner
            else:
                self._next_player()

            if self._terminal():
                reward += 2.0 * self._resolve_contract()
                self.phase = Phase.DONE
                self.done = True

        if self.step_count >= self.max_steps:
            self.done = True
            reward -= 0.5

        self._maybe_play_opponents()

        if self.done and self.anti_draw_reward and abs(reward) < 1e-6:
            reward -= 0.2

        return self._get_obs(), reward, self.done, False, {}

    # =========================
    # Opponents
    # =========================

    def _sample_opponents(self):
        self.opponents.clear()
        if not self.opponent_paths:
            return

        paths = random.sample(
            self.opponent_paths,
            k=min(2, len(self.opponent_paths))
        )

        for pid, path in zip([1, 2], paths):
            self.opponents[pid] = MaskablePPO.load(path)

    def _maybe_play_opponents(self):
        while not self.done and self.current_player != self.learning_player:
            obs = self._get_obs()
            mask = self.get_action_mask()

            model = self.opponents.get(self.current_player)
            if model is None:
                action = random.choice(self.get_legal_actions())
            else:
                action, _ = model.predict(
                    obs,
                    action_masks=mask,
                    deterministic=True,
                )
            self.step(action)

    # =========================
    # Trick
    # =========================

    def _resolve_trick(self) -> int:
        lead_suit = card_suit(self.trick_cards[0][1])

        def strength(card: int):
            suit = card_suit(card)
            rank = card_rank(card)
            if suit == self.trump:
                return (2, rank)
            if suit == lead_suit:
                return (1, rank)
            return (0, rank)

        return max(self.trick_cards, key=lambda pc: strength(pc[1]))[0]

    # =========================
    # Contract
    # =========================

    def _resolve_contract(self) -> float:
        bid = self.bids[self.contract_player]
        points = self.tricks_won[self.contract_player] * 10
        success = points >= bid

        if self.contract_player == self.learning_player:
            return 1.0 if success else -1.0
        else:
            return -1.0 if success else 1.0

    # =========================
    # Legal actions
    # =========================

    def get_legal_actions(self) -> List[int]:
        if self.phase == Phase.BIDDING:
            return list(range(0, 20))

        if self.phase == Phase.TRUMP_SELECTION:
            return list(range(20, 25))

        if self.phase == Phase.PLAY:
            if not self.trick_cards:
                cards = self.hands[self.current_player]
            else:
                lead = card_suit(self.trick_cards[0][1])
                same = [c for c in self.hands[self.current_player] if card_suit(c) == lead]
                cards = same if same else self.hands[self.current_player]
            return [25 + c for c in cards]

        return []

    def get_action_mask(self) -> np.ndarray:
        mask = np.zeros(self.action_space.n, dtype=np.bool_)
        for a in self.get_legal_actions():
            mask[a] = True
        return mask

    def action_masks(self) -> np.ndarray:
        return self.get_action_mask()

    # =========================
    # Helpers
    # =========================

    def _next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players

    def _terminal(self) -> bool:
        return all(len(h) == 0 for h in self.hands)

    # =========================
    # Observation
    # =========================

    def _get_obs(self) -> np.ndarray:
        obs = []

        obs.append(self.current_player / 2)
        obs.append(self.phase.value / 3)
        obs.append(self.lead_player / 2)

        obs.append(0.0 if self.trump is None else self.trump.value / 4)

        obs.extend([len(self.hands[i]) / 10 for i in range(3)])
        obs.extend([self.tricks_won[i] / 10 for i in range(3)])

        obs.append(1.0 if self.current_player == self.contract_player else 0.0)
        obs.append(
            0.0 if self.contract_player is None
            else (self.tricks_won[self.contract_player] * 10)
                 / max(self.bids[self.contract_player], 1)
        )

        return np.array(obs, dtype=np.float32)

    # =========================
    # Eval hook (Stage 9+)
    # =========================

    def eval_vs(self, opponent_paths, episodes=100):
        wins = 0

        agent = MaskablePPO.load(opponent_paths[0])

        for ep in range(episodes):
            self.opponent_paths = opponent_paths[1:]
            obs, _ = self.reset(seed=ep)
            done = False
            ep_reward = 0.0

            while not done:
                if self.current_player == self.learning_player:
                    mask = self.get_action_mask()
                    action, _ = agent.predict(
                        obs,
                        action_masks=mask,
                        deterministic=True,
                    )
                else:
                    action = random.choice(self.get_legal_actions())

                obs, reward, done, _, _ = self.step(action)
                ep_reward += reward

            if ep_reward > 0:
                wins += 1

        return wins, episodes

