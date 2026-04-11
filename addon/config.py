from .ankiaddonconfig import ConfigManager, ConfigWindow
from .config_tabs import (
    HotkeyTabManager,
    apply_trackpad_actions,
    general_tab,
    get_trackpad_action,
    hotkey_tabs,
    support_tab,
    trackpad_tab,
)
from .event import refresh_config

__all__ = [
    "HotkeyTabManager",
    "apply_trackpad_actions",
    "get_trackpad_action",
]


def on_window_open(conf_window: "ConfigWindow") -> None:
    conf_window.execute_on_close(refresh_config)


conf = ConfigManager()
conf.use_custom_window()
conf.on_window_open(on_window_open)
conf.add_config_tab(general_tab)
conf.add_config_tab(hotkey_tabs)
conf.add_config_tab(trackpad_tab)
conf.add_config_tab(support_tab)
