from enum import Enum


class DiffType(Enum):
    ADDED = 1
    REMOVED = 2
    SAME = 3
    MODIFIED = 4


class TextMode(Enum):
    FROMFILE = 1
    DIFF = 2
    FROMUSER = 3
