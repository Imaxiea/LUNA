from dataclasses import dataclass
from enum import Enum


class ButtonType(Enum):
    """鼠标按键类型。"""

    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    X1 = "x1"
    X2 = "x2"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ClickEvent:
    """鼠标点击事件。"""

    x: int
    y: int
    button: ButtonType
    timestamp: float