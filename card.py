"""
card.py - Card Representation for Klondike Solitaire
===================================================

Academic Data Structures & Algorithms Implementation
Defines standard playing cards, suits, ranks, colors, and ANSI visual rendering.
"""

from typing import Optional


class Suit:
    """Suit constants and Unicode symbols for standard 52-card deck."""
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

    # Symbols
    SYMBOLS = {
        HEARTS: "♥",
        DIAMONDS: "♦",
        CLUBS: "♣",
        SPADES: "♠",
    }

    # Standard Solitaire Colors
    COLORS = {
        HEARTS: "Red",
        DIAMONDS: "Red",
        CLUBS: "Black",
        SPADES: "Black",
    }

    # Short codes
    SHORT_CODES = {
        HEARTS: "H",
        DIAMONDS: "D",
        CLUBS: "C",
        SPADES: "S",
    }

    SHORT_TO_SUIT = {
        "H": HEARTS,
        "D": DIAMONDS,
        "C": CLUBS,
        "S": SPADES,
        "♥": HEARTS,
        "♦": DIAMONDS,
        "♣": CLUBS,
        "♠": SPADES,
    }


class Rank:
    """Rank constants (1=Ace to 13=King) and display names."""
    NAMES = {
        1: "A",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
        11: "J",
        12: "Q",
        13: "K",
    }

    FULL_NAMES = {
        1: "Ace",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
        11: "Jack",
        12: "Queen",
        13: "King",
    }

    STRING_TO_RANK = {
        "A": 1,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
    }


class Card:
    """
    Represents an individual playing card in Klondike Solitaire.

    Attributes:
        suit (str): Suit name ('Hearts', 'Diamonds', 'Clubs', 'Spades').
        rank (int): Integer rank from 1 (Ace) to 13 (King).
        is_face_up (bool): Visibility state of the card.
        color (str): 'Red' for Hearts/Diamonds, 'Black' for Clubs/Spades.
        id (str): Unique card identifier (e.g., 'H-A', 'S-10', 'D-K').
    """

    # ANSI Color Escape Codes
    COLOR_RESET = "\033[0m"
    COLOR_RED = "\033[91m"
    COLOR_BLACK = "\033[97m"       # Bright white for dark terminal readability
    COLOR_CARD_BACK = "\033[90m"   # Gray for card back
    COLOR_EMPTY = "\033[38;5;240m" # Muted for empty slots

    def __init__(self, suit: str, rank: int, is_face_up: bool = False):
        if suit not in Suit.SYMBOLS:
            raise ValueError(f"Invalid suit: {suit}")
        if rank < 1 or rank > 13:
            raise ValueError(f"Invalid rank: {rank}. Must be between 1 and 13.")

        self.suit: str = suit
        self.rank: int = rank
        self.is_face_up: bool = is_face_up
        self.color: str = Suit.COLORS[suit]
        self.symbol: str = Suit.SYMBOLS[suit]
        self.short_suit: str = Suit.SHORT_CODES[suit]
        self.rank_str: str = Rank.NAMES[rank]
        self.id: str = f"{self.short_suit}-{self.rank_str}"

    @property
    def is_red(self) -> bool:
        """Returns True if the card is Red (Hearts or Diamonds)."""
        return self.color == "Red"

    @property
    def is_black(self) -> bool:
        """Returns True if the card is Black (Clubs or Spades)."""
        return self.color == "Black"

    def flip(self) -> None:
        """Toggles face-up / face-down orientation."""
        self.is_face_up = not self.is_face_up

    def can_stack_on_tableau(self, target: Optional["Card"]) -> bool:
        """
        Validates Klondike Tableau stacking rules:
        - Must be descending rank: self.rank == target.rank - 1.
        - Must alternate colors: self.color != target.color.
        - If target is None (empty column), only a King (rank 13) can be placed.
        """
        if target is None:
            return self.rank == 13
        return (self.rank == target.rank - 1) and (self.color != target.color)

    def can_stack_on_foundation(self, target_top: Optional["Card"]) -> bool:
        """
        Validates Klondike Foundation stacking rules:
        - If foundation is empty (target_top is None): must be an Ace (rank 1).
        - If foundation is not empty: must be same suit and ascending rank (self.rank == target_top.rank + 1).
        """
        if target_top is None:
            return self.rank == 1
        return (self.suit == target_top.suit) and (self.rank == target_top.rank + 1)

    def display(self, use_color: bool = True) -> str:
        """
        Returns a formatted 5-character string representation of the card.
        Examples:
            Face-up:   '[ 7♥ ]', '[10♠ ]', '[ K♦ ]'
            Face-down: '[ ? ]'
        """
        if not self.is_face_up:
            if use_color:
                return f"{self.COLOR_CARD_BACK}[ ? ]{self.COLOR_RESET}"
            return "[ ? ]"

        # Format rank & symbol to occupy 3 chars inside brackets
        # e.g., ' 7♥' (3 chars), '10♠' (3 chars), ' A♦' (3 chars)
        if len(self.rank_str) == 1:
            core = f" {self.rank_str}{self.symbol}"
        else:
            core = f"{self.rank_str}{self.symbol}"

        if use_color:
            color_code = self.COLOR_RED if self.is_red else self.COLOR_BLACK
            return f"[{color_code}{core}{self.COLOR_RESET}]"
        return f"[{core}]"

    def __str__(self) -> str:
        return self.display(use_color=False)

    def __repr__(self) -> str:
        state = "UP" if self.is_face_up else "DN"
        return f"Card({self.id}, {state})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.suit, self.rank))
