"""
Description: 前端后端同步调用API。
"""
from dataclasses import dataclass, field


@dataclass
class SessionData:
    phase: str = 'waiting'
    state = 0
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)
    confirmed: int = 0


data = SessionData()
