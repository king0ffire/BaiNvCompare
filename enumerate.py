from enum import Enum

class DiffType(Enum):
    ADDED = 1
    REMOVED = 2
    SAME = 3
    MODIFIED = 4
