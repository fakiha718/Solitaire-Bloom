# Klondike Solitaire - Data Structures & Algorithms (DSA) Mid-Term Project

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Unit%20Tests-19%20Passing%20(100%25)-brightgreen.svg)]()
[![Data Structures](https://img.shields.io/badge/Data%20Structures-From%20Scratch-orange.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-LIFO%20%7C%20FIFO%20%7C%20DLL-purple.svg)]()

---

## 1. Executive Summary

This project is a comprehensive, academic-grade implementation of **Klondike Solitaire** developed strictly from first principles for a **Data Structures and Algorithms (DSA)** course. 

All primary container operations (stacks, queues, and doubly linked lists) are **engineered entirely from scratch** using pointer-based linked node architectures, completely avoiding high-level abstractions (such as `collections.deque`, `queue.Queue`, or Python list manipulation for FIFO/LIFO behaviors).

### Key Technical Achievements
- **Academic Pointers**: Full pointer-based Node implementations with explicit forward (`next`) and backward (`prev`) references.
- **Constant-Time Multi-Card Moves**: $O(1)$ pointer rewiring for Tableau run transfers via custom Doubly Linked List **sublist slicing** and **splicing**.
- **Dual-Stack Command Pattern**: Full reversible state history providing infinite **Undo** and **Redo** capabilities.
- **Exact State Inversion**: Reversal of FIFO queue draws via an $O(1)$ `prepend()` operation and exact stack sequence restoration during stock recycle.
- **Strategic Heuristic Hint Engine**: Prioritized move generator that detects unblocking opportunities, safe foundation placements, and King migrations.
- **Terminal UI**: ANSI-colored, Unicode-rendered board with dynamic status messages and robust command parsing.

---

## 2. System Architecture & DSA Mapping

The following table illustrates how fundamental data structures directly power the Klondike Solitaire game components:

| Solitaire Component | Data Structure | Pointer Architecture | Primary Operations | Time Complexity |
|---|---|---|---|---|
| **Stockpile (Draw Pile)** | `Queue<T>` (FIFO) | Singly Linked (`_head`, `_tail`) | `enqueue()`, `dequeue()`, `prepend()`, `peek()` | $O(1)$ Time, $O(1)$ Space |
| **Waste Pile** | `Stack<T>` (LIFO) | Singly Linked (`_top`) | `push()`, `pop()`, `peek()` | $O(1)$ Time, $O(1)$ Space |
| **4 Foundation Piles** | `Stack<T>` (LIFO) | Singly Linked (`_top`) | `push()`, `pop()`, `peek()` | $O(1)$ Time, $O(1)$ Space |
| **7 Tableau Columns** | `DoublyLinkedList<T>` | Doubly Linked (`head`, `tail`) | `append()`, `pop_tail()`, `split_sublist()`, `splice()` | $O(1)$ Splice, $O(k)$ Slice |
| **Undo / Redo History** | Dual `Stack<MoveRecord>` | Singly Linked (`_top`) | `push()`, `pop()`, `clear()` | $O(1)$ Time, $O(1)$ Space |
| **Card Metadata Registry** | `HashMap` (Dictionary) | Hash Table | `lookup`, `update` | Average $O(1)$ |
| **Initial Deck Generation**| `Array` (Python list) | Contiguous Array | Generation, Fisher-Yates `shuffle()` | $O(52) = O(1)$ |

---

## 3. Data Structure Specifications & Complexity Analysis

### 3.1 `Node<T>` (Pointer Primitive)
Foundational building block supporting both singly and doubly linked topologies:
- `data: T`: Generic payload.
- `next: Optional[Node[T]]`: Forward successor pointer.
- `prev: Optional[Node[T]]`: Backward predecessor pointer.

### 3.2 `Stack<T>` (LIFO)
Maintains a single `_top` reference pointing to the most recently inserted node.
- **`push(item)`**: $O(1)$ — Allocates a new node pointing to the current `_top` and updates `_top`.
- **`pop()`**: $O(1)$ — Advances `_top` to `_top.next` and returns the node's payload. Raises `IndexError` on underflow.
- **`peek()`**: $O(1)$ — Inspects `_top.data` without pointer alteration.
- **`clear()`**: $O(1)$ — Resets `_top = None` and `_size = 0`.

### 3.3 `Queue<T>` (FIFO)
Maintains distinct `_head` (front for dequeue) and `_tail` (rear for enqueue) pointers.
- **`enqueue(item)`**: $O(1)$ — Appends to `_tail.next` and advances `_tail`.
- **`dequeue()`**: $O(1)$ — Removes from `_head` and advances `_head = _head.next`.
- **`prepend(item)`**: $O(1)$ — Inserts at `_head`. **Academic Highlight**: Essential for the exact, constant-time reversal of FIFO draw actions when executing an `undo()`.

### 3.4 `DoublyLinkedList<T>` (Bidirectional Cascading List)
Maintains `head` and `tail` references with bidirectional links across all nodes.
- **`append(item)`**: $O(1)$ — Inserts after `tail` and updates `tail`.
- **`pop_tail()`**: $O(1)$ — Removes `tail`, updating `tail = tail.prev` and disconnecting forward pointer.
- **`pop_head()`**: $O(1)$ — Removes `head`, updating `head = head.next` and disconnecting backward pointer.
- **`split_sublist(start_node)`**: $O(1)$ pointer disconnect, $O(k)$ node traversal where $k$ is slice length to update size. Detaches `start_node` through `tail` into a standalone `DoublyLinkedList`.
- **`splice(other_dll)`**: $O(1)$ — Connects `self.tail.next` to `other_dll.head` and `other_dll.head.prev` to `self.tail`, then sets `self.tail = other_dll.tail`. Transfers all elements with zero array copies.

---

## 4. Klondike Solitaire Mechanics & Rules

### Initial Deal
- **Tableaux**: 7 columns. Column $i$ ($0 \le i \le 6$) contains $i + 1$ cards. Only the bottom/tail card of each column is initially face-up. Total cards in tableaux = 28.
- **Stockpile**: Remaining 24 cards enqueued face-down in the Stock Queue.
- **Waste Pile**: Initially empty.
- **Foundations**: 4 stacks (Hearts $\heartsuit$, Diamonds $\diamondsuit$, Clubs $\clubsuit$, Spades $\spadesuit$), initially empty.

### Movement & Placement Rules
1. **Tableau Stacking**: Cards placed on a tableau column must be in **descending rank** ($R_{\text{card}} = R_{\text{target}} - 1$) and **alternating colors** (Red on Black or Black on Red). An empty column can **only** be occupied by a **King** (Rank 13) or a run headed by a King.
2. **Foundation Stacking**: Must be built in **ascending rank** ($1 \le R \le 13$) of the **identical suit**, starting from Ace ($R=1$) up to King ($R=13$).
3. **Card Reveals**: When a tableau move uncovers a face-down card at the column's tail, that card is immediately flipped face-up and awards a score bonus.
4. **Foundation to Tableau**: Players may pull top cards from a foundation back to the tableau if it creates a valid descending sequence to unblock stuck columns.

### Standard Scoring System
- **Waste to Tableau**: $+5$ points
- **Waste to Foundation**: $+10$ points
- **Tableau to Foundation**: $+10$ points
- **Exposing Hidden Tableau Card**: $+5$ points
- **Foundation to Tableau**: $-15$ points
- **Recycling Waste to Stock**: $-20$ points (score floored at 0)

---

## 5. Dual-Stack Undo / Redo (Command Pattern)

The engine implements a fully deterministic Command Pattern:
- **`MoveRecord`**: Stores all transaction details (`move_type`, `src`, `dst`, `card_count`, `cards`, `flipped_card`, `score_delta`).
- **`undo_stack: Stack[MoveRecord]`**: Every committed move is pushed here.
- **`redo_stack: Stack[MoveRecord]`**: Cleared upon any new action; populated when `undo()` is invoked.

### Move Reversal Matrix
- **`DRAW` Undo**: Pop from Waste stack $\rightarrow$ flip face-down $\rightarrow$ `prepend()` back to front of Stock queue.
- **`RECYCLE` Undo**: Drain Stock queue $\rightarrow$ push cards back to Waste stack in reversed order, restoring the exact previous stack configuration.
- **`TABLEAU_TO_TABLEAU` Undo**: Re-split the spliced run from the destination column and splice it back onto the source column. If the source had exposed a hidden card, that card is flipped back to face-down.
- **`TABLEAU_TO_FOUNDATION` Undo**: Pop card from Foundation stack $\rightarrow$ push back onto source Tableau column $\rightarrow$ unflip exposed card if applicable.

---

## 6. Strategic Heuristic Hint Engine

When requested via `hint` or `h`, the engine analyzes all legal transitions and sorts recommendations by heuristic priority:

1. **Priority 1**: Foundation moves of low rank (Aces and Twos) which are universally safe.
2. **Priority 2 & 3**: Higher-rank Tableau or Waste cards that can advance Foundations.
3. **Priority 4**: Tableau-to-Tableau moves that uncover a hidden face-down card.
4. **Priority 5**: Waste card transfers to Tableau columns that advance board mobility.
5. **Priority 6**: Moving a King to an empty column to unlock buried cards underneath.
6. **Priority 7**: Other valid Tableau-to-Tableau builds.
7. **Priority 8 & 9**: Drawing from Stock or recycling Waste.

---

## 7. Interactive Terminal CLI Interface

The interface features a crisp ANSI layout with Unicode card suits:

```text
==================================================================================
                     ♠ ♥ KLONDIKE SOLITAIRE ♦ ♣
==================================================================================
 Score:   45  |  Moves:  12  |  Time: 01:24  |  Foundations: 4/52  |  Undo: 8  |  Redo: 0
----------------------------------------------------------------------------------
 [STOCK]         [WASTE]                    [FOUNDATIONS]
  [O] (18)       [ 7♥ ]         ♥:[ A♥ ]  ♦:[ - ]  ♣:[ 2♣ ]  ♠:[ - ]
----------------------------------------------------------------------------------
  [T1]    [T2]    [T3]    [T4]    [T5]    [T6]    [T7]   
 [ K♠ ]  [ ? ]   [ ? ]   [ ? ]   [ ? ]   [ ? ]   [ ? ]  
         [ 9♦ ]  [ ? ]   [ ? ]   [ ? ]   [ ? ]   [ ? ]  
                 [ 8♣ ]  [ ? ]   [ ? ]   [ ? ]   [ ? ]  
                         [ J♥ ]  [ ? ]   [ ? ]   [ ? ]  
                                 [10♠ ]  [ ? ]   [ ? ]  
                                         [ 6♦ ]  [ ? ]  
                                                 [ Q♣ ] 
==================================================================================
[*] Moved [ 7♥ ] from Waste to Tableau 3.
----------------------------------------------------------------------------------
Command (d=draw, wt=waste->tab, tf=tab->found, m=move, u=undo, h=hint, q=quit): 
```

### Command Reference Table

| Category | Command | Description | Example |
|---|---|---|---|
| **Stock & Waste** | `d`, `draw` | Draw card from Stock (or recycle Waste if Stock is empty) | `d` |
| | `wf` | Move Waste card to its matching Foundation | `wf` |
| | `wt <col>` | Move Waste card to Tableau column (1-7) | `wt 3` or `w t 3` |
| **Tableau Moves** | `tf <col>` | Move exposed card of Tableau column (1-7) to Foundation | `tf 2` or `t f 2` |
| | `m <src> <dst>` | Move all valid face-up cards from `<src>` to `<dst>` | `m 1 2` |
| | `m <src> <dst> <count>` | Move `<count>` cards from Tableau `<src>` to `<dst>` | `m 3 5 2` |
| | `m <src> <dst> <card>` | Move run starting at `<card>` from `<src>` to `<dst>` | `m 7 6 C-8` or `m 1 2 10H` |
| **Foundation Moves**| `ft <suit> <col>` | Move top Foundation card back down to Tableau | `ft H 4` or `ft ♥ 4` |
| **Assistance** | `u`, `undo` | Undo the last move (Dual-Stack command pattern) | `u` |
| | `r`, `redo` | Redo the last undone move | `r` |
| | `h`, `hint` | Get top strategic move suggestion in status bar | `h` |
| | `h all` | Display complete list of all available legal moves | `h all` |
| | `a`, `auto` | Automatically perform one safe foundation move | `a` |
| **Controls** | `new [seed]` | Start a new game (optional integer seed for replayability)| `new 42` |
| | `help` | View complete in-game manual and help screen | `help` |
| | `q`, `quit` | Exit the game | `q` |

---

## 8. File Structure & Responsibilities

```text
mid project DSA/
│
├── card.py              # Card, Suit, Rank representations and ANSI rendering
├── data_structures.py   # Scratch Node, Stack (LIFO), Queue (FIFO), DoublyLinkedList
├── solitaire.py         # KlondikeSolitaire engine, move validation, dual-stack undo/redo, hints
├── main.py              # SolitaireCLI interactive terminal interface with ANSI VT100
├── test_solitaire.py    # 19 Academic unit tests verifying all structures and edge cases
└── README.md            # Comprehensive project documentation and academic report
```

---

## 9. Verification & Unit Testing

The project includes an automated test suite (`test_solitaire.py`) verifying:
1. **`TestDataStructures`**:
   - `Stack`: LIFO order, underflow exception handling, empty states, sizing.
   - `Queue`: FIFO order, underflow handling, $O(1)$ front prepend for undo.
   - `DoublyLinkedList`: Append, prepend, pop tail, pop head, search, `__contains__`, empty exceptions.
   - **Pointer Slicing & Splicing**: Verifying that multi-node segments detach and reattach seamlessly in constant time with correct neighbor pointers.
2. **`TestCard`**:
   - Card construction, string formatting, Tableau color-alternating stacking rules, Foundation suit-matching rules.
3. **`TestKlondikeSolitaire`**:
   - Initial deal specifications (28 tableau cards, 24 stock cards).
   - Draw, recycle, and exact undo/redo preservation of waste ordering.
   - Tableau-to-Tableau single card and multi-card run transfers.
   - Hidden card reveal and undo reversal.
   - Foundation moves, Foundation-to-Tableau moves, and victory detection when all 52 cards reach Foundations.
   - Strategic hint heuristic generation.

### Running the Test Suite
```bash
python test_solitaire.py
```

Expected Output:
```text
...................
----------------------------------------------------------------------
Ran 19 tests in 0.008s

OK
```

### Running the Games

The project provides three tailored interfaces:

#### Option 1: Native Desktop GUI (Tkinter Window)
A native desktop application featuring fluid drag-and-drop, sweet pastel felt aesthetics, cute bow emblems, hints, and zero external installations:
```bash
python gui.py
```

#### Option 2: Modern Web Browser Game (Kawaii Princess Edition)
An interactive browser experience with glassmorphism, 4 cute themes (🌸 Sakura Blossom, 🍓 Strawberry Milk, 💜 Lavender Fairy, 🍬 Cotton Candy Cloud), magical synthesized chimes, and fairy victory confetti:
```bash
python server.py
```
*(Or simply double-click `web/index.html` or `Run_Browser_Game.bat`!)*

#### Option 3: Terminal CLI
ANSI-colored VT100 interactive console interface:
```bash
python main.py
```

---

## 10. Academic Authorship & Attribution
- **Course**: Data Structures & Algorithms (CS201 / DSA)
- **Topic**: Pointer-Based Abstract Data Types, Non-Linear Lists, and Game State Management
- **Platform**: Python 3 (Cross-Platform: Windows, macOS, Linux)
"# Solitaire-Bloom" 
