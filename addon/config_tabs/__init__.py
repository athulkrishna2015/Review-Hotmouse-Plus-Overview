from .general import general_tab
from .support import support_tab
from .hotkeys import HotkeyTabManager, hotkey_tabs
from .trackpad import apply_trackpad_actions, get_trackpad_action, trackpad_tab

__all__ = [
    "HotkeyTabManager",
    "apply_trackpad_actions",
    "general_tab",
    "get_trackpad_action",
    "hotkey_tabs",
    "support_tab",
    "trackpad_tab",
]
