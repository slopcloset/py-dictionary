from __future__ import annotations
from typing import Any
from dataclasses import dataclass


@dataclass
class Node:
    key: Any
    key_hash: int
    value: Any


class Dictionary:
    def __init__(self) -> None:
        self._set_to_defaults()

    def __setitem__(self, key: Any, value: Any) -> None:
        if self._needs_resize():
            self._resize()

        index, found = self._find_slot(key)

        if found:
            self.nodes[index].value = value  # type: ignore
        else:
            key_hash = hash(key)
            self.nodes[index] = Node(key, key_hash, value)
            self.size += 1

    def __getitem__(self, key: Any) -> Any:
        index, found = self._find_slot(key)
        if found and self.nodes[index] is not None:
            return self.nodes[index].value  # type: ignore
        else:
            raise KeyError(key)

    def __len__(self) -> int:
        return self.size

    def clear(self) -> None:
        self._set_to_defaults()

    def __delitem__(self, key: Any) -> None:
        index, found = self._find_slot(key)
        if found and self.nodes[index] is not None:
            self.nodes[index] = None
            self.size -= 1
        else:
            raise KeyError(key)

    def get(self, key: Any, default: Any = None) -> Any:
        index, found = self._find_slot(key)
        if found and self.nodes[index] is not None:
            return self.nodes[index].value  # type: ignore
        else:
            return default

    def pop(self, key: Any, default: Any = None) -> Any:
        index, found = self._find_slot(key)
        if found and self.nodes[index] is not None:
            value = self.nodes[index].value  # type: ignore
            self.nodes[index] = None
            self.size -= 1
            return value
        elif default is not None:
            return default
        else:
            raise KeyError(key)

    def update(self, other_dict: Dictionary) -> None:
        for node in other_dict.nodes:
            if node is not None:
                self[node.key] = node.value

    def __iter__(self) -> Any:
        return iter([node.key for node in self.nodes if node is not None])

    def _find_slot(self, key: Any) -> tuple[int, bool]:
        index = hash(key) % self.capacity
        original_index = index

        while self.nodes[index] is not None:
            if self.nodes[index].key == key:  # type: ignore
                return index, True
            index = (index + 1) % self.capacity
            if index == original_index:
                break

        return index, False

    def _resize(self) -> None:
        old_nodes = self.nodes

        self.capacity *= 2
        self.size = 0
        self.nodes = [None] * self.capacity

        for node in old_nodes:
            if node is not None:
                self[node.key] = node.value

    def _needs_resize(self) -> bool:
        return self.size / self.capacity >= self.load_factor

    def _set_to_defaults(self) -> None:
        self.capacity = 8
        self.size = 0
        self.load_factor = 0.75
        self.nodes: list[Node | None] = [None] * self.capacity
