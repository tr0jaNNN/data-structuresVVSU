from collections import deque
import copy
from typing import Any, List, Optional, Dict, Tuple


class BSTNode:
    def __init__(self, value: Any):
        self.value = value
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None

    def insert(self, value: Any):
        if value == self.value:
            return  # ignore duplicates for simplicity
        if value < self.value:
            if self.left:
                self.left.insert(value)
            else:
                self.left = BSTNode(value)
        else:
            if self.right:
                self.right.insert(value)
            else:
                self.right = BSTNode(value)

    def find_min(self) -> "BSTNode":
        node = self
        while node.left:
            node = node.left
        return node

    def delete(self, value: Any) -> Optional["BSTNode"]:
        if value < self.value:
            if self.left:
                self.left = self.left.delete(value)
        elif value > self.value:
            if self.right:
                self.right = self.right.delete(value)
        else:
            # found node
            if not self.left and not self.right:
                return None
            if not self.left:
                return self.right
            if not self.right:
                return self.left
            # two children: replace with inorder successor
            successor = self.right.find_min()
            self.value = successor.value
            self.right = self.right.delete(successor.value)
        return self

    def search(self, value: Any) -> bool:
        if value == self.value:
            return True
        if value < self.value:
            return self.left.search(value) if self.left else False
        return self.right.search(value) if self.right else False

    def preorder_serialize(self) -> List:
        """Serialize tree into list with None markers (preorder)."""
        out = [self.value]
        out += self.left.preorder_serialize() if self.left else [None]
        out += self.right.preorder_serialize() if self.right else [None]
        return out

    @staticmethod
    def preorder_deserialize(data: List) -> Tuple[Optional["BSTNode"], List]:
        """Deserialize from preorder list with None markers. Returns (node, remaining_list)."""
        if not data:
            return None, []
        head = data.pop(0)
        if head is None:
            return None, data
        node = BSTNode(head)
        node.left, data = BSTNode.preorder_deserialize(data)
        node.right, data = BSTNode.preorder_deserialize(data)
        return node, data


class BST:
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, value: Any):
        if self.root:
            self.root.insert(value)
        else:
            self.root = BSTNode(value)

    def delete(self, value: Any):
        if self.root:
            self.root = self.root.delete(value)

    def search(self, value: Any) -> bool:
        return self.root.search(value) if self.root else False

    def serialize(self) -> List:
        return self.root.preorder_serialize() if self.root else [None]

    def deserialize(self, data: List):
        data_copy = data.copy()
        node, _ = BSTNode.preorder_deserialize(data_copy)
        self.root = node

    def inorder_list(self) -> List:
        out = []

        def dfs(n: Optional[BSTNode]):
            if not n:
                return
            dfs(n.left)
            out.append(n.value)
            dfs(n.right)

        dfs(self.root)
        return out


class DataStructuresManager:
    def __init__(self):
        self.stack: List[Any] = []
        self.queue: deque = deque()
        self.bst: BST = BST()

        # history stores snapshots BEFORE each operation for undo
        self.history: List[Dict] = []
        # op_log stores performed operations (for display/export)
        self.op_log: List[Dict] = []

    def _snapshot(self) -> Dict:
        return {
            "stack": copy.deepcopy(self.stack),
            "queue": list(self.queue),
            "bst": copy.deepcopy(self.bst.serialize()),
        }

    def _restore(self, state: Dict):
        self.stack = copy.deepcopy(state["stack"])
        self.queue = deque(state["queue"])
        self.bst = BST()
        self.bst.deserialize(state["bst"])

    # Stack operations
    def push(self, value: Any):
        self.history.append(self._snapshot())
        self.stack.append(value)
        self.op_log.append({"ds": "stack", "op": "push", "value": value})

    def pop(self) -> Optional[Any]:
        if not self.stack:
            return None
        self.history.append(self._snapshot())
        val = self.stack.pop()
        self.op_log.append({"ds": "stack", "op": "pop", "value": val})
        return val

    # Queue operations
    def enqueue(self, value: Any):
        self.history.append(self._snapshot())
        self.queue.append(value)
        self.op_log.append({"ds": "queue", "op": "enqueue", "value": value})

    def dequeue(self) -> Optional[Any]:
        if not self.queue:
            return None
        self.history.append(self._snapshot())
        val = self.queue.popleft()
        self.op_log.append({"ds": "queue", "op": "dequeue", "value": val})
        return val

    # BST operations
    def bst_insert(self, value: Any):
        self.history.append(self._snapshot())
        self.bst.insert(value)
        self.op_log.append({"ds": "bst", "op": "insert", "value": value})

    def bst_delete(self, value: Any):
        existed = self.bst.search(value)
        self.history.append(self._snapshot())
        self.bst.delete(value)
        self.op_log.append({"ds": "bst", "op": "delete", "value": value, "existed": existed})

    def bst_search(self, value: Any) -> bool:
        self.op_log.append({"ds": "bst", "op": "search", "value": value})
        return self.bst.search(value)

    # Undo last operation (revert to previous snapshot)
    def undo(self) -> Optional[Dict]:
        if not self.history:
            return None
        prev_state = self.history.pop()
        # determine last op for log trimming
        last_op = self.op_log.pop() if self.op_log else None
        self._restore(prev_state)
        return last_op

    # Utilities
    def get_state(self) -> Dict:
        return {
            "stack": list(self.stack),
            "queue": list(self.queue),
            "bst_inorder": self.bst.inorder_list(),
            "bst_serialized": self.bst.serialize(),
        }

    def get_log(self) -> List[Dict]:
        return list(self.op_log)


# --- ASCII BST renderer (levels) ---

def bst_levels(serialized: List) -> str:
    """
    Быстрая визуализация дерева по уровням из сериализованного preorder списка с None-маркерами.
    Для учебной демонстрации: показывает nodes по уровням.
    """
    if serialized == [None]:
        return "[ empty ]"

    # восстановить дерево
    tree = BST()
    tree.deserialize(serialized)

    # BFS to collect levels
    from collections import deque
    q = deque()
    q.append(tree.root)
    levels = []
    while q:
        level_size = len(q)
        level_vals = []
        any_node = False
        for _ in range(level_size):
            node = q.popleft()
            if node is None:
                level_vals.append(".")
                q.append(None)
                q.append(None)
            else:
                any_node = True
                level_vals.append(str(node.value))
                q.append(node.left if node.left else None)
                q.append(node.right if node.right else None)
        if not any_node:
            break
        levels.append(level_vals)
    # create pretty lines with spacing
    lines = []
    width = max(len(level) for level in levels)
    for i, lvl in enumerate(levels):
        indent = " " * (2 ** (len(levels) - i - 1))
        line = indent + ("   ").join(v.center(3) for v in lvl)
        lines.append(line)
    return "\n".join(lines)

