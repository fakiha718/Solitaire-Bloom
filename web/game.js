/**
 * game.js - Klondike Solitaire Core Engine & Interactive Web Controller
 * ====================================================================
 * Academic DSA Architecture:
 * 1. Node: Pointer primitive for singly & doubly linked chains.
 * 2. Stack (LIFO): Foundations, Waste, Undo/Redo stacks.
 * 3. Queue (FIFO): Stockpile draw pile with O(1) prepend for undo.
 * 4. DoublyLinkedList: Tableau columns with true O(1) sublist splicing.
 * 5. Web Audio API: Synthesized sound effects without external audio assets.
 * 6. Confetti Particle Engine: Interactive victory celebration.
 */

// ============================================================================
// 1. Data Structures & Algorithms (Academic Implementation)
// ============================================================================

class Node {
  constructor(data, next = null, prev = null) {
    this.data = data;
    this.next = next;
    this.prev = prev;
  }
}

class Stack {
  constructor() {
    this._top = null;
    this._size = 0;
  }

  push(item) {
    const node = new Node(item, this._top, null);
    this._top = node;
    this._size++;
  }

  pop() {
    if (this.isEmpty()) throw new Error("Pop from empty Stack");
    const val = this._top.data;
    this._top = this._top.next;
    this._size--;
    return val;
  }

  peek() {
    return this._top ? this._top.data : null;
  }

  isEmpty() {
    return this._size === 0;
  }

  size() {
    return this._size;
  }

  clear() {
    this._top = null;
    this._size = 0;
  }

  toList() {
    const arr = [];
    let curr = this._top;
    while (curr) {
      arr.push(curr.data);
      curr = curr.next;
    }
    arr.reverse(); // Bottom to Top
    return arr;
  }
}

class Queue {
  constructor() {
    this._head = null;
    this._tail = null;
    this._size = 0;
  }

  enqueue(item) {
    const node = new Node(item);
    if (this.isEmpty()) {
      this._head = node;
      this._tail = node;
    } else {
      this._tail.next = node;
      this._tail = node;
    }
    this._size++;
  }

  dequeue() {
    if (this.isEmpty()) throw new Error("Dequeue from empty Queue");
    const val = this._head.data;
    this._head = this._head.next;
    if (!this._head) this._tail = null;
    this._size--;
    return val;
  }

  prepend(item) {
    const node = new Node(item, this._head, null);
    this._head = node;
    if (!this._tail) this._tail = node;
    this._size++;
  }

  peek() {
    return this._head ? this._head.data : null;
  }

  isEmpty() {
    return this._size === 0;
  }

  size() {
    return this._size;
  }

  clear() {
    this._head = null;
    this._tail = null;
    this._size = 0;
  }

  toList() {
    const arr = [];
    let curr = this._head;
    while (curr) {
      arr.push(curr.data);
      curr = curr.next;
    }
    return arr;
  }
}

class DoublyLinkedList {
  constructor() {
    this.head = null;
    this.tail = null;
    this._size = 0;
  }

  append(item) {
    const node = new Node(item, null, this.tail);
    if (this.isEmpty()) {
      this.head = node;
      this.tail = node;
    } else {
      this.tail.next = node;
      this.tail = node;
    }
    this._size++;
    return node;
  }

  popTail() {
    if (this.isEmpty()) throw new Error("popTail from empty DLL");
    const val = this.tail.data;
    if (this._size === 1) {
      this.head = null;
      this.tail = null;
    } else {
      this.tail = this.tail.prev;
      this.tail.next = null;
    }
    this._size--;
    return val;
  }

  peekTail() {
    return this.tail ? this.tail.data : null;
  }

  isEmpty() {
    return this._size === 0;
  }

  size() {
    return this._size;
  }

  clear() {
    this.head = null;
    this.tail = null;
    this._size = 0;
  }

  findNode(targetCard) {
    let curr = this.head;
    while (curr) {
      if (curr.data.id === targetCard.id) return curr;
      curr = curr.next;
    }
    return null;
  }

  splitSublist(startNode) {
    if (this.isEmpty()) throw new Error("Cannot split empty DLL");

    let k = 0;
    let curr = startNode;
    while (curr) {
      k++;
      curr = curr.next;
    }

    const sublist = new DoublyLinkedList();
    const oldTail = this.tail;

    if (startNode === this.head) {
      sublist.head = this.head;
      sublist.tail = this.tail;
      sublist._size = this._size;

      this.head = null;
      this.tail = null;
      this._size = 0;
    } else {
      const prevNode = startNode.prev;
      prevNode.next = null;
      startNode.prev = null;

      this.tail = prevNode;
      this._size -= k;

      sublist.head = startNode;
      sublist.tail = oldTail;
      sublist._size = k;
    }

    return sublist;
  }

  splice(other) {
    if (other.isEmpty()) return;

    if (this.isEmpty()) {
      this.head = other.head;
      this.tail = other.tail;
      this._size = other._size;
    } else {
      this.tail.next = other.head;
      other.head.prev = this.tail;
      this.tail = other.tail;
      this._size += other._size;
    }

    other.head = null;
    other.tail = null;
    other._size = 0;
  }

  toList() {
    const arr = [];
    let curr = this.head;
    while (curr) {
      arr.push(curr.data);
      curr = curr.next;
    }
    return arr;
  }
}

// ============================================================================
// 2. Card Representation
// ============================================================================

const SUITS = {
  HEARTS: "Hearts",
  DIAMONDS: "Diamonds",
  CLUBS: "Clubs",
  SPADES: "Spades",
};

const SUIT_SYMBOLS = {
  Hearts: "♥",
  Diamonds: "♦",
  Clubs: "♣",
  Spades: "♠",
};

const SUIT_COLORS = {
  Hearts: "Red",
  Diamonds: "Red",
  Clubs: "Black",
  Spades: "Black",
};

const RANK_NAMES = {
  1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7",
  8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K"
};

class Card {
  constructor(suit, rank, isFaceUp = false) {
    this.suit = suit;
    this.rank = rank;
    this.isFaceUp = isFaceUp;
    this.color = SUIT_COLORS[suit];
    this.symbol = SUIT_SYMBOLS[suit];
    this.rankStr = RANK_NAMES[rank];
    this.id = `${suit[0]}-${this.rankStr}`;
  }

  get isRed() {
    return this.color === "Red";
  }

  flip() {
    this.isFaceUp = !this.isFaceUp;
  }

  canStackOnTableau(target) {
    if (!target) return this.rank === 13; // King on empty column
    return (this.rank === target.rank - 1) && (this.color !== target.color);
  }

  canStackOnFoundation(targetTop) {
    if (!targetTop) return this.rank === 1; // Ace starts foundation
    return (this.suit === targetTop.suit) && (this.rank === targetTop.rank + 1);
  }
}

// ============================================================================
// 3. Web Audio Synthesizer (Zero External Dependencies)
// ============================================================================

class SoundFX {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  _init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume();
    }
  }

  playFlip() {
    if (!this.enabled) return;
    this._init();
    if (!this.ctx) return;

    // Sweet cheerful sparkle bubble pop
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(1046.50, this.ctx.currentTime); // C6
    osc.frequency.exponentialRampToValueAtTime(1760.00, this.ctx.currentTime + 0.05); // A6

    gain.gain.setValueAtTime(0.14, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.06);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.06);
  }

  playSnap() {
    if (!this.enabled) return;
    this._init();
    if (!this.ctx) return;

    // Gentle cute drop pop
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(783.99, this.ctx.currentTime); // G5
    osc.frequency.exponentialRampToValueAtTime(440.00, this.ctx.currentTime + 0.07); // A4

    gain.gain.setValueAtTime(0.16, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.07);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.07);
  }

  playWin() {
    if (!this.enabled) return;
    this._init();
    if (!this.ctx) return;

    // Sparkling fairy celesta music box arpeggio
    const notes = [523.25, 659.25, 783.99, 1046.50, 1318.51, 1567.98]; // C5, E5, G5, C6, E6, G6
    notes.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sine";
      const startT = this.ctx.currentTime + idx * 0.11;
      osc.frequency.setValueAtTime(freq, startT);

      gain.gain.setValueAtTime(0.18, startT);
      gain.gain.exponentialRampToValueAtTime(0.001, startT + 0.4);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(startT);
      osc.stop(startT + 0.4);
    });
  }
}

// ============================================================================
// 4. Klondike Solitaire Web Engine
// ============================================================================

class WebSolitaire {
  constructor() {
    this.stock = new Queue();
    this.waste = new Stack();
    this.foundations = {
      Hearts: new Stack(),
      Diamonds: new Stack(),
      Clubs: new Stack(),
      Spades: new Stack(),
    };
    this.tableaux = Array.from({ length: 7 }, () => new DoublyLinkedList());

    this.undoStack = new Stack();
    this.redoStack = new Stack();
    this.cardRegistry = {}; // HashMap/Dictionary: Maps card.id -> { card, pile, isFaceUp }

    this.score = 0;
    this.movesCount = 0;
    this.startTime = Date.now();
    this.isWon = false;

    this.startNewGame();
  }

  startNewGame() {
    this.stock.clear();
    this.waste.clear();
    Object.values(this.foundations).forEach(f => f.clear());
    this.tableaux.forEach(t => t.clear());

    this.undoStack.clear();
    this.redoStack.clear();
    this.score = 0;
    this.movesCount = 0;
    this.startTime = Date.now();
    this.isWon = false;

    // Build 52-card deck
    const deck = [];
    Object.values(SUITS).forEach(suit => {
      for (let r = 1; r <= 13; r++) {
        deck.push(new Card(suit, r, false));
      }
    });

    // Fisher-Yates Shuffle
    for (let i = deck.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }

    // Deal 7 Tableaux
    let deckIdx = 0;
    for (let col = 0; col < 7; col++) {
      for (let i = 0; i <= col; i++) {
        const card = deck[deckIdx++];
        card.isFaceUp = (i === col);
        this.tableaux[col].append(card);
      }
    }

    // Remaining 24 to Stock
    while (deckIdx < 52) {
      const card = deck[deckIdx++];
      card.isFaceUp = false;
      this.stock.enqueue(card);
    }
    this.refreshCardRegistry();
  }

  refreshCardRegistry() {
    this.cardRegistry = {};
    this.stock.toList().forEach((c, idx) => {
      this.cardRegistry[c.id] = { card: c, pile: "stock", index: idx, isFaceUp: c.isFaceUp };
    });
    this.waste.toList().forEach((c, idx) => {
      this.cardRegistry[c.id] = { card: c, pile: "waste", index: idx, isFaceUp: c.isFaceUp };
    });
    Object.entries(this.foundations).forEach(([suit, stack]) => {
      stack.toList().forEach((c, idx) => {
        this.cardRegistry[c.id] = { card: c, pile: `foundation_${suit}`, index: idx, isFaceUp: c.isFaceUp };
      });
    });
    this.tableaux.forEach((dll, colIdx) => {
      dll.toList().forEach((c, idx) => {
        this.cardRegistry[c.id] = { card: c, pile: `tableau_${colIdx}`, index: idx, isFaceUp: c.isFaceUp };
      });
    });
  }

  commitMove(record) {
    this.undoStack.push(record);
    this.redoStack.clear();
    this.movesCount++;
    this.score = Math.max(0, this.score + record.scoreDelta);
    this.refreshCardRegistry();
  }

  draw() {
    if (!this.stock.isEmpty()) {
      const card = this.stock.dequeue();
      card.isFaceUp = true;
      this.waste.push(card);

      this.commitMove({
        type: "DRAW",
        cards: [card],
        scoreDelta: 0,
      });
      return { success: true, msg: `Drew ${card.rankStr}${card.symbol} to Waste` };
    } else {
      if (this.waste.isEmpty()) return { success: false, msg: "Stock and Waste are both empty" };

      const recycled = [];
      while (!this.waste.isEmpty()) {
        const card = this.waste.pop();
        card.isFaceUp = false;
        this.stock.enqueue(card);
        recycled.push(card);
      }

      const scoreDelta = this.score >= 20 ? -20 : -this.score;
      this.commitMove({
        type: "RECYCLE",
        cards: recycled,
        scoreDelta: scoreDelta,
      });
      return { success: true, msg: "Recycled Waste back into Stock" };
    }
  }

  wasteToTableau(colIdx) {
    if (this.waste.isEmpty()) return { success: false, msg: "Waste is empty" };
    const col = this.tableaux[colIdx];
    const card = this.waste.peek();

    if (!card.canStackOnTableau(col.peekTail())) {
      return { success: false, msg: "Invalid Tableau placement" };
    }

    const popped = this.waste.pop();
    col.append(popped);

    this.commitMove({
      type: "WASTE_TO_TABLEAU",
      dst: colIdx,
      cards: [popped],
      scoreDelta: 5,
    });
    return { success: true, msg: `Moved ${card.rankStr}${card.symbol} to Column ${colIdx + 1}` };
  }

  wasteToFoundation() {
    if (this.waste.isEmpty()) return { success: false, msg: "Waste is empty" };
    const card = this.waste.peek();
    const foundation = this.foundations[card.suit];

    if (!card.canStackOnFoundation(foundation.peek())) {
      return { success: false, msg: "Cannot move to Foundation" };
    }

    const popped = this.waste.pop();
    foundation.push(popped);

    this.commitMove({
      type: "WASTE_TO_FOUNDATION",
      suit: card.suit,
      cards: [popped],
      scoreDelta: 10,
    });
    this.checkWin();
    return { success: true, msg: `Moved ${card.rankStr}${card.symbol} to Foundation` };
  }

  tableauToFoundation(colIdx) {
    const col = this.tableaux[colIdx];
    if (col.isEmpty()) return { success: false, msg: "Column is empty" };

    const card = col.peekTail();
    if (!card.isFaceUp) return { success: false, msg: "Card is face down" };

    const foundation = this.foundations[card.suit];
    if (!card.canStackOnFoundation(foundation.peek())) {
      return { success: false, msg: "Cannot move to Foundation" };
    }

    const popped = col.popTail();
    foundation.push(popped);

    let scoreDelta = 10;
    let flippedCard = null;
    const newTail = col.peekTail();
    if (newTail && !newTail.isFaceUp) {
      newTail.flip();
      flippedCard = newTail;
      scoreDelta += 5;
    }

    this.commitMove({
      type: "TABLEAU_TO_FOUNDATION",
      src: colIdx,
      suit: card.suit,
      cards: [popped],
      flippedCard: flippedCard,
      scoreDelta: scoreDelta,
    });
    this.checkWin();
    return { success: true, msg: `Moved ${card.rankStr}${card.symbol} to Foundation` };
  }

  tableauToTableau(srcIdx, card, dstIdx) {
    if (srcIdx === dstIdx) return { success: false, msg: "Same column" };
    const srcCol = this.tableaux[srcIdx];
    const dstCol = this.tableaux[dstIdx];

    const startNode = srcCol.findNode(card);
    if (!startNode || !startNode.data.isFaceUp) return { success: false, msg: "Cannot move face-down card" };

    if (!card.canStackOnTableau(dstCol.peekTail())) {
      return { success: false, msg: "Invalid stacking sequence" };
    }

    // Count moving cards
    const moving = [];
    let curr = startNode;
    while (curr) {
      moving.push(curr.data);
      curr = curr.next;
    }

    const sublist = srcCol.splitSublist(startNode);
    dstCol.splice(sublist);

    let scoreDelta = 0;
    let flippedCard = null;
    const newSrcTail = srcCol.peekTail();
    if (newSrcTail && !newSrcTail.isFaceUp) {
      newSrcTail.flip();
      flippedCard = newSrcTail;
      scoreDelta += 5;
    }

    this.commitMove({
      type: "TABLEAU_TO_TABLEAU",
      src: srcIdx,
      dst: dstIdx,
      cards: moving,
      cardCount: moving.length,
      flippedCard: flippedCard,
      scoreDelta: scoreDelta,
    });
    return { success: true, msg: `Moved ${moving.length} card(s) to Column ${dstIdx + 1}` };
  }

  foundationToTableau(suit, colIdx) {
    const foundation = this.foundations[suit];
    if (!foundation || foundation.isEmpty()) return { success: false, msg: "Foundation is empty" };

    const card = foundation.peek();
    const col = this.tableaux[colIdx];

    if (!card.canStackOnTableau(col.peekTail())) {
      return { success: false, msg: "Cannot move to Tableau" };
    }

    const popped = foundation.pop();
    col.append(popped);

    this.commitMove({
      type: "FOUNDATION_TO_TABLEAU",
      suit: suit,
      dst: colIdx,
      cards: [popped],
      scoreDelta: -15,
    });
    return { success: true, msg: `Moved ${card.rankStr}${card.symbol} from Foundation to Column ${colIdx + 1}` };
  }

  undo() {
    if (this.undoStack.isEmpty()) return { success: false, msg: "Nothing to undo" };
    const m = this.undoStack.pop();

    if (m.type === "DRAW") {
      const card = this.waste.pop();
      card.isFaceUp = false;
      this.stock.prepend(card);
    } else if (m.type === "RECYCLE") {
      for (let i = 0; i < m.cards.length; i++) this.stock.dequeue();
      for (let i = m.cards.length - 1; i >= 0; i--) {
        const c = m.cards[i];
        c.isFaceUp = true;
        this.waste.push(c);
      }
    } else if (m.type === "WASTE_TO_TABLEAU") {
      const card = this.tableaux[m.dst].popTail();
      this.waste.push(card);
    } else if (m.type === "WASTE_TO_FOUNDATION") {
      const card = this.foundations[m.suit].pop();
      this.waste.push(card);
    } else if (m.type === "TABLEAU_TO_FOUNDATION") {
      const card = this.foundations[m.suit].pop();
      if (m.flippedCard) m.flippedCard.isFaceUp = false;
      this.tableaux[m.src].append(card);
    } else if (m.type === "TABLEAU_TO_TABLEAU") {
      const srcCol = this.tableaux[m.src];
      const dstCol = this.tableaux[m.dst];
      if (m.flippedCard) m.flippedCard.isFaceUp = false;

      // Slice back
      const splitIdx = dstCol.size() - m.cardCount;
      let curr = dstCol.head;
      for (let i = 0; i < splitIdx; i++) curr = curr.next;
      const sublist = dstCol.splitSublist(curr);
      srcCol.splice(sublist);
    } else if (m.type === "FOUNDATION_TO_TABLEAU") {
      const card = this.tableaux[m.dst].popTail();
      this.foundations[m.suit].push(card);
    }

    this.score = Math.max(0, this.score - m.scoreDelta);
    this.movesCount++;
    this.redoStack.push(m);
    this.refreshCardRegistry();
    this.isWon = false;
    return { success: true, msg: `Undid ${m.type}` };
  }

  redo() {
    if (this.redoStack.isEmpty()) return { success: false, msg: "Nothing to redo" };
    const m = this.redoStack.pop();

    if (m.type === "DRAW") {
      const card = this.stock.dequeue();
      card.isFaceUp = true;
      this.waste.push(card);
    } else if (m.type === "RECYCLE") {
      while (!this.waste.isEmpty()) {
        const c = this.waste.pop();
        c.isFaceUp = false;
        this.stock.enqueue(c);
      }
    } else if (m.type === "WASTE_TO_TABLEAU") {
      const card = this.waste.pop();
      this.tableaux[m.dst].append(card);
    } else if (m.type === "WASTE_TO_FOUNDATION") {
      const card = this.waste.pop();
      this.foundations[m.suit].push(card);
    } else if (m.type === "TABLEAU_TO_FOUNDATION") {
      const card = this.tableaux[m.src].popTail();
      if (m.flippedCard) m.flippedCard.isFaceUp = true;
      this.foundations[m.suit].push(card);
    } else if (m.type === "TABLEAU_TO_TABLEAU") {
      const srcCol = this.tableaux[m.src];
      const dstCol = this.tableaux[m.dst];
      const splitIdx = srcCol.size() - m.cardCount;
      let curr = srcCol.head;
      for (let i = 0; i < splitIdx; i++) curr = curr.next;
      const sublist = srcCol.splitSublist(curr);
      dstCol.splice(sublist);
      if (m.flippedCard) m.flippedCard.isFaceUp = true;
    } else if (m.type === "FOUNDATION_TO_TABLEAU") {
      const card = this.foundations[m.suit].pop();
      this.tableaux[m.dst].append(card);
    }

    this.score = Math.max(0, this.score + m.scoreDelta);
    this.movesCount++;
    this.undoStack.push(m);
    this.refreshCardRegistry();
    this.checkWin();
    return { success: true, msg: `Redid ${m.type}` };
  }

  checkWin() {
    const total = Object.values(this.foundations).reduce((acc, f) => acc + f.size(), 0);
    if (total === 52) {
      this.isWon = true;
      return true;
    }
    return false;
  }

  getHints() {
    const hints = [];

    // 1. Tableau to Foundation
    this.tableaux.forEach((col, idx) => {
      const tail = col.peekTail();
      if (tail && tail.isFaceUp) {
        const f = this.foundations[tail.suit];
        if (tail.canStackOnFoundation(f.peek())) {
          hints.push({
            priority: tail.rank <= 2 ? 1 : 2,
            desc: `Move ${tail.rankStr}${tail.symbol} from Col ${idx + 1} to Foundation`,
            cardId: tail.id,
            action: () => this.tableauToFoundation(idx),
          });
        }
      }
    });

    // 2. Waste to Foundation
    if (!this.waste.isEmpty()) {
      const w = this.waste.peek();
      const f = this.foundations[w.suit];
      if (w.canStackOnFoundation(f.peek())) {
        hints.push({
          priority: w.rank <= 2 ? 1 : 3,
          desc: `Move ${w.rankStr}${w.symbol} from Waste to Foundation`,
          cardId: w.id,
          action: () => this.wasteToFoundation(),
        });
      }
    }

    // 3. Tableau to Tableau
    this.tableaux.forEach((srcCol, srcIdx) => {
      let curr = srcCol.head;
      let hasHidden = false;
      while (curr) {
        if (!curr.data.isFaceUp) {
          hasHidden = true;
        } else {
          const card = curr.data;
          this.tableaux.forEach((dstCol, dstIdx) => {
            if (dstIdx === srcIdx) return;
            const dstTail = dstCol.peekTail();
            if (card.canStackOnTableau(dstTail)) {
              let prio = 7;
              if (!dstTail && hasHidden) prio = 4;
              else if (hasHidden && curr.prev && !curr.prev.data.isFaceUp) prio = 4;
              hints.push({
                priority: prio,
                desc: `Move ${card.rankStr}${card.symbol} run from Col ${srcIdx + 1} to Col ${dstIdx + 1}`,
                cardId: card.id,
                action: () => this.tableauToTableau(srcIdx, card, dstIdx),
              });
            }
          });
        }
        curr = curr.next;
      }
    });

    // 4. Waste to Tableau
    if (!this.waste.isEmpty()) {
      const w = this.waste.peek();
      this.tableaux.forEach((col, idx) => {
        if (w.canStackOnTableau(col.peekTail())) {
          hints.push({
            priority: 5,
            desc: `Move ${w.rankStr}${w.symbol} from Waste to Col ${idx + 1}`,
            cardId: w.id,
            action: () => this.wasteToTableau(idx),
          });
        }
      });
    }

    // 5. Draw
    if (!this.stock.isEmpty()) {
      hints.push({
        priority: 8,
        desc: "Draw the next card from the Stockpile",
        cardId: null,
        action: () => this.draw(),
      });
    } else if (!this.waste.isEmpty()) {
      hints.push({
        priority: 9,
        desc: "Recycle the Waste pile into Stock",
        cardId: null,
        action: () => this.draw(),
      });
    }

    hints.sort((a, b) => a.priority - b.priority);
    return hints;
  }
}

// ============================================================================
// 5. Confetti Victory Particles
// ============================================================================

class ConfettiEngine {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.particles = [];
    this.animId = null;
    this.resize();
    window.addEventListener("resize", () => this.resize());
  }

  resize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  start() {
    this.particles = [];
    const glyphs = ["💖", "🌸", "✨", "🎀", "⭐", "🍓", "🍬"];
    for (let i = 0; i < 90; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height - this.canvas.height,
        glyph: glyphs[Math.floor(Math.random() * glyphs.length)],
        size: Math.random() * 16 + 18,
        vx: Math.random() * 3 - 1.5,
        vy: Math.random() * 3 + 2,
        rot: Math.random() * 360,
        vrot: Math.random() * 4 - 2,
      });
    }
    this.animate();
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.rot += p.vrot;

      if (p.y > this.canvas.height) {
        p.y = -30;
        p.x = Math.random() * this.canvas.width;
      }

      this.ctx.save();
      this.ctx.translate(p.x, p.y);
      this.ctx.rotate((p.rot * Math.PI) / 180);
      this.ctx.font = `${p.size}px sans-serif`;
      this.ctx.textAlign = "center";
      this.ctx.textBaseline = "middle";
      this.ctx.fillText(p.glyph, 0, 0);
      this.ctx.restore();
    });

    this.animId = requestAnimationFrame(() => this.animate());
  }

  stop() {
    if (this.animId) cancelAnimationFrame(this.animId);
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
}

// ============================================================================
// 6. UI Controller & DOM Orchestration
// ============================================================================

class UIController {
  constructor() {
    this.engine = new WebSolitaire();
    this.sound = new SoundFX();
    this.confetti = new ConfettiEngine(document.getElementById("confetti-canvas"));

    this.themes = ["theme-sakura", "theme-strawberry", "theme-lavender", "theme-bubblegum"];
    this.themeNames = ["🌙 Magical Girl", "🌊 Sailor Moon", "🌸 Sakura Anime", "💜 Yami Kawaii"];
    this.currThemeIdx = 0;

    // Drag State
    this.draggedCards = null;
    this.dragSource = null;

    this.initDOM();
    this.bindEvents();
    this.render();

    // Timer
    setInterval(() => this.updateTimer(), 1000);
  }

  initDOM() {
    this.dom = {
      stockContainer: document.getElementById("stock-container"),
      stockCounter: document.getElementById("stock-counter"),
      slotStock: document.getElementById("slot-stock"),
      wasteContainer: document.getElementById("waste-container"),
      foundations: {
        Hearts: document.getElementById("foundation-hearts-container"),
        Diamonds: document.getElementById("foundation-diamonds-container"),
        Clubs: document.getElementById("foundation-clubs-container"),
        Spades: document.getElementById("foundation-spades-container"),
      },
      tableaux: Array.from({ length: 7 }, (_, i) => document.getElementById(`col-${i}`).querySelector(".cards-cascade")),
      tableauCols: Array.from({ length: 7 }, (_, i) => document.getElementById(`col-${i}`)),
      statScore: document.getElementById("stat-score"),
      statMoves: document.getElementById("stat-moves"),
      statFoundations: document.getElementById("stat-foundations"),
      statTime: document.getElementById("stat-time"),
      statusText: document.getElementById("status-text"),
      btnUndo: document.getElementById("btn-undo"),
      btnRedo: document.getElementById("btn-redo"),
      hintBanner: document.getElementById("hint-banner"),
      hintText: document.getElementById("hint-text"),
      victoryModal: document.getElementById("victory-modal"),
      helpModal: document.getElementById("help-modal"),
    };
  }

  bindEvents() {
    // Toolbar buttons
    document.getElementById("btn-new-game").onclick = () => this.handleNewGame();
    document.getElementById("btn-undo").onclick = () => this.handleUndo();
    document.getElementById("btn-redo").onclick = () => this.handleRedo();
    document.getElementById("btn-hint").onclick = () => this.handleHint();
    document.getElementById("btn-auto").onclick = () => this.handleAutoStep();
    document.getElementById("btn-theme").onclick = () => this.handleSwitchTheme();
    document.getElementById("btn-sound").onclick = () => this.handleToggleSound();
    document.getElementById("btn-help").onclick = () => this.dom.helpModal.classList.remove("hidden");
    document.getElementById("btn-help-close").onclick = () => this.dom.helpModal.classList.add("hidden");
    document.getElementById("hint-close").onclick = () => this.dom.hintBanner.classList.add("hidden");

    // Victory Modal
    document.getElementById("btn-vic-play-again").onclick = () => {
      this.dom.victoryModal.classList.add("hidden");
      this.confetti.stop();
      this.handleNewGame();
    };
    document.getElementById("btn-vic-close").onclick = () => {
      this.dom.victoryModal.classList.add("hidden");
      this.confetti.stop();
    };

    // Stockpile Click
    this.dom.slotStock.onclick = () => {
      const res = this.engine.draw();
      if (res.success) {
        this.sound.playFlip();
        this.setStatus(res.msg);
        this.render();
      }
    };

    // Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
        e.preventDefault();
        this.handleUndo();
      } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") {
        e.preventDefault();
        this.handleRedo();
      } else if (e.code === "Space") {
        e.preventDefault();
        this.dom.slotStock.click();
      } else if (e.key.toLowerCase() === "h") {
        this.handleHint();
      } else if (e.key.toLowerCase() === "a") {
        this.handleAutoStep();
      } else if (e.key.toLowerCase() === "n") {
        this.handleNewGame();
      }
    });

    // Drop Zone Setup on Foundations & Tableaux
    this.setupDropZones();
  }

  createCardElement(card, opts = {}) {
    const el = document.createElement("div");
    el.className = `card ${card.isRed ? "suit-red" : "suit-black"} ${card.isFaceUp ? "" : "card-back"}`;
    el.dataset.id = card.id;

    if (!card.isFaceUp) {
      return el;
    }

    el.draggable = true;

    let courtCardGlyph = card.symbol;
    if (card.rank === 13) courtCardGlyph = "👑";
    else if (card.rank === 12) courtCardGlyph = "💖";
    else if (card.rank === 11) courtCardGlyph = "🎀";
    else if (card.rank === 1) courtCardGlyph = "✨";

    el.innerHTML = `
      <div class="card-content">
        <div class="card-corner top">
          <span class="corner-rank">${card.rankStr}</span>
          <span class="corner-suit">${card.symbol}</span>
        </div>
        <div class="card-center ${card.rank > 10 || card.rank === 1 ? 'court-card' : ''}">${courtCardGlyph}</div>
        <div class="card-corner bottom">
          <span class="corner-rank">${card.rankStr}</span>
          <span class="corner-suit">${card.symbol}</span>
        </div>
      </div>
    `;

    // Drag Start
    el.addEventListener("dragstart", (e) => {
      e.stopPropagation();
      this.draggedCards = opts.getRun ? opts.getRun() : [card];
      this.dragSource = opts.source;
      el.classList.add("is-dragging");
      e.dataTransfer.setData("text/plain", card.id);
      e.dataTransfer.effectAllowed = "move";
    });

    el.addEventListener("dragend", () => {
      el.classList.remove("is-dragging");
      this.clearDropHighlights();
    });

    // Double Click Quick Move
    el.addEventListener("dblclick", (e) => {
      e.stopPropagation();
      this.quickMove(card, opts.source);
    });

    return el;
  }

  setupDropZones() {
    // Foundation Drop Zones
    Object.entries(SUITS).forEach(([_, suit]) => {
      const slot = document.getElementById(`foundation-${suit.toLowerCase()}`);
      slot.addEventListener("dragover", (e) => {
        e.preventDefault();
        slot.classList.add("drag-over");
      });
      slot.addEventListener("dragleave", () => slot.classList.remove("drag-over"));
      slot.addEventListener("drop", (e) => {
        e.preventDefault();
        slot.classList.remove("drag-over");
        if (!this.draggedCards || this.draggedCards.length !== 1) return;

        const card = this.draggedCards[0];
        if (card.suit !== suit) return;

        if (this.dragSource.type === "waste") {
          const res = this.engine.wasteToFoundation();
          if (res.success) {
            this.sound.playSnap();
            this.setStatus(res.msg);
            this.render();
          }
        } else if (this.dragSource.type === "tableau") {
          const res = this.engine.tableauToFoundation(this.dragSource.col);
          if (res.success) {
            this.sound.playSnap();
            this.setStatus(res.msg);
            this.render();
          }
        }
      });
    });

    // Tableau Drop Zones
    this.dom.tableauCols.forEach((colEl, colIdx) => {
      colEl.addEventListener("dragover", (e) => {
        e.preventDefault();
        colEl.classList.add("drag-over");
      });
      colEl.addEventListener("dragleave", () => colEl.classList.remove("drag-over"));
      colEl.addEventListener("drop", (e) => {
        e.preventDefault();
        colEl.classList.remove("drag-over");
        if (!this.draggedCards || this.draggedCards.length === 0) return;

        const leadCard = this.draggedCards[0];
        if (this.dragSource.type === "waste") {
          const res = this.engine.wasteToTableau(colIdx);
          if (res.success) {
            this.sound.playSnap();
            this.setStatus(res.msg);
            this.render();
          }
        } else if (this.dragSource.type === "tableau") {
          const res = this.engine.tableauToTableau(this.dragSource.col, leadCard, colIdx);
          if (res.success) {
            this.sound.playSnap();
            this.setStatus(res.msg);
            this.render();
          }
        } else if (this.dragSource.type === "foundation") {
          const res = this.engine.foundationToTableau(this.dragSource.suit, colIdx);
          if (res.success) {
            this.sound.playSnap();
            this.setStatus(res.msg);
            this.render();
          }
        }
      });
    });
  }

  clearDropHighlights() {
    document.querySelectorAll(".drag-over").forEach(el => el.classList.remove("drag-over"));
  }

  quickMove(card, source) {
    if (source.type === "waste") {
      let res = this.engine.wasteToFoundation();
      if (!res.success) {
        for (let col = 0; col < 7; col++) {
          res = this.engine.wasteToTableau(col);
          if (res.success) break;
        }
      }
      if (res.success) {
        this.sound.playSnap();
        this.setStatus(res.msg);
        this.render();
      }
    } else if (source.type === "tableau") {
      const col = this.engine.tableaux[source.col];
      if (col.peekTail() === card) {
        let res = this.engine.tableauToFoundation(source.col);
        if (!res.success) {
          for (let dst = 0; dst < 7; dst++) {
            if (dst === source.col) continue;
            res = this.engine.tableauToTableau(source.col, card, dst);
            if (res.success) break;
          }
        }
        if (res.success) {
          this.sound.playSnap();
          this.setStatus(res.msg);
          this.render();
        }
      } else if (card.isFaceUp) {
        // Multi-card run move
        for (let dst = 0; dst < 7; dst++) {
          if (dst === source.col) continue;
          const res = this.engine.tableauToTableau(source.col, card, dst);
          if (res.success) {
            this.sound.playSnap();
            this.setStatus(res.msg);
            this.render();
            break;
          }
        }
      }
    } else if (source.type === "foundation") {
      for (let col = 0; col < 7; col++) {
        const res = this.engine.foundationToTableau(source.suit, col);
        if (res.success) {
          this.sound.playSnap();
          this.setStatus(res.msg);
          this.render();
          break;
        }
      }
    }
  }

  render(highlightId = null) {
    // 1. Stockpile
    this.dom.stockContainer.innerHTML = "";
    const stockSize = this.engine.stock.size();
    this.dom.stockCounter.textContent = stockSize;
    if (stockSize > 0) {
      const back = document.createElement("div");
      back.className = "card card-back";
      this.dom.stockContainer.appendChild(back);
    }

    // 2. Waste Pile
    this.dom.wasteContainer.innerHTML = "";
    const wasteList = this.engine.waste.toList();
    if (wasteList.length > 0) {
      const topCard = wasteList[wasteList.length - 1];
      const el = this.createCardElement(topCard, {
        source: { type: "waste" }
      });
      if (topCard.id === highlightId) el.classList.add("hint-highlight");
      this.dom.wasteContainer.appendChild(el);
    }

    // 3. Foundations
    Object.entries(SUITS).forEach(([_, suit]) => {
      const container = this.dom.foundations[suit];
      container.innerHTML = "";
      const fStack = this.engine.foundations[suit];
      const topCard = fStack.peek();
      if (topCard) {
        const el = this.createCardElement(topCard, {
          source: { type: "foundation", suit: suit }
        });
        container.appendChild(el);
      }
    });

    // 4. Tableaux
    this.engine.tableaux.forEach((col, colIdx) => {
      const cascade = this.dom.tableaux[colIdx];
      cascade.innerHTML = "";
      const cards = col.toList();
      let topOffset = 0;

      cards.forEach((card, idx) => {
        const el = this.createCardElement(card, {
          source: { type: "tableau", col: colIdx },
          getRun: () => cards.slice(idx),
        });
        el.style.top = `${topOffset}px`;
        if (card.id === highlightId) el.classList.add("hint-highlight");
        cascade.appendChild(el);

        topOffset += card.isFaceUp ? 28 : 18;
      });
    });

    // 5. Metrics & Status
    this.dom.statScore.textContent = this.engine.score;
    this.dom.statMoves.textContent = this.engine.movesCount;
    const fTotal = Object.values(this.engine.foundations).reduce((acc, f) => acc + f.size(), 0);
    this.dom.statFoundations.textContent = `${fTotal}/52`;

    this.dom.btnUndo.disabled = this.engine.undoStack.isEmpty();
    this.dom.btnRedo.disabled = this.engine.redoStack.isEmpty();

    // Check Victory
    if (this.engine.isWon) {
      this.handleVictory();
    }
  }

  updateTimer() {
    const elapsed = Math.floor((Date.now() - this.engine.startTime) / 1000);
    const m = String(Math.floor(elapsed / 60)).padStart(2, "0");
    const s = String(elapsed % 60).padStart(2, "0");
    this.dom.statTime.textContent = `${m}:${s}`;
  }

  setStatus(msg) {
    this.dom.statusText.textContent = msg;
  }

  handleNewGame() {
    this.engine.startNewGame();
    this.setStatus("Fresh hand dealt! Good luck.");
    this.dom.hintBanner.classList.add("hidden");
    this.render();
  }

  handleUndo() {
    const res = this.engine.undo();
    if (res.success) {
      this.sound.playSnap();
      this.setStatus(res.msg);
      this.render();
    }
  }

  handleRedo() {
    const res = this.engine.redo();
    if (res.success) {
      this.sound.playSnap();
      this.setStatus(res.msg);
      this.render();
    }
  }

  handleHint() {
    const hints = this.engine.getHints();
    if (!hints || hints.length === 0) {
      this.setStatus("No hints available. No legal moves remaining.");
      return;
    }

    const top = hints[0];
    this.dom.hintText.textContent = `${top.desc}`;
    this.dom.hintBanner.classList.remove("hidden");
    this.render(top.cardId);
  }

  handleAutoStep() {
    const hints = this.engine.getHints();
    const foundationMove = hints.find(h => h.priority <= 3 && h.desc.includes("Foundation"));
    if (foundationMove) {
      const res = foundationMove.action();
      if (res.success) {
        this.sound.playSnap();
        this.setStatus(`⚡ AUTO: ${res.msg}`);
        this.render();
      }
    } else {
      this.setStatus("No automatic safe foundation moves available.");
    }
  }

  handleSwitchTheme() {
    document.body.classList.remove(this.themes[this.currThemeIdx]);
    this.currThemeIdx = (this.currThemeIdx + 1) % this.themes.length;
    document.body.classList.add(this.themes[this.currThemeIdx]);
    this.setStatus(`✨ Aesthetic switched to ${this.themeNames[this.currThemeIdx]} ✨`);
  }

  handleToggleSound() {
    this.sound.enabled = !this.sound.enabled;
    document.getElementById("icon-sound-on").classList.toggle("hidden", !this.sound.enabled);
    document.getElementById("icon-sound-off").classList.toggle("hidden", this.sound.enabled);
    this.setStatus(`Sound ${this.sound.enabled ? "Enabled" : "Muted"}`);
  }

  handleVictory() {
    this.sound.playWin();
    this.confetti.start();

    document.getElementById("vic-score").textContent = this.engine.score;
    document.getElementById("vic-moves").textContent = this.engine.movesCount;
    document.getElementById("vic-time").textContent = this.dom.statTime.textContent;
    this.dom.victoryModal.classList.remove("hidden");
  }
}

// Initialize Application when DOM is ready

// Initialize Application when DOM is ready
window.addEventListener("DOMContentLoaded", () => {
  window.app = new UIController();
});
