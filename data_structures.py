"""
data_structures.py - Custom Data Structure Implementations
==========================================================

Academic Data Structures & Algorithms Implementation
Provides foundational pointer-based data structures built strictly from scratch:
1. Node: Singly and doubly linked node representation.
2. Stack (LIFO): Linked-list based Stack for Foundations & Undo/Redo history.
3. Queue (FIFO): Head/Tail pointer-based Queue for the Stockpile draw pile.
4. DoublyLinkedList: Pointer-based DLL with slicing & O(1) splicing for Tableau columns.
"""

from typing import Generic, TypeVar, Optional, List, Iterator, Callable, Any

T = TypeVar("T")


class Node(Generic[T]):
    """
    A foundational linked-list Node supporting both singly and doubly linked architectures.

    Attributes:
        data (T): Payload value held by the node.
        next (Optional[Node[T]]): Reference to the successor node.
        prev (Optional[Node[T]]): Reference to the predecessor node.
    """

    def __init__(
        self,
        data: T,
        next_node: Optional["Node[T]"] = None,
        prev_node: Optional["Node[T]"] = None,
    ):
        self.data: T = data
        self.next: Optional["Node[T]"] = next_node
        self.prev: Optional["Node[T]"] = prev_node

    def __repr__(self) -> str:
        return f"Node({self.data})"


# =====================================================================
# Stack (LIFO) Implementation
# =====================================================================

class Stack(Generic[T]):
    """
    Academic LIFO (Last-In, First-Out) Stack built via a pointer-based singly linked list.

    Complexity:
        - push():     O(1) Time | O(1) Space
        - pop():      O(1) Time | O(1) Space
        - peek():     O(1) Time | O(1) Space
        - is_empty(): O(1) Time | O(1) Space
        - size():     O(1) Time | O(1) Space

    Usage in Klondike Solitaire:
        - Foundation piles (Ace to King build-ups).
        - Waste pile (drawn cards stacked face-up).
        - Undo and Redo command history stacks.
    """

    def __init__(self) -> None:
        self._top: Optional[Node[T]] = None
        self._size: int = 0

    def push(self, item: T) -> None:
        """
        Pushes an item onto the top of the stack.
        Time Complexity: O(1)
        """
        new_node = Node(item, next_node=self._top)
        self._top = new_node
        self._size += 1

    def pop(self) -> T:
        """
        Removes and returns the item from the top of the stack.
        Raises IndexError if the stack is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise IndexError("pop from empty Stack")
        assert self._top is not None
        popped_data = self._top.data
        self._top = self._top.next
        self._size -= 1
        return popped_data

    def peek(self) -> Optional[T]:
        """
        Returns the item at the top of the stack without removing it.
        Returns None if the stack is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        assert self._top is not None
        return self._top.data

    def is_empty(self) -> bool:
        """
        Returns True if the stack contains no elements, False otherwise.
        Time Complexity: O(1)
        """
        return self._size == 0

    def size(self) -> int:
        """
        Returns the total number of items currently in the stack.
        Time Complexity: O(1)
        """
        return self._size

    def clear(self) -> None:
        """
        Empties the stack in O(1) time by dropping the top pointer.
        Time Complexity: O(1)
        """
        self._top = None
        self._size = 0

    def to_list(self) -> List[T]:
        """
        Returns items from bottom to top as a Python list (useful for display & snapshots).
        Time Complexity: O(N)
        """
        items: List[T] = []
        curr = self._top
        while curr is not None:
            items.append(curr.data)
            curr = curr.next
        items.reverse()  # Reverse so index 0 is bottom, index -1 is top
        return items

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        """Yields items from top to bottom."""
        curr = self._top
        while curr is not None:
            yield curr.data
            curr = curr.next

    def __repr__(self) -> str:
        return f"Stack(size={self._size}, top={self.peek()})"


# =====================================================================
# Queue (FIFO) Implementation
# =====================================================================

class Queue(Generic[T]):
    """
    Academic FIFO (First-In, First-Out) Queue built via linked nodes with
    explicit head (front) and tail (rear) pointers.

    Complexity:
        - enqueue():  O(1) Time | O(1) Space
        - dequeue():  O(1) Time | O(1) Space
        - peek():     O(1) Time | O(1) Space
        - prepend():  O(1) Time | O(1) Space (for exact LIFO undo operations)
        - is_empty(): O(1) Time | O(1) Space
        - size():     O(1) Time | O(1) Space

    Usage in Klondike Solitaire:
        - Stockpile (cards dealt from the front in strict FIFO draw sequence).
    """

    def __init__(self) -> None:
        self._head: Optional[Node[T]] = None  # Front of queue (dequeue end)
        self._tail: Optional[Node[T]] = None  # Rear of queue (enqueue end)
        self._size: int = 0

    def enqueue(self, item: T) -> None:
        """
        Adds an item to the rear of the queue.
        Time Complexity: O(1)
        """
        new_node = Node(item)
        if self.is_empty():
            self._head = new_node
            self._tail = new_node
        else:
            assert self._tail is not None
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def dequeue(self) -> T:
        """
        Removes and returns the item from the front of the queue.
        Raises IndexError if the queue is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise IndexError("dequeue from empty Queue")
        assert self._head is not None
        dequeued_data = self._head.data
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return dequeued_data

    def peek(self) -> Optional[T]:
        """
        Returns the item at the front of the queue without removing it.
        Returns None if the queue is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        assert self._head is not None
        return self._head.data

    def prepend(self, item: T) -> None:
        """
        Inserts an item back at the front of the queue.
        Academic Note: Essential for O(1) exact reversal of a dequeue operation during Undo.
        Time Complexity: O(1)
        """
        new_node = Node(item, next_node=self._head)
        self._head = new_node
        if self._tail is None:
            self._tail = new_node
        self._size += 1

    def is_empty(self) -> bool:
        """
        Returns True if the queue contains no elements, False otherwise.
        Time Complexity: O(1)
        """
        return self._size == 0

    def size(self) -> int:
        """
        Returns the total number of items currently in the queue.
        Time Complexity: O(1)
        """
        return self._size

    def clear(self) -> None:
        """
        Empties the queue in O(1) time.
        Time Complexity: O(1)
        """
        self._head = None
        self._tail = None
        self._size = 0

    def to_list(self) -> List[T]:
        """
        Returns items from front to rear as a Python list.
        Time Complexity: O(N)
        """
        items: List[T] = []
        curr = self._head
        while curr is not None:
            items.append(curr.data)
            curr = curr.next
        return items

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        """Yields items from front to rear."""
        curr = self._head
        while curr is not None:
            yield curr.data
            curr = curr.next

    def __repr__(self) -> str:
        return f"Queue(size={self._size}, front={self.peek()})"


# =====================================================================
# Doubly Linked List Implementation
# =====================================================================

class DoublyLinkedList(Generic[T]):
    """
    Academic Doubly Linked List with head and tail pointers.

    Key Features:
        - Bidirectional traversal.
        - O(1) tail/head insertions and deletions.
        - Sublist Slicing: O(k) extraction of runs from an arbitrary starting node.
        - Splicing: O(1) pointer-based concatenation of another DoublyLinkedList.

    Complexity:
        - append():           O(1) Time | O(1) Space
        - prepend():          O(1) Time | O(1) Space
        - pop_tail():         O(1) Time | O(1) Space
        - peek_tail():        O(1) Time | O(1) Space
        - peek_head():        O(1) Time | O(1) Space
        - search():           O(N) Time | O(1) Space
        - split_sublist():    O(k) Time (count slice nodes) | O(1) pointer rewiring
        - splice():           O(1) Time | O(1) Space

    Usage in Klondike Solitaire:
        - The 7 Tableau columns, enabling multi-card face-up runs to be sliced
          from a source column and spliced onto a destination column in constant time.
    """

    def __init__(self) -> None:
        self.head: Optional[Node[T]] = None
        self.tail: Optional[Node[T]] = None
        self._size: int = 0

    def append(self, item: T) -> Node[T]:
        """
        Appends an item to the tail of the list.
        Time Complexity: O(1)
        """
        new_node = Node(item, next_node=None, prev_node=self.tail)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1
        return new_node

    def prepend(self, item: T) -> Node[T]:
        """
        Prepends an item to the head of the list.
        Time Complexity: O(1)
        """
        new_node = Node(item, next_node=self.head, prev_node=None)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            assert self.head is not None
            self.head.prev = new_node
            self.head = new_node
        self._size += 1
        return new_node

    def pop_tail(self) -> T:
        """
        Removes and returns the item at the tail of the list.
        Raises IndexError if list is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise IndexError("pop_tail from empty DoublyLinkedList")
        assert self.tail is not None
        removed_data = self.tail.data
        if self._size == 1:
            self.head = None
            self.tail = None
        else:
            self.tail = self.tail.prev
            assert self.tail is not None
            self.tail.next = None
        self._size -= 1
        return removed_data

    def pop_head(self) -> T:
        """
        Removes and returns the item at the head of the list.
        Raises IndexError if list is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise IndexError("pop_head from empty DoublyLinkedList")
        assert self.head is not None
        removed_data = self.head.data
        if self._size == 1:
            self.head = None
            self.tail = None
        else:
            self.head = self.head.next
            assert self.head is not None
            self.head.prev = None
        self._size -= 1
        return removed_data

    def peek_tail(self) -> Optional[T]:
        """
        Returns the data of the tail node without removing it.
        Time Complexity: O(1)
        """
        return self.tail.data if self.tail is not None else None

    def peek_head(self) -> Optional[T]:
        """
        Returns the data of the head node without removing it.
        Time Complexity: O(1)
        """
        return self.head.data if self.head is not None else None

    def is_empty(self) -> bool:
        """Returns True if the list contains no nodes, False otherwise."""
        return self._size == 0

    def size(self) -> int:
        """Returns the total number of nodes in the list."""
        return self._size

    def search(self, predicate: Callable[[T], bool]) -> Optional[Node[T]]:
        """
        Traverses forward from head to find the first node satisfying the predicate.
        Time Complexity: O(N)
        """
        curr = self.head
        while curr is not None:
            if predicate(curr.data):
                return curr
            curr = curr.next
        return None

    def find_node(self, target_value: T) -> Optional[Node[T]]:
        """
        Traverses forward to find a node whose data equals target_value.
        Time Complexity: O(N)
        """
        return self.search(lambda x: x == target_value)

    def split_sublist(self, start_node: Node[T]) -> "DoublyLinkedList[T]":
        """
        Splits this list at `start_node`, detaching `start_node` through `self.tail`
        from this list and returning a new DoublyLinkedList containing the severed run.

        Time Complexity:
            - Pointer adjustment: O(1)
            - Size calculation:   O(k) where k is the number of severed nodes
        """
        if self.is_empty():
            raise ValueError("Cannot split an empty DoublyLinkedList")

        # Count severed nodes to maintain accurate sizes
        k = 0
        curr: Optional[Node[T]] = start_node
        while curr is not None:
            k += 1
            curr = curr.next

        new_list: DoublyLinkedList[T] = DoublyLinkedList()
        old_tail = self.tail

        if start_node is self.head:
            # Slicing the entire list
            new_list.head = self.head
            new_list.tail = self.tail
            new_list._size = self._size

            self.head = None
            self.tail = None
            self._size = 0
        else:
            # Severing a mid-to-end portion
            prev_node = start_node.prev
            assert prev_node is not None
            prev_node.next = None
            start_node.prev = None

            self.tail = prev_node
            self._size -= k

            new_list.head = start_node
            new_list.tail = old_tail
            new_list._size = k

        return new_list

    def splice(self, other: "DoublyLinkedList[T]") -> None:
        """
        Splices another DoublyLinkedList to the tail of this list in O(1) time.
        Transfers all nodes from `other` and clears `other`.

        Time Complexity: O(1)
        """
        if other.is_empty():
            return

        if self.is_empty():
            self.head = other.head
            self.tail = other.tail
            self._size = other._size
        else:
            assert self.tail is not None
            assert other.head is not None
            self.tail.next = other.head
            other.head.prev = self.tail
            self.tail = other.tail
            self._size += other._size

        # Reset other list to empty state
        other.head = None
        other.tail = None
        other._size = 0

    def get_node_at(self, index: int) -> Optional[Node[T]]:
        """
        Returns the node at the specified 0-based index.
        Time Complexity: O(N)
        """
        if index < 0 or index >= self._size:
            return None
        curr = self.head
        for _ in range(index):
            if curr is None:
                return None
            curr = curr.next
        return curr

    def traverse_forward(self) -> Iterator[T]:
        """Yields items from head to tail."""
        curr = self.head
        while curr is not None:
            yield curr.data
            curr = curr.next

    def traverse_backward(self) -> Iterator[T]:
        """Yields items from tail to head."""
        curr = self.tail
        while curr is not None:
            yield curr.data
            curr = curr.prev

    def to_list(self) -> List[T]:
        """Converts DoublyLinkedList to Python list (head to tail)."""
        return list(self.traverse_forward())

    def clear(self) -> None:
        """Clears the list in O(1) time."""
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        return self.traverse_forward()

    def __contains__(self, item: Any) -> bool:
        """Returns True if item is found in the list."""
        return self.find_node(item) is not None

    def __repr__(self) -> str:
        items = self.to_list()
        return f"DoublyLinkedList(size={self._size}, items={items})"
