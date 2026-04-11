from typing import Callable, Dict, Optional, Set, Tuple
from enum import Enum

from aqt import mw
from aqt.qt import Qt, QPoint
from aqt.utils import tooltip

if False:  # typing-only
    from .manager import HotmouseManager

_manager: Optional["HotmouseManager"] = None


def set_manager(manager: "HotmouseManager") -> None:
    global _manager
    _manager = manager


def turn_on() -> None:
    if _manager and not _manager.enabled:
        _manager.enable()
        tooltip("Enabled hotmouse")


def turn_off() -> None:
    if _manager and _manager.enabled:
        _manager.disable()
        tooltip("Disabled hotmouse")


def toggle_on_off() -> None:
    if not _manager:
        return
    if _manager.enabled:
        _manager.disable()
        tooltip("Disabled hotmouse")
    else:
        _manager.enable()
        tooltip("Enabled hotmouse")


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


def show_answer() -> None:
    if mw.state == "review" and getattr(mw.reviewer, "state", None) == "question":
        try:
            mw.reviewer._showAnswer()
        except Exception:
            pass


def _study_now_from_overview() -> None:
    if mw.state != "overview" or not hasattr(mw, "overview") or mw.overview is None:
        return
    try:
        if hasattr(mw.overview, "onStudy") and callable(mw.overview.onStudy):
            mw.overview.onStudy()
            return
    except Exception:
        pass
    try:
        if hasattr(mw.overview, "_linkHandler") and callable(mw.overview._linkHandler):
            mw.overview._linkHandler("study")
            return
    except Exception:
        pass


def _go_deck_browser() -> None:
    try:
        if hasattr(mw, "onDeckBrowser") and callable(mw.onDeckBrowser):
            mw.onDeckBrowser()
        elif hasattr(mw, "moveToState"):
            mw.moveToState("deckBrowser")
    except Exception:
        pass


def _is_congrats_screen() -> bool:
    if mw.state != "review":
        return False
    r = getattr(mw, "reviewer", None)
    rstate = getattr(r, "state", None)
    return rstate not in ("question", "answer")


class Button(Enum):
    left = Qt.MouseButton.LeftButton
    right = Qt.MouseButton.RightButton
    middle = Qt.MouseButton.MiddleButton
    xbutton1 = Qt.MouseButton.XButton1
    xbutton2 = Qt.MouseButton.XButton2


class WheelDir(Enum):
    DOWN = -1
    UP = 1
    LEFT = 2
    RIGHT = 3

    @classmethod
    def from_qt(
        cls, angle_delta: QPoint, invert_x: bool = True
    ) -> Tuple[Optional["WheelDir"], int]:
        # When invert_x is True (natural scrolling), negate deltaX so that
        # LEFT/RIGHT match the physical swipe direction rather than the
        # scroll direction.
        dx = -angle_delta.x() if invert_x else angle_delta.x()
        dy = angle_delta.y()
        if abs(dy) >= abs(dx) and dy != 0:
            return (cls.UP if dy > 0 else cls.DOWN), dy
        elif abs(dx) > abs(dy) and dx != 0:
            return (cls.RIGHT if dx > 0 else cls.LEFT), dx
        return None, 0

    @classmethod
    def from_web(
        cls, dx: float, dy: float, invert_x: bool = True
    ) -> Tuple[Optional["WheelDir"], float]:
        # When invert_x is True (natural scrolling), negate deltaX.
        if invert_x:
            dx = -dx
        if abs(dy) >= abs(dx) and dy != 0:
            return (cls.DOWN if dy > 0 else cls.UP), dy
        elif abs(dx) > abs(dy) and dx != 0:
            return (cls.RIGHT if dx > 0 else cls.LEFT), dx
        return None, 0


ACTIONS: Dict[str, Callable[[], None]] = {
    "": lambda: None,
    "<none>": lambda: None,
    "on": turn_on,
    "off": turn_off,
    "on_off": toggle_on_off,
    "undo": lambda: mw.onUndo() if mw.form.actionUndo.isEnabled() else None,
    "undo_hotmouse": lambda: _manager.undo_last_hotmouse_action() if _manager else None,
    "show_ans": show_answer,
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
    "study_now": _study_now_from_overview,
    "deck_browser": _go_deck_browser,
}

ACTION_OPTS = list(ACTIONS.keys())

_HOTMOUSE_UNDO_TRACK_SKIP_ACTIONS: Set[str] = {
    "",
    "<none>",
    "undo",
    "undo_hotmouse",
}

_NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS: Set[str] = {
    "on",
    "off",
    "on_off",
    "show_ans",
    "study_now",
    "deck_browser",
    "audio",
    "replay_voice",
    "record_voice",
}

__all__ = [
    "ACTION_OPTS",
    "ACTIONS",
    "Button",
    "WheelDir",
    "_HOTMOUSE_UNDO_TRACK_SKIP_ACTIONS",
    "_NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS",
    "_study_now_from_overview",
    "set_manager",
    "toggle_on_off",
]
