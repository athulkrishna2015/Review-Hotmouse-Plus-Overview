from typing import Any, Callable, List, Dict, Optional, Tuple, Set, no_type_check

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
    "undo_hotmouse": lambda: manager.undo_last_hotmouse_action(),
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

_HOTMOUSE_UNDO_TRACKED_ACTIONS: Set[str] = {
    "again",
    "hard",
    "good",
    "easy",
    "delete",
    "suspend_card",
    "suspend_note",
    "bury_card",
    "bury_note",
    "mark",
    "red",
    "orange",
    "green",
    "blue",
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
        self._suspend_reasons: Set[str] = set()
        self._suspend_prev_enabled: bool = False
        self._hotmouse_undo_text: Optional[str] = None
        self._track_hotmouse_undo_next: bool = False
        self._track_hotmouse_undo_set_at: Optional[datetime.datetime] = None
        self.refresh_shortcuts()

    def add_menu(self) -> None:
        # Add Config option
        from .config import conf
        self.conf_action = QAction("Review Hotmouse Config", mw)
        self.conf_action.triggered.connect(conf.open_config)
        mw.form.menuTools.addAction(self.conf_action)

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def suspend(self, reason: str) -> None:
        if reason in self._suspend_reasons:
            return
        if not self._suspend_reasons:
            self._suspend_prev_enabled = self.enabled
            if self.enabled:
                self.disable()
        self._suspend_reasons.add(reason)

    def resume(self, reason: str) -> None:
        if reason not in self._suspend_reasons:
            return
        self._suspend_reasons.remove(reason)
        if not self._suspend_reasons:
            if self._suspend_prev_enabled:
                self.enable()
            self._suspend_prev_enabled = False

    def refresh_shortcuts(self) -> None:
        self.has_wheel_hotkey = any("wheel" in s for s in config["shortcuts"].keys())
        print("has wheel", self.has_wheel_hotkey)

    def mark_next_undo_as_hotmouse(self, action_str: str) -> None:
        if action_str in _HOTMOUSE_UNDO_TRACKED_ACTIONS:
            self._track_hotmouse_undo_next = True
            self._track_hotmouse_undo_set_at = datetime.datetime.now()

    def on_undo_state_did_change(self, info: Any) -> None:
        undo_text = getattr(info, "undo_text", None)
        can_undo = bool(getattr(info, "can_undo", False))

        if self._track_hotmouse_undo_next:
            self._track_hotmouse_undo_next = False
            age_ok = False
            if self._track_hotmouse_undo_set_at is not None:
                age = datetime.datetime.now() - self._track_hotmouse_undo_set_at
                age_ok = age.total_seconds() <= 5
            self._track_hotmouse_undo_set_at = None
            if age_ok and can_undo and isinstance(undo_text, str):
                self._hotmouse_undo_text = undo_text
            else:
                self._hotmouse_undo_text = None
            return

        # If the undo head changes due to non-hotmouse actions, drop the token.
        if self._hotmouse_undo_text and (
            not can_undo or undo_text != self._hotmouse_undo_text
        ):
            self._hotmouse_undo_text = None

    def undo_last_hotmouse_action(self) -> None:
        tracked_undo_text = self._hotmouse_undo_text
        if not tracked_undo_text:
            return

        info = mw.undo_actions_info()
        can_undo = bool(getattr(info, "can_undo", False))
        undo_text = getattr(info, "undo_text", None)
        if not can_undo or undo_text != tracked_undo_text:
            self._hotmouse_undo_text = None
            return

        self._hotmouse_undo_text = None
        mw.undo()

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
        if action_str == "undo" and hotkey_str in ("q_click_right", "a_click_right"):
            # Backward-compatible behavior: right-click undo is scoped to hotmouse actions.
            action_str = "undo_hotmouse"

        if not self.enabled and action_str not in ("on", "on_off"):
            return False

        if not action_str:
            return False

        if config["tooltip"]:
            tooltip(action_str)

        self.mark_next_undo_as_hotmouse(action_str)
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
        # Double-click middle button to toggle addon
        if event.type() == QEvent.Type.MouseButtonDblClick:
            if isinstance(event, QMouseEvent) and event.button() == Qt.MouseButton.MiddleButton:
                toggle_on_off()
                return True

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
            if isinstance(event, QWheelEvent):
                # 1. Scrollbar check
                if config.get("wheel_ignore_scrollbar", True):
                    width = 0
                    if hasattr(obj, "width") and isinstance(obj.width, (int, float)):
                        width = obj.width
                    elif hasattr(obj, "width") and callable(obj.width):
                        width = obj.width()
                    elif hasattr(obj, "geometry"):
                        width = obj.geometry().width()

                    if width > 0:
                        try:
                            # Qt6
                            x = event.position().x()
                        except AttributeError:
                            # Qt5
                            x = event.pos().x()

                        if x > width - 30:
                            return False

                # 2. Bottom bar check (only relevant in review)
                if config.get("wheel_only_on_bottom_bar", False) and mw.state == "review":
                    is_bottom = False
                    curr = obj
                    while curr:
                        if curr == mw.bottomWeb:
                            is_bottom = True
                            break
                        try:
                            curr = curr.parent()
                        except AttributeError:
                            break
                    if not is_bottom:
                        return False

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

# Resolve context classes lazily to avoid import-order timing issues.
def _aqt_context_type(module_name: str, class_name: str) -> Optional[type]:
    module = getattr(aqt, module_name, None)
    cls = getattr(module, class_name, None)
    return cls if isinstance(cls, type) else None


def _is_overview_context(context: Any) -> bool:
    overview_type = _aqt_context_type("overview", "Overview")
    return bool(overview_type and isinstance(context, overview_type))


def _is_reviewer_context(context: Any) -> bool:
    reviewer_type = _aqt_context_type("reviewer", "Reviewer")
    return bool(reviewer_type and isinstance(context, reviewer_type))


def _is_review_state() -> bool:
    return getattr(mw, "state", None) == "review"

_EFDRC_EDIT_REASON = "efdr_edit"
_EFDRC_FOCUS_PREFIX = "EFDRC!focuson#"
_EFDRC_RELOAD = "EFDRC!reload"

def _handle_external_editing_message(message: str, context: Any) -> None:
    # "Edit Field During Review (Cloze)" sends these pycmd messages.
    if not isinstance(message, str):
        return
    normalized = message.strip()
    if normalized.startswith(_EFDRC_FOCUS_PREFIX):
        # Context can vary across Anki/EFDRC versions; fallback to review state.
        if _is_reviewer_context(context) or _is_review_state():
            manager.suspend(_EFDRC_EDIT_REASON)
    elif normalized == _EFDRC_RELOAD:
        # Always clear suspension on reload even if context changed.
        manager.resume(_EFDRC_EDIT_REASON)

def inject_web_content(web_content: WebContent, context: Optional[Any]) -> None:
    """Inject wheel detector into Reviewer and Overview webviews."""
    if not (_is_reviewer_context(context) or _is_overview_context(context)):
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
    _handle_external_editing_message(message, context)
    addon_key = "ReviewHotmouse#"
    if not message.startswith(addon_key):
        return handled

    req = json.loads(message[len(addon_key) :])  # type: Dict[str, Any]

    if req.get("key") == "wheel":
        # Check if we should ignore this wheel event based on location
        if config.get("wheel_ignore_scrollbar", True) and req.get("is_scrollbar"):
            return (False, None)

        if (
            config.get("wheel_only_on_bottom_bar", False)
            and not req.get("is_bottom")
            and mw.state == "review"
        ):
            return (False, None)

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
    manager.add_menu()
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
if hasattr(gui_hooks, "undo_state_did_change"):
    gui_hooks.undo_state_did_change.append(manager.on_undo_state_did_change)
