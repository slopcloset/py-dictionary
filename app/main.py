from __future__ import annotations
from typing import Any
from dataclasses import dataclass


_DELETED = object()


@dataclass
class Node:
    key: Any
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
            self.nodes[index] = Node(key, value)
            self.size += 1

    def __getitem__(self, key: Any) -> Any:
        index, found = self._find_slot(key)
        if found and self.nodes[index] is not None:
            return self.nodes[index].value  # type: ignore
        else:
            raise KeyError(f"Key not found: {key}")

    def __len__(self) -> int:
        return self.size

    def clear(self) -> None:
        self._set_to_defaults()

    def __delitem__(self, key: Any) -> None:
        index, found = self._find_slot(key)
        if found and self.nodes[index] is not None:
            self.nodes[index] = _DELETED
            self.size -= 1
        else:
            raise KeyError(f"Key not found: {key}")

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
            self.nodes[index] = _DELETED
            self.size -= 1
            return value
        elif default is not None:
            return default
        else:
            raise KeyError(f"Key not found: {key}")

    def update(self, other_dict: Dictionary) -> None:
        for node in other_dict.nodes:
            if node is not None:
                self[node.key] = node.value

    def __iter__(self) -> Any:
        return iter([node.key for node in self.nodes
                     if node is not None and node is not _DELETED])

    def _find_slot(self, key: Any) -> tuple[int, bool]:
        index = hash(key) % self.capacity
        original_index = index
        first_deleted = None

        while True:
            current = self.nodes[index]

            if current is None:
                slot = first_deleted if first_deleted is not None else index
                return slot, False

            if current is _DELETED:
                if first_deleted is None:
                    first_deleted = index

            if (current is not None
               and current is not _DELETED
               and current.key == key):
                return index, True

            index = (index + 1) % self.capacity
            if index == original_index:
                break

        slot = first_deleted if first_deleted is not None else index
        return slot, False

    def _resize(self) -> None:
        old_nodes = self.nodes

        self.capacity *= 2
        self.size = 0
        self.nodes = [None] * self.capacity

        for node in old_nodes:
            if node is not None and node is not _DELETED:
                self[node.key] = node.value

    def _needs_resize(self) -> bool:
        return self.size / self.capacity >= self.load_factor

    def _set_to_defaults(self) -> None:
        self.capacity = 8
        self.size = 0
        self.load_factor = 0.75
        self.nodes: list[Node | Any] = [None] * self.capacity
