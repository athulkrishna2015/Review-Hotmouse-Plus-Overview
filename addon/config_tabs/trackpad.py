from typing import List, Dict, Tuple, Set

from aqt.qt import *

from ..ankiaddonconfig import ConfigWindow
from ..event import ACTION_OPTS

TRACKPAD_ACTION_OPTS = ["<none>"] + [a for a in ACTION_OPTS if a not in ("", "<none>")]
TRACKPAD_CONTEXTS: List[Tuple[str, str]] = [
    ("q", "Question"),
    ("a", "Answer"),
    ("o", "Overview"),
    ("c", "Congratulations"),
]
TRACKPAD_DIRECTIONS: List[Tuple[str, str]] = [
    ("up", "Swipe Up"),
    ("down", "Swipe Down"),
    ("left", "Swipe Left"),
    ("right", "Swipe Right"),
]


def trackpad_hotkey(scope: str, direction: str) -> str:
    return f"{scope}_wheel_{direction}"


def get_trackpad_action(shortcuts: Dict[str, str], scope: str, direction: str) -> str:
    action = shortcuts.get(trackpad_hotkey(scope, direction), "<none>")
    if action not in ACTION_OPTS or action == "":
        return "<none>"
    return action


def apply_trackpad_actions(
    shortcuts: Dict[str, str], actions: Dict[Tuple[str, str], str]
) -> Dict[str, str]:
    updated = dict(shortcuts)
    for (scope, direction), action in actions.items():
        hotkey = trackpad_hotkey(scope, direction)
        if action in ACTION_OPTS and action not in ("", "<none>"):
            updated[hotkey] = action
        else:
            updated.pop(hotkey, None)
    return updated


def trackpad_tab(conf_window: ConfigWindow) -> None:
    tab = conf_window.add_tab("Trackpad Actions")
    tab.text(
        "Configure swipe actions for trackpads and smooth wheel gestures. "
        "These controls edit the plain wheel bindings for each screen.",
        multiline=True,
    )
    tab.text(
        "Distance threshold and smart scroll behavior still live in the General tab.",
        multiline=True,
    )
    tab.space(8)

    dropdowns: Dict[Tuple[str, str], QComboBox] = {}
    dirty_keys: Set[Tuple[str, str]] = set()
    sync_state = {"updating": False}

    for scope, label in TRACKPAD_CONTEXTS:
        group = tab.vcontainer()
        group.text(f"<b>{label}</b>", html=True, size=14)
        for direction, direction_label in TRACKPAD_DIRECTIONS:
            row = group.hlayout()
            row.text(direction_label)
            row.space(7)
            dropdown = QComboBox()
            dropdown.insertItems(0, TRACKPAD_ACTION_OPTS)
            row.addWidget(dropdown)
            row.stretch()
            dropdowns[(scope, direction)] = dropdown

            def mark_dirty(_idx: int, key: Tuple[str, str] = (scope, direction)) -> None:
                if not sync_state["updating"]:
                    dirty_keys.add(key)

            dropdown.currentIndexChanged.connect(mark_dirty)
        tab.hseparator()
        tab.space(6)

    def on_update() -> None:
        sync_state["updating"] = True
        shortcuts = conf_window.conf.get("shortcuts", {})
        for (scope, direction), dropdown in dropdowns.items():
            action = get_trackpad_action(shortcuts, scope, direction)
            dropdown.setCurrentIndex(TRACKPAD_ACTION_OPTS.index(action))
        sync_state["updating"] = False
        dirty_keys.clear()

    def save_trackpad_actions() -> None:
        if not dirty_keys:
            return
        shortcuts = conf_window.conf.get("shortcuts", {})
        actions = {
            key: TRACKPAD_ACTION_OPTS[dropdowns[key].currentIndex()]
            for key in dirty_keys
        }
        conf_window.conf.set("shortcuts", apply_trackpad_actions(shortcuts, actions))
        dirty_keys.clear()

    conf_window.widget_updates.append(on_update)
    conf_window.execute_on_save(save_trackpad_actions)
