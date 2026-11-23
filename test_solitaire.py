"""
test_solitaire.py - Academic Unit Tests for Klondike Solitaire
=============================================================

Comprehensive test suite verifying:
1. Custom Data Structures (Node, Stack, Queue, DoublyLinkedList split & splice).
2. Card mechanics and validation rules.
3. Solitaire engine setup, moves, card reveals, scoring, and win detection.
4. Dual-stack Undo and Redo operations.
5. Strategic hint suggestions.
"""

import unittest
from card import Card, Suit, Rank
from data_structures import Node, Stack, Queue, DoublyLinkedList
from solitaire import KlondikeSolitaire, MoveType


class TestDataStructures(unittest.TestCase):
    """Verifies academic pointer-based custom data structures."""

    def test_node_pointers(self):
        n1 = Node(10)
        n2 = Node(20, next_node=None, prev_node=n1)
        n1.next = n2
        self.assertEqual(n1.data, 10)
        self.assertEqual(n1.next.data, 20)
        self.assertEqual(n2.prev.data, 10)

    def test_stack_lifo(self):
        s: Stack[int] = Stack[int]()
        self.assertTrue(s.is_empty())
        self.assertEqual(s.size(), 0)
        self.assertIsNone(s.peek())

        # Underflow check
        with self.assertRaises(IndexError):
            s.pop()

        # Push elements
        s.push(100)
        s.push(200)
        s.push(300)
        self.assertFalse(s.is_empty())
        self.assertEqual(s.size(), 3)
        self.assertEqual(s.peek(), 300)

        # Pop elements (LIFO order)
        self.assertEqual(s.pop(), 300)
        self.assertEqual(s.pop(), 200)
        self.assertEqual(s.size(), 1)
        self.assertEqual(s.peek(), 100)
        self.assertEqual(s.pop(), 100)
        self.assertTrue(s.is_empty())

    def test_queue_fifo(self):
        q: Queue[str] = Queue[str]()
        self.assertTrue(q.is_empty())
        self.assertEqual(q.size(), 0)
        self.assertIsNone(q.peek())

        # Underflow check
        with self.assertRaises(IndexError):
            q.dequeue()

        # Enqueue elements
        q.enqueue("first")
        q.enqueue("second")
        q.enqueue("third")
        self.assertFalse(q.is_empty())
        self.assertEqual(q.size(), 3)
        self.assertEqual(q.peek(), "first")

        # Dequeue elements (FIFO order)
        self.assertEqual(q.dequeue(), "first")
        self.assertEqual(q.dequeue(), "second")
        self.assertEqual(q.size(), 1)
        self.assertEqual(q.peek(), "third")

        # Test prepend (for LIFO undo of FIFO queue)
        q.prepend("restored_front")
        self.assertEqual(q.size(), 2)
        self.assertEqual(q.peek(), "restored_front")
        self.assertEqual(q.dequeue(), "restored_front")
        self.assertEqual(q.dequeue(), "third")
        self.assertTrue(q.is_empty())

    def test_doubly_linked_list_basic_operations(self):
        dll: DoublyLinkedList[int] = DoublyLinkedList[int]()
        self.assertTrue(dll.is_empty())
        self.assertEqual(dll.size(), 0)
        self.assertIsNone(dll.peek_head())
        self.assertIsNone(dll.peek_tail())

        # Append
        dll.append(1)
        dll.append(2)
        dll.append(3)
        self.assertEqual(dll.size(), 3)
        self.assertEqual(dll.peek_head(), 1)
        self.assertEqual(dll.peek_tail(), 3)
        self.assertEqual(dll.to_list(), [1, 2, 3])

        # Prepend
        dll.prepend(0)
        self.assertEqual(dll.size(), 4)
        self.assertEqual(dll.peek_head(), 0)
        self.assertEqual(dll.to_list(), [0, 1, 2, 3])

        # Pop tail
        self.assertEqual(dll.pop_tail(), 3)
        self.assertEqual(dll.size(), 3)
        self.assertEqual(dll.peek_tail(), 2)
        self.assertEqual(dll.to_list(), [0, 1, 2])

        # Pop head
        self.assertEqual(dll.pop_head(), 0)
        self.assertEqual(dll.size(), 2)
        self.assertEqual(dll.peek_head(), 1)
        self.assertEqual(dll.to_list(), [1, 2])

        # Contains
        self.assertTrue(1 in dll)
        self.assertTrue(2 in dll)
        self.assertFalse(99 in dll)

        # Pop remaining
        self.assertEqual(dll.pop_tail(), 2)
        self.assertEqual(dll.pop_tail(), 1)
        self.assertTrue(dll.is_empty())

        with self.assertRaises(IndexError):
            dll.pop_tail()
        with self.assertRaises(IndexError):
            dll.pop_head()

    def test_doubly_linked_list_split_and_splice(self):
        """
        Academic test verifying O(1) pointer slicing and O(1) splicing
        used for multi-card runs in Tableau columns.
        """
        dll1: DoublyLinkedList[str] = DoublyLinkedList[str]()
        for item in ["A", "B", "C", "D", "E"]:
            dll1.append(item)

        self.assertEqual(dll1.to_list(), ["A", "B", "C", "D", "E"])
        self.assertEqual(dll1.size(), 5)

        # Locate node "C"
        node_c = dll1.find_node("C")
        self.assertIsNotNone(node_c)

        # Split sublist starting from "C"
        sublist = dll1.split_sublist(node_c)

        # dll1 should now contain ["A", "B"]
        self.assertEqual(dll1.to_list(), ["A", "B"])
        self.assertEqual(dll1.size(), 2)
        self.assertEqual(dll1.peek_tail(), "B")
        self.assertIsNone(dll1.tail.next)

        # sublist should contain ["C", "D", "E"]
        self.assertEqual(sublist.to_list(), ["C", "D", "E"])
        self.assertEqual(sublist.size(), 3)
        self.assertEqual(sublist.peek_head(), "C")
        self.assertEqual(sublist.peek_tail(), "E")
        self.assertIsNone(sublist.head.prev)
        self.assertIsNone(sublist.tail.next)

        # Splice sublist onto target dll2: ["X", "Y"]
        dll2: DoublyLinkedList[str] = DoublyLinkedList[str]()
        dll2.append("X")
        dll2.append("Y")

        dll2.splice(sublist)

        # dll2 should now contain ["X", "Y", "C", "D", "E"]
        self.assertEqual(dll2.to_list(), ["X", "Y", "C", "D", "E"])
        self.assertEqual(dll2.size(), 5)
        self.assertEqual(dll2.peek_head(), "X")
        self.assertEqual(dll2.peek_tail(), "E")

        # sublist should now be cleanly emptied
        self.assertTrue(sublist.is_empty())
        self.assertEqual(sublist.size(), 0)
        self.assertIsNone(sublist.head)
        self.assertIsNone(sublist.tail)


class TestCard(unittest.TestCase):
    """Verifies Card properties and stacking logic."""

    def test_card_initialization(self):
        c = Card(Suit.HEARTS, 10, is_face_up=True)
        self.assertEqual(c.suit, Suit.HEARTS)
        self.assertEqual(c.rank, 10)
        self.assertEqual(c.color, "Red")
        self.assertEqual(c.rank_str, "10")
        self.assertEqual(c.id, "H-10")
        self.assertTrue(c.is_face_up)

    def test_tableau_stacking_rules(self):
        red_king = Card(Suit.HEARTS, 13, is_face_up=True)
        black_king = Card(Suit.SPADES, 13, is_face_up=True)
        black_queen = Card(Suit.SPADES, 12, is_face_up=True)
        red_queen = Card(Suit.DIAMONDS, 12, is_face_up=True)
        red_jack = Card(Suit.HEARTS, 11, is_face_up=True)

        # Empty column (None): Only Kings allowed
        self.assertTrue(red_king.can_stack_on_tableau(None))
        self.assertTrue(black_king.can_stack_on_tableau(None))
        self.assertFalse(red_queen.can_stack_on_tableau(None))

        # Alternating color & descending rank (12 onto 13)
        self.assertTrue(black_queen.can_stack_on_tableau(red_king))
        self.assertFalse(red_queen.can_stack_on_tableau(red_king))  # Same color (Red on Red)
        self.assertFalse(red_jack.can_stack_on_tableau(red_king))   # Wrong rank (11 on 13)

    def test_foundation_stacking_rules(self):
        ace_hearts = Card(Suit.HEARTS, 1, is_face_up=True)
        two_hearts = Card(Suit.HEARTS, 2, is_face_up=True)
        two_spades = Card(Suit.SPADES, 2, is_face_up=True)
        three_hearts = Card(Suit.HEARTS, 3, is_face_up=True)

        # Empty foundation: Only Ace allowed
        self.assertTrue(ace_hearts.can_stack_on_foundation(None))
        self.assertFalse(two_hearts.can_stack_on_foundation(None))

        # Ascending rank with matching suit
        self.assertTrue(two_hearts.can_stack_on_foundation(ace_hearts))
        self.assertFalse(two_spades.can_stack_on_foundation(ace_hearts))  # Wrong suit
        self.assertFalse(three_hearts.can_stack_on_foundation(ace_hearts)) # Wrong rank


class TestKlondikeSolitaire(unittest.TestCase):
    """Verifies complete game state, moves, undo/redo, scoring, and hints."""

    def setUp(self):
        # Use deterministic seed for reproducible tests
        self.game = KlondikeSolitaire(seed=42)

    def test_initial_deal_specifications(self):
        """
        Tableau setup: 7 columns. Column i (1 to 7) has i cards.
        Only bottom/tail card of each column is face-up.
        Remaining 24 cards in Stock Queue. Waste empty. Foundations empty.
        Total = 52 cards.
        """
        # Tableau columns
        total_tableau_cards = 0
        for col_idx in range(7):
            col = self.game.tableaux[col_idx]
            expected_count = col_idx + 1
            self.assertEqual(col.size(), expected_count)
            total_tableau_cards += col.size()

            # Verify face-down vs face-up
            curr = col.head
            idx = 0
            while curr is not None:
                is_last = (idx == expected_count - 1)
                self.assertEqual(curr.data.is_face_up, is_last)
                curr = curr.next
                idx += 1

        self.assertEqual(total_tableau_cards, 28)

        # Stockpile Queue
        self.assertEqual(self.game.stock.size(), 24)
        for card in self.game.stock:
            self.assertFalse(card.is_face_up)

        # Waste Stack
        self.assertTrue(self.game.waste.is_empty())

        # Foundations
        for f in self.game.foundations.values():
            self.assertTrue(f.is_empty())

        # Registry has all 52 cards
        self.assertEqual(len(self.game.card_registry), 52)

    def test_draw_and_recycle(self):
        initial_stock_size = self.game.stock.size()
        self.assertEqual(initial_stock_size, 24)

        # Draw 1 card
        success, msg = self.game.draw()
        self.assertTrue(success)
        self.assertEqual(self.game.stock.size(), 23)
        self.assertEqual(self.game.waste.size(), 1)
        self.assertTrue(self.game.waste.peek().is_face_up)

        # Draw all remaining cards
        while not self.game.stock.is_empty():
            self.game.draw()

        self.assertEqual(self.game.stock.size(), 0)
        self.assertEqual(self.game.waste.size(), 24)

        # Recycle
        success, msg = self.game.draw()
        self.assertTrue(success)
        self.assertEqual(self.game.stock.size(), 24)
        self.assertEqual(self.game.waste.size(), 0)

    def test_undo_and_redo_draw(self):
        initial_stock_size = self.game.stock.size()
        success, _ = self.game.draw()
        self.assertTrue(success)
        self.assertEqual(self.game.stock.size(), initial_stock_size - 1)
        self.assertEqual(self.game.waste.size(), 1)

        # Undo DRAW
        undo_ok, _ = self.game.undo()
        self.assertTrue(undo_ok)
        self.assertEqual(self.game.stock.size(), initial_stock_size)
        self.assertEqual(self.game.waste.size(), 0)

        # Redo DRAW
        redo_ok, _ = self.game.redo()
        self.assertTrue(redo_ok)
        self.assertEqual(self.game.stock.size(), initial_stock_size - 1)
        self.assertEqual(self.game.waste.size(), 1)

    def test_undo_and_redo_recycle(self):
        """Verifies that undoing and redoing RECYCLE preserves exact order of cards."""
        # Empty stock completely into waste
        while not self.game.stock.is_empty():
            self.game.draw()

        original_waste_order = [c.id for c in self.game.waste.to_list()]
        original_top_card = self.game.waste.peek().id

        # Execute Recycle
        success, _ = self.game.draw()
        self.assertTrue(success)
        self.assertEqual(self.game.stock.size(), 24)
        self.assertEqual(self.game.waste.size(), 0)

        # Undo Recycle
        undo_ok, _ = self.game.undo()
        self.assertTrue(undo_ok)
        self.assertEqual(self.game.stock.size(), 0)
        self.assertEqual(self.game.waste.size(), 24)
        self.assertEqual(self.game.waste.peek().id, original_top_card)
        self.assertEqual([c.id for c in self.game.waste.to_list()], original_waste_order)

        # Redo Recycle
        redo_ok, _ = self.game.redo()
        self.assertTrue(redo_ok)
        self.assertEqual(self.game.stock.size(), 24)
        self.assertEqual(self.game.waste.size(), 0)

    def test_tableau_to_tableau_and_undo(self):
        """
        Manually construct a deterministic tableau state to test sublist slice,
        splice, card reveal, score update, and undo reversal.
        """
        col0 = self.game.tableaux[0]
        col1 = self.game.tableaux[1]

        col0.clear()
        col1.clear()

        # Col 0: Face-down card + Red 8 (face-up)
        c_hidden = Card(Suit.CLUBS, 5, is_face_up=False)
        c_red8 = Card(Suit.HEARTS, 8, is_face_up=True)
        col0.append(c_hidden)
        col0.append(c_red8)

        # Col 1: Black 9 (face-up)
        c_black9 = Card(Suit.SPADES, 9, is_face_up=True)
        col1.append(c_black9)

        initial_moves = self.game.moves_count
        initial_score = self.game.score

        # Move Red 8 from Col 0 to Col 1 (onto Black 9)
        success, msg = self.game.tableau_to_tableau(0, "H-8", 1)
        self.assertTrue(success)

        # Col 1 should now have Black 9 -> Red 8
        self.assertEqual(col1.size(), 2)
        self.assertEqual(col1.peek_tail().id, "H-8")

        # Col 0 should now have only c_hidden, which must be auto-flipped to face-up!
        self.assertEqual(col0.size(), 1)
        self.assertTrue(col0.peek_tail().is_face_up)
        self.assertEqual(self.game.moves_count, initial_moves + 1)
        self.assertEqual(self.game.score, initial_score + 5)  # +5 for revealing card

        # Test Undo: Red 8 moves back, c_hidden is flipped back to face-down!
        undo_ok, _ = self.game.undo()
        self.assertTrue(undo_ok)
        self.assertEqual(col1.size(), 1)
        self.assertEqual(col0.size(), 2)
        self.assertEqual(col0.peek_tail().id, "H-8")
        self.assertFalse(c_hidden.is_face_up)  # Restored to face-down
        self.assertEqual(self.game.score, initial_score)

    def test_tableau_to_foundation_and_win_condition(self):
        """
        Tests moving card to foundation and triggering victory condition.
        """
        col0 = self.game.tableaux[0]
        col0.clear()
        ace_h = Card(Suit.HEARTS, 1, is_face_up=True)
        col0.append(ace_h)

        success, msg = self.game.tableau_to_foundation(0)
        self.assertTrue(success)
        self.assertEqual(self.game.foundations[Suit.HEARTS].size(), 1)
        self.assertEqual(self.game.foundations[Suit.HEARTS].peek().id, "H-A")

        # Undo
        self.game.undo()
        self.assertEqual(self.game.foundations[Suit.HEARTS].size(), 0)
        self.assertEqual(col0.peek_tail().id, "H-A")

    def test_multi_card_tableau_move(self):
        """Tests moving a multi-card face-up run from one column to another."""
        col0 = self.game.tableaux[0]
        col1 = self.game.tableaux[1]
        col0.clear()
        col1.clear()

        # Col 0: 7♥ -> 6♠ -> 5♦
        c7 = Card(Suit.HEARTS, 7, is_face_up=True)
        c6 = Card(Suit.SPADES, 6, is_face_up=True)
        c5 = Card(Suit.DIAMONDS, 5, is_face_up=True)
        col0.append(c7)
        col0.append(c6)
        col0.append(c5)

        # Col 1: 8♣
        c8 = Card(Suit.CLUBS, 8, is_face_up=True)
        col1.append(c8)

        # Move the entire 3-card run from col0 to col1
        success, msg = self.game.tableau_to_tableau(0, "H-7", 1)
        self.assertTrue(success)
        self.assertEqual(col0.size(), 0)
        self.assertEqual(col1.size(), 4)
        self.assertEqual([c.id for c in col1.to_list()], ["C-8", "H-7", "S-6", "D-5"])

        # Undo the 3-card run move
        undo_ok, _ = self.game.undo()
        self.assertTrue(undo_ok)
        self.assertEqual(col0.size(), 3)
        self.assertEqual(col1.size(), 1)
        self.assertEqual([c.id for c in col0.to_list()], ["H-7", "S-6", "D-5"])
        self.assertEqual([c.id for c in col1.to_list()], ["C-8"])

    def test_foundation_to_tableau_and_undo(self):
        """Tests moving a card from foundation back to tableau and undoing."""
        col0 = self.game.tableaux[0]
        col0.clear()
        col0.append(Card(Suit.SPADES, 5, is_face_up=True))

        foundation = self.game.foundations[Suit.HEARTS]
        foundation.clear()
        foundation.push(Card(Suit.HEARTS, 1, is_face_up=True))
        foundation.push(Card(Suit.HEARTS, 2, is_face_up=True))
        foundation.push(Card(Suit.HEARTS, 3, is_face_up=True))
        foundation.push(Card(Suit.HEARTS, 4, is_face_up=True))

        initial_score = self.game.score
        # Move 4♥ from foundation to col0 (onto 5♠)
        success, msg = self.game.foundation_to_tableau("H", 0)
        self.assertTrue(success)
        self.assertEqual(foundation.size(), 3)
        self.assertEqual(col0.size(), 2)
        self.assertEqual(col0.peek_tail().id, "H-4")
        self.assertEqual(self.game.score, max(0, initial_score - 15))

        # Undo
        undo_ok, _ = self.game.undo()
        self.assertTrue(undo_ok)
        self.assertEqual(foundation.size(), 4)
        self.assertEqual(foundation.peek().id, "H-4")
        self.assertEqual(col0.size(), 1)

    def test_waste_to_tableau_and_foundation(self):
        """Tests waste card movement to tableau and foundation."""
        self.game.waste.clear()
        # Push Ace of Clubs to waste
        ace_c = Card(Suit.CLUBS, 1, is_face_up=True)
        self.game.waste.push(ace_c)

        # Move to foundation
        success, msg = self.game.waste_to_foundation()
        self.assertTrue(success)
        self.assertEqual(self.game.foundations[Suit.CLUBS].size(), 1)
        self.assertTrue(self.game.waste.is_empty())

        # Undo
        self.game.undo()
        self.assertEqual(self.game.waste.size(), 1)
        self.assertEqual(self.game.foundations[Suit.CLUBS].size(), 0)

        # Move to empty tableau column: Ace cannot go to empty column (only King)
        col_empty = self.game.tableaux[0]
        col_empty.clear()
        success, err = self.game.waste_to_tableau(0)
        self.assertFalse(success)

        # Replace waste with King
        self.game.waste.clear()
        king_d = Card(Suit.DIAMONDS, 13, is_face_up=True)
        self.game.waste.push(king_d)
        success, msg = self.game.waste_to_tableau(0)
        self.assertTrue(success)
        self.assertEqual(col_empty.size(), 1)
        self.assertEqual(col_empty.peek_tail().id, "D-K")

    def test_win_condition_full(self):
        """Verifies victory condition triggers when 52 cards are on foundations."""
        for suit in [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]:
            f = self.game.foundations[suit]
            f.clear()
            for r in range(1, 14):
                f.push(Card(suit, r, is_face_up=True))

        self.assertTrue(self.game._check_win_condition())
        self.assertTrue(self.game.is_game_won)

    def test_hint_engine(self):
        """Verifies hint generator produces actionable hints without crashing."""
        hints = self.game.get_hints()
        self.assertIsInstance(hints, list)
        self.assertGreater(len(hints), 0)
        top_hint = hints[0]
        self.assertIsNotNone(top_hint.command_suggestion)
        self.assertIsNotNone(top_hint.description)


if __name__ == "__main__":
    unittest.main()

