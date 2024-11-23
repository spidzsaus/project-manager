from __future__ import annotations

class IDComparable:
    id: object
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash((type(self), self.id))