from typing import Any, Callable, List, Dict, Optional, Tuple, no_type_check

from enum import Enum

import datetime

import json

from anki.hooks import wrap

from aqt import mw, gui_hooks

from aqt.qt import *

from aqt.utils import tooltip

from aqt.webview import AnkiWebView, WebContent

import aqt

def WEBVIEW_TARGETS() -> List[AnkiWebView]:
    # Implemented as a function so attributes are resolved when called.
    # In case mw.web is reassigned to a different object
    return [mw.web, mw.bottomWeb]

config = mw.addonManager.getConfig(__name__)

def refresh_config() -> None:
    global config
    config = mw.addonManager.getConfig(__name__)
    manager.refresh_shortcuts()

def turn_on() -> None:
    if not manager.enabled:
        manager.enable()
        tooltip("Enabled hotmouse")

def turn_off() -> None:
    if manager.enabled:
        manager.disable()
        tooltip("Disabled hotmouse")

def toggle_on_off() -> None:
    if manager.enabled:
        manager.disable()
        tooltip("Disabled hotmouse")
    else:
        manager.enable()
        tooltip("Enabled hotmouse")

# event.py

def answer_again() -> None:
    if mw.reviewer.state == "answer":
        mw.reviewer._answerCard(1)

def answer_hard() -> None:
    if mw.reviewer.state == "answer":
        cnt = mw.col.sched.answerButtons(mw.reviewer.card)
        if cnt == 4:
            mw.reviewer._answerCard(2)

def answer_good() -> None:
    if mw.reviewer.state == "answer":
        cnt = mw.col.sched.answerButtons(mw.reviewer.card)
        if cnt == 2:
            mw.reviewer._answerCard(2)
        elif cnt == 3:
            mw.reviewer._answerCard(2)
        elif cnt == 4:
            mw.reviewer._answerCard(3)

def answer_easy() -> None:
    if mw.reviewer.state == "answer":
        cnt = mw.col.sched.answerButtons(mw.reviewer.card)
        if cnt == 3:
            mw.reviewer._answerCard(3)
        elif cnt == 4:
            mw.reviewer._answerCard(4)

def _study_now_from_overview() -> None:
    """Trigger the Overview 'Study Now' action if available."""
    if mw.state != "overview" or not hasattr(mw, "overview") or mw.overview is None:
        return
    try:
        if hasattr(mw.overview, "onStudy") and callable(mw.overview.onStudy):  # type: ignore[attr-defined]
            mw.overview.onStudy()  # type: ignore[attr-defined]
            return
    except Exception:
        pass
    try:
        if hasattr(mw.overview, "_linkHandler") and callable(mw.overview._linkHandler):  # type: ignore[attr-defined]
            mw.overview._linkHandler("study")  # type: ignore[attr-defined]
            return
    except Exception:
        pass

def _go_deck_browser() -> None:
    """Navigate to the Deck Browser (same as pressing D)."""
    try:
        if hasattr(mw, "onDeckBrowser") and callable(mw.onDeckBrowser):
            mw.onDeckBrowser()
        elif hasattr(mw, "moveToState"):
            mw.moveToState("deckBrowser")  # type: ignore[arg-type]
    except Exception:
        pass

def _is_congrats_screen() -> bool:
    """Heuristic for the 'Congratulations' summary screen."""
    if mw.state != "review":
        return False
    r = getattr(mw, "reviewer", None)
    rstate = getattr(r, "state", None)
    return rstate not in ("question", "answer")

ACTIONS: Dict[str, Callable[[], None]] = {
    "": lambda: None,
    "on": turn_on,
    "off": turn_off,
    "on_off": toggle_on_off,
    "undo": lambda: mw.onUndo() if mw.form.actionUndo.isEnabled() else None,
    "show_ans": lambda: mw.reviewer._getTypedAnswer(),
    "again": answer_again,
    "hard": answer_hard,
    "good": answer_good,
    "easy": answer_easy,
    "delete": lambda: mw.reviewer.onDelete(),
    "suspend_card": lambda: mw.reviewer.onSuspendCard(),
    "suspend_note": lambda: mw.reviewer.onSuspend(),
    "bury_card": lambda: mw.reviewer.onBuryCard(),
    "bury_note": lambda: mw.reviewer.onBuryNote(),
    "mark": lambda: mw.reviewer.onMark(),
    "red": lambda: mw.reviewer.setFlag(1),
    "orange": lambda: mw.reviewer.setFlag(2),
    "green": lambda: mw.reviewer.setFlag(3),
    "blue": lambda: mw.reviewer.setFlag(4),
    "audio": lambda: mw.reviewer.replayAudio(),
    "record_voice": lambda: mw.reviewer.onRecordVoice(),
    "replay_voice": lambda: mw.reviewer.onReplayRecorded(),
    # Overview
    "study_now": _study_now_from_overview,
    # New: go to Deck Browser (for o_* and c_* mappings)
    "deck_browser": _go_deck_browser,
}

ACTION_OPTS = list(ACTIONS.keys())

class Button(Enum):
    left = Qt.MouseButton.LeftButton
    right = Qt.MouseButton.RightButton
    middle = Qt.MouseButton.MiddleButton
    xbutton1 = Qt.MouseButton.XButton1
    xbutton2 = Qt.MouseButton.XButton2

class WheelDir(Enum):
    DOWN = -1
    UP = 1

    @classmethod
    def from_qt(cls, angle_delta: QPoint) -> Optional["WheelDir"]:
        delta = angle_delta.y()
        if delta > 0:
            return cls.UP
        elif delta < 0:
            return cls.DOWN
        else:
            return None

    @classmethod
    def from_web(cls, delta: int) -> Optional["WheelDir"]:
        # web and qt have opposite delta sign
        if delta < 0:
            return cls.UP
        elif delta > 0:
            return cls.DOWN
        else:
            return None

class HotmouseManager:
    has_wheel_hotkey: bool

    def __init__(self) -> None:
        self.enabled = config["default_enabled"]
        self.last_scroll_time = datetime.datetime.now()
        self.last_click_time = datetime.datetime.now()  # NEW: Track last click time
        self.add_menu()
        self.refresh_shortcuts()

    def add_menu(self) -> None:
        self.action = QAction("Enable/Disable Review Hotmouse", mw)
        self.action.triggered.connect(toggle_on_off)
        mw.form.menuTools.addAction(self.action)
        self.update_menu()

    def update_menu(self) -> None:
        self.action.setText("Disable Review Hotmouse" if self.enabled else "Enable Review Hotmouse")

    def enable(self) -> None:
        self.enabled = True
        self.update_menu()

    def disable(self) -> None:
        self.enabled = False
        self.update_menu()

    def refresh_shortcuts(self) -> None:
        self.has_wheel_hotkey = any("wheel" in s for s in config["shortcuts"].keys())
        print("has wheel", self.has_wheel_hotkey)

    def uses_btn(self, btn: Button) -> bool:
        return any(btn.name in s for s in config["shortcuts"].keys())

    def uses_btn_in_scope(self, scope: str, btn: Button) -> bool:
        return any(k.startswith(f"{scope}_") and btn.name in k for k in config["shortcuts"].keys())

    @staticmethod
    def get_pressed_buttons(qbuttons: "Qt.MouseButton") -> List[Button]:
        buttons: List[Button] = []
        for b in Button:
            if qbuttons & b.value:  # type: ignore
                buttons.append(b)
        return buttons

    @staticmethod
    def build_hotkey(
        btns: List[Button],
        wheel: Optional[WheelDir] = None,
        click: Optional[Button] = None,
    ) -> str:
        # Overview / Reviewer (question/answer/congrats) scopes
        if mw.state == "overview":
            scope = "o"
        elif mw.state == "review":
            if mw.reviewer.state == "question":
                scope = "q"
            elif mw.reviewer.state == "answer":
                scope = "a"
            else:
                scope = "c"  # congratulations/summary
        else:
            scope = "x"

        parts: List[str] = [scope]
        for btn in btns:
            parts.append(f"press_{btn.name}")
        if click:
            parts.append(f"click_{click.name}")
        if wheel == WheelDir.UP:
            parts.append("wheel_up")
        elif wheel == WheelDir.DOWN:
            parts.append("wheel_down")
        return "_".join(parts)

    def execute_shortcut(self, hotkey_str: str) -> bool:
        if self.enabled and config["z_debug"]:
            tooltip(hotkey_str)

        action_str = config["shortcuts"].get(hotkey_str, "")

        if not self.enabled and action_str not in ("on", "on_off"):
            return False

        if not action_str:
            return False

        if config["tooltip"]:
            tooltip(action_str)

        ACTIONS[action_str]()  # run action

        # Let rating happen immediately after showing the answer
        if action_str == "show_ans":
            self.last_scroll_time -= datetime.timedelta(
                milliseconds=config.get("threshold_wheel_ms", 350) + 1
            )

        return True

    def on_mouse_press(self, event: QMouseEvent) -> bool:
        # NEW: Add click threshold check
        curr_time = datetime.datetime.now()
        time_diff = curr_time - self.last_click_time
        click_threshold_ms = config.get("threshold_click_ms", 0)
        
        # If threshold is set and not enough time has passed, ignore this click
        if click_threshold_ms > 0 and time_diff.total_seconds() * 1000 < click_threshold_ms:
            return self.enabled
        
        self.last_click_time = curr_time  # Update last click time
        
        btns = self.get_pressed_buttons(event.buttons())
        btn = event.button()
        try:
            pressed = Button(event.button())
            if pressed in btns:
                btns.remove(pressed)
        except ValueError:
            print(f"Review Hotmouse: Unknown Button Pressed: {btn}")
            return False

        hotkey_str = self.build_hotkey(btns, click=pressed)
        return self.execute_shortcut(hotkey_str)

    def on_mouse_scroll(self, event: QWheelEvent) -> bool:
        wheel_dir = WheelDir.from_qt(event.angleDelta())
        if wheel_dir is None:
            return False
        return self.handle_scroll(wheel_dir, event.buttons())

    def handle_scroll(self, wheel_dir: WheelDir, qbtns: "Qt.MouseButton") -> bool:
        curr_time = datetime.datetime.now()
        time_diff = curr_time - self.last_scroll_time
        self.last_scroll_time = curr_time

        if time_diff.total_seconds() * 1000 > config["threshold_wheel_ms"]:
            btns = self.get_pressed_buttons(qbtns)
            hotkey_str = self.build_hotkey(btns, wheel=wheel_dir)
            return self.execute_shortcut(hotkey_str)
        else:
            return self.enabled

class HotmouseEventFilter(QObject):
    @no_type_check
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        # Single path: let the hotkey system handle both Overview and Review (incl. Congrats)
        if event.type() == QEvent.Type.MouseButtonPress:
            if isinstance(event, QMouseEvent) and manager.on_mouse_press(event):
                return True

        # Swallow context menu when right-click is bound in current scope
        if event.type() == QEvent.Type.ContextMenu:
            # Overview
            if mw.state == "overview" and manager.uses_btn_in_scope("o", Button.right):
                return True
            # Review: question/answer
            if mw.state == "review" and manager.enabled and manager.uses_btn(Button.right):
                rstate = getattr(mw.reviewer, "state", None)
                if rstate in ("question", "answer"):
                    return True
            # Congrats as its own scope
            if _is_congrats_screen() and manager.uses_btn_in_scope("c", Button.right):
                return True

        # Native Qt wheel only used during reviewer; Overview wheel comes via JS
        if mw.state == "review" and event.type() == QEvent.Type.Wheel:
            if manager.has_wheel_hotkey and manager.on_mouse_scroll(event):  # type: ignore[arg-type]
                return True

        if event.type() == QEvent.Type.ChildAdded:
            add_event_filter(event.child())

        return False

def add_event_filter(object: QObject) -> None:
    object.installEventFilter(hotmouseEventFilter)
    for w in object.children():
        add_event_filter(w)

def on_context_menu(
    target: QWebEngineView,
    ev: QContextMenuEvent,
    _old: Callable = lambda t, e: None,
) -> None:
    if target not in WEBVIEW_TARGETS():
        _old(target, ev)
        return

    # When in review and the addon is actively using right-click, swallow menu
    if manager.enabled and mw.state == "review" and manager.uses_btn(Button.right):
        return None

    _old(target, ev)

# Safer class lookup for Overview/Reviewer types to avoid import timing issues
_OverviewT = getattr(getattr(aqt, "overview", object), "Overview", object)
_ReviewerT = getattr(getattr(aqt, "reviewer", object), "Reviewer", object)

def inject_web_content(web_content: WebContent, context: Optional[Any]) -> None:
    """Inject wheel detector into Reviewer and Overview webviews."""
    if not isinstance(context, (_ReviewerT, _OverviewT)):
        return
    addon_package = mw.addonManager.addonFromModule(__name__)
    web_content.js.append(f"/_addons/{addon_package}/web/detect_wheel.js")

def _has_overview_wheel_mappings() -> bool:
    """Returns True if any o_wheel_* shortcut exists."""
    sc = mw.addonManager.getConfig(__name__).get("shortcuts", {})
    return any(k.startswith("o_wheel_") for k in sc.keys())

def handle_js_message(
    handled: Tuple[bool, Any], message: str, context: Any
) -> Tuple[bool, Any]:
    """Receive pycmd message from detect_wheel.js and route via shortcuts."""
    addon_key = "ReviewHotmouse#"
    if not message.startswith(addon_key):
        return handled

    req = json.loads(message[len(addon_key) :])  # type: Dict[str, Any]

    if req.get("key") == "wheel":
        wheel_dir = WheelDir.from_web(int(req.get("value", 0)))
        if wheel_dir is None:
            return (False, None)

        qbtns = mw.app.mouseButtons()
        executed = manager.handle_scroll(wheel_dir, qbtns)

        # Fallback only if NO overview wheel mapping exists
        if (
            not executed
            and mw.state == "overview"
            and wheel_dir == WheelDir.DOWN
            and not _has_overview_wheel_mappings()
        ):
            _study_now_from_overview()
            executed = True

        return (executed, executed)

    return handled

def install_event_handlers() -> None:
    for target in WEBVIEW_TARGETS():
        add_event_filter(target)

    if hasattr(AnkiWebView, "contextMenuEvent"):
        AnkiWebView.contextMenuEvent = wrap(
            AnkiWebView.contextMenuEvent, on_context_menu, "around"
        )
    else:
        AnkiWebView.contextMenuEvent = on_context_menu

# Instantiate and register AFTER all functions are defined
manager = HotmouseManager()
hotmouseEventFilter = HotmouseEventFilter()

mw.addonManager.setWebExports(__name__, r"web/.*\.(css|js)")
gui_hooks.main_window_did_init.append(install_event_handlers)
gui_hooks.webview_will_show_context_menu.append(
    lambda wv, m: (
        not manager.enabled
        and mw.state == "review"
        and m.addAction("Enable Hotmouse").triggered.connect(turn_on)
    )
)
gui_hooks.webview_will_set_content.append(inject_web_content)
gui_hooks.webview_did_receive_js_message.append(handle_js_message)
