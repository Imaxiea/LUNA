"""配置模块：集中管理鼠标点击监听选项。"""

from dataclasses import dataclass
from typing import Literal, get_args

ListenScope = Literal["global"]
ClickType = Literal["all", "left", "right", "middle"]
OutputTarget = Literal["stdout"]


@dataclass(frozen=True)
class Config:
    """监听配置。"""

    listen_scope: ListenScope = "global"
    click_type: ClickType = "all"
    output_target: OutputTarget = "stdout"

    def __post_init__(self) -> None:
        if self.listen_scope not in get_args(ListenScope):
            raise ValueError(f"Invalid listen_scope: {self.listen_scope}")
        if self.click_type not in get_args(ClickType):
            raise ValueError(f"Invalid click_type: {self.click_type}")
        if self.output_target not in get_args(OutputTarget):
            raise ValueError(f"Invalid output_target: {self.output_target}")


def load_config() -> Config:
    """加载监听配置，当前返回默认的全局监听、全部按键、stdout 输出。"""
    return Config()


__all__ = [
    "Config",
    "ClickType",
    "ListenScope",
    "OutputTarget",
    "load_config",
]
