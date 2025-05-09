from __future__ import annotations

from typing import Any


class IDComparable:
    id: Any

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((type(self), self.id))
