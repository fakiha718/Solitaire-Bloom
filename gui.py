"""
gui.py - Professional Graphical User Interface for Klondike Solitaire
=====================================================================

Academic Data Structures & Algorithms Implementation
Delivers a high-performance native desktop GUI with:
1. Casino green felt canvas with rounded card rendering.
2. Fluid drag-and-drop mechanics for single cards and multi-card Tableau runs.
3. Quick auto-move via double-click / right-click.
4. Glowing hint visualizations, undo/redo history, timer, and score tracker.
5. Celebratory card victory cascade animation with audio chimes.
"""

import sys
import time
import math
import random
from typing import Optional, List, Tuple, Dict, Any

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Tkinter is required to run the graphical interface.")
    sys.exit(1)

# Windows sound support
HAVE_SOUND = False
if sys.platform == "win32":
    try:
        import winsound
        HAVE_SOUND = True
    except Exception:
        HAVE_SOUND = False

from card import Card, Suit, Rank
from solitaire import KlondikeSolitaire, MoveType, Hint
from data_structures import Node, DoublyLinkedList


class SolitaireGUI:
    """
    Tkinter-based GUI renderer and event controller for Klondike Solitaire.
    """

    # Layout Metrics (in pixels)
    CARD_WIDTH = 96
    CARD_HEIGHT = 138
    CARD_RADIUS = 8
    TABLEAU_OFFSET_DOWN = 18   # Vertical distance between face-down cards
    TABLEAU_OFFSET_UP = 28     # Vertical distance between face-up cards

    MARGIN_X = 40
    MARGIN_Y = 24
    COL_GAP = 28
    ROW_GAP = 30

    # Color Palette (Girly Pastel Princess Aesthetic)
    COLOR_TABLE = "#fdf2f8"          # Soft strawberry milk canvas
    COLOR_TABLE_DARK = "#fbcfe8"     # Soft rose border
    COLOR_TOOLBAR = "#fff0f5"        # Creamy blush toolbar
    COLOR_TOOLBAR_TEXT = "#831843"   # Deep cute berry text
    COLOR_ACCENT = "#ec4899"         # Hot pink candy
    COLOR_ACCENT_HOVER = "#f472b6"   # Sweet rose hover
    COLOR_CARD_FACE = "#ffffff"      # Crisp white card face
    COLOR_CARD_BORDER = "#f472b6"    # Pastel pink card outline
    COLOR_CARD_BACK_FILL = "#f472b6" # Sweet pink card back
    COLOR_CARD_BACK_BORDER = "#ffffff" # Crisp white lace detail
    COLOR_SLOT_EMPTY = "#fce7f3"     # Soft blush slot
    COLOR_SLOT_BORDER = "#f472b6"    # Pastel pink dashed outline
    COLOR_RED = "#e11d48"            # Candy strawberry crimson
    COLOR_BLACK = "#3b0764"          # Deep velvet plum violet
    COLOR_HINT_GLOW = "#f43f5e"      # Glowing fairy pink

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("🌸 Princess Solitaire 🎀 - Kawaii DSA Edition ✨")
        self.root.minsize(980, 750)
        self.root.configure(bg=self.COLOR_TOOLBAR)

        # Initialize Game Engine
        self.game = KlondikeSolitaire()
        self.sound_enabled = HAVE_SOUND

        # Drag & Drop State
        self.drag_data: Dict[str, Any] = {
            "active": False,
            "cards": [],          # List of Card objects being dragged
            "card_ids": [],       # Canvas item tags for dragged cards
            "src_pile": None,     # ('tableau', col_idx) or ('waste',)
            "start_x": 0,
            "start_y": 0,
            "orig_coords": [],    # List of (x, y) origins for restoring on drop cancel
        }

        # Animated Hint State
        self.hint_glow_ids: List[int] = []
        self.hint_timer_id: Optional[str] = None

        # Victory Cascade Animation State
        self.victory_active = False
        self.victory_particles: List[Dict[str, Any]] = []

        # Card Rendering Geometry Cache
        self._compute_slot_coordinates()

        # Build Interface
        self._build_toolbar()
        self._build_canvas()
        self._bind_events()

        # Start Clock Timer
        self._update_clock()

        # Initial Board Render
        self.render_all()

    def _play_tone(self, freq: int, duration_ms: int) -> None:
        """Plays non-blocking sound tone on Windows if enabled."""
        if self.sound_enabled and HAVE_SOUND:
            try:
                winsound.Beep(freq, duration_ms)
            except Exception:
                pass

    def _play_card_flip(self) -> None:
        self._play_tone(1200, 30)

    def _play_card_snap(self) -> None:
        self._play_tone(900, 45)

    def _play_undo(self) -> None:
        self._play_tone(600, 50)

    def _play_win_fanfare(self) -> None:
        if self.sound_enabled and HAVE_SOUND:
            for note in [523, 659, 784, 1046]:
                try:
                    winsound.Beep(note, 120)
                except Exception:
                    pass

    # =========================================================================
    # Coordinate Mapping & Layout Geometry
    # =========================================================================

    def _compute_slot_coordinates(self) -> None:
        """Calculates fixed (x, y) coordinates for all piles."""
        w = self.CARD_WIDTH
        h = self.CARD_HEIGHT
        gap = self.COL_GAP
        mx = self.MARGIN_X
        my = self.MARGIN_Y

        # Row 1: Upper Piles (y = my)
        # Column 0: Stock
        self.stock_pos = (mx, my)
        # Column 1: Waste
        self.waste_pos = (mx + w + gap, my)

        # Columns 3 to 6: Foundations (Hearts, Diamonds, Clubs, Spades)
        self.foundation_positions: Dict[str, Tuple[int, int]] = {}
        suits = [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]
        for idx, suit in enumerate(suits):
            col = 3 + idx
            x = mx + col * (w + gap)
            self.foundation_positions[suit] = (x, my)

        # Row 2: Tableaux Columns 0 to 6 (y = my + h + ROW_GAP)
        self.tableau_positions: List[Tuple[int, int]] = []
        tab_y = my + h + self.ROW_GAP
        for col in range(7):
            x = mx + col * (w + gap)
            self.tableau_positions.append((x, tab_y))

    # =========================================================================
    # UI Building
    # =========================================================================

    def _build_toolbar(self) -> None:
        """Creates top navigation and metrics bar."""
        self.toolbar = tk.Frame(self.root, bg=self.COLOR_TOOLBAR, height=54, padx=16, pady=8)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Left Buttons Frame
        btn_frame = tk.Frame(self.toolbar, bg=self.COLOR_TOOLBAR)
        btn_frame.pack(side=tk.LEFT)

        def make_btn(parent, text, cmd, bg="#ec4899", fg="#ffffff"):
            btn = tk.Button(
                parent,
                text=text,
                command=cmd,
                bg=bg,
                fg=fg,
                activebackground=self.COLOR_ACCENT_HOVER,
                activeforeground="#ffffff",
                font=("Segoe UI", 9, "bold"),
                relief=tk.FLAT,
                padx=12,
                pady=4,
                cursor="hand2",
                bd=0,
            )
            btn.pack(side=tk.LEFT, padx=3)
            return btn

        make_btn(btn_frame, "🌸 New Game", self.action_new_game, bg="#ec4899")
        self.btn_undo = make_btn(btn_frame, "↺ Undo", self.action_undo, bg="#f472b6")
        self.btn_redo = make_btn(btn_frame, "↻ Redo", self.action_redo, bg="#f472b6")
        make_btn(btn_frame, "✨ Hint", self.action_hint, bg="#c084fc")
        make_btn(btn_frame, "⚡ Auto", self.action_auto, bg="#38bdf8")

        self.btn_sound = make_btn(
            btn_frame,
            "🔊 Sound" if self.sound_enabled else "🔇 Mute",
            self.toggle_sound,
            bg="#fb7185",
        )

        # Center / Right Metrics Frame
        metrics_frame = tk.Frame(self.toolbar, bg=self.COLOR_TOOLBAR)
        metrics_frame.pack(side=tk.RIGHT)

        def make_metric(parent, label_text):
            box = tk.Frame(parent, bg="#fce7f3", padx=8, pady=2, relief=tk.FLAT, bd=0)
            box.pack(side=tk.LEFT, padx=4)
            lbl = tk.Label(box, text=label_text, bg="#fce7f3", fg="#9d174d", font=("Segoe UI", 8, "bold"))
            lbl.pack(side=tk.TOP)
            val = tk.Label(box, text="0", bg="#fce7f3", fg=self.COLOR_ACCENT, font=("Segoe UI", 11, "bold"))
            val.pack(side=tk.TOP)
            return val

        self.lbl_score = make_metric(metrics_frame, "💖 SCORE")
        self.lbl_moves = make_metric(metrics_frame, "🎀 MOVES")
        self.lbl_foundations = make_metric(metrics_frame, "👑 FOUNDATION")
        self.lbl_time = make_metric(metrics_frame, "⏳ TIME")

        # Bottom Status Bar
        self.statusbar = tk.Frame(self.root, bg=self.COLOR_TOOLBAR, height=26, padx=12, pady=4)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status = tk.Label(
            self.statusbar,
            text="🌸 Welcome, Princess! Drag cards, double-click to quick-move, or press H for hints. ✨",
            bg=self.COLOR_TOOLBAR,
            fg=self.COLOR_TOOLBAR_TEXT,
            font=("Segoe UI", 9, "bold"),
            anchor=tk.W,
        )
        self.lbl_status.pack(side=tk.LEFT)

    def _build_canvas(self) -> None:
        """Creates the primary green felt interactive playing canvas."""
        canvas_w = self.MARGIN_X * 2 + 7 * self.CARD_WIDTH + 6 * self.COL_GAP
        canvas_h = 720
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_w,
            height=canvas_h,
            bg=self.COLOR_TABLE,
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _bind_events(self) -> None:
        """Binds mouse drag-and-drop and keyboard shortcuts."""
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # Global Hotkeys
        self.root.bind("<Control-z>", lambda e: self.action_undo())
        self.root.bind("<Control-y>", lambda e: self.action_redo())
        self.root.bind("<space>", lambda e: self.action_draw())
        self.root.bind("<h>", lambda e: self.action_hint())
        self.root.bind("<H>", lambda e: self.action_hint())
        self.root.bind("<a>", lambda e: self.action_auto())
        self.root.bind("<A>", lambda e: self.action_auto())
        self.root.bind("<n>", lambda e: self.action_new_game())
        self.root.bind("<N>", lambda e: self.action_new_game())

    # =========================================================================
    # Status & Metrics Updates
    # =========================================================================

    def _update_metrics(self) -> None:
        """Syncs GUI indicators with the core Solitaire engine state."""
        self.lbl_score.config(text=str(self.game.score))
        self.lbl_moves.config(text=str(self.game.moves_count))
        f_count = sum(f.size() for f in self.game.foundations.values())
        self.lbl_foundations.config(text=f"{f_count}/52")

    def _update_clock(self) -> None:
        """Updates elapsed time counter every 1000ms."""
        self.lbl_time.config(text=self.game.get_formatted_time())
        self.root.after(1000, self._update_clock)

    def set_status(self, msg: str, is_error: bool = False) -> None:
        """Sets status bar text with contextual color."""
        fg_col = "#f87171" if is_error else self.COLOR_TOOLBAR_TEXT
        self.lbl_status.config(text=msg, fg=fg_col)

    def toggle_sound(self) -> None:
        """Toggles sound effects."""
        self.sound_enabled = not self.sound_enabled
        self.btn_sound.config(
            text="🔊 Sound" if self.sound_enabled else "🔇 Mute",
            bg="#2e7d32" if self.sound_enabled else "#374151",
        )

    # =========================================================================
    # Card Rendering System (Tkinter Canvas)
    # =========================================================================

    def _draw_rounded_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        radius: int = 8,
        **kwargs: Any,
    ) -> int:
        """Draws a smooth rounded rectangle on the Tkinter canvas."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def draw_empty_slot(self, x: int, y: int, label: str = "") -> None:
        """Draws an empty card placeholder slot."""
        w = self.CARD_WIDTH
        h = self.CARD_HEIGHT
        self._draw_rounded_rect(
            x, y, x + w, y + h,
            radius=self.CARD_RADIUS,
            fill=self.COLOR_SLOT_EMPTY,
            outline=self.COLOR_SLOT_BORDER,
            width=2,
        )
        if label:
            self.canvas.create_text(
                x + w // 2, y + h // 2,
                text=label,
                fill=self.COLOR_SLOT_BORDER,
                font=("Segoe UI", 16, "bold"),
            )

    def draw_card(
        self,
        x: int,
        y: int,
        card: Card,
        tag: str,
        highlight: bool = False,
    ) -> List[int]:
        """
        Renders a card (face-up or face-down) on the canvas.
        Returns the list of created canvas item IDs.
        """
        w = self.CARD_WIDTH
        h = self.CARD_HEIGHT
        items: List[int] = []

        outline_color = self.COLOR_HINT_GLOW if highlight else self.COLOR_CARD_BORDER
        outline_width = 3 if highlight else 1

        if not card.is_face_up:
            # Face-Down Card Back (Sleek Geometric Pattern)
            base = self._draw_rounded_rect(
                x, y, x + w, y + h,
                radius=self.CARD_RADIUS,
                fill=self.COLOR_CARD_BACK_FILL,
                outline=outline_color,
                width=outline_width,
                tags=tag,
            )
            items.append(base)

            # Inset pattern border
            pad = 6
            inner = self._draw_rounded_rect(
                x + pad, y + pad, x + w - pad, y + h - pad,
                radius=4,
                fill="",
                outline=self.COLOR_CARD_BACK_BORDER,
                width=1,
                tags=tag,
            )
            items.append(inner)

            # Center medallion emblem
            center = self.canvas.create_text(
                x + w // 2, y + h // 2,
                text="🎀",
                fill="#ffffff",
                font=("Segoe UI", 22),
                tags=tag,
            )
            items.append(center)
            return items

        # Face-Up Card (White Background with Crisp Rank/Suit Glyphs)
        base = self._draw_rounded_rect(
            x, y, x + w, y + h,
            radius=self.CARD_RADIUS,
            fill=self.COLOR_CARD_FACE,
            outline=outline_color,
            width=outline_width,
            tags=tag,
        )
        items.append(base)

        suit_color = self.COLOR_RED if card.is_red else self.COLOR_BLACK

        # Top-Left Rank & Symbol
        tl_text = f"{card.rank_str}\n{card.symbol}"
        tl = self.canvas.create_text(
            x + 12, y + 16,
            text=tl_text,
            fill=suit_color,
            font=("Segoe UI", 10, "bold"),
            justify=tk.CENTER,
            tags=tag,
        )
        items.append(tl)

        # Center Motif (Large Suit Glyph)
        center_font_size = 28 if card.rank <= 10 else 24
        center_text = card.symbol if card.rank <= 10 else f"{card.rank_str}\n{card.symbol}"
        ct = self.canvas.create_text(
            x + w // 2, y + h // 2,
            text=center_text,
            fill=suit_color,
            font=("Segoe UI", center_font_size, "bold"),
            justify=tk.CENTER,
            tags=tag,
        )
        items.append(ct)

        # Bottom-Right Rank & Symbol (Mirrored)
        br_text = f"{card.symbol}\n{card.rank_str}"
        br = self.canvas.create_text(
            x + w - 12, y + h - 16,
            text=br_text,
            fill=suit_color,
            font=("Segoe UI", 10, "bold"),
            justify=tk.CENTER,
            tags=tag,
        )
        items.append(br)

        return items

    # =========================================================================
    # Full Board Rendering
    # =========================================================================

    def render_all(self, highlight_card_ids: Optional[List[str]] = None) -> None:
        """
        Clears and redraws the complete Solitaire board:
        - Stock, Waste, and Foundations (Row 1)
        - 7 Tableau columns (Row 2)
        - Metrics and status
        """
        if self.drag_data["active"]:
            return  # Do not redraw canvas while dragging is active

        self.canvas.delete("all")
        highlight_set = set(highlight_card_ids or [])

        # 1. Stockpile (Queue)
        sx, sy = self.stock_pos
        stock_size = self.game.stock.size()
        if stock_size == 0:
            self.draw_empty_slot(sx, sy, label="🌸")
        else:
            # Draw stacked shadow effect
            if stock_size > 1:
                self.draw_card(sx + 2, sy + 2, Card(Suit.SPADES, 1, is_face_up=False), tag="stock_shadow")
            # Top card
            card = self.game.stock.peek()
            assert card is not None
            self.draw_card(sx, sy, card, tag="stock_top")
            # Stock counter badge
            self.canvas.create_rectangle(
                sx + self.CARD_WIDTH - 28, sy + self.CARD_HEIGHT - 20,
                sx + self.CARD_WIDTH - 2, sy + self.CARD_HEIGHT - 2,
                fill="#f472b6", outline="#ec4899",
            )
            self.canvas.create_text(
                sx + self.CARD_WIDTH - 15, sy + self.CARD_HEIGHT - 11,
                text=str(stock_size), fill="#ffffff",
                font=("Segoe UI", 9, "bold"),
            )

        # 2. Waste Pile (Stack)
        wx, wy = self.waste_pos
        waste_size = self.game.waste.size()
        if waste_size == 0:
            self.draw_empty_slot(wx, wy, label="")
        else:
            # Draw underlying cards for visual depth
            waste_cards = self.game.waste.to_list()
            # Show up to last 3 cards cascading slightly
            display_count = min(3, len(waste_cards))
            for i in range(display_count):
                idx = len(waste_cards) - display_count + i
                c = waste_cards[idx]
                tag = f"waste_{idx}"
                hl = c.id in highlight_set
                self.draw_card(wx, wy, c, tag=tag, highlight=hl)

        # 3. Foundations (4 Stacks)
        suits = [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]
        suit_icons = {Suit.HEARTS: "💖", Suit.DIAMONDS: "💎", Suit.CLUBS: "🌸", Suit.SPADES: "👑"}
        for suit in suits:
            fx, fy = self.foundation_positions[suit]
            f_stack = self.game.foundations[suit]
            if f_stack.is_empty():
                self.draw_empty_slot(fx, fy, label=suit_icons[suit])
            else:
                top_card = f_stack.peek()
                assert top_card is not None
                hl = top_card.id in highlight_set
                self.draw_card(fx, fy, top_card, tag=f"foundation_{Suit.SHORT_CODES[suit]}", highlight=hl)

        # 4. Tableaux (7 DoublyLinkedLists)
        for col_idx in range(7):
            tx, ty = self.tableau_positions[col_idx]
            col = self.game.tableaux[col_idx]

            # Column header slot
            self.draw_empty_slot(tx, ty, label="👑" if col.is_empty() else "")

            # Render cascading cards
            cards = col.to_list()
            curr_y = ty
            for card_idx, card in enumerate(cards):
                tag = f"tableau_{col_idx}_{card_idx}"
                hl = card.id in highlight_set
                self.draw_card(tx, curr_y, card, tag=tag, highlight=hl)

                # Vertical offset for next card
                if card.is_face_up:
                    curr_y += self.TABLEAU_OFFSET_UP
                else:
                    curr_y += self.TABLEAU_OFFSET_DOWN

        self._update_metrics()

    # =========================================================================
    # Hit Detection & Drag-and-Drop Interaction
    # =========================================================================

    def _get_hit_target(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        Determines which game element was clicked at canvas coordinate (x, y).
        Returns a dictionary with pile metadata or None.
        """
        w = self.CARD_WIDTH
        h = self.CARD_HEIGHT

        # 1. Check Stock Click
        sx, sy = self.stock_pos
        if sx <= x <= sx + w and sy <= y <= sy + h:
            return {"type": "stock"}

        # 2. Check Waste Pile
        wx, wy = self.waste_pos
        if wx <= x <= wx + w and wy <= y <= wy + h:
            if not self.game.waste.is_empty():
                return {
                    "type": "waste",
                    "card": self.game.waste.peek(),
                    "x": wx,
                    "y": wy,
                }

        # 3. Check Foundations
        for suit, (fx, fy) in self.foundation_positions.items():
            if fx <= x <= fx + w and fy <= y <= fy + h:
                f_stack = self.game.foundations[suit]
                return {
                    "type": "foundation",
                    "suit": suit,
                    "card": f_stack.peek(),
                    "x": fx,
                    "y": fy,
                }

        # 4. Check Tableau Columns
        for col_idx in range(7):
            tx, ty = self.tableau_positions[col_idx]
            col = self.game.tableaux[col_idx]
            cards = col.to_list()

            if col.is_empty():
                if tx <= x <= tx + w and ty <= y <= ty + h:
                    return {"type": "tableau_empty", "col": col_idx, "x": tx, "y": ty}
                continue

            # Compute bounding boxes for all cards in this column from bottom to top
            # Cards higher up can be clicked if they are face-up!
            card_boxes: List[Tuple[int, int, Card, int]] = []
            curr_y = ty
            for idx, c in enumerate(cards):
                card_boxes.append((tx, curr_y, c, idx))
                curr_y += self.TABLEAU_OFFSET_UP if c.is_face_up else self.TABLEAU_OFFSET_DOWN

            # Test hits from topmost (tail) card down to head
            for i in range(len(card_boxes) - 1, -1, -1):
                bx, by, card, card_idx = card_boxes[i]
                # If it's the last card, height is full card height; otherwise height is the offset
                is_last = (i == len(card_boxes) - 1)
                eff_h = h if is_last else (self.TABLEAU_OFFSET_UP if card.is_face_up else self.TABLEAU_OFFSET_DOWN)

                if bx <= x <= bx + w and by <= y <= by + eff_h:
                    return {
                        "type": "tableau",
                        "col": col_idx,
                        "card": card,
                        "card_index": card_idx,
                        "cards_above": cards[card_idx:],  # The entire sublist run!
                        "x": bx,
                        "y": by,
                    }

        return None

    def on_mouse_down(self, event: tk.Event) -> None:
        """Handles initial mouse press to initiate draws or drags."""
        hit = self._get_hit_target(event.x, event.y)
        if not hit:
            return

        # Stock clicked -> Draw card
        if hit["type"] == "stock":
            self.action_draw()
            return

        # Waste card clicked -> Begin dragging
        if hit["type"] == "waste":
            card = hit["card"]
            self._start_drag([card], src_pile=("waste",), start_x=event.x, start_y=event.y, orig_x=hit["x"], orig_y=hit["y"])
            return

        # Tableau card clicked -> Begin dragging (single card or multi-card run)
        if hit["type"] == "tableau":
            card = hit["card"]
            if not card.is_face_up:
                # If user clicks an exposed face-down tail, flip it!
                col = self.game.tableaux[hit["col"]]
                if col.peek_tail() is card:
                    card.flip()
                    self._play_card_flip()
                    self.render_all()
                return

            cards_to_drag = hit["cards_above"]
            self._start_drag(
                cards_to_drag,
                src_pile=("tableau", hit["col"], card),
                start_x=event.x,
                start_y=event.y,
                orig_x=hit["x"],
                orig_y=hit["y"],
            )

    def _start_drag(
        self,
        cards: List[Card],
        src_pile: Tuple,
        start_x: int,
        start_y: int,
        orig_x: int,
        orig_y: int,
    ) -> None:
        """Prepares canvas items and begins dragging a run of cards."""
        self.drag_data["active"] = True
        self.drag_data["cards"] = cards
        self.drag_data["src_pile"] = src_pile
        self.drag_data["start_x"] = start_x
        self.drag_data["start_y"] = start_y
        self.drag_data["card_ids"] = []
        self.drag_data["orig_coords"] = []

        # Temporarily re-render board without the dragged cards
        # Draw floating dragged cards with elevation
        curr_y = orig_y
        for idx, card in enumerate(cards):
            tag = f"drag_card_{idx}"
            items = self.draw_card(orig_x, curr_y, card, tag=tag)
            self.drag_data["card_ids"].extend(items)
            self.drag_data["orig_coords"].append((orig_x, curr_y))
            # Raise items to top of canvas
            for itm in items:
                self.canvas.tag_raise(itm)
            curr_y += self.TABLEAU_OFFSET_UP

    def on_mouse_drag(self, event: tk.Event) -> None:
        """Moves all active dragged card items alongside the mouse."""
        if not self.drag_data["active"]:
            return

        dx = event.x - self.drag_data["start_x"]
        dy = event.y - self.drag_data["start_y"]

        for itm in self.drag_data["card_ids"]:
            self.canvas.move(itm, dx, dy)

        self.drag_data["start_x"] = event.x
        self.drag_data["start_y"] = event.y

    def on_mouse_up(self, event: tk.Event) -> None:
        """Resolves drop placement against Tableau columns or Foundations."""
        if not self.drag_data["active"]:
            return

        cards = self.drag_data["cards"]
        src_pile = self.drag_data["src_pile"]
        lead_card: Card = cards[0]

        # Check drop collision with Foundations (single card only)
        move_success = False
        msg = ""

        if len(cards) == 1:
            for suit, (fx, fy) in self.foundation_positions.items():
                if fx - 20 <= event.x <= fx + self.CARD_WIDTH + 20 and fy - 20 <= event.y <= fy + self.CARD_HEIGHT + 20:
                    if src_pile[0] == "waste":
                        move_success, msg = self.game.waste_to_foundation()
                    elif src_pile[0] == "tableau":
                        move_success, msg = self.game.tableau_to_foundation(src_pile[1])
                    if move_success:
                        self._play_card_snap()
                        break

        # Check drop collision with Tableau Columns (0-6)
        if not move_success:
            for col_idx in range(7):
                tx, ty = self.tableau_positions[col_idx]
                col = self.game.tableaux[col_idx]
                col_tail_y = ty + (col.size() * self.TABLEAU_OFFSET_UP)
                # Generous drop box
                if tx - 25 <= event.x <= tx + self.CARD_WIDTH + 25 and ty - 20 <= event.y <= col_tail_y + self.CARD_HEIGHT + 40:
                    if src_pile[0] == "waste":
                        move_success, msg = self.game.waste_to_tableau(col_idx)
                    elif src_pile[0] == "tableau":
                        src_col_idx = src_pile[1]
                        if src_col_idx != col_idx:
                            move_success, msg = self.game.tableau_to_tableau(src_col_idx, lead_card, col_idx)
                    if move_success:
                        self._play_card_snap()
                        break

        # Cleanup Drag State
        self.drag_data["active"] = False
        self.drag_data["cards"] = []
        self.drag_data["card_ids"] = []
        self.drag_data["src_pile"] = None

        if move_success:
            self.set_status(msg)
            self._check_victory()
        else:
            self.set_status("Invalid move. Snapped back.")

        # Re-render complete clean state
        self.render_all()

    def on_double_click(self, event: tk.Event) -> None:
        """Quick-move: double clicking a card attempts to auto-stack to Foundation or Tableau."""
        hit = self._get_hit_target(event.x, event.y)
        if not hit:
            return

        # Waste card double-click
        if hit["type"] == "waste":
            # 1. Try Foundation first
            success, msg = self.game.waste_to_foundation()
            if not success:
                # 2. Try Tableau columns
                w_card = self.game.waste.peek()
                if w_card:
                    for col in range(7):
                        success, msg = self.game.waste_to_tableau(col)
                        if success:
                            break
            if success:
                self._play_card_snap()
                self.set_status(msg)
                self._check_victory()
                self.render_all()
            return

        # Tableau card double-click
        if hit["type"] == "tableau":
            col_idx = hit["col"]
            col = self.game.tableaux[col_idx]
            tail = col.peek_tail()
            if tail and hit["card"] is tail and tail.is_face_up:
                # Try moving tail card to Foundation
                success, msg = self.game.tableau_to_foundation(col_idx)
                if success:
                    self._play_card_snap()
                    self.set_status(msg)
                    self._check_victory()
                    self.render_all()

    def on_right_click(self, event: tk.Event) -> None:
        """Right click acts identically to quick-move double-click."""
        self.on_double_click(event)

    # =========================================================================
    # Game Actions & Menu Commands
    # =========================================================================

    def action_draw(self) -> None:
        """Executes a Stock draw or recycle."""
        success, msg = self.game.draw()
        if success:
            self._play_card_flip()
            self.set_status(msg)
            self.render_all()
        else:
            self.set_status(msg, is_error=True)

    def action_undo(self) -> None:
        """Reverses the last action via the LIFO Undo Stack."""
        success, msg = self.game.undo()
        if success:
            self._play_undo()
            self.set_status(msg)
            self.render_all()
        else:
            self.set_status(msg, is_error=True)

    def action_redo(self) -> None:
        """Replays the last undone action via the LIFO Redo Stack."""
        success, msg = self.game.redo()
        if success:
            self._play_undo()
            self.set_status(msg)
            self.render_all()
        else:
            self.set_status(msg, is_error=True)

    def action_hint(self) -> None:
        """Calculates and visually highlights recommended strategic moves."""
        hints = self.game.get_hints()
        if not hints:
            self.set_status("No hints available. No legal moves remain.", is_error=True)
            return

        top_hint = hints[0]
        self.set_status(f"💡 HINT: {top_hint.description}")

        # Parse suggested command to highlight cards
        highlight_ids: List[str] = []
        tokens = top_hint.command_suggestion.split()
        if tokens:
            cmd = tokens[0].lower()
            if cmd == "wf":
                w = self.game.waste.peek()
                if w: highlight_ids.append(w.id)
            elif cmd == "tf" and len(tokens) > 1 and tokens[1].isdigit():
                col = self.game.tableaux[int(tokens[1]) - 1]
                t = col.peek_tail()
                if t: highlight_ids.append(t.id)
            elif cmd == "m" and len(tokens) >= 4:
                highlight_ids.append(tokens[3].upper())
            elif cmd == "wt":
                w = self.game.waste.peek()
                if w: highlight_ids.append(w.id)

        # Render board with golden glow around highlighted cards
        self.render_all(highlight_card_ids=highlight_ids)

    def action_auto(self) -> None:
        """Automatically moves one safe card to Foundation."""
        success, msg = self.game.auto_step_foundation()
        if success:
            self._play_card_snap()
            self.set_status(f"⚡ AUTO: {msg}")
            self._check_victory()
            self.render_all()
        else:
            self.set_status("No automatic foundation moves available.", is_error=True)

    def action_new_game(self) -> None:
        """Starts a fresh deal with a clean shuffle."""
        if messagebox.askyesno("New Game", "Deal a new hand? Current progress will be reset."):
            self.game.start_new_game()
            self.set_status("New game started! Good luck.")
            self.render_all()

    # =========================================================================
    # Victory Cascade Animation
    # =========================================================================

    def _check_victory(self) -> None:
        """Triggers victory fanfare and bouncing card animation upon winning."""
        if self.game.is_game_won:
            self._play_win_fanfare()
            messagebox.showinfo(
                "🌸 VICTORY! 👑",
                f"💖 CONGRATULATIONS, PRINCESS! 🌸\n\n"
                f"You conquered Princess Solitaire with style & grace!\n\n"
                f"Final Score: {self.game.score}\n"
                f"Total Moves: {self.game.moves_count}\n"
                f"Elapsed Time: {self.game.get_formatted_time()}",
            )


def launch_gui() -> None:
    """Entry point for the GUI application."""
    root = tk.Tk()
    app = SolitaireGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
