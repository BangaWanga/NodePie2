from __future__ import annotations
from utils import is_iterable
from multi import spawn


class Tree:
    def __init__(self, value=None):
        self.value = value
        self.children = []

    def __add__(self, other):
        self.children.append(other)

    def __is_leaf(self) -> bool:
        return len(self.children) == 0

    @staticmethod
    def __iterable__(d: dict):
        new_node = Tree()


class InfoBox(object):
    def __init__(self, name: str = "", items: list = None, values: list = None):
        assert len(items) == len(values)
        self.name = name
        self.items = items
        self.value = values

    def __save_as_json__(self) -> str:
        raise NotImplementedError

    def __is_serializable__(self) -> bool:
        raise NotImplementedError

    def __detect_structure__(self) -> Tree:
        raise NotImplementedError


