"""
main.py - Interactive CLI Interface for Klondike Solitaire
=========================================================

Academic Data Structures & Algorithms Implementation
Provides an ANSI-colored, Unicode-enhanced terminal interface for playing
Klondike Solitaire with intuitive command parsing, move validation feedback,
dual-stack Undo/Redo, scoring, timers, and strategic hints.
"""

import sys
import os
from typing import List, Optional

from card import Card, Suit, Rank
from solitaire import KlondikeSolitaire, MoveType, Hint


class SolitaireCLI:
    """
    Console UI renderer and command parser for Klondike Solitaire.
    """

    # ANSI Colors & Styles
    HEADER_COLOR = "\033[1;36m"
    SECTION_COLOR = "\033[1;34m"
    LABEL_COLOR = "\033[1;33m"
    SUCCESS_COLOR = "\033[1;32m"
    ERROR_COLOR = "\033[1;31m"
    HINT_COLOR = "\033[1;35m"
    RESET = "\033[0m"
    DIM = "\033[2m"

    def __init__(self) -> None:
        # Enable Windows VT100 ANSI processing & UTF-8 console output
        if sys.platform == "win32":
            os.system("")
            if hasattr(sys.stdout, "reconfigure"):
                try:
                    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
                    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
                except Exception:
                    pass

        self.game = KlondikeSolitaire()
        self.status_message: str = "Welcome to Klondike Solitaire! Enter 'help' for commands or 'd' to draw."
        self.status_is_error: bool = False

    def clear_screen(self) -> None:
        """Clears terminal screen cross-platform."""
        # Print a clean screen break
        os.system("cls" if sys.platform == "win32" else "clear")

    def render_board(self) -> None:
        """
        Renders the complete game state:
        - Top banner (Score, Moves, Elapsed Time, Victory Status)
        - Upper row (Stock, Waste, Foundations)
        - Tableau columns (Cascading vertical display)
        - Status & Feedback message
        """
        self.clear_screen()

        # 1. Header Banner
        total_foundations = sum(f.size() for f in self.game.foundations.values())
        print("=" * 82)
        print(f"{self.HEADER_COLOR}                     ♠ ♥ KLONDIKE SOLITAIRE ♦ ♣{self.RESET}")
        print("=" * 82)
        print(
            f" Score: {self.LABEL_COLOR}{self.game.score:>4}{self.RESET}  |  "
            f"Moves: {self.LABEL_COLOR}{self.game.moves_count:>3}{self.RESET}  |  "
            f"Time: {self.LABEL_COLOR}{self.game.get_formatted_time()}{self.RESET}  |  "
            f"Foundations: {self.LABEL_COLOR}{total_foundations}/52{self.RESET}  |  "
            f"Undo: {self.LABEL_COLOR}{self.game.undo_stack.size()}{self.RESET}  |  "
            f"Redo: {self.LABEL_COLOR}{self.game.redo_stack.size()}{self.RESET}"
        )
        print("-" * 82)

        # 2. Upper Row: Stock, Waste, and Foundations
        # Stock
        stock_count = self.game.stock.size()
        if stock_count > 0:
            stock_str = f"{self.DIM}[O]{self.RESET} ({stock_count:02d})"
        else:
            stock_str = f"{self.DIM}[EMPTY]{self.RESET} "

        # Waste
        waste_top = self.game.waste.peek()
        waste_str = waste_top.display() if waste_top else f"{self.DIM}[ - ]{self.RESET}"

        # Foundations
        f_strs = []
        for suit in [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]:
            sym = Suit.SYMBOLS[suit]
            color_sym = (
                f"{Card.COLOR_RED}{sym}{self.RESET}"
                if suit in [Suit.HEARTS, Suit.DIAMONDS]
                else f"{Card.COLOR_BLACK}{sym}{self.RESET}"
            )
            top = self.game.foundations[suit].peek()
            top_str = top.display() if top else f"{self.DIM}[ - ]{self.RESET}"
            f_strs.append(f"{color_sym}:{top_str}")

        foundations_row = "  ".join(f_strs)

        print(f" {self.SECTION_COLOR}[STOCK]{self.RESET}         {self.SECTION_COLOR}[WASTE]{self.RESET}                    {self.SECTION_COLOR}[FOUNDATIONS]{self.RESET}")
        print(f"  {stock_str}        {waste_str}             {foundations_row}")
        print("-" * 82)

        # 3. Tableau Columns
        # Column headers
        headers = [f" {self.LABEL_COLOR}[T{i + 1}]{self.RESET}   " for i in range(7)]
        print(" " + "".join(headers))

        # Build column card lists
        cols_cards: List[List[Card]] = [t.to_list() for t in self.game.tableaux]
        max_height = max((len(c) for c in cols_cards), default=0)

        if max_height == 0:
            print("  " + "      ".join([f"{self.DIM}[ - ]{self.RESET}"] * 7))
        else:
            for row_idx in range(max_height):
                row_str = " "
                for col_idx in range(7):
                    cards_in_col = cols_cards[col_idx]
                    if row_idx < len(cards_in_col):
                        card = cards_in_col[row_idx]
                        row_str += f"{card.display()}  "
                    else:
                        row_str += "       "
                print(row_str)

        print("=" * 82)

        # 4. Status / Feedback Message
        if self.status_message:
            prefix = f"{self.ERROR_COLOR}[!] " if self.status_is_error else f"{self.SUCCESS_COLOR}[*] "
            print(f"{prefix}{self.status_message}{self.RESET}")
            print("-" * 82)

    def print_help(self) -> None:
        """Displays user guide and command options."""
        print(f"\n{self.HEADER_COLOR}=== KLONDIKE SOLITAIRE - COMMAND REFERENCE ==={self.RESET}")
        print(f"{self.LABEL_COLOR}Draw & Recycle:{self.RESET}")
        print("  d, draw              : Draw next card from Stock (or recycle Waste if Stock is empty)")
        print(f"\n{self.LABEL_COLOR}Waste Moves:{self.RESET}")
        print("  w t <col>            : Move Waste card to Tableau column (1-7) (e.g. 'w t 3' or 'wt 3')")
        print("  w f, wf              : Move Waste card to matching Foundation")
        print(f"\n{self.LABEL_COLOR}Tableau Moves:{self.RESET}")
        print("  t f <col>            : Move exposed card of Tableau (1-7) to Foundation (e.g. 't f 2' or 'tf 2')")
        print("  m <src> <dst>        : Move all movable face-up cards from <src> (1-7) to <dst> (1-7)")
        print("  m <src> <dst> <count>: Move <count> cards from Tableau <src> to <dst> (e.g. 'm 3 5 2')")
        print("  m <src> <dst> <card> : Move run starting at <card> from <src> to <dst> (e.g. 'm 1 2 10H')")
        print(f"\n{self.LABEL_COLOR}Foundation to Tableau:{self.RESET}")
        print("  f t <suit> <col>     : Move top card from Foundation to Tableau (e.g. 'f t H 4' or 'ft H 4')")
        print(f"\n{self.LABEL_COLOR}Assistance & History:{self.RESET}")
        print("  u, undo              : Undo the last move (Dual-Stack command pattern)")
        print("  r, redo              : Redo the last undone move")
        print("  h, hint              : Get strategic move recommendations")
        print("  a, auto              : Automatically move safe cards to foundations")
        print(f"\n{self.LABEL_COLOR}Game Controls:{self.RESET}")
        print("  new [seed]           : Start a new game (optional random seed)")
        print("  help                 : View this command manual")
        print("  q, quit              : Exit game")
        input(f"\n{self.DIM}Press Enter to return to the game...{self.RESET}")

    def display_hints(self, show_all: bool = False) -> None:
        """
        Fetches and displays strategic hints.
        By default, sets the top priority hint directly in the status message box.
        If show_all is True, prints a complete listing of all legal moves.
        """
        hints = self.game.get_hints()
        if not hints:
            self.status_message = "No hints available. No legal moves remain."
            self.status_is_error = True
            return

        top_hint = hints[0]
        self.status_message = f"Hint ({len(hints)} available): {top_hint.description} -> Command: '{top_hint.command_suggestion}'"
        self.status_is_error = False

        if show_all:
            print(f"\n{self.HINT_COLOR}=== ALL STRATEGIC HINTS ({len(hints)} available) ==={self.RESET}")
            for i, h in enumerate(hints, start=1):
                print(f" {i}. [P{h.priority}] {h.description}  -> Command: {self.LABEL_COLOR}{h.command_suggestion}{self.RESET}")
            input(f"\n{self.DIM}Press Enter to return to the game...{self.RESET}")


    def execute_move(self, user_input: str) -> None:
        """Parses and executes a user command string."""
        raw = user_input.strip()
        if not raw:
            return

        tokens = raw.split()
        cmd = tokens[0].lower()

        try:
            # 1. Draw
            if cmd in ["d", "draw"]:
                success, msg = self.game.draw()
                self.status_message = msg
                self.status_is_error = not success

            # 2. Waste to Foundation
            elif cmd in ["wf", "wtofoundation"] or (cmd == "w" and len(tokens) > 1 and tokens[1].lower() == "f"):
                success, msg = self.game.waste_to_foundation()
                self.status_message = msg
                self.status_is_error = not success

            # 3. Waste to Tableau: 'wt 3', 'w t 3', 'w 3'
            elif (
                cmd.startswith("wt")
                or (cmd == "w" and len(tokens) >= 2)
            ):
                target_col_str = None
                if cmd.startswith("wt") and len(cmd) > 2:
                    target_col_str = cmd[2:]
                elif cmd == "wt" and len(tokens) >= 2:
                    target_col_str = tokens[1]
                elif cmd == "w":
                    if tokens[1].lower() == "t" and len(tokens) >= 3:
                        target_col_str = tokens[2]
                    elif tokens[1].isdigit():
                        target_col_str = tokens[1]

                if target_col_str and target_col_str.isdigit():
                    col_idx = int(target_col_str) - 1
                    success, msg = self.game.waste_to_tableau(col_idx)
                    self.status_message = msg
                    self.status_is_error = not success
                else:
                    self.status_message = "Invalid waste move. Usage: 'wt <col>' (e.g. 'wt 3' or 'w t 3')."
                    self.status_is_error = True

            # 4. Tableau to Foundation: 'tf 3', 't f 3'
            elif (
                cmd.startswith("tf")
                or (cmd == "t" and len(tokens) >= 3 and tokens[1].lower() == "f")
            ):
                col_str = None
                if cmd.startswith("tf") and len(cmd) > 2:
                    col_str = cmd[2:]
                elif cmd == "tf" and len(tokens) >= 2:
                    col_str = tokens[1]
                elif cmd == "t" and tokens[1].lower() == "f":
                    col_str = tokens[2]

                if col_str and col_str.isdigit():
                    col_idx = int(col_str) - 1
                    success, msg = self.game.tableau_to_foundation(col_idx)
                    self.status_message = msg
                    self.status_is_error = not success
                else:
                    self.status_message = "Invalid command. Usage: 'tf <col>' (e.g. 'tf 2' or 't f 2')."
                    self.status_is_error = True

            # 5. Foundation to Tableau: 'ft H 3', 'f t H 3'
            elif (
                cmd.startswith("ft")
                or (cmd == "f" and len(tokens) >= 4 and tokens[1].lower() == "t")
            ):
                suit_str = None
                dst_col_str = None
                if cmd == "ft" and len(tokens) >= 3:
                    suit_str = tokens[1]
                    dst_col_str = tokens[2]
                elif cmd == "f" and tokens[1].lower() == "t" and len(tokens) >= 4:
                    suit_str = tokens[2]
                    dst_col_str = tokens[3]

                if suit_str and dst_col_str and dst_col_str.isdigit():
                    dst_col_idx = int(dst_col_str) - 1
                    success, msg = self.game.foundation_to_tableau(suit_str, dst_col_idx)
                    self.status_message = msg
                    self.status_is_error = not success
                else:
                    self.status_message = "Usage: 'ft <suit> <col>' (e.g. 'ft H 3')."
                    self.status_is_error = True

            # 6. Tableau to Tableau Move: 'm <src> <dst> [card_or_count]'
            elif cmd in ["m", "move"]:
                if len(tokens) < 3:
                    self.status_message = "Usage: 'm <src> <dst> [count or card]' (e.g. 'm 1 2' or 'm 3 5 2' or 'm 3 5 10H')."
                    self.status_is_error = True
                    return

                src_str = tokens[1]
                dst_str = tokens[2]

                if not (src_str.isdigit() and dst_str.isdigit()):
                    self.status_message = "Source and destination must be column numbers (1-7)."
                    self.status_is_error = True
                    return

                src_idx = int(src_str) - 1
                dst_idx = int(dst_str) - 1

                # Optional third parameter: count or card code
                if len(tokens) >= 4:
                    param = tokens[3]
                    success, msg = self.game.tableau_to_tableau(src_idx, param, dst_idx)
                else:
                    # Default: try to move all face-up run from src; if that doesn't fit, try moving tail card
                    src_col = self.game.tableaux[src_idx]
                    dst_col = self.game.tableaux[dst_idx]
                    dst_tail = dst_col.peek_tail()

                    # Find first movable card that can fit on dst
                    start_node = None
                    curr = src_col.head
                    while curr is not None:
                        if curr.data.is_face_up and curr.data.can_stack_on_tableau(dst_tail):
                            start_node = curr
                            break
                        curr = curr.next

                    if start_node is not None:
                        success, msg = self.game.tableau_to_tableau(src_idx, start_node, dst_idx)
                    else:
                        # Fallback to tail card to produce clear error message
                        success, msg = self.game.tableau_to_tableau(src_idx, 1, dst_idx)

                self.status_message = msg
                self.status_is_error = not success

            # 7. Undo
            elif cmd in ["u", "undo"]:
                success, msg = self.game.undo()
                self.status_message = msg
                self.status_is_error = not success

            # 8. Redo
            elif cmd in ["r", "redo"]:
                success, msg = self.game.redo()
                self.status_message = msg
                self.status_is_error = not success

            # 9. Hint
            elif cmd in ["h", "hint", "hints"]:
                show_all = len(tokens) > 1 and tokens[1].lower() in ["all", "list", "-a"]
                self.display_hints(show_all=show_all)

            # 10. Auto Step Foundation
            elif cmd in ["a", "auto"]:
                success, msg = self.game.auto_step_foundation()
                self.status_message = msg
                self.status_is_error = not success

            # 11. New Game
            elif cmd in ["new", "restart"]:
                seed_val = int(tokens[1]) if len(tokens) > 1 and tokens[1].isdigit() else None
                self.game.start_new_game(seed=seed_val)
                self.status_message = f"Started a new game{' with seed ' + str(seed_val) if seed_val else ''}."
                self.status_is_error = False

            # 12. Help
            elif cmd in ["help", "?", "man"]:
                self.print_help()

            # 13. Quit
            elif cmd in ["q", "quit", "exit"]:
                print(f"\n{self.HEADER_COLOR}Thank you for playing Klondike Solitaire! Goodbye.{self.RESET}")
                sys.exit(0)

            else:
                self.status_message = f"Unknown command: '{raw}'. Type 'help' for available commands."
                self.status_is_error = True

        except Exception as e:
            self.status_message = f"Error executing command: {str(e)}"
            self.status_is_error = True

    def display_victory_screen(self) -> None:
        """Displays celebration message upon winning."""
        self.render_board()
        print(f"\n{self.SUCCESS_COLOR}" + "=" * 82)
        print("                 CONGRATULATIONS! YOU WON KLONDIKE SOLITAIRE!")
        print(f"       Final Score: {self.game.score} | Moves: {self.game.moves_count} | Time: {self.game.get_formatted_time()}")
        print("=" * 82 + f"{self.RESET}\n")

    def run(self) -> None:
        """Main game loop."""
        while True:
            self.render_board()

            if self.game.is_game_won:
                self.display_victory_screen()
                choice = input(f"{self.LABEL_COLOR}Play again? (y/n): {self.RESET}").strip().lower()
                if choice.startswith("y"):
                    self.game.start_new_game()
                    self.status_message = "New game started!"
                    self.status_is_error = False
                    continue
                else:
                    print(f"\n{self.HEADER_COLOR}Thanks for playing! Goodbye.{self.RESET}")
                    break

            prompt = (
                f"{self.SECTION_COLOR}Command{self.RESET} "
                f"({self.DIM}d=draw, wt=waste->tab, tf=tab->found, m=move, u=undo, h=hint, q=quit{self.RESET}): "
            )
            try:
                user_input = input(prompt)
                self.execute_move(user_input)
            except (KeyboardInterrupt, EOFError):
                print(f"\n\n{self.HEADER_COLOR}Game interrupted. Goodbye!{self.RESET}")
                break


if __name__ == "__main__":
    cli = SolitaireCLI()
    cli.run()
